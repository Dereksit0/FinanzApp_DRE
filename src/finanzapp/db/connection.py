"""Gestión de la conexión a SQLite y del esquema.

Única clase que conoce el motor de persistencia. El repositorio pide la
conexión aquí; el resto de capas nunca ve `sqlite3`.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

_RUTA_SCHEMA = Path(__file__).with_name("schema.sql")


class BaseDatos:
    def __init__(self, ruta: str | Path, inicializar: bool = True) -> None:
        self.ruta = str(ruta)
        if self.ruta != ":memory:":
            Path(self.ruta).parent.mkdir(parents=True, exist_ok=True)

        self._conexion = sqlite3.connect(self.ruta, check_same_thread=False)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute("PRAGMA foreign_keys = ON")

        if inicializar:
            self.inicializar_esquema()

    @property
    def conexion(self) -> sqlite3.Connection:
        return self._conexion

    def inicializar_esquema(self) -> None:
        script = _RUTA_SCHEMA.read_text(encoding="utf-8")
        self._conexion.executescript(script)
        self._conexion.commit()

    def cerrar(self) -> None:
        self._conexion.close()
