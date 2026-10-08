"""Configuración global de FinanzApp."""

import os
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

DIRECTORIO_DATOS = RAIZ_PROYECTO / "data"
RUTA_DB = Path(os.environ.get("FINANZAPP_DB", DIRECTORIO_DATOS / "finanzapp.db"))

# Límites de validación (usados por la capa de servicio)
DESCRIPCION_MAX = 200
