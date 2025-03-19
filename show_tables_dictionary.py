from db_connection import SQLServerConnection

def get_tables_info(connection: SQLServerConnection):
    """Obtiene información detallada de todas las tablas en la base de datos"""
    query = """
    SELECT 
        t.name AS table_name,
        SCHEMA_NAME(t.schema_id) AS schema_name,
        p.value AS table_description
    FROM sys.tables t
    LEFT JOIN sys.extended_properties p ON 
        p.major_id = t.object_id AND 
        p.minor_id = 0 AND 
        p.name = 'MS_Description'
    ORDER BY schema_name, table_name
    """
    
    print("\nObteniendo lista de tablas...")
    tables = connection.execute_query(query)
    
    # Agrupar por esquema
    schemas = {}
    for table in tables:
        schema = table[1] or 'dbo'
        if schema not in schemas:
            schemas[schema] = []
        schemas[schema].append({
            'name': table[0],
            'description': table[2] if table[2] else 'Sin descripción'
        })
    
    return schemas

def main():
    # Configuración
    SERVER = "192.168.10.191"
    USERNAME = "consultor"
    PASSWORD = "Consultor1"
    DATABASE = "DynamicsAx1_PRODUCTIVO"
    
    # Crear conexión
    connection = SQLServerConnection(SERVER, USERNAME, PASSWORD, DATABASE)
    
    if connection.connect():
        print(f"Conectado a la base de datos: {DATABASE}")
        
        # Obtener información de las tablas
        schemas = get_tables_info(connection)
        
        # Mostrar resultados
        total_tables = sum(len(tables) for tables in schemas.values())
        print(f"\nEncontradas {total_tables} tablas en {len(schemas)} esquemas:")
        
        for schema_name, tables in schemas.items():
            print(f"\nEsquema: {schema_name}")
            print("-" * 80)
            
            for table in tables:
                print(f"Tabla: {table['name']}")
                print(f"Descripción: {table['description']}")
                print("-" * 40)
        
        connection.close()
        print("\nConexión cerrada.")

if __name__ == "__main__":
    main()
