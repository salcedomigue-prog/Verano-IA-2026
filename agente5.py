"""
Sesión 5 de agentes · Leer PDFs (papers de la tesis)

Damos al agente la capacidad de leer artículos científicos en PDF.
Dos herramientas nuevas:
  - contar_paginas(ruta): cuántas páginas tiene el PDF.
  - leer_pagina_pdf(ruta, pagina): el texto de UNA página concreta.

Guardar el número de página es clave: en la sesión 7 lo necesitaremos para
citar frases textuales (APA pide la página de la cita).

Requisitos (una vez):  uv add pypdf
"""

import os
from pypdf import PdfReader
from smolagents import tool, ToolCallingAgent, LiteLLMModel


def _ruta(ruta: str) -> str:
    # Expande '~' a la carpeta del usuario, para poder apuntar a
    # ~/TESIS doctoral MAS/... sin escribir la ruta completa.
    return os.path.expanduser(ruta.strip())


# --- HERRAMIENTA 1 ---
@tool
def contar_paginas(ruta: str) -> str:
    """Devuelve el número de páginas de un archivo PDF.

    Args:
        ruta: Ruta del PDF, por ejemplo '~/TESIS doctoral MAS/Gripe_Florin.pdf'.
    """
    try:
        lector = PdfReader(_ruta(ruta))
        return f"El PDF tiene {len(lector.pages)} páginas."
    except Exception as e:
        return f"Error al abrir el PDF: {e}"


# --- HERRAMIENTA 2 ---
@tool
def leer_pagina_pdf(ruta: str, pagina: int) -> str:
    """Devuelve el texto de una página concreta de un PDF (la primera es la 1).

    Args:
        ruta: Ruta del PDF, por ejemplo '~/TESIS doctoral MAS/Gripe_Florin.pdf'.
        pagina: Número de página a leer, empezando en 1.
    """
    try:
        lector = PdfReader(_ruta(ruta))
        n = len(lector.pages)
        if pagina < 1 or pagina > n:
            return f"Error: la página {pagina} no existe (el PDF tiene {n})."
        texto = lector.pages[pagina - 1].extract_text() or "(página sin texto extraíble)"
        return f"[Página {pagina}]\n{texto[:3500]}"
    except Exception as e:
        return f"Error al leer la página: {e}"


model = LiteLLMModel(model_id="anthropic/claude-haiku-4-5")
agente = ToolCallingAgent(tools=[contar_paginas, leer_pagina_pdf], model=model)


if __name__ == "__main__":
    pdf = "~/TESIS doctoral MAS/Publicaciones LEER/0 GRIPE_FLORIN/0 Gripe_Florin.pdf"
    tarea = (
        f"Tienes un artículo científico en '{pdf}'. "
        "Primero averigua cuántas páginas tiene. "
        "Luego lee la página 1 y dime en 2 frases de qué trata el artículo."
    )
    resultado = agente.run(tarea)
    print(f"\n==> RESPUESTA FINAL: {resultado}")
