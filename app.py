"""
================================================================================
 ALMA — Donde cuidar también significa ser cuidada
================================================================================
Aplicación web en Flask que reproduce el boceto/wireframe de 8 secciones:
  1. Inicio
  2. ¿Quiénes somos?
  3. Campamento de Verano
  4. Inscripción
  5. Comunidad
  6. Nuestro impacto
  7. Historias
  8. Mensaje final / Footer

Toda la información visible en el sitio (textos, valores, días del
campamento, estadísticas, testimonios, campos del formulario, etc.) vive
aquí como estructuras de datos en Python, para que el contenido se pueda
editar sin tocar el HTML.

Cómo correrlo:
    1) pip install flask
    2) python app.py
    3) Abrir http://127.0.0.1:5000 en el navegador

Estructura de carpetas esperada:
    alma_site/
        app.py                  <- este archivo
        templates/
            index.html
            404.html
        static/
            css/style.css
            js/script.js
            images/              <- AQUÍ VAN TUS IMÁGENES (ver IMAGE_MANIFEST)
================================================================================
"""

from __future__ import annotations

import os
import re
import json
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    abort,
)

# ==============================================================================
# 1. CONFIGURACIÓN GENERAL
# ==============================================================================


class Config:
    """Configuración base de la aplicación."""

    SECRET_KEY = os.environ.get("ALMA_SECRET_KEY", "alma-dev-key-cambiar-en-produccion")
    DEBUG = os.environ.get("ALMA_DEBUG", "1") == "1"
    SITE_NAME = "ALMA"
    SITE_TAGLINE = "Donde cuidar también significa ser cuidada."
    SITE_DESCRIPTION = (
        "Acompañamos a madres jóvenes de niños autistas para que nunca "
        "tengan que caminar solas."
    )
    CONTACT_EMAIL = "hola@almacomunidad.org"
    WHATSAPP_LINK = "https://chat.whatsapp.com/CAMBIAR-ESTE-ENLACE"
    INSTAGRAM_LINK = "https://instagram.com/alma.comunidad"
    FACEBOOK_LINK = "https://facebook.com/alma.comunidad"
    CURRENT_YEAR = datetime.now().year


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alma")


# ==============================================================================
# 2. MANIFIESTO DE IMÁGENES
# ------------------------------------------------------------------------------
# Este diccionario es la lista EXACTA de archivos que debes colocar dentro de
# static/images/ para que la página se vea igual que el boceto. El nombre de
# archivo (filename) es el que ya está escrito en el HTML, así que si guardas
# tus imágenes con estos nombres exactos, no necesitas tocar ningún template.
# ==============================================================================

IMAGE_MANIFEST = {
    "logo": {
        "filename": "logo-alma.png",
        "usado_en": "Barra lateral de navegación y footer",
        "descripcion": "Logotipo circular de ALMA (arcoíris + figura con corazón).",
        "tamano_recomendado": "200x200 px, fondo transparente, PNG",
    },
    "hero_ilustracion": {
        "filename": "hero-arcoiris-alma.png",
        "usado_en": "Sección 1 - Inicio (lado derecho del hero)",
        "descripcion": "Ilustración grande del arcoíris con la figura ALMA y hojas decorativas.",
        "tamano_recomendado": "1100x900 px, fondo transparente, PNG",
    },
    "hero_corazon": {
        "filename": "icono-corazon-lila.png",
        "usado_en": "Sección 1 - Inicio, junto al arcoíris",
        "descripcion": "Ícono de corazón color lavanda/rosa.",
        "tamano_recomendado": "120x120 px, PNG transparente",
    },
    "hoja_decorativa_1": {
        "filename": "hoja-decorativa-1.png",
        "usado_en": "Fondo decorativo sección 1",
        "descripcion": "Rama u hoja ilustrada, tono verde/lavanda, semitransparente.",
        "tamano_recomendado": "400x400 px, PNG transparente",
    },
    "hoja_decorativa_2": {
        "filename": "hoja-decorativa-2.png",
        "usado_en": "Fondo decorativo sección 1",
        "descripcion": "Segunda rama/hoja ilustrada para balancear la composición.",
        "tamano_recomendado": "400x400 px, PNG transparente",
    },
    "arbol_dia5": {
        "filename": "arbol-dia5.png",
        "usado_en": "Sección 3 - Campamento, tarjeta 'Día 5 presencial'",
        "descripcion": "Ilustración de un árbol para representar la plantación.",
        "tamano_recomendado": "500x500 px, PNG transparente",
    },
    "familia_plantando": {
        "filename": "familia-plantando-arbol.png",
        "usado_en": "Sección 3 - Campamento, tarjeta 'Día 5 presencial'",
        "descripcion": "Fotografía de madres/niños plantando un árbol juntos.",
        "tamano_recomendado": "1000x1100 px, JPG, orientación vertical",
    },
    "madre_hija_abrazo": {
        "filename": "madre-hija-abrazo.png",
        "usado_en": "Sección 4 - Inscripción (lado derecho del formulario)",
        "descripcion": "Fotografía cálida de una madre abrazando a su hija/hijo.",
        "tamano_recomendado": "800x1000 px, JPG, orientación vertical",
    },
    "grupo_apoyo_mujeres": {
        "filename": "grupo-apoyo-mujeres.png",
        "usado_en": "Sección 5 - Comunidad",
        "descripcion": "Fotografía de un grupo de mujeres sentadas conversando, ambiente cálido.",
        "tamano_recomendado": "1200x800 px, JPG, orientación horizontal",
    },
    "flores_footer": {
        "filename": "flores-decorativas-footer.png",
        "usado_en": "Sección 8 - Mensaje final / Footer",
        "descripcion": "Ilustración decorativa de flores/corazones para el pie de página.",
        "tamano_recomendado": "1200x300 px, PNG transparente",
    },
    "icono_whatsapp": {
        "filename": "icono-whatsapp.svg",
        "usado_en": "Botón 'Únete al grupo de WhatsApp'",
        "descripcion": "Ícono oficial de WhatsApp en color blanco o verde.",
        "tamano_recomendado": "24x24 px, SVG o PNG",
    },
}


ALT_TEXT = {
    # Texto alternativo (accesibilidad) para cada imagen del manifiesto.
    # Se usa en el atributo alt="" de cada <img> en templates/index.html.
    "logo": "Logotipo de ALMA: arcoíris con figura y corazón",
    "hero_ilustracion": "Ilustración de un arcoíris con una figura sosteniendo un corazón, rodeada de hojas",
    "hero_corazon": "Ícono decorativo de un corazón color lavanda",
    "hoja_decorativa_1": "Ilustración decorativa de una rama con hojas",
    "hoja_decorativa_2": "Ilustración decorativa de una segunda rama con hojas",
    "arbol_dia5": "Ilustración de un árbol representando el cierre del campamento",
    "familia_plantando": "Madres y niños plantando un árbol juntos al aire libre",
    "madre_hija_abrazo": "Una madre abrazando con cariño a su hija",
    "grupo_apoyo_mujeres": "Grupo de mujeres sentadas en círculo conversando y apoyándose",
    "madre_hijo_naturaleza": "Una madre abrazando a su hijo al aire libre, rodeados de naturaleza",
    "flores_footer": "Ilustración decorativa de flores y corazones",
    "icono_whatsapp": "Ícono de WhatsApp",
}


def get_alt_text(image_key: str) -> str:
    """Devuelve el texto alternativo de accesibilidad para una imagen del
    manifiesto, o una cadena genérica si la clave no existe."""
    return ALT_TEXT.get(image_key, "Imagen del sitio ALMA")


def seed_demo_enrollments() -> None:
    """
    Agrega un par de inscripciones de ejemplo al almacenamiento en memoria.
    Útil solo para ver cómo luce /admin/inscripciones durante el
    desarrollo local; no se llama automáticamente en producción.
    """
    ejemplos = [
        EnrollmentSubmission(
            nombre_completo="Rosa Elena Gómez",
            edad="27",
            correo="rosa.gomez@correo.com",
            ciudad="Santiago",
            telefono="809-222-3333",
            como_supiste="Recomendación de una amiga",
        ),
        EnrollmentSubmission(
            nombre_completo="Yulissa Martínez",
            edad="33",
            correo="yulissa.m@correo.com",
            ciudad="Licey al Medio",
            telefono="829-444-5555",
            como_supiste="Un profesional de la salud",
        ),
    ]
    for ejemplo in ejemplos:
        if ejemplo.is_valid():
            ENROLLMENTS_STORE.append(ejemplo.to_dict())


def print_image_setup_instructions() -> str:
    """
    Devuelve instrucciones legibles en consola sobre dónde colocar cada
    imagen. Se ejecuta automáticamente al iniciar el servidor (ver bloque
    __main__ al final del archivo).
    """
    lines = [
        "",
        "=" * 78,
        "IMÁGENES NECESARIAS — colócalas dentro de: static/images/",
        "=" * 78,
    ]
    for key, meta in IMAGE_MANIFEST.items():
        lines.append(f"- {meta['filename']:<32} -> {meta['usado_en']}")
        lines.append(f"    {meta['descripcion']} ({meta['tamano_recomendado']})")
    lines.append("=" * 78)
    return "\n".join(lines)


def check_missing_images() -> list[str]:
    """Revisa static/images/ y devuelve la lista de archivos que faltan."""
    missing = []
    if not os.path.isdir(STATIC_IMAGES_DIR):
        return [meta["filename"] for meta in IMAGE_MANIFEST.values()]
    existing = set(os.listdir(STATIC_IMAGES_DIR))
    for meta in IMAGE_MANIFEST.values():
        if meta["filename"] not in existing:
            missing.append(meta["filename"])
    return missing


# ==============================================================================
# 3. CONTENIDO — SECCIÓN 1: INICIO (HERO)
# ==============================================================================

NAV_ITEMS = [
    {"id": "inicio", "label": "Inicio", "icon": "home"},
    {"id": "quienes-somos", "label": "¿Quiénes somos?", "icon": "users"},
    {"id": "Programa", "label": "Campamento", "icon": "sun"},
    {"id": "inscripcion", "label": "Inscripción", "icon": "edit"},
    {"id": "comunidad", "label": "Comunidad", "icon": "message-circle"},
    {"id": "impacto", "label": "Nuestro impacto", "icon": "bar-chart"},
    {"id": "contacto", "label": "Contacto", "icon": "mail"},
]

HERO_CONTENT = {
    "eyebrow_words": ["Acompañamiento", "Lazos", "Maternidad", "Autocuidado"],
    "title_line_1": "Donde cuidar",
    "title_line_2": "también significa",
    "title_highlight": "ser cuidada.",
    "subtitle": (
        "Acompañamos a madres jóvenes de niños autistas para que nunca "
        "tengan que caminar solas."
    ),
    "cta_primary": {"label": "Quiero ser parte de ALMA", "target": "inscripcion"},
    "cta_secondary": {"label": "Conoce nuestra historia", "target": "quienes-somos"},
    "quote": (
        "Detrás de cada niño que necesita apoyo, también hay una madre "
        "que necesita ser escuchada."
    ),
}

# ==============================================================================
# 4. CONTENIDO — SECCIÓN 2: ¿QUIÉNES SOMOS?
# ==============================================================================

ABOUT_CONTENT = {
    "title": "¿Qué es ALMA?",
    "body": (
        "ALMA es una organización creada para brindar acompañamiento, "
        "orientación y espacios de bienestar a madres jóvenes de niños "
        "autistas, fortaleciendo su salud emocional y creando una "
        "comunidad donde se sientan escuchadas, comprendidas y apoyadas."
    ),
    "mision": {
        "title": "Misión",
        "text": (
            "Brindar acompañamiento, orientación y espacios de bienestar "
            "a madres jóvenes de niños autistas, fortaleciendo su salud "
            "emocional y creando una comunidad donde se sientan "
            "escuchadas, comprendidas y apoyadas."
        ),
    },
    "vision": {
        "title": "Visión",
        "text": (
            "Construir una comunidad donde ninguna madre joven se sienta "
            "sola, promoviendo una maternidad acompañada, saludable e "
            "inclusiva."
        ),
    },
}

VALUES = [
    {
        "title": "Empatía",
        "text": "Escuchamos y comprendemos sin juzgar.",
        "icon": "heart",
    },
    {
        "title": "Respeto",
        "text": "Reconocemos las necesidades y experiencias de cada madre.",
        "icon": "hand-heart",
    },
    {
        "title": "Inclusión",
        "text": "Valoramos cada historia y cada familia.",
        "icon": "puzzle",
    },
    {
        "title": "Bienestar",
        "text": "Recordamos que cuidar a mamá también es importante.",
        "icon": "sun",
    },
    {
        "title": "Comunidad",
        "text": "Crecemos y nos apoyamos juntas.",
        "icon": "users",
    },
    {
        "title": "Esperanza",
        "text": "Promovemos nuevas oportunidades y un futuro mejor.",
        "icon": "sparkles",
    },
]

# ==============================================================================
# 5. CONTENIDO — SECCIÓN 3: CAMPAMENTO DE VERANO
# ==============================================================================

CAMP_INTRO = {
    "title": "Programa ALMA",
    "subtitle": "5 días para conectar, aprender y sanar.",
}

CAMP_DAYS = [
    {
        "number": 1,
        "title": "Conocernos",
        "morning": "Inteligencia Emocional",
        "afternoon": "Terapias 8:00 AM - 10:00 AM",
        "presencial": False,
    },
    {
        "number": 2,
        "title": "Comprender",
        "morning": "Salud Mental",
        "afternoon": "Terapias 8:00 AM - 10:00 AM",
        "presencial": False,
    },
    {
        "number": 3,
        "title": "Riesgos",
        "morning": "Depresion",
        "afternoon": "Terapias 8:00 AM - 10:00 AM",
        "presencial": False,
    },
    {
        "number": 4,
        "title": "Fortalecernos",
        "morning": "Autocuidado",
        "afternoon": "Terapias 8:00 AM - 10:00 AM",
        "presencial": False,
    },
    {
        "number": 5,
        "title": "Renacer",
        "morning": "Superacion personal/Oportunidades de trabajo",
        "afternoon": "Charla 8:00 AM - 10:00 AM",
        "presencial": True,
    },
]

CAMP_DAY5_HIGHLIGHT = {
    "tag": "DÍA 6 PRESENCIAL",
    "title": "Dejamos una huella",
    "body": (
        "Cierre presencial con actividades especiales y plantación de "
        "árboles."
    ),
    "footnote": "Un árbol por cada historia, una huella por cada mamá.",
}

CAMP_FEATURES = [
    {
        "title": "Charlas y talleres en la mañana",
        "text": (
            "Espacios de aprendizaje, reflexión y herramientas para tu "
            "bienestar."
        ),
        "icon": "sun",
    },
    {
        "title": "Terapias en la tarde/noche",
        "text": (
            "Sesiones terapéuticas en grupos pequeños con 5 psicólogos "
            "especializadas."
        ),
        "icon": "moon",
    },
    {
        "title": "Talleristas invitados cada día",
        "text": (
            "Diferentes profesionales que te acompañarán con actividades "
            "prácticas y significativas."
        ),
        "icon": "user-check",
    },
]

# ==============================================================================
# 6. CONTENIDO — SECCIÓN 4: INSCRIPCIÓN
# ==============================================================================

ENROLLMENT_CONTENT = {
    "title": "Tu historia también importa",
    "subtitle": "Queremos conocerte y saber cómo podemos acompañarte.",
    "steps": [
        {"number": 1, "label": "Cuéntanos sobre ti"},
        {"number": 2, "label": "Conoce ALMA"},
        {"number": 3, "label": "Forma parte de la comunidad"},
    ],
    "cta": "Quiero ser parte de ALMA",
}

# Cada campo describe cómo se debe renderizar Y cómo se debe validar
# en el backend. name = el atributo "name" del <input> en el HTML.
ENROLLMENT_FORM_FIELDS = [
    {"name": "nombre_completo", "label": "Nombre completo", "type": "text",
     "placeholder": "Escribe tu nombre", "required": True},
    {"name": "edad", "label": "Edad", "type": "number",
     "placeholder": "Tu edad", "required": True},
    {"name": "correo", "label": "Correo electrónico", "type": "email",
     "placeholder": "ejemplo@correo.com", "required": True},
    {"name": "ciudad", "label": "Ciudad", "type": "text",
     "placeholder": "Tu ciudad", "required": True},
    {"name": "telefono", "label": "Teléfono / WhatsApp", "type": "tel",
     "placeholder": "809-000-0000", "required": True},
    {"name": "como_supiste", "label": "¿Cómo supiste de ALMA?", "type": "select",
     "required": True, "options": [
         "Selecciona una opción",
         "Redes sociales",
         "Recomendación de una amiga",
         "Un profesional de la salud",
         "Un evento o campamento",
         "Otro",
     ]},
]

# ==============================================================================
# 7. CONTENIDO — SECCIÓN 5: COMUNIDAD
# ==============================================================================

COMMUNITY_CONTENT = {
    "title": "Ahora ya no estás sola.",
    "body_lines": [
        "Tu primer paso ya está dado.",
        "Ahora puedes formar parte de una comunidad de madres que están "
        "recorriendo caminos similares.",
    ],
    "card_title": "Bienvenida a ALMA",
    "card_body": "Un espacio seguro, lleno de apoyo, comprensión y esperanza.",
    "whatsapp_cta": "Únete al grupo de WhatsApp",
}

# ==============================================================================
# 8. CONTENIDO — SECCIÓN 6: NUESTRO IMPACTO
# ==============================================================================

IMPACT_CONTENT = {
    "title": "El impacto que queremos crear",
    "quote": "Cada número representa una historia, cada historia representa una familia.",
}

IMPACT_STATS = [
    {"value": 50, "label": "Madres acompañadas", "icon": "users"},
    {"value": 20, "label": "Sesiones de orientación", "icon": "heart"},
    {"value": 23, "label": "Talleres realizados", "icon": "book-open"},
    {"value": 50, "label": "Árboles plantados", "icon": "tree"},
    {"value": 50, "label": "Historias acompañadas", "icon": "message-circle"},
]


# ==============================================================================
# 10. CONTENIDO — SECCIÓN 8: MENSAJE FINAL / FOOTER
# ==============================================================================

CLOSING_CONTENT = {
    "line_1": "Cuidar a mamá también es importante.",
    "line_2": "Recuerda: no estás sola, estamos contigo.",
    "cta": "Quiero ser parte de ALMA",
}

FOOTER_CONTENT = {
    "tagline": "ALMA · Donde cuidar también significa ser cuidada.",
    "rights": f"© {Config.CURRENT_YEAR} ALMA. Todos los derechos reservados.",
    "social": [
        {"name": "Instagram", "url": Config.INSTAGRAM_LINK, "icon": "instagram"},
        {"name": "Facebook", "url": Config.FACEBOOK_LINK, "icon": "facebook"},
        {"name": "WhatsApp", "url": Config.WHATSAPP_LINK, "icon": "whatsapp"},
    ],
}


# ==============================================================================
# 11. IDENTIDAD VISUAL — TOKENS DE DISEÑO
# ------------------------------------------------------------------------------
# Estos valores describen la paleta y tipografía del boceto en un solo lugar.
# Se inyectan como variables CSS (:root) desde la plantilla base, así que si
# alguna vez quieres retocar un color, basta con cambiarlo aquí.
# ==============================================================================

DESIGN_TOKENS = {
    "color": {
        "crema_fondo": "#FDF8F3",
        "lila_primario": "#6E3B9E",
        "lila_oscuro": "#4A2A6B",
        "lila_suave": "#EFE3FA",
        "rosa_acento": "#E187A8",
        "rosa_suave": "#FBE6EE",
        "verde_salvia": "#8FB79A",
        "verde_suave": "#E7F1E8",
        "amarillo_calido": "#F3C969",
        "texto_principal": "#3A2E45",
        "texto_secundario": "#6E6376",
        "blanco": "#FFFFFF",
        "borde_suave": "#EDE3F2",
    },
    "tipografia": {
        "display": "'Fraunces', 'Georgia', serif",
        "cuerpo": "'Nunito Sans', 'Segoe UI', sans-serif",
    },
    "radio_borde": {
        "chico": "10px",
        "mediano": "18px",
        "grande": "28px",
        "pastilla": "999px",
    },
}


# ==============================================================================
# 12. VALIDACIÓN DEL FORMULARIO DE INSCRIPCIÓN
# ==============================================================================

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9()+\-\s]{7,20}$")
NAME_REGEX = re.compile(r"^[A-Za-zÀ-ÿñÑ\s'.-]{3,80}$")


class FieldValidator:
    """Clase base para validar un campo individual del formulario."""

    error_message = "Este campo no es válido."

    def is_valid(self, value: str) -> bool:  # pragma: no cover - interfaz
        raise NotImplementedError

    def validate(self, value: str) -> Optional[str]:
        """Devuelve None si es válido, o un mensaje de error si no lo es."""
        return None if self.is_valid(value) else self.error_message


class NameValidator(FieldValidator):
    error_message = "Escribe tu nombre completo (solo letras y espacios)."

    def is_valid(self, value: str) -> bool:
        return bool(value) and bool(NAME_REGEX.match(value.strip()))


class AgeValidator(FieldValidator):
    error_message = "Ingresa una edad válida (entre 14 y 70 años)."

    def is_valid(self, value: str) -> bool:
        return value.isdigit() and 14 <= int(value) <= 70


class EmailValidator(FieldValidator):
    error_message = "Ingresa un correo electrónico válido."

    def is_valid(self, value: str) -> bool:
        return bool(value) and bool(EMAIL_REGEX.match(value))


class CityValidator(FieldValidator):
    error_message = "Ingresa tu ciudad."

    def is_valid(self, value: str) -> bool:
        return bool(value) and len(value.strip()) >= 2


class PhoneValidator(FieldValidator):
    error_message = "Ingresa un teléfono válido (mínimo 7 dígitos)."

    def is_valid(self, value: str) -> bool:
        digits_only = re.sub(r"\D", "", value or "")
        return bool(value) and bool(PHONE_REGEX.match(value)) and len(digits_only) >= 7


class SelectValidator(FieldValidator):
    error_message = "Selecciona cómo supiste de ALMA."

    def __init__(self, placeholder: str = "Selecciona una opción"):
        self.placeholder = placeholder

    def is_valid(self, value: str) -> bool:
        return bool(value) and value != self.placeholder


FIELD_VALIDATORS = {
    "nombre_completo": NameValidator(),
    "edad": AgeValidator(),
    "correo": EmailValidator(),
    "ciudad": CityValidator(),
    "telefono": PhoneValidator(),
    "como_supiste": SelectValidator(),
}


@dataclass
class EnrollmentSubmission:
    """Representa una inscripción enviada desde el formulario."""

    nombre_completo: str = ""
    edad: str = ""
    correo: str = ""
    ciudad: str = ""
    telefono: str = ""
    como_supiste: str = ""
    fecha_envio: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    errores: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        self.errores = {}
        for field_name, validator in FIELD_VALIDATORS.items():
            value = getattr(self, field_name, "")
            error = validator.validate(value)
            if error:
                self.errores[field_name] = error
        return len(self.errores) == 0

    def to_dict(self) -> dict:
        return asdict(self)

    def primer_nombre(self) -> str:
        partes = self.nombre_completo.strip().split(" ")
        return partes[0] if partes else self.nombre_completo


def sanitize(value: Optional[str]) -> str:
    """Limpia espacios y caracteres de control de un campo de texto."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


# Almacenamiento simple en memoria (para producción, reemplazar por una
# base de datos real: PostgreSQL, SQLite + SQLAlchemy, Airtable, etc.)
ENROLLMENTS_STORE: list[dict] = []


# ==============================================================================
# 13. PROTECCIÓN CONTRA ENVÍOS MASIVOS (RATE LIMITING BÁSICO)
# ------------------------------------------------------------------------------
# Un limitador simple en memoria para evitar que alguien envíe el
# formulario de inscripción decenas de veces por segundo (spam/bots).
# Para producción real se recomienda Flask-Limiter + Redis.
# ==============================================================================


class SimpleRateLimiter:
    """Limita cuántas veces una misma IP puede llamar a una acción."""

    def __init__(self, max_intentos: int = 5, ventana_segundos: int = 60):
        self.max_intentos = max_intentos
        self.ventana_segundos = ventana_segundos
        self._registro: dict[str, list[float]] = {}

    def permitir(self, identificador: str) -> bool:
        ahora = datetime.utcnow().timestamp()
        intentos = self._registro.setdefault(identificador, [])
        # Descarta intentos fuera de la ventana de tiempo
        intentos[:] = [t for t in intentos if ahora - t < self.ventana_segundos]
        if len(intentos) >= self.max_intentos:
            return False
        intentos.append(ahora)
        return True


enrollment_rate_limiter = SimpleRateLimiter(max_intentos=5, ventana_segundos=60)


# ==============================================================================
# 12. CONTEXTO COMÚN PARA TODAS LAS PÁGINAS
# ==============================================================================


def build_base_context() -> dict:
    """Reúne todo el contenido que la plantilla necesita para renderizar
    la página completa de una sola vez (single page con anclas)."""
    return {
        "site": {
            "name": Config.SITE_NAME,
            "tagline": Config.SITE_TAGLINE,
            "description": Config.SITE_DESCRIPTION,
            "whatsapp_link": Config.WHATSAPP_LINK,
            "instagram_link": Config.INSTAGRAM_LINK,
            "facebook_link": Config.FACEBOOK_LINK,
            "year": Config.CURRENT_YEAR,
        },
        "nav_items": NAV_ITEMS,
        "hero": HERO_CONTENT,
        "about": ABOUT_CONTENT,
        "values": VALUES,
        "camp_intro": CAMP_INTRO,
        "camp_days": CAMP_DAYS,
        "camp_day5": CAMP_DAY5_HIGHLIGHT,
        "camp_features": CAMP_FEATURES,
        "enrollment": ENROLLMENT_CONTENT,
        "enrollment_fields": ENROLLMENT_FORM_FIELDS,
        "community": COMMUNITY_CONTENT,
        "impact": IMPACT_CONTENT,
        "impact_stats": IMPACT_STATS,
        "closing": CLOSING_CONTENT,
        "footer": FOOTER_CONTENT,
        "images": {key: meta["filename"] for key, meta in IMAGE_MANIFEST.items()},
    }


# ==============================================================================
# 13. RUTAS
# ==============================================================================


@app.route("/")
def index():
    """Página única (one-page) con las 8 secciones del boceto."""
    context = build_base_context()
    missing = check_missing_images()
    if missing:
        logger.info("Faltan imágenes por agregar: %s", ", ".join(missing))
    context["missing_images"] = missing
    return render_template("index.html", **context)


@app.route("/inscripcion", methods=["POST"])
def inscripcion():
    """
    Recibe el formulario de la sección 4 (Inscripción), lo valida y lo
    guarda. Responde en JSON para que el formulario se pueda enviar por
    AJAX sin recargar la página (ver static/js/script.js).
    """
    cliente_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "desconocido")
    if not enrollment_rate_limiter.permitir(cliente_ip):
        return jsonify({
            "ok": False,
            "mensaje": "Demasiados intentos. Por favor espera un momento antes de volver a intentar.",
        }), 429

    data = request.form

    submission = EnrollmentSubmission(
        nombre_completo=sanitize(data.get("nombre_completo")),
        edad=sanitize(data.get("edad")),
        correo=sanitize(data.get("correo")),
        ciudad=sanitize(data.get("ciudad")),
        telefono=sanitize(data.get("telefono")),
        como_supiste=sanitize(data.get("como_supiste")),
    )

    if not submission.is_valid():
        return jsonify({"ok": False, "errores": submission.errores}), 400

    ENROLLMENTS_STORE.append(submission.to_dict())
    logger.info("Nueva inscripción recibida de %s", submission.nombre_completo)

    # Aquí es donde, en producción, enviarías un correo de bienvenida,
    # guardarías en la base de datos real, o dispararías una automatización.

    return jsonify({
        "ok": True,
        "mensaje": (
            f"¡Gracias, {submission.primer_nombre()}! "
            "Tu historia también importa. Te contactaremos muy pronto."
        ),
    })


@app.route("/admin/inscripciones")
def admin_inscripciones():
    """
    Vista simple (solo para desarrollo) para revisar las inscripciones
    guardadas en memoria. En producción esto debería protegerse con
    autenticación.
    """
    return jsonify({"total": len(ENROLLMENTS_STORE), "inscripciones": ENROLLMENTS_STORE})


@app.route("/estado-imagenes")
def estado_imagenes():
    """Endpoint de utilidad: muestra qué imágenes faltan por agregar."""
    missing = check_missing_images()
    return jsonify({
        "carpeta": "static/images/",
        "total_requeridas": len(IMAGE_MANIFEST),
        "faltantes": missing,
        "completo": len(missing) == 0,
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "site": Config.SITE_NAME})


@app.route("/robots.txt")
def robots_txt():
    """robots.txt básico para motores de búsqueda."""
    contenido = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return app.response_class(contenido, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    """
    Genera un sitemap.xml simple. Como el sitio es de una sola página con
    anclas (#inicio, #quienes-somos, etc.) se listan las anclas principales
    para ayudar a los buscadores a entender la estructura del contenido.
    """
    base_url = request.url_root.rstrip("/")
    urls = [f"{base_url}/#{item['id']}" for item in NAV_ITEMS]
    urls.insert(0, f"{base_url}/")

    entradas = "\n".join(
        f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>" for u in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entradas}\n"
        "</urlset>"
    )
    return app.response_class(xml, mimetype="application/xml")


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html", site=build_base_context()["site"]), 404


@app.errorhandler(500)
def server_error(_error):
    logger.exception("Error interno del servidor")
    return jsonify({"ok": False, "mensaje": "Ocurrió un error interno."}), 500


# ==============================================================================
# 14. FILTROS Y FUNCIONES ÚTILES PARA JINJA2
# ==============================================================================


@app.template_filter("miles")
def formato_miles(value: int) -> str:
    """Formatea un número con separador de miles: 1234 -> 1,234."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


@app.template_filter("primer_nombre")
def primer_nombre_filtro(nombre_completo: str) -> str:
    """Filtro Jinja2: devuelve solo la primera palabra de un nombre."""
    if not nombre_completo:
        return ""
    return nombre_completo.strip().split(" ")[0]


@app.template_filter("iniciales")
def iniciales_filtro(nombre_completo: str) -> str:
    """Filtro Jinja2: devuelve las iniciales de un nombre, ej. 'María Gómez' -> 'MG'."""
    if not nombre_completo:
        return ""
    partes = nombre_completo.strip().split(" ")
    letras = [p[0].upper() for p in partes if p]
    return "".join(letras[:2])


@app.context_processor
def inject_globals():
    """Variables disponibles automáticamente en cualquier plantilla."""
    return {
        "current_year": Config.CURRENT_YEAR,
        "site_name": Config.SITE_NAME,
    }


# ==============================================================================
# 15. COMANDOS DE LÍNEA DE COMANDOS (flask <comando>)
# ------------------------------------------------------------------------------
# Ejemplos de uso desde la terminal, estando dentro de la carpeta del
# proyecto y con la variable FLASK_APP configurada (o usando `python -m flask`):
#
#     flask check-images       -> revisa qué imágenes faltan
#     flask list-enrollments   -> lista las inscripciones guardadas en memoria
#     flask show-tokens        -> imprime la paleta de colores/tipografía
# ==============================================================================


@app.cli.command("check-images")
def cli_check_images():
    """Comando: revisa qué imágenes faltan en static/images/."""
    missing = check_missing_images()
    if not missing:
        print("✅ Todas las imágenes requeridas están presentes.")
        return
    print(f"⚠  Faltan {len(missing)} imágenes:")
    for filename in missing:
        print(f"   - {filename}")


@app.cli.command("list-enrollments")
def cli_list_enrollments():
    """Comando: imprime las inscripciones guardadas en memoria."""
    if not ENROLLMENTS_STORE:
        print("Todavía no hay inscripciones registradas.")
        return
    for i, registro in enumerate(ENROLLMENTS_STORE, start=1):
        print(f"{i}. {registro['nombre_completo']} — {registro['correo']} — {registro['ciudad']}")


@app.cli.command("show-tokens")
def cli_show_tokens():
    """Comando: imprime la paleta de colores y tipografía del sitio."""
    print(json.dumps(DESIGN_TOKENS, indent=2, ensure_ascii=False))


# ==============================================================================
# 16. PRUEBAS RÁPIDAS DE HUMO (SMOKE TESTS)
# ------------------------------------------------------------------------------
# Estas funciones no usan un framework de pruebas para mantenerlas simples;
# se ejecutan solo si corres este archivo con el argumento "test":
#     python app.py test
# ==============================================================================


def _run_smoke_tests() -> None:
    print("Ejecutando pruebas rápidas...\n")

    # 1) Un envío completamente vacío debe fallar
    vacio = EnrollmentSubmission()
    assert not vacio.is_valid(), "Un formulario vacío no debería ser válido"
    assert len(vacio.errores) == len(FIELD_VALIDATORS)
    print("[OK] Formulario vacío es rechazado correctamente.")

    # 2) Un envío válido debe pasar
    valido = EnrollmentSubmission(
        nombre_completo="María Fernández",
        edad="29",
        correo="maria@correo.com",
        ciudad="Santo Domingo",
        telefono="809-555-1234",
        como_supiste="Redes sociales",
    )
    assert valido.is_valid(), f"Debería ser válido, errores: {valido.errores}"
    print("[OK] Formulario completo y correcto es aceptado.")

    # 3) Un correo mal formado debe fallar solo en ese campo
    correo_malo = EnrollmentSubmission(
        nombre_completo="María Fernández",
        edad="29",
        correo="no-es-un-correo",
        ciudad="Santo Domingo",
        telefono="809-555-1234",
        como_supiste="Redes sociales",
    )
    assert not correo_malo.is_valid()
    assert "correo" in correo_malo.errores
    assert "nombre_completo" not in correo_malo.errores
    print("[OK] Correo inválido se detecta de forma aislada.")

    # 4) El limitador de intentos debe bloquear después del máximo
    limitador_prueba = SimpleRateLimiter(max_intentos=2, ventana_segundos=60)
    assert limitador_prueba.permitir("ip-test")
    assert limitador_prueba.permitir("ip-test")
    assert not limitador_prueba.permitir("ip-test")
    print("[OK] El limitador de intentos bloquea correctamente tras el máximo.")

    # 5) El manifiesto de imágenes no debe tener nombres de archivo repetidos
    nombres = [meta["filename"] for meta in IMAGE_MANIFEST.values()]
    assert len(nombres) == len(set(nombres)), "Hay nombres de imagen duplicados"
    print("[OK] El manifiesto de imágenes no tiene nombres duplicados.")

    print("\n✅ Todas las pruebas pasaron correctamente.")


# ==============================================================================
# 17. PUNTO DE ENTRADA
# ==============================================================================

if __name__ == "__main__":
    import sys

    os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        _run_smoke_tests()
        sys.exit(0)

    print(print_image_setup_instructions())
    missing_now = check_missing_images()
    if missing_now:
        print(f"\n⚠  Te faltan {len(missing_now)} imágenes por agregar todavía.\n")
    else:
        print("\n✅ ¡Todas las imágenes requeridas están presentes!\n")

    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
