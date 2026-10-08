"""Componentes de presentación reutilizables.

Solo transforman objetos de dominio en vistas; no contienen reglas de
negocio ni acceden a la base de datos.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..models.categoria import Categoria
from ..models.gasto import Gasto


def gastos_a_dataframe(gastos: list[Gasto]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": gasto.id,
                "Fecha": gasto.fecha,
                "Categoría": gasto.categoria.etiqueta,
                "Monto": round(float(gasto.monto), 2),
                "Descripción": gasto.descripcion,
            }
            for gasto in gastos
        ],
        columns=["ID", "Fecha", "Categoría", "Monto", "Descripción"],
    )


def render_tabla(gastos: list[Gasto]) -> None:
    if not gastos:
        st.info("No hay gastos que coincidan con el filtro actual.")
        return
    st.dataframe(
        gastos_a_dataframe(gastos),
        hide_index=True,
        column_config={
            "Monto": st.column_config.NumberColumn("Monto", format="%.2f"),
            "Fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
        },
    )


def render_grafica(totales: dict[Categoria, float]) -> None:
    if not totales:
        st.info("No hay datos para graficar con el filtro actual.")
        return
    datos = pd.DataFrame(
        {
            "Categoría": [categoria.etiqueta for categoria in totales],
            "Total": list(totales.values()),
        }
    )
    st.bar_chart(datos, x="Categoría", y="Total")
