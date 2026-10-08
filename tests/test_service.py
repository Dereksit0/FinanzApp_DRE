"""Pruebas de la lógica de negocio de GastoService."""

from datetime import date

import pytest

from finanzapp.db import BaseDatos
from finanzapp.models import Categoria, Gasto
from finanzapp.repositories import GastoRepository
from finanzapp.services import GastoService


@pytest.fixture
def service():
    db = BaseDatos(":memory:")
    repo = GastoRepository(db)
    try:
        yield GastoService(repo)
    finally:
        db.cerrar()


# --- crear_gasto / validaciones -------------------------------------------

def test_crear_gasto_persiste_y_asigna_id(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 12.5, "Almuerzo")

    assert gasto.id is not None
    assert service.repo.obtener_por_id(gasto.id).monto == 12.5


def test_crear_gasto_normaliza_monto_a_float(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 10, "")

    assert isinstance(gasto.monto, float)


def test_descripcion_opcional_se_normaliza_a_vacio(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 5, None)

    assert gasto.descripcion == ""


def test_descripcion_se_recorta(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 5, "  taxi  ")

    assert gasto.descripcion == "taxi"


@pytest.mark.parametrize("monto", [0, -1, -0.01])
def test_monto_no_positivo_falla(service, monto):
    with pytest.raises(ValueError, match="mayor que cero"):
        service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, monto, "")


@pytest.mark.parametrize("monto", ["10", None, True, float("nan"), float("inf")])
def test_monto_no_numerico_o_no_finito_falla(service, monto):
    with pytest.raises(ValueError, match="monto"):
        service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, monto, "")


def test_fecha_invalida_falla(service):
    with pytest.raises(ValueError, match="fecha"):
        service.crear_gasto("2026-01-10", Categoria.COMIDA, 10, "")


def test_categoria_invalida_falla(service):
    with pytest.raises(ValueError, match="categoría"):
        service.crear_gasto(date(2026, 1, 10), "Comida", 10, "")


def test_descripcion_demasiado_larga_falla(service):
    with pytest.raises(ValueError, match="descripción"):
        service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 10, "x" * 201)


def test_validar_gasto_valido_no_lanza(service):
    service.validar(Gasto(date(2026, 1, 10), Categoria.OCIO, 9.99, "cine"))


# --- actualizar / borrar ---------------------------------------------------

def test_actualizar_gasto_valida_y_persiste(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 10, "a")
    gasto.monto = 20
    gasto.categoria = Categoria.OCIO

    service.actualizar_gasto(gasto)

    guardado = service.repo.obtener_por_id(gasto.id)
    assert guardado.monto == 20.0
    assert guardado.categoria is Categoria.OCIO


def test_actualizar_gasto_invalido_falla(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 10, "a")
    gasto.monto = -5

    with pytest.raises(ValueError, match="mayor que cero"):
        service.actualizar_gasto(gasto)


def test_borrar_gasto(service):
    gasto = service.crear_gasto(date(2026, 1, 10), Categoria.COMIDA, 10, "a")

    assert service.borrar_gasto(gasto.id) is True
    assert service.repo.obtener_por_id(gasto.id) is None


# --- listar_gastos / filtrado ---------------------------------------------

def _sembrar(service):
    service.crear_gasto(date(2026, 1, 5), Categoria.COMIDA, 10, "")
    service.crear_gasto(date(2026, 1, 20), Categoria.TRANSPORTE, 20, "")
    service.crear_gasto(date(2026, 2, 15), Categoria.COMIDA, 30, "")


def test_listar_sin_filtros_devuelve_todo(service):
    _sembrar(service)

    assert len(service.listar_gastos()) == 3


def test_filtra_por_rango_de_fechas(service):
    _sembrar(service)

    resultado = service.listar_gastos(date(2026, 1, 1), date(2026, 1, 31))

    assert [g.monto for g in resultado] == [20, 10]


def test_filtra_por_fecha_desde_solo(service):
    _sembrar(service)

    resultado = service.listar_gastos(fecha_desde=date(2026, 1, 20))

    assert {g.monto for g in resultado} == {20, 30}


def test_filtra_por_categoria(service):
    _sembrar(service)

    resultado = service.listar_gastos(categoria=Categoria.COMIDA)

    assert {g.monto for g in resultado} == {10, 30}


def test_filtra_por_rango_y_categoria(service):
    _sembrar(service)

    resultado = service.listar_gastos(
        date(2026, 1, 1), date(2026, 1, 31), Categoria.COMIDA
    )

    assert [g.monto for g in resultado] == [10]


def test_rango_invertido_falla(service):
    with pytest.raises(ValueError, match="posterior"):
        service.listar_gastos(date(2026, 2, 1), date(2026, 1, 1))


def test_categoria_invalida_en_filtro_falla(service):
    with pytest.raises(ValueError, match="categoría"):
        service.listar_gastos(categoria="Comida")


def test_filtro_sin_resultados_devuelve_lista_vacia(service):
    _sembrar(service)

    assert service.listar_gastos(date(2030, 1, 1), date(2030, 12, 31)) == []


# --- agregados -------------------------------------------------------------

def test_total_y_total_por_categoria(service):
    _sembrar(service)

    gastos = service.listar_gastos()

    assert service.total(gastos) == 60.0
    assert service.total_por_categoria(gastos) == {
        Categoria.TRANSPORTE: 20.0,
        Categoria.COMIDA: 40.0,
    }
