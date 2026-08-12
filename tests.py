"""
================================================================================
 tests.py — Suite de pruebas para el sitio ALMA
================================================================================
Corre estas pruebas con:

    python -m unittest tests.py -v

o simplemente:

    python tests.py

Cubren:
  - Validadores de campos individuales (nombre, edad, correo, ciudad, teléfono)
  - El flujo completo de EnrollmentSubmission
  - El limitador de intentos (rate limiter)
  - Las rutas HTTP principales usando el cliente de pruebas de Flask
  - Que el manifiesto de imágenes esté bien formado
================================================================================
"""

import json
import unittest

from app import (
    app,
    EnrollmentSubmission,
    FIELD_VALIDATORS,
    NameValidator,
    AgeValidator,
    EmailValidator,
    CityValidator,
    PhoneValidator,
    SelectValidator,
    SimpleRateLimiter,
    IMAGE_MANIFEST,
    NAV_ITEMS,
    VALUES,
    CAMP_DAYS,
    IMPACT_STATS,
    TESTIMONIALS,
    sanitize,
    check_missing_images,
)


# ==============================================================================
# Pruebas de validadores individuales
# ==============================================================================


class TestNameValidator(unittest.TestCase):
    def setUp(self):
        self.validator = NameValidator()

    def test_nombre_valido(self):
        self.assertTrue(self.validator.is_valid("María Fernández"))

    def test_nombre_con_apostrofe_y_guion(self):
        self.assertTrue(self.validator.is_valid("Ana Luisa D'León-Vargas"))

    def test_nombre_vacio_invalido(self):
        self.assertFalse(self.validator.is_valid(""))

    def test_nombre_muy_corto_invalido(self):
        self.assertFalse(self.validator.is_valid("Al"))

    def test_nombre_con_numeros_invalido(self):
        self.assertFalse(self.validator.is_valid("María123"))


class TestAgeValidator(unittest.TestCase):
    def setUp(self):
        self.validator = AgeValidator()

    def test_edad_valida(self):
        self.assertTrue(self.validator.is_valid("29"))

    def test_edad_limite_inferior(self):
        self.assertTrue(self.validator.is_valid("14"))

    def test_edad_limite_superior(self):
        self.assertTrue(self.validator.is_valid("70"))

    def test_edad_fuera_de_rango(self):
        self.assertFalse(self.validator.is_valid("5"))
        self.assertFalse(self.validator.is_valid("120"))

    def test_edad_no_numerica(self):
        self.assertFalse(self.validator.is_valid("treinta"))


class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = EmailValidator()

    def test_correo_valido(self):
        self.assertTrue(self.validator.is_valid("madre@ejemplo.com"))

    def test_correo_sin_arroba_invalido(self):
        self.assertFalse(self.validator.is_valid("madre.ejemplo.com"))

    def test_correo_sin_dominio_invalido(self):
        self.assertFalse(self.validator.is_valid("madre@ejemplo"))

    def test_correo_vacio_invalido(self):
        self.assertFalse(self.validator.is_valid(""))


class TestCityValidator(unittest.TestCase):
    def setUp(self):
        self.validator = CityValidator()

    def test_ciudad_valida(self):
        self.assertTrue(self.validator.is_valid("Santiago"))

    def test_ciudad_vacia_invalida(self):
        self.assertFalse(self.validator.is_valid(""))

    def test_ciudad_un_caracter_invalida(self):
        self.assertFalse(self.validator.is_valid("S"))


class TestPhoneValidator(unittest.TestCase):
    def setUp(self):
        self.validator = PhoneValidator()

    def test_telefono_valido_con_guiones(self):
        self.assertTrue(self.validator.is_valid("809-555-1234"))

    def test_telefono_valido_con_espacios(self):
        self.assertTrue(self.validator.is_valid("809 555 1234"))

    def test_telefono_muy_corto_invalido(self):
        self.assertFalse(self.validator.is_valid("123"))

    def test_telefono_con_letras_invalido(self):
        self.assertFalse(self.validator.is_valid("809-ABC-1234"))


class TestSelectValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SelectValidator()

    def test_opcion_valida(self):
        self.assertTrue(self.validator.is_valid("Redes sociales"))

    def test_placeholder_invalido(self):
        self.assertFalse(self.validator.is_valid("Selecciona una opción"))

    def test_vacio_invalido(self):
        self.assertFalse(self.validator.is_valid(""))


# ==============================================================================
# Pruebas del formulario completo (EnrollmentSubmission)
# ==============================================================================


class TestEnrollmentSubmission(unittest.TestCase):
    def test_formulario_completo_valido(self):
        submission = EnrollmentSubmission(
            nombre_completo="Carmen Rosa Peña",
            edad="24",
            correo="carmen@correo.com",
            ciudad="Licey al Medio",
            telefono="809-000-0000",
            como_supiste="Un profesional de la salud",
        )
        self.assertTrue(submission.is_valid())
        self.assertEqual(submission.errores, {})

    def test_formulario_vacio_reporta_todos_los_errores(self):
        submission = EnrollmentSubmission()
        self.assertFalse(submission.is_valid())
        self.assertEqual(len(submission.errores), len(FIELD_VALIDATORS))

    def test_primer_nombre(self):
        submission = EnrollmentSubmission(nombre_completo="Ana María Reyes")
        self.assertEqual(submission.primer_nombre(), "Ana")

    def test_to_dict_incluye_todos_los_campos(self):
        submission = EnrollmentSubmission(nombre_completo="Test Usuario")
        data = submission.to_dict()
        for campo in ("nombre_completo", "edad", "correo", "ciudad", "telefono", "como_supiste"):
            self.assertIn(campo, data)


class TestSanitize(unittest.TestCase):
    def test_quita_espacios_extra(self):
        self.assertEqual(sanitize("  Ana   María  "), "Ana María")

    def test_valor_none_devuelve_cadena_vacia(self):
        self.assertEqual(sanitize(None), "")


# ==============================================================================
# Pruebas del limitador de intentos
# ==============================================================================


class TestSimpleRateLimiter(unittest.TestCase):
    def test_permite_hasta_el_maximo(self):
        limiter = SimpleRateLimiter(max_intentos=3, ventana_segundos=60)
        self.assertTrue(limiter.permitir("ip-1"))
        self.assertTrue(limiter.permitir("ip-1"))
        self.assertTrue(limiter.permitir("ip-1"))

    def test_bloquea_despues_del_maximo(self):
        limiter = SimpleRateLimiter(max_intentos=2, ventana_segundos=60)
        limiter.permitir("ip-2")
        limiter.permitir("ip-2")
        self.assertFalse(limiter.permitir("ip-2"))

    def test_ips_distintas_no_se_afectan(self):
        limiter = SimpleRateLimiter(max_intentos=1, ventana_segundos=60)
        self.assertTrue(limiter.permitir("ip-a"))
        self.assertTrue(limiter.permitir("ip-b"))


# ==============================================================================
# Pruebas del contenido (datos que alimentan el HTML)
# ==============================================================================


class TestContenido(unittest.TestCase):
    def test_hay_ocho_o_mas_items_de_navegacion(self):
        self.assertGreaterEqual(len(NAV_ITEMS), 8)

    def test_hay_seis_valores(self):
        self.assertEqual(len(VALUES), 6)

    def test_hay_cinco_dias_de_campamento(self):
        self.assertEqual(len(CAMP_DAYS), 5)

    def test_dia_cinco_es_presencial(self):
        dia_5 = [d for d in CAMP_DAYS if d["number"] == 5][0]
        self.assertTrue(dia_5["presencial"])

    def test_hay_cinco_estadisticas_de_impacto(self):
        self.assertEqual(len(IMPACT_STATS), 5)

    def test_hay_al_menos_tres_testimonios(self):
        self.assertGreaterEqual(len(TESTIMONIALS), 3)

    def test_manifiesto_de_imagenes_sin_duplicados(self):
        nombres = [meta["filename"] for meta in IMAGE_MANIFEST.values()]
        self.assertEqual(len(nombres), len(set(nombres)))


# ==============================================================================
# Pruebas de las rutas HTTP (usando el cliente de pruebas de Flask)
# ==============================================================================


class TestRutas(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_pagina_principal_carga(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("ALMA", respuesta.get_data(as_text=True))

    def test_health_check(self):
        respuesta = self.client.get("/health")
        self.assertEqual(respuesta.status_code, 200)
        data = json.loads(respuesta.get_data(as_text=True))
        self.assertEqual(data["status"], "ok")

    def test_robots_txt(self):
        respuesta = self.client.get("/robots.txt")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("User-agent", respuesta.get_data(as_text=True))

    def test_sitemap_xml(self):
        respuesta = self.client.get("/sitemap.xml")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("<urlset", respuesta.get_data(as_text=True))

    def test_estado_imagenes(self):
        respuesta = self.client.get("/estado-imagenes")
        self.assertEqual(respuesta.status_code, 200)
        data = json.loads(respuesta.get_data(as_text=True))
        self.assertIn("faltantes", data)

    def test_inscripcion_con_datos_invalidos_devuelve_400(self):
        respuesta = self.client.post("/inscripcion", data={})
        self.assertEqual(respuesta.status_code, 400)

    def test_inscripcion_con_datos_validos_devuelve_200(self):
        respuesta = self.client.post("/inscripcion", data={
            "nombre_completo": "Yolanda Pérez",
            "edad": "31",
            "correo": "yolanda@correo.com",
            "ciudad": "Santiago",
            "telefono": "809-111-2222",
            "como_supiste": "Redes sociales",
        })
        self.assertEqual(respuesta.status_code, 200)
        data = json.loads(respuesta.get_data(as_text=True))
        self.assertTrue(data["ok"])

    def test_pagina_no_encontrada_devuelve_404(self):
        respuesta = self.client.get("/esta-ruta-no-existe")
        self.assertEqual(respuesta.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
