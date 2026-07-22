"""
Sesión 7 de agentes · Banco de citas VERIFICADO

Objetivo: extraer las frases más citables de un paper, cada una con su página
y una traducción al español, y GARANTIZAR que son literales (verbatim).

Patrón clave: el MODELO propone, el CÓDIGO verifica.
  1. Extraemos el texto del PDF, página a página.
  2. Pedimos al modelo hasta N frases destacadas en JSON (cita, página, traducción).
  3. En Python comprobamos que cada frase existe LITERALMENTE en el PDF.
     Las que no coinciden se descartan (anti-invención).
  4. Guardamos el banco de citas verificado en un JSON.

Requisitos: uv add anthropic pypdf  (ya instalados)
"""

import os
import re
import json
import difflib
import unicodedata
import anthropic
from pypdf import PdfReader

client = anthropic.Anthropic()


def _ruta(ruta):
    return os.path.expanduser(ruta.strip())


def normaliza(texto):
    """Deja el texto comparable: minúsculas y espacios colapsados.
    Se usa para la sugerencia de pasaje parecido (legible)."""
    return re.sub(r"\s+", " ", texto).strip().lower()


def clave(texto):
    """Reduce el texto a SOLO letras y números (sin espacios, guiones,
    ligaduras ni acentos). Así la verificación no falla por la 'basura'
    que mete pypdf al extraer PDFs académicos (ligaduras fi/fl, palabras
    partidas con guion al final de línea, doble columna, etc.)."""
    # NFKD descompone ligaduras (ﬁ -> fi) y acentos (é -> e + tilde).
    t = unicodedata.normalize("NFKD", texto).lower()
    return re.sub(r"[^a-z0-9]", "", t)


# --- 1. EXTRAER EL TEXTO POR PÁGINAS ---
def extraer_paginas(ruta):
    lector = PdfReader(_ruta(ruta))
    paginas = {}
    for i, pagina in enumerate(lector.pages, start=1):
        paginas[i] = pagina.extract_text() or ""
    return paginas


# --- 2. PEDIR AL MODELO FRASES CANDIDATAS (en JSON) ---
def proponer_citas(texto_completo, n=8):
    prompt = f"""Aquí tienes el texto de un artículo científico, con marcas [Página N].

Extrae las {n} frases MÁS destacadas y citables (definiciones, hallazgos clave,
afirmaciones metodológicas importantes). Requisitos ESTRICTOS:
- Copia cada frase LITERALMENTE, palabra por palabra, tal como aparece (en inglés).
- No la parafrasees ni la acortes con "...".
- Indica el número de página donde aparece.
- Añade una traducción al español de apoyo.

Responde SOLO con un JSON válido, sin texto alrededor, con esta forma:
[
  {{"cita": "frase literal en inglés", "pagina": 3, "traduccion": "traducción en español"}}
]

TEXTO:
{texto_completo[:45000]}
"""
    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    bruto = respuesta.content[0].text.strip()
    # Quitamos posibles ``` que a veces envuelven el JSON.
    bruto = re.sub(r"^```(json)?|```$", "", bruto.strip(), flags=re.MULTILINE).strip()
    return json.loads(bruto)


# Partimos todo el PDF en "frases" reales, para poder sugerir la más parecida.
def frases_del_pdf(paginas):
    frases = []  # lista de (texto_frase, pagina)
    for num, txt in paginas.items():
        for trozo in re.split(r"(?<=[.!?])\s+", txt):
            trozo = trozo.strip()
            if len(trozo) >= 15:
                frases.append((trozo, num))
    return frases


# --- 3. VERIFICAR CADA FRASE CONTRA EL PDF ---
def verificar(citas, paginas):
    clave_global = clave("\n".join(paginas.values()))
    frases_reales = frases_del_pdf(paginas)
    frases_norm = [normaliza(f) for f, _ in frases_reales]

    verificadas, a_revisar = [], []
    for c in citas:
        cita = c.get("cita", "")
        frase_clave = clave(cita)
        if len(frase_clave) < 15:
            c["verificada"] = False
            c["motivo"] = "demasiado corta"
            c["posible_original"] = ""
            a_revisar.append(c)
            continue

        if frase_clave in clave_global:
            # Coincide (ignorando espacios/guiones/ligaduras): verificada.
            pagina_real = c.get("pagina")
            for num, txt in paginas.items():
                if frase_clave in clave(txt):
                    pagina_real = num
                    break
            c["pagina"] = pagina_real
            c["verificada"] = True
            verificadas.append(c)
        else:
            # No coincide: NO la tiramos. La marcamos y buscamos la frase
            # real más parecida del PDF como sugerencia para corregir a mano.
            c["verificada"] = False
            c["motivo"] = "no coincide exactamente - revisar a mano"
            parecidas = difflib.get_close_matches(normaliza(cita), frases_norm, n=1, cutoff=0.5)
            if parecidas:
                idx = frases_norm.index(parecidas[0])
                original, pag = frases_reales[idx]
                c["posible_original"] = original
                c["pagina"] = pag  # página donde está el pasaje parecido
            else:
                c["posible_original"] = "(no se encontró un pasaje parecido)"
            a_revisar.append(c)
    return verificadas, a_revisar


# --- 4. PEDIR LA REFERENCIA APA ---
def referencia_apa(texto_completo):
    prompt = (
        "A partir de la primera página de este artículo, dame SOLO la referencia "
        "en formato APA (autores, año, título, revista, volumen, páginas), en una línea:\n\n"
        + texto_completo[:2500]
    )
    r = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text.strip()


if __name__ == "__main__":
    pdf = "~/TESIS doctoral MAS/Publicaciones LEER/0 GRIPE_FLORIN/0 Gripe_Florin.pdf"
    salida = "~/TESIS doctoral MAS/Publicaciones LEER/0 GRIPE_FLORIN/Banco de citas - Gripe Florin.json"

    print("1) Extrayendo texto del PDF...")
    paginas = extraer_paginas(pdf)
    texto = "\n".join(f"[Página {n}]\n{t}" for n, t in paginas.items())

    print("2) Pidiendo frases candidatas al modelo...")
    candidatas = proponer_citas(texto, n=8)
    print(f"   El modelo propuso {len(candidatas)} frases.")

    print("3) Verificando cada frase contra el PDF...")
    verificadas, a_revisar = verificar(candidatas, paginas)
    print(f"   Verificadas: {len(verificadas)}  |  Para revisar a mano: {len(a_revisar)}")
    for c in a_revisar:
        print(f"     - REVISAR ({c['motivo']}): {c.get('cita', '')[:60]}...")

    print("4) Obteniendo la referencia APA y guardando...")
    banco = {
        "referencia_apa": referencia_apa(texto),
        "citas_verificadas": verificadas,
        "citas_a_revisar": a_revisar,  # NO verificadas: corrígelas a mano si quieres
    }
    with open(_ruta(salida), "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)

    print(f"\n==> Guardado: {len(verificadas)} verificadas + "
          f"{len(a_revisar)} para revisar, en:\n    {salida}")
