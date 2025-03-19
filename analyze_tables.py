from db_connection import SQLServerConnection
from typing import Dict, List
import json

class DatabaseAnalyzer:
    def __init__(self, connection: SQLServerConnection):
        self.conn = connection

    def get_all_tables(self) -> List[str]:
        """Obtiene todas las tablas de la base de datos actual"""
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        result = self.conn.execute_query(query)
        return [row[0] for row in result] if result else []

    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Obtiene información detallada de las columnas de una tabla"""
        query = """
        SELECT 
            c.name AS column_name,
            t.name AS data_type,
            c.max_length,
            c.is_nullable,
            CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END as is_primary_key,
            CASE WHEN fk.parent_column_id IS NOT NULL THEN 1 ELSE 0 END as is_foreign_key,
            OBJECT_NAME(fk.referenced_object_id) as referenced_table,
            COL_NAME(fk.referenced_object_id, fk.referenced_column_id) as referenced_column
        FROM sys.columns c
        INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
        LEFT JOIN (
            SELECT ic.object_id, ic.column_id
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            WHERE i.is_primary_key = 1
        ) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
        LEFT JOIN sys.foreign_key_columns fk ON c.object_id = fk.parent_object_id 
            AND c.column_id = fk.parent_column_id
        WHERE c.object_id = OBJECT_ID(?)
        ORDER BY c.column_id;
        """
        result = self.conn.execute_query(query, [table_name])
        columns = []
        if result:
            for row in result:
                column = {
                    'name': row[0],
                    'data_type': row[1],
                    'max_length': row[2],
                    'is_nullable': row[3],
                    'is_primary_key': bool(row[4]),
                    'is_foreign_key': bool(row[5]),
                    'referenced_table': row[6],
                    'referenced_column': row[7]
                }
                columns.append(column)
        return columns

    def analyze_database_structure(self) -> Dict:
        """Analiza la estructura completa de la base de datos"""
        database_structure = {}
        tables = self.get_all_tables()
        
        print(f"Encontradas {len(tables)} tablas. Analizando estructura...")
        
        for i, table in enumerate(tables, 1):
            print(f"Analizando tabla {i}/{len(tables)}: {table}")
            columns = self.get_table_columns(table)
            database_structure[table] = columns
            
        return database_structure

def main():
    # Configuración de la conexión
    SERVER = "192.168.10.191"
    USERNAME = "consultor"
    PASSWORD = "Consultor1"
    DATABASE = "DynamicsAx1_PRODUCTIVO"
    
    # Crear conexión
    connection = SQLServerConnection(SERVER, USERNAME, PASSWORD, DATABASE)
    
    if connection.connect():
        print(f"\nAnalizando base de datos: {DATABASE}")
        
        # Crear analizador y obtener estructura
        analyzer = DatabaseAnalyzer(connection)
        database_structure = analyzer.analyze_database_structure()
        
        # Guardar resultado en un archivo JSON
        output_file = f"{DATABASE}_structure.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database_structure, f, indent=2, ensure_ascii=False)
        
        print(f"\nEstructura de la base de datos guardada en: {output_file}")
        
        # Mostrar un resumen
        print("\nResumen de algunas tablas encontradas:")
        table_count = 0
        for table, columns in database_structure.items():
            if table_count >= 10:  # Mostrar solo las primeras 10 tablas con columnas
                break
            if columns:  # Solo mostrar tablas que tienen columnas
                pk_columns = [col['name'] for col in columns if col['is_primary_key']]
                fk_columns = [(col['name'], col['referenced_table']) for col in columns if col['is_foreign_key']]
                print(f"\nTabla: {table}")
                print(f"- Columnas totales: {len(columns)}")
                print(f"- Claves primarias: {', '.join(pk_columns) if pk_columns else 'Ninguna'}")
                if fk_columns:
                    print("- Claves foráneas:")
                    for fk_name, ref_table in fk_columns:
                        print(f"  * {fk_name} -> {ref_table}")
                table_count += 1
    
        # Cerrar conexión
        connection.close()

if __name__ == "__main__":
    main()
