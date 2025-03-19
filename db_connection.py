import pyodbc
from typing import Optional, List, Any

class SQLServerConnection:
    def __init__(self, server: str, username: str, password: str, database: Optional[str] = None):
        self.server = server
        self.username = username
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establece la conexión con SQL Server"""
        try:
            connection_string = (
                f"DRIVER={{SQL Server}};"
                f"SERVER={self.server};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
            
            if self.database:
                connection_string += f"DATABASE={self.database};"

            print("Intentando conectar a SQL Server...")
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            print("Conexión establecida exitosamente!")
            # Mostrar las bases de datos disponibles
            self.show_databases()
            return True
        except pyodbc.Error as e:
            print(f"Error al conectar: {str(e)}")
            return False

    def show_databases(self):
        """Muestra todas las bases de datos disponibles"""
        try:
            self.cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
            databases = self.cursor.fetchall()
            print("\nBases de datos disponibles:")
            for db in databases:
                print(f"- {db[0]}")
        except pyodbc.Error as e:
            print(f"Error al obtener bases de datos: {str(e)}")

    def execute_query(self, query: str, params: List[Any] = None) -> Optional[List[tuple]]:
        """Ejecuta una consulta SQL con parámetros opcionales"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Error al ejecutar la consulta: {str(e)}")
            return None

    def close(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Conexión cerrada.")

def main():
    # Configuración de la conexión
    SERVER = "192.168.10.191"
    USERNAME = "consultor"
    PASSWORD = "Consultor1"
    
    # Crear instancia de la conexión
    db = SQLServerConnection(SERVER, USERNAME, PASSWORD)
    
    # Intentar conectar
    if db.connect():
        # Aquí puedes agregar tus consultas
        print("\nPuedes agregar tus consultas SQL aquí.")
        
        # Ejemplo: seleccionar una base de datos específica
        db_name = input("\nIngrese el nombre de la base de datos a usar: ")
        if db_name:
            db.execute_query(f"USE {db_name}")
            print(f"Base de datos actual: {db_name}")
    
    # Cerrar conexión al finalizar
    db.close()

if __name__ == "__main__":
    main()
