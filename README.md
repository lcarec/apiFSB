# Dynamics AX Table Structure Viewer

Una aplicación para visualizar y analizar la estructura de tablas en Dynamics AX, permitiendo:

- Búsqueda de tablas por nombre o columnas
- Visualización de la estructura detallada de cada tabla
- Vista previa de datos
- Información sobre relaciones entre tablas (llaves primarias y foráneas)

## Características

- Interfaz gráfica intuitiva usando tkinter
- Búsqueda en tiempo real con barra de progreso
- Vista detallada de campos, tipos de datos y relaciones
- Vista previa de los primeros registros de cada tabla
- Soporte para scroll horizontal en tablas anchas

## Requisitos

- Python 3.x
- pyodbc
- tkinter (incluido en Python)

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecutar la aplicación:
```bash
python table_structure_viewer.py
```

2. Usar la barra de búsqueda para encontrar tablas
3. Seleccionar una tabla para ver su estructura
4. La vista previa de datos se cargará automáticamente

## Estructura del Proyecto

- `table_structure_viewer.py`: Aplicación principal con la interfaz gráfica
- `db_connection.py`: Clase para manejar la conexión a la base de datos
- `DynamicsAx1_PRODUCTIVO_structure.json`: Estructura de las tablas
- `table_analysis.json`: Análisis de relaciones entre tablas

## Notas de Seguridad

- Las credenciales de la base de datos deben configurarse de manera segura
- Se recomienda usar un usuario con permisos de solo lectura
- No se incluyen datos sensibles en el repositorio
