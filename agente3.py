"""
Sesión 3 de agentes · Tool use OFICIAL de la API

En la sesión 2 inventábamos el protocolo (ACCION: ...) y parseábamos texto
a mano. Aquí usamos el mecanismo REAL de la API de Anthropic:

- Describimos la herramienta en un formato estructurado (TOOLS).
- Cuando el modelo quiere usarla, la API devuelve un bloque 'tool_use'
  con los argumentos ya extraídos (stop_reason == "tool_use").
- Ejecutamos la función y devolvemos el resultado como 'tool_result'.

Es más robusto: ya no dependemos de que el modelo escriba el formato exacto.
"""

import anthropic

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno


# --- 1. LA HERRAMIENTA (función normal de Python) ---
def leer_archivo(ruta: str) -> str:
    try:
        with open(ruta.strip(), "r", encoding="utf-8") as f:
            return f.read()[:4000]
    except FileNotFoundError:
        return f"Error: no existe el archivo '{ruta}'."
    except Exception as e:
        return f"Error al leer: {e}"


# --- 2. DESCRIPCIÓN DE LA HERRAMIENTA PARA LA API ---
# Este esquema es lo que le permite a la API extraer los argumentos por ti.
TOOLS = [
    {
        "name": "leer_archivo",
        "description": "Lee y devuelve el contenido de un archivo de texto local.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta del archivo a leer, p. ej. 'nota_prueba.txt'.",
                }
            },
            "required": ["ruta"],
        },
    }
]

# Mapa nombre -> función, para ejecutar la que pida el modelo.
FUNCIONES = {"leer_archivo": leer_archivo}


# --- 3. EL BUCLE con tool use oficial ---
def agente(pregunta: str, max_pasos: int = 5) -> str:
    mensajes = [{"role": "user", "content": pregunta}]

    for paso in range(1, max_pasos + 1):
        respuesta = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            tools=TOOLS,               # <-- le pasamos las herramientas
            messages=mensajes,
        )

        # Guardamos la respuesta completa del modelo en el historial.
        mensajes.append({"role": "assistant", "content": respuesta.content})

        # --- ¿El modelo quiere usar una herramienta? ---
        if respuesta.stop_reason == "tool_use":
            # Puede pedir una o varias; procesamos todas.
            resultados = []
            for bloque in respuesta.content:
                if bloque.type == "tool_use":
                    nombre = bloque.name
                    args = bloque.input
                    print(f"\n[Paso {paso}] El agente usa la herramienta "
                          f"'{nombre}' con {args}")
                    salida = FUNCIONES[nombre](**args)   # ejecuta la función
                    resultados.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,        # enlaza pregunta-respuesta
                        "content": salida,
                    })
            # Devolvemos los resultados como un mensaje 'user'.
            mensajes.append({"role": "user", "content": resultados})
        else:
            # No pide herramienta: es la respuesta final en texto.
            for bloque in respuesta.content:
                if bloque.type == "text":
                    return bloque.text.strip()

    return "No llegué a una respuesta en el número de pasos permitido."


# --- 4. PROBARLO ---
if __name__ == "__main__":
    pregunta = "Lee el archivo 'nota_prueba.txt' y dime en una frase de qué trata."
    print(f"PREGUNTA: {pregunta}")
    final = agente(pregunta)
    print(f"\n==> RESPUESTA FINAL: {final}")
