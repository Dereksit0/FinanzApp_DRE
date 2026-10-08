"""Modelo de dominio `Gasto`.

Es una estructura de datos "tonta": solo almacena y serializa. Las reglas
de negocio (monto > 0, fecha válida, longitud de descripción) NO viven
aquí, sino en la capa de servicio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping, Optional

from .categoria import Categoria


@dataclass
class Gasto:
    fecha: date
    categoria: Categoria
    monto: float
    descripcion: str = ""
    id: Optional[int] = field(default=None, compare=False)

    def to_dict(self) -> dict[str, Any]:
        """Representación apta para persistencia (tipos primitivos)."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "categoria": self.categoria.name,
            "monto": float(self.monto),
            "descripcion": self.descripcion or "",
        }

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Gasto":
        """Construye un Gasto a partir de una fila de SQLite."""
        return cls(
            id=row["id"],
            fecha=date.fromisoformat(row["fecha"]),
            categoria=Categoria.desde_nombre(row["categoria"]),
            monto=float(row["monto"]),
            descripcion=row["descripcion"] or "",
        )
