"""
Sesión 2 de agentes · El agente lee archivos

Novedad respecto a la sesión 1: ahora el agente tiene una herramienta que
toca el mundo real (el sistema de archivos), no solo hace cuentas.
Le preguntamos algo sobre un documento que NO está en su cabeza; para
responder, tendrá que leerlo con la herramienta.

Es el mismo bucle Pensar -> Actuar -> Observar, con otra herramienta.
"""

import anthropic

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno


# --- 1. LA HERRAMIENTA: leer un archivo de texto ---
def leer_archivo(ruta: str) -> str:
    """Devuelve el contenido de un archivo de texto."""
    try:
        with open(ruta.strip(), "r", encoding="utf-8") as f:
            contenido = f.read()
        # Recortamos por si el archivo fuera enorme (hoy no lo será).
        return contenido[:4000]
    except FileNotFoundError:
        return f"Error: no existe el archivo '{ruta}'."
    except Exception as e:
        return f"Error al leer: {e}"


# --- 2. INSTRUCCIONES (protocolo de la herramienta) ---
SISTEMA = """Eres un agente que responde preguntas sobre documentos.

Tienes UNA herramienta disponible:
- leer_archivo(ruta): devuelve el texto de un archivo.

En cada turno responde en UNA de estas dos formas EXACTAS:

1) Si necesitas leer un archivo:
ACCION: leer_archivo(RUTA)

2) Si ya puedes responder al usuario:
RESPUESTA: tu respuesta aquí

No inventes el contenido del documento: si no lo has leído, léelo primero."""


# --- 3. EL BUCLE (idéntico en estructura al de la sesión 1) ---
def agente(pregunta: str, max_pasos: int = 5) -> str:
    mensajes = [{"role": "user", "content": pregunta}]

    for paso in range(1, max_pasos + 1):
        respuesta = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            system=SISTEMA,
            messages=mensajes,
        )
        texto = respuesta.content[0].text.strip()
        print(f"\n[Paso {paso}] El agente piensa:\n{texto}")
        mensajes.append({"role": "assistant", "content": texto})

        if texto.startswith("RESPUESTA:"):
            return texto[len("RESPUESTA:"):].strip()

        if texto.startswith("ACCION:"):
            ruta = texto[texto.find("(") + 1: texto.rfind(")")]
            resultado = leer_archivo(ruta)
            print(f"[Paso {paso}] Leo el archivo '{ruta}' ({len(resultado)} caracteres).")
            mensajes.append({
                "role": "user",
                "content": f"OBSERVACION: el contenido del archivo es:\n{resultado}",
            })
        else:
            mensajes.append({
                "role": "user",
                "content": "Recuerda: responde solo con ACCION: o RESPUESTA:",
            })

    return "No llegué a una respuesta en el número de pasos permitido."


# --- 4. PROBARLO ---
if __name__ == "__main__":
    # Preguntamos algo que el agente NO puede saber sin leer el archivo.
    pregunta = "Lee el archivo 'nota_prueba.txt' y dime en una frase de qué trata."
    print(f"PREGUNTA: {pregunta}")
    final = agente(pregunta)
    print(f"\n==> RESPUESTA FINAL: {final}")
