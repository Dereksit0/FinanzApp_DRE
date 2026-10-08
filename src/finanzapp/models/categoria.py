"""Enum de categorías de gasto.

En dominio el gasto guarda un `Categoria`; en SQLite se persiste
`Categoria.name` (clave estable). La conversión texto <-> enum vive en
este tipo y la invoca el repositorio en su frontera de persistencia.
"""

from __future__ import annotations

from enum import Enum


class Categoria(Enum):
    COMIDA = "Comida"
    TRANSPORTE = "Transporte"
    OCIO = "Ocio"
    SERVICIOS = "Servicios"
    SALUD = "Salud"
    OTROS = "Otros"

    @property
    def etiqueta(self) -> str:
        """Texto legible para mostrar en la UI."""
        return self.value

    def __str__(self) -> str:
        return self.value

    @classmethod
    def desde_nombre(cls, nombre: str) -> "Categoria":
        """Reconstruye la categoría a partir de su clave persistida."""
        try:
            return cls[str(nombre).strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Categoría desconocida: {nombre!r}") from exc

    @classmethod
    def desde_etiqueta(cls, etiqueta: str) -> "Categoria":
        """Reconstruye la categoría a partir de su texto visible."""
        buscada = str(etiqueta).strip().lower()
        for categoria in cls:
            if categoria.value.lower() == buscada:
                return categoria
        raise ValueError(f"Categoría desconocida: {etiqueta!r}")

    @classmethod
    def opciones(cls) -> list[str]:
        """Lista de etiquetas para poblar selectores en la UI."""
        return [categoria.value for categoria in cls]
