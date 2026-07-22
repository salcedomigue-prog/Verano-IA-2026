"""
Sesión 6 de agentes · El agente que ficha papers

Primer entregable real: el agente lee un paper completo y produce una FICHA
comparativa estructurada (siempre los mismos campos), y la guarda en un
archivo Markdown junto al PDF.

Herramientas:
  - extraer_texto_pdf(ruta): todo el texto del PDF, con marcas de página.
  - guardar_ficha(ruta_salida, contenido): escribe la ficha en un archivo.

Requisitos:  uv add pypdf smolagents litellm  (ya instalados en sesiones previas)
"""

import os
from pypdf import PdfReader
from smolagents import tool, ToolCallingAgent, LiteLLMModel


def _ruta(ruta: str) -> str:
    return os.path.expanduser(ruta.strip())


# --- HERRAMIENTA 1: leer el PDF entero ---
@tool
def extraer_texto_pdf(ruta: str) -> str:
    """Extrae todo el texto de un PDF, marcando cada página con [Página N].

    Args:
        ruta: Ruta del PDF a leer.
    """
    try:
        lector = PdfReader(_ruta(ruta))
        partes = []
        for i, pagina in enumerate(lector.pages, start=1):
            texto = pagina.extract_text() or ""
            partes.append(f"[Página {i}]\n{texto}")
        completo = "\n\n".join(partes)
        # Límite generoso para no saturar; suficiente para un paper típico.
        return completo[:45000]
    except Exception as e:
        return f"Error al leer el PDF: {e}"


# --- HERRAMIENTA 2: guardar la ficha ---
@tool
def guardar_ficha(ruta_salida: str, contenido: str) -> str:
    """Guarda el texto de la ficha en un archivo (lo crea o lo sobrescribe).

    Args:
        ruta_salida: Ruta del archivo a escribir, por ejemplo '~/.../Ficha.md'.
        contenido: El texto completo de la ficha.
    """
    try:
        destino = _ruta(ruta_salida)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"Ficha guardada en {destino}"
    except Exception as e:
        return f"Error al guardar: {e}"


model = LiteLLMModel(model_id="anthropic/claude-haiku-4-5")
agente = ToolCallingAgent(
    tools=[extraer_texto_pdf, guardar_ficha], model=model
)


# La plantilla de la ficha: SIEMPRE los mismos campos, para poder comparar.
PLANTILLA = """# Ficha: <título del artículo>

- **Referencia (APA):** autores (año). Título. Revista, volumen(número), páginas.
- **Objetivo:** qué pregunta de investigación responde.
- **Modelo / método:** qué modelo o técnica usa (SIR, EDP, calibración...).
- **Datos:** qué datos usa y de dónde.
- **Resultado principal:** el hallazgo clave, con cifras si las hay.
- **Limitaciones / hueco:** qué deja sin resolver.
- **Relevancia para mi tesis:** una frase sobre por qué me sirve.
"""


if __name__ == "__main__":
    pdf = "~/TESIS doctoral MAS/Publicaciones LEER/0 GRIPE_FLORIN/0 Gripe_Florin.pdf"
    salida = "~/TESIS doctoral MAS/Publicaciones LEER/0 GRIPE_FLORIN/Ficha - Gripe Florin.md"

    tarea = (
        f"Lee el artículo científico en '{pdf}' usando extraer_texto_pdf. "
        "Luego redacta una ficha en español siguiendo EXACTAMENTE esta plantilla "
        f"(mismos campos, en Markdown):\n\n{PLANTILLA}\n\n"
        "Rellena cada campo basándote SOLO en el contenido del artículo, sin inventar. "
        "Mi tesis trata de modelizar la gripe con ecuaciones en derivadas parciales "
        "en el corredor Corea del Sur - Valencia, tenlo en cuenta para el campo de relevancia. "
        f"Finalmente, guarda la ficha con guardar_ficha en '{salida}'."
    )
    resultado = agente.run(tarea)
    print(f"\n==> {resultado}")
