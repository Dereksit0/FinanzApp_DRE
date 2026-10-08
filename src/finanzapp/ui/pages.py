"""Página principal de FinanzApp.

Toda interacción con los datos pasa por `GastoService`. La UI nunca
importa el repositorio ni SQLite.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from ..models.categoria import Categoria
from ..models.gasto import Gasto
from ..services.gasto_service import GastoService
from . import components

_TODAS = "Todas"


def render(service: GastoService) -> None:
    st.title("FinanzApp")
    st.caption("Control de gastos personales")

    todos = service.listar_gastos()
    fecha_desde, fecha_hasta, categoria = _render_filtros(todos)

    _render_registro(service)

    st.divider()
    st.subheader("Gastos")

    try:
        gastos = service.listar_gastos(fecha_desde, fecha_hasta, categoria)
    except ValueError as error:
        st.error(str(error))
        return

    _render_resumen(service, gastos)

    col_tabla, col_grafica = st.columns([3, 2])
    with col_tabla:
        st.markdown("**Tabla**")
        components.render_tabla(gastos)
    with col_grafica:
        st.markdown("**Gasto por categoría**")
        components.render_grafica(service.total_por_categoria(gastos))

    st.divider()
    _render_editor(service, gastos)


def _marcar_filtros_manuales() -> None:
    st.session_state["_filtros_manuales"] = True


def _render_filtros(todos: list[Gasto]):
    fechas = [gasto.fecha for gasto in todos]
    hoy = date.today()
    min_datos = min(fechas) if fechas else hoy
    max_datos = max(fechas + [hoy])

    # Mientras el usuario no toque los filtros, el rango por defecto abarca
    # SIEMPRE todos los datos (así nunca se ocultan gastos recién cargados).
    if not st.session_state.get("_filtros_manuales", False):
        st.session_state["filtro_desde"] = min_datos
        st.session_state["filtro_hasta"] = max_datos
        st.session_state["filtro_categoria"] = _TODAS

    with st.sidebar:
        st.header("Filtros")
        fecha_desde = st.date_input(
            "Desde", key="filtro_desde", on_change=_marcar_filtros_manuales
        )
        fecha_hasta = st.date_input(
            "Hasta", key="filtro_hasta", on_change=_marcar_filtros_manuales
        )
        opcion = st.selectbox(
            "Categoría",
            [_TODAS, *Categoria.opciones()],
            key="filtro_categoria",
            on_change=_marcar_filtros_manuales,
        )
        if st.button("Restablecer filtros"):
            st.session_state["_filtros_manuales"] = False
            st.rerun()

    categoria = None if opcion == _TODAS else Categoria.desde_etiqueta(opcion)
    return fecha_desde, fecha_hasta, categoria


def _render_registro(service: GastoService) -> None:
    with st.expander("Registrar nuevo gasto", expanded=True):
        with st.form("form_registro", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            fecha = col1.date_input("Fecha", value=date.today(), key="reg_fecha")
            categoria = col2.selectbox(
                "Categoría", Categoria.opciones(), key="reg_categoria"
            )
            monto = col3.number_input(
                "Monto",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key="reg_monto",
            )
            descripcion = st.text_input(
                "Descripción (opcional)", key="reg_descripcion"
            )
            enviado = st.form_submit_button("Registrar")

    if not enviado:
        return
    try:
        service.crear_gasto(
            fecha=fecha,
            categoria=Categoria.desde_etiqueta(categoria),
            monto=monto,
            descripcion=descripcion,
        )
    except ValueError as error:
        st.error(str(error))
        return
    st.success("Gasto registrado.")
    st.rerun()


def _render_resumen(service: GastoService, gastos: list[Gasto]) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Nº de gastos", len(gastos))
    col2.metric("Total filtrado", f"{service.total(gastos):,.2f}")
    col3.metric("Categorías", len(service.total_por_categoria(gastos)))


def _render_editor(service: GastoService, gastos: list[Gasto]) -> None:
    st.subheader("Editar o eliminar gasto")
    if not gastos:
        st.info("No hay gastos para editar con el filtro actual.")
        return

    ids = [gasto.id for gasto in gastos]
    if st.session_state.get("editor_id") not in ids:
        st.session_state["editor_id"] = ids[0]

    etiquetas = {
        gasto.id: (
            f"#{gasto.id} · {gasto.fecha} · "
            f"{gasto.categoria.etiqueta} · {gasto.monto:.2f}"
        )
        for gasto in gastos
    }
    id_seleccionado = st.selectbox(
        "Selecciona un gasto",
        ids,
        format_func=lambda i: etiquetas[i],
        key="editor_id",
    )
    gasto = next(g for g in gastos if g.id == id_seleccionado)

    _form_edicion(service, gasto)
    _boton_eliminar(service, gasto)


def _form_edicion(service: GastoService, gasto: Gasto) -> None:
    indice_categoria = Categoria.opciones().index(gasto.categoria.etiqueta)
    with st.form(f"form_edicion_{gasto.id}"):
        col1, col2, col3 = st.columns(3)
        fecha = col1.date_input(
            "Fecha", value=gasto.fecha, key=f"edit_fecha_{gasto.id}"
        )
        categoria = col2.selectbox(
            "Categoría",
            Categoria.opciones(),
            index=indice_categoria,
            key=f"edit_categoria_{gasto.id}",
        )
        monto = col3.number_input(
            "Monto",
            min_value=0.0,
            value=float(gasto.monto),
            step=0.01,
            format="%.2f",
            key=f"edit_monto_{gasto.id}",
        )
        descripcion = st.text_input(
            "Descripción (opcional)",
            value=gasto.descripcion,
            key=f"edit_descripcion_{gasto.id}",
        )
        guardado = st.form_submit_button("Guardar cambios")

    if not guardado:
        return
    try:
        gasto.fecha = fecha
        gasto.categoria = Categoria.desde_etiqueta(categoria)
        gasto.monto = monto
        gasto.descripcion = descripcion
        service.actualizar_gasto(gasto)
    except ValueError as error:
        st.error(str(error))
        return
    st.success("Gasto actualizado.")
    st.rerun()


def _boton_eliminar(service: GastoService, gasto: Gasto) -> None:
    if st.button("Eliminar gasto", key=f"borrar_{gasto.id}"):
        st.session_state["confirmar_borrado"] = gasto.id

    if st.session_state.get("confirmar_borrado") != gasto.id:
        return

    st.warning(
        f"¿Eliminar el gasto #{gasto.id} "
        f"({gasto.categoria.etiqueta}, {gasto.monto:.2f})? "
        "Esta acción no se puede deshacer."
    )
    col_confirmar, col_cancelar = st.columns(2)
    if col_confirmar.button("Sí, eliminar", type="primary", key=f"conf_{gasto.id}"):
        service.borrar_gasto(gasto.id)
        st.session_state.pop("confirmar_borrado", None)
        st.session_state.pop("editor_id", None)
        st.success("Gasto eliminado.")
        st.rerun()
    if col_cancelar.button("Cancelar", key=f"cancel_{gasto.id}"):
        st.session_state.pop("confirmar_borrado", None)
        st.rerun()
