"""Punto de entrada de FinanzApp.

Ejecutar con:
    streamlit run app.py

Aquí se construyen las dependencias (BaseDatos -> GastoRepository ->
GastoService) y se ceden a la capa de UI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st

from finanzapp.config import RUTA_DB
from finanzapp.db import BaseDatos
from finanzapp.repositories import GastoRepository
from finanzapp.services import GastoService
from finanzapp.ui import render


@st.cache_resource
def obtener_servicio() -> GastoService:
    db = BaseDatos(RUTA_DB)
    return GastoService(GastoRepository(db))


def main() -> None:
    st.set_page_config(page_title="FinanzApp", layout="wide")
    render(obtener_servicio())


if __name__ == "__main__":
    main()
