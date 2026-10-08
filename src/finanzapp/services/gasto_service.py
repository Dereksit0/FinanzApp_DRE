"""Lógica de negocio de gastos.

Aquí viven las reglas (validaciones) y el filtrado por fechas/categoría.
El servicio delega la persistencia en `GastoRepository` y nunca toca SQL.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Optional

from ..config import DESCRIPCION_MAX
from ..models.categoria import Categoria
from ..models.gasto import Gasto
from ..repositories.gasto_repository import GastoRepository


class GastoService:
    def __init__(self, repo: GastoRepository) -> None:
        self.repo = repo

    def validar(self, gasto: Gasto) -> None:
        """Aplica las reglas de negocio a un gasto.

        Lanza `ValueError` con un mensaje claro si algo no cumple.
        """
        if not isinstance(gasto.fecha, date):
            raise ValueError("La fecha debe ser una fecha válida.")

        if not isinstance(gasto.categoria, Categoria):
            raise ValueError("La categoría debe ser una categoría válida.")

        monto = gasto.monto
        if isinstance(monto, bool) or not isinstance(monto, (int, float)):
            raise ValueError("El monto debe ser un número.")
        if not math.isfinite(monto):
            raise ValueError("El monto debe ser un número finito.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")

        if len(gasto.descripcion or "") > DESCRIPCION_MAX:
            raise ValueError(
                f"La descripción no puede superar {DESCRIPCION_MAX} caracteres."
            )

    def crear_gasto(
        self,
        fecha: date,
        categoria: Categoria,
        monto: float,
        descripcion: str = "",
    ) -> Gasto:
        gasto = Gasto(
            fecha=fecha,
            categoria=categoria,
            monto=monto,
            descripcion="" if descripcion is None else str(descripcion).strip(),
        )
        self.validar(gasto)
        gasto.monto = float(gasto.monto)
        self.repo.insertar(gasto)
        return gasto

    def actualizar_gasto(self, gasto: Gasto) -> None:
        if gasto.id is None:
            raise ValueError("No se puede actualizar un gasto sin id.")
        gasto.descripcion = "" if gasto.descripcion is None else str(gasto.descripcion).strip()
        self.validar(gasto)
        gasto.monto = float(gasto.monto)
        self.repo.actualizar(gasto)

    def borrar_gasto(self, id_gasto: int) -> bool:
        return self.repo.borrar(id_gasto)

    def listar_gastos(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        categoria: Optional[Categoria] = None,
    ) -> list[Gasto]:
        """Devuelve los gastos que cumplen el rango de fechas y la categoría.

        El filtrado es una regla de negocio y se aplica en memoria; para uso
        personal el volumen es bajo. Devuelve la misma vista que consumirán
        la tabla y la gráfica.
        """
        if fecha_desde is not None and fecha_hasta is not None:
            if fecha_desde > fecha_hasta:
                raise ValueError("La fecha inicial no puede ser posterior a la final.")
        if categoria is not None and not isinstance(categoria, Categoria):
            raise ValueError("La categoría debe ser una categoría válida.")

        gastos = self.repo.listar()
        return [
            gasto
            for gasto in gastos
            if (fecha_desde is None or gasto.fecha >= fecha_desde)
            and (fecha_hasta is None or gasto.fecha <= fecha_hasta)
            and (categoria is None or gasto.categoria is categoria)
        ]

    def total(self, gastos: list[Gasto]) -> float:
        return round(sum(gasto.monto for gasto in gastos), 2)

    def total_por_categoria(self, gastos: list[Gasto]) -> dict[Categoria, float]:
        totales: dict[Categoria, float] = {}
        for gasto in gastos:
            totales[gasto.categoria] = round(
                totales.get(gasto.categoria, 0.0) + gasto.monto, 2
            )
        return totales
