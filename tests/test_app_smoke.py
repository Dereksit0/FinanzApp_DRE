"""Pruebas de humo de la UI con el runner headless de Streamlit (AppTest)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APP = RAIZ / "app.py"


def _widget(lista, key):
    for widget in lista:
        if widget.key == key:
            return widget
    raise AssertionError(f"Widget con key {key!r} no encontrado")


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("FINANZAPP_DB", str(tmp_path / "test.db"))
    for nombre in [n for n in sys.modules if n == "finanzapp" or n.startswith("finanzapp.")]:
        del sys.modules[nombre]
    st.cache_resource.clear()
    instancia = AppTest.from_file(str(APP))
    instancia.run(timeout=60)
    return instancia


def _registrar(app, monto, descripcion=""):
    _widget(app.number_input, "reg_monto").set_value(monto)
    _widget(app.text_input, "reg_descripcion").set_value(descripcion)
    _widget(app.button, "FormSubmitter:form_registro-Registrar").click()
    app.run(timeout=60)


def test_arranca_sin_excepciones(app):
    assert not app.exception
    assert app.title[0].value == "FinanzApp"


def test_arranca_sin_gastos_muestra_tabla_vacia(app):
    assert len(app.dataframe) == 0
    assert any("No hay gastos" in i.value for i in app.info)


def test_registrar_gasto_aparece_en_tabla(app):
    _registrar(app, 15.5, "Cafe")

    assert not app.exception
    assert len(app.dataframe) == 1
    tabla = app.dataframe[0].value
    assert tabla["Monto"].tolist() == [15.5]
    assert tabla["Descripción"].tolist() == ["Cafe"]


def test_gasto_con_fecha_pasada_es_visible_por_defecto(app):
    _widget(app.date_input, "reg_fecha").set_value(date(2020, 1, 1))
    _widget(app.number_input, "reg_monto").set_value(5.0)
    _widget(app.text_input, "reg_descripcion").set_value("Antiguo")
    _widget(app.button, "FormSubmitter:form_registro-Registrar").click()
    app.run(timeout=60)

    assert not app.exception
    assert len(app.dataframe) == 1
    assert _widget(app.selectbox, "editor_id") is not None


def test_editar_gasto_actualiza_tabla(app):
    _registrar(app, 10.0, "Original")

    _widget(app.number_input, "edit_monto_1").set_value(42.0)
    _widget(app.text_input, "edit_descripcion_1").set_value("Actualizado")
    _widget(app.button, "FormSubmitter:form_edicion_1-Guardar cambios").click()
    app.run(timeout=60)

    assert not app.exception
    tabla = app.dataframe[0].value
    assert tabla["Monto"].tolist() == [42.0]
    assert tabla["Descripción"].tolist() == ["Actualizado"]


def test_eliminar_gasto_pide_confirmacion_y_borra(app):
    _registrar(app, 20.0, "Cena")
    assert len(app.dataframe) == 1

    _widget(app.button, "borrar_1").click()
    app.run(timeout=60)
    assert any("¿Eliminar" in w.value for w in app.warning)
    assert len(app.dataframe) == 1

    _widget(app.button, "conf_1").click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) == 0
