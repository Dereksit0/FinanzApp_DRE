"""Acceso a datos de `Gasto`. Solo CRUD, sin reglas de negocio.

Responsabilidades:
  * Ejecutar SQL contra SQLite.
  * Mapear filas <-> objetos `Gasto` (incluye la conversión de `Categoria`).

Lo que NO hace: validar reglas de negocio ni filtrar por fechas. Eso vive
en `GastoService`.
"""

from __future__ import annotations

from typing import Optional

from ..db.connection import BaseDatos
from ..models.gasto import Gasto


class GastoRepository:
    def __init__(self, db: BaseDatos) -> None:
        self.db = db

    def insertar(self, gasto: Gasto) -> int:
        datos = gasto.to_dict()
        cursor = self.db.conexion.execute(
            "INSERT INTO gastos (fecha, categoria, monto, descripcion) "
            "VALUES (?, ?, ?, ?)",
            (
                datos["fecha"],
                datos["categoria"],
                datos["monto"],
                datos["descripcion"],
            ),
        )
        self.db.conexion.commit()
        gasto.id = cursor.lastrowid
        return int(cursor.lastrowid)

    def actualizar(self, gasto: Gasto) -> None:
        if gasto.id is None:
            raise ValueError("No se puede actualizar un gasto sin id.")
        datos = gasto.to_dict()
        cursor = self.db.conexion.execute(
            "UPDATE gastos SET fecha = ?, categoria = ?, monto = ?, descripcion = ? "
            "WHERE id = ?",
            (
                datos["fecha"],
                datos["categoria"],
                datos["monto"],
                datos["descripcion"],
                gasto.id,
            ),
        )
        self.db.conexion.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"No existe un gasto con id={gasto.id}.")

    def borrar(self, id_gasto: int) -> bool:
        cursor = self.db.conexion.execute(
            "DELETE FROM gastos WHERE id = ?", (id_gasto,)
        )
        self.db.conexion.commit()
        return cursor.rowcount > 0

    def listar(self) -> list[Gasto]:
        filas = self.db.conexion.execute(
            "SELECT * FROM gastos ORDER BY fecha DESC, id DESC"
        ).fetchall()
        return [Gasto.from_row(fila) for fila in filas]

    def obtener_por_id(self, id_gasto: int) -> Optional[Gasto]:
        fila = self.db.conexion.execute(
            "SELECT * FROM gastos WHERE id = ?", (id_gasto,)
        ).fetchone()
        return Gasto.from_row(fila) if fila is not None else None
