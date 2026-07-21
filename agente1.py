"""
Sesión 1 de agentes · Mini-agente con el ciclo Pensar -> Actuar -> Observar

Idea: el LLM es solo el "cerebro" (genera texto). Es ESTE código el que
lee lo que dice, ejecuta acciones (herramientas) y le devuelve el resultado.
Repetimos el bucle hasta que el modelo da una respuesta final.

La única "herramienta" de hoy es una calculadora. El modelo NO sabe hacer
cuentas fiables, así que aprenderá a delegarlas en nuestra herramienta.
"""

import anthropic

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno


# --- 1. LA HERRAMIENTA (una simple función de Python) ---
def calculadora(expresion: str) -> str:
    """Evalúa una expresión aritmética, p. ej. '1234 * 5678'."""
    try:
        # Solo permitimos números y operadores básicos por seguridad.
        permitido = set("0123456789+-*/(). ")
        if not set(expresion) <= permitido:
            return "Error: la expresión contiene caracteres no permitidos."
        return str(eval(expresion))
    except Exception as e:
        return f"Error al calcular: {e}"


# --- 2. LAS INSTRUCCIONES (system prompt) ---
# Le enseñamos al modelo el "protocolo" para pedir la herramienta.
SISTEMA = """Eres un agente que resuelve tareas paso a paso.

Tienes UNA herramienta disponible:
- calculadora(expresion): devuelve el resultado de una operación aritmética.

En cada turno debes responder en UNA de estas dos formas EXACTAS:

1) Si necesitas calcular algo:
ACCION: calculadora(EXPRESION)

2) Si ya tienes la respuesta final para el usuario:
RESPUESTA: tu respuesta aquí

No escribas nada más fuera de ese formato."""


# --- 3. EL BUCLE DEL AGENTE ---
def agente(pregunta: str, max_pasos: int = 5) -> str:
    # El historial de la conversación: aquí se van acumulando los mensajes.
    mensajes = [{"role": "user", "content": pregunta}]

    for paso in range(1, max_pasos + 1):
        # --- PENSAR: el modelo decide qué hacer ---
        respuesta = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            system=SISTEMA,
            messages=mensajes,
        )
        texto = respuesta.content[0].text.strip()
        print(f"\n[Paso {paso}] El agente piensa:\n{texto}")

        # Guardamos lo que dijo el modelo en el historial.
        mensajes.append({"role": "assistant", "content": texto})

        # --- ¿Ha terminado? ---
        if texto.startswith("RESPUESTA:"):
            return texto[len("RESPUESTA:"):].strip()

        # --- ACTUAR: si pide una acción, la ejecutamos nosotros ---
        if texto.startswith("ACCION:"):
            # Extraemos lo que va dentro de calculadora( ... )
            dentro = texto[texto.find("(") + 1: texto.rfind(")")]
            resultado = calculadora(dentro)
            print(f"[Paso {paso}] Ejecuto calculadora({dentro}) = {resultado}")

            # --- OBSERVAR: le devolvemos el resultado al modelo ---
            mensajes.append({
                "role": "user",
                "content": f"OBSERVACION: el resultado es {resultado}",
            })
        else:
            # Si no siguió el formato, se lo recordamos.
            mensajes.append({
                "role": "user",
                "content": "Recuerda: responde solo con ACCION: o RESPUESTA:",
            })

    return "No llegué a una respuesta en el número de pasos permitido."


# --- 4. PROBARLO ---
if __name__ == "__main__":
    pregunta = "En un colegio hay 3 clases de 25, 28 y 22 alumnos. Si cada alumno paga 12 € para una excursión, "
    pregunta += "¿cuánto se recauda en total?"
    print(f"PREGUNTA: {pregunta}")
    final = agente(pregunta)
    print(f"\n==> RESPUESTA FINAL: {final}")
