"""Script de verificación manual del CRUD.

Uso:
    python scripts/demo_crud.py

Crea una base de datos temporal, ejecuta insertar / listar / actualizar /
borrar y muestra el resultado por consola.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finanzapp.db import BaseDatos  # noqa: E402
from finanzapp.models import Categoria, Gasto  # noqa: E402
from finanzapp.repositories import GastoRepository  # noqa: E402


def main() -> None:
    ruta = Path(tempfile.gettempdir()) / "finanzapp_demo.db"
    if ruta.exists():
        ruta.unlink()

    db = BaseDatos(ruta)
    repo = GastoRepository(db)

    print("== Insertar ==")
    for gasto in (
        Gasto(date(2026, 1, 10), Categoria.COMIDA, 12.50, "Almuerzo"),
        Gasto(date(2026, 2, 3), Categoria.TRANSPORTE, 30.00, "Tren"),
        Gasto(date(2026, 2, 20), Categoria.OCIO, 8.99, ""),
    ):
        nuevo_id = repo.insertar(gasto)
        print(f"  id={nuevo_id}  {gasto.categoria.etiqueta:<12} {gasto.monto:>7.2f}  {gasto.descripcion}")

    print("\n== Listar (orden fecha desc) ==")
    for gasto in repo.listar():
        print(f"  id={gasto.id}  {gasto.fecha}  {gasto.categoria.etiqueta:<12} {gasto.monto:>7.2f}")

    print("\n== Actualizar id=2 ==")
    objetivo = repo.obtener_por_id(2)
    objetivo.monto = 45.75
    objetivo.categoria = Categoria.SERVICIOS
    repo.actualizar(objetivo)
    recargado = repo.obtener_por_id(2)
    print(f"  id={recargado.id}  {recargado.categoria.etiqueta}  {recargado.monto:.2f}")

    print("\n== Borrar id=1 ==")
    print(f"  borrado: {repo.borrar(1)}")
    print(f"  restantes: {[g.id for g in repo.listar()]}")

    db.cerrar()
    print("\nOK: CRUD verificado.")


if __name__ == "__main__":
    main()
