"""
Sesión 4 de agentes · El mismo agente, pero con un FRAMEWORK (smolagents)

Compara esto con agente3.py. Allí escribimos a mano:
  - el bucle for con max_pasos
  - la detección de stop_reason == "tool_use"
  - la construcción de los bloques tool_result
  - el historial de mensajes

Aquí NADA de eso aparece: smolagents lo hace por dentro. Nosotros solo:
  1. definimos la herramienta con el decorador @tool
  2. elegimos el modelo
  3. creamos el agente y le damos la tarea

Requisitos (una vez):  uv add smolagents litellm
"""

from smolagents import tool, ToolCallingAgent, LiteLLMModel


# --- 1. LA HERRAMIENTA ---
# El decorador @tool convierte esta función en una herramienta para el agente.
# ¡El docstring NO es decorativo! smolagents lo lee para saber qué hace la
# herramienta y qué parámetros tiene. Por eso va tan detallado.
@tool
def leer_archivo(ruta: str) -> str:
    """Lee y devuelve el contenido de un archivo de texto local.

    Args:
        ruta: Ruta del archivo a leer, por ejemplo 'nota_prueba.txt'.
    """
    try:
        with open(ruta.strip(), "r", encoding="utf-8") as f:
            return f.read()[:4000]
    except FileNotFoundError:
        return f"Error: no existe el archivo '{ruta}'."
    except Exception as e:
        return f"Error al leer: {e}"


# --- 2. EL MODELO ---
# LiteLLM usa tu ANTHROPIC_API_KEY del entorno automáticamente.
model = LiteLLMModel(model_id="anthropic/claude-haiku-4-5")


# --- 3. EL AGENTE ---
# Le pasamos la lista de herramientas y el modelo. Y ya está.
agente = ToolCallingAgent(tools=[leer_archivo], model=model)


# --- 4. PROBARLO ---
if __name__ == "__main__":
    tarea = "Lee el archivo 'nota_prueba.txt' y dime en una frase de qué trata."
    resultado = agente.run(tarea)
    print(f"\n==> RESPUESTA FINAL: {resultado}")
