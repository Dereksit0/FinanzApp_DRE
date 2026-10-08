# FinanzApp

Aplicación de control de gastos personales construida en Python con [Streamlit](https://streamlit.io/)
para la interfaz y SQLite como almacenamiento local.

## Funcionalidades

1. **Registrar un gasto** — fecha, categoría, monto y descripción (opcional).
2. **Tabla con filtro por rango de fechas** — vista tabular de los gastos, filtrable por
   fecha (desde/hasta) y categoría.
3. **Editar / eliminar** — selecciona un gasto por ID, edítalo en un formulario precargado
   o elimínalo con confirmación en dos pasos.
4. **Gráfica de gasto por categoría** — resumen visual que refleja exactamente los datos
   que se ven en la tabla (respeta el filtro activo).

## Requisitos

- Python 3.10 o superior.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

Se abrirá la app en el navegador. La base de datos se crea automáticamente en
`data/finanzapp.db` (excluida del control de versiones).

## Pruebas

```bash
pytest
```

## Estructura del proyecto

```
finanzapp/
├─ app.py                      # Punto de entrada (Streamlit)
├─ requirements.txt
├─ src/finanzapp/
│  ├─ config.py                # Configuración (ruta de la BD, límites)
│  ├─ models/                  # Gasto y Categoria (dominio)
│  ├─ db/                      # Conexión SQLite y esquema
│  ├─ repositories/            # GastoRepository (acceso a datos)
│  ├─ services/                # GastoService (validaciones y filtrado)
│  └─ ui/                      # Componentes y páginas de Streamlit
├─ scripts/demo_crud.py        # Verificación manual del CRUD
└─ tests/                      # Pruebas con pytest
```

## Arquitectura

Arquitectura por capas con dependencias unidireccionales:

```
UI  →  GastoService  →  GastoRepository  →  BaseDatos (SQLite)
```

- **UI**: solo interactúa con `GastoService`; nunca toca SQLite.
- **GastoService**: reglas de negocio (monto > 0, fecha válida, filtrado por fechas).
- **GastoRepository**: única puerta de acceso a datos (CRUD).
- **BaseDatos**: gestión de la conexión y del esquema.
