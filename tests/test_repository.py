"""Pruebas mínimas del CRUD de GastoRepository contra SQLite en memoria."""

from datetime import date

import pytest

from finanzapp.db import BaseDatos
from finanzapp.models import Categoria, Gasto
from finanzapp.repositories import GastoRepository


@pytest.fixture
def repo():
    db = BaseDatos(":memory:")
    try:
        yield GastoRepository(db)
    finally:
        db.cerrar()


def _gasto(fecha=date(2026, 1, 10), categoria=Categoria.COMIDA, monto=12.5, desc="Almuerzo"):
    return Gasto(fecha=fecha, categoria=categoria, monto=monto, descripcion=desc)


def test_insertar_asigna_id(repo):
    gasto = _gasto()
    id_generado = repo.insertar(gasto)

    assert id_generado == 1
    assert gasto.id == 1


def test_listar_ordenado_por_fecha_desc(repo):
    repo.insertar(_gasto(fecha=date(2026, 1, 1), monto=10))
    repo.insertar(_gasto(fecha=date(2026, 3, 1), monto=30))
    repo.insertar(_gasto(fecha=date(2026, 2, 1), monto=20))

    fechas = [g.fecha for g in repo.listar()]

    assert fechas == [date(2026, 3, 1), date(2026, 2, 1), date(2026, 1, 1)]


def test_obtener_por_id_reconstruye_categoria(repo):
    id_generado = repo.insertar(_gasto(categoria=Categoria.TRANSPORTE))

    recuperado = repo.obtener_por_id(id_generado)

    assert recuperado is not None
    assert recuperado.categoria is Categoria.TRANSPORTE
    assert recuperado.monto == 12.5


def test_obtener_por_id_inexistente_devuelve_none(repo):
    assert repo.obtener_por_id(999) is None


def test_actualizar_modifica_los_campos(repo):
    gasto = _gasto()
    repo.insertar(gasto)

    gasto.monto = 99.99
    gasto.categoria = Categoria.OCIO
    gasto.descripcion = "Cine"
    repo.actualizar(gasto)

    guardado = repo.obtener_por_id(gasto.id)
    assert guardado.monto == 99.99
    assert guardado.categoria is Categoria.OCIO
    assert guardado.descripcion == "Cine"


def test_actualizar_sin_id_falla(repo):
    with pytest.raises(ValueError):
        repo.actualizar(_gasto())


def test_borrar_devuelve_true_y_elimina(repo):
    id_generado = repo.insertar(_gasto())

    assert repo.borrar(id_generado) is True
    assert repo.obtener_por_id(id_generado) is None
    assert repo.listar() == []


def test_borrar_inexistente_devuelve_false(repo):
    assert repo.borrar(123) is False


def test_descripcion_vacia_se_persiste_como_texto(repo):
    id_generado = repo.insertar(_gasto(desc=""))

    guardado = repo.obtener_por_id(id_generado)
    assert guardado.descripcion == ""
