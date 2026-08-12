"""
================================================================================
 generar_css.py — Genera static/css/style.css a partir de DESIGN_TOKENS
================================================================================
Este script NO es obligatorio para correr el sitio (ya existe un
static/css/style.css listo para usar), pero se incluye para que quede
claro cómo la paleta de colores definida en app.py (DESIGN_TOKENS) se
traduce en variables CSS reales.

Uso:
    python generar_css.py

Esto sobrescribe static/css/style.css con las variables :root actualizadas
seguidas del resto de las reglas de estilo del sitio.
================================================================================
"""

import os
from app import DESIGN_TOKENS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "static", "css", "style.css")


def generar_variables_css() -> str:
    """Convierte DESIGN_TOKENS en un bloque :root { ... } de variables CSS."""
    lineas = [":root {"]

    for nombre, valor in DESIGN_TOKENS["color"].items():
        variable = nombre.replace("_", "-")
        lineas.append(f"    --color-{variable}: {valor};")

    lineas.append("")
    for nombre, valor in DESIGN_TOKENS["tipografia"].items():
        variable = nombre.replace("_", "-")
        lineas.append(f"    --font-{variable}: {valor};")

    lineas.append("")
    for nombre, valor in DESIGN_TOKENS["radio_borde"].items():
        variable = nombre.replace("_", "-")
        lineas.append(f"    --radio-{variable}: {valor};")

    lineas.append("}")
    return "\n".join(lineas)


REGLAS_BASE = """
/* ==========================================================================
   Reglas generadas automáticamente a partir de los tokens de diseño.
   Para el resto de las reglas de layout, ver el bloque principal de
   static/css/style.css (secciones 1 a 8 del boceto).
   ========================================================================== */

* { box-sizing: border-box; }

body {
    background: var(--color-crema-fondo);
    color: var(--color-texto-principal);
    font-family: var(--font-cuerpo);
    margin: 0;
}

h1, h2, h3, .display {
    font-family: var(--font-display);
    color: var(--color-lila-oscuro);
}

.btn-primario {
    background: var(--color-lila-primario);
    color: var(--color-blanco);
    border-radius: var(--radio-pastilla);
}

.btn-secundario {
    background: transparent;
    color: var(--color-lila-primario);
    border: 1.5px solid var(--color-lila-primario);
    border-radius: var(--radio-pastilla);
}

.tarjeta {
    background: var(--color-blanco);
    border: 1px solid var(--color-borde-suave);
    border-radius: var(--radio-mediano);
}

.badge-rosa {
    background: var(--color-rosa-suave);
    color: var(--color-rosa-acento);
    border-radius: var(--radio-pastilla);
}

.badge-verde {
    background: var(--color-verde-suave);
    color: var(--color-verde-salvia);
    border-radius: var(--radio-pastilla);
}
""".strip("\n")


def construir_hoja_de_estilos() -> str:
    return generar_variables_css() + "\n\n" + REGLAS_BASE + "\n"


def main() -> None:
    contenido = construir_hoja_de_estilos()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    if os.path.exists(OUTPUT_PATH):
        respuesta = input(
            f"'{OUTPUT_PATH}' ya existe. ¿Sobrescribir con las variables "
            "generadas desde DESIGN_TOKENS? [s/N]: "
        ).strip().lower()
        if respuesta != "s":
            print("Operación cancelada. No se modificó ningún archivo.")
            return

    with open(OUTPUT_PATH, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print(f"✅ Variables CSS escritas en: {OUTPUT_PATH}")
    print(
        "\nNota: este archivo generado solo contiene las variables de color/"
        "tipografía y algunas reglas base. El diseño completo de las 8 "
        "secciones vive en el static/css/style.css entregado junto al "
        "proyecto — no lo sobrescribas a menos que quieras reconstruirlo "
        "desde cero."
    )


if __name__ == "__main__":
    main()
