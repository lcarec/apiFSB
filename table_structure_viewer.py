import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from typing import Dict, List
import time
from db_connection import SQLServerConnection

class TableStructureViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Estructura de Tablas")
        self.root.geometry("1400x900")  # Ventana más ancha
        
        # Cargar el diccionario de estructura
        with open('DynamicsAx1_PRODUCTIVO_structure.json', 'r', encoding='utf-8') as f:
            self.structure = json.load(f)
        
        # Conexión a la base de datos
        self.db = SQLServerConnection(
            "192.168.10.191",
            "consultor",
            "Consultor1",
            "DynamicsAx1_PRODUCTIVO"
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame superior para búsqueda
        search_frame = ttk.LabelFrame(main_frame, text="Búsqueda", padding="5")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Entrada de búsqueda
        ttk.Label(search_frame, text="Palabra clave:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar(value="LEDGER")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        
        # Opciones de búsqueda
        self.search_tables = tk.BooleanVar(value=True)
        self.search_columns = tk.BooleanVar(value=True)
        ttk.Checkbutton(search_frame, text="Buscar en nombres de tablas", 
                       variable=self.search_tables).grid(row=0, column=2, padx=5)
        ttk.Checkbutton(search_frame, text="Buscar en nombres de columnas", 
                       variable=self.search_columns).grid(row=0, column=3, padx=5)
        
        # Botón de búsqueda
        self.search_button = ttk.Button(search_frame, text="Buscar", 
                                      command=self.search)
        self.search_button.grid(row=0, column=4, padx=5)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(search_frame, 
                                      variable=self.progress_var,
                                      maximum=100,
                                      mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), 
                          padx=5, pady=5)
        
        # Etiqueta de estado
        self.status_var = tk.StringVar(value="Listo")
        self.status_label = ttk.Label(search_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, columnspan=5)
        
        # Frame para resultados con padding
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="5")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dividir el área de resultados en paneles
        results_paned = ttk.PanedWindow(results_frame, orient=tk.VERTICAL)
        results_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel superior: Lista de tablas
        tables_frame = ttk.Frame(results_paned)
        results_paned.add(tables_frame, weight=1)
        
        ttk.Label(tables_frame, text="Tablas encontradas:").grid(row=0, column=0, sticky=tk.W)
        
        self.tables_list = ttk.Treeview(tables_frame, columns=("name",), show="headings", height=6)
        self.tables_list.heading("name", text="Nombre de la tabla")
        self.tables_list.column("name", width=200)  # Ancho fijo para la tabla
        self.tables_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        tables_scroll = ttk.Scrollbar(tables_frame, orient=tk.VERTICAL, command=self.tables_list.yview)
        tables_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tables_list.configure(yscrollcommand=tables_scroll.set)
        
        # Panel medio: Estructura de la tabla
        structure_frame = ttk.Frame(results_paned)
        results_paned.add(structure_frame, weight=2)
        
        ttk.Label(structure_frame, text="Estructura de la tabla:").grid(row=0, column=0, sticky=tk.W)
        
        # TreeView para mostrar los campos
        columns = ("name", "type", "nullable", "key", "references")
        self.fields_list = ttk.Treeview(structure_frame, columns=columns, show="headings", height=8)
        
        # Configurar columnas con anchos fijos
        self.fields_list.heading("name", text="Campo")
        self.fields_list.heading("type", text="Tipo")
        self.fields_list.heading("nullable", text="Nullable")
        self.fields_list.heading("key", text="Llave")
        self.fields_list.heading("references", text="Referencia")
        
        self.fields_list.column("name", width=200)
        self.fields_list.column("type", width=150)
        self.fields_list.column("nullable", width=80)
        self.fields_list.column("key", width=80)
        self.fields_list.column("references", width=300)
        
        self.fields_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        fields_scroll = ttk.Scrollbar(structure_frame, orient=tk.VERTICAL, command=self.fields_list.yview)
        fields_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.fields_list.configure(yscrollcommand=fields_scroll.set)
        
        # Panel inferior: Vista previa de datos
        preview_frame = ttk.Frame(results_paned)
        results_paned.add(preview_frame, weight=2)
        
        ttk.Label(preview_frame, text="Vista previa de datos:").grid(row=0, column=0, sticky=tk.W)
        
        # Contenedor con scroll para la vista previa
        preview_container = ttk.Frame(preview_frame)
        preview_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)
        
        # TreeView para mostrar los datos
        self.data_list = ttk.Treeview(preview_container, show="headings", height=5)
        self.data_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars para la vista previa
        data_scroll_y = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.data_list.yview)
        data_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        data_scroll_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.data_list.xview)
        data_scroll_x.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.data_list.configure(yscrollcommand=data_scroll_y.set, xscrollcommand=data_scroll_x.set)
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        tables_frame.columnconfigure(0, weight=1)
        tables_frame.rowconfigure(1, weight=1)
        structure_frame.columnconfigure(0, weight=1)
        structure_frame.rowconfigure(1, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Vincular eventos
        self.tables_list.bind('<<TreeviewSelect>>', self.show_table_details)
        self.search_entry.bind('<Return>', lambda e: self.search())
        
        # Realizar búsqueda inicial
        self.search()
    
    def update_progress(self, current, total, status_text=""):
        """Actualiza la barra de progreso y el estado"""
        progress = (current / total) * 100
        self.progress_var.set(progress)
        if status_text:
            self.status_var.set(status_text)
        self.root.update_idletasks()
    
    def search(self):
        """Realiza la búsqueda en la estructura"""
        # Deshabilitar botón durante la búsqueda
        self.search_button.configure(state='disabled')
        self.status_var.set("Buscando...")
        self.progress_var.set(0)
        
        keyword = self.search_var.get().upper()
        search_tables = self.search_tables.get()
        search_columns = self.search_columns.get()
        
        # Limpiar resultados anteriores
        for item in self.tables_list.get_children():
            self.tables_list.delete(item)
        
        for item in self.fields_list.get_children():
            self.fields_list.delete(item)
            
        for item in self.data_list.get_children():
            self.data_list.delete(item)
        
        found_tables = []
        total_tables = len(self.structure)
        
        # Buscar en todas las tablas
        for i, (table_name, columns) in enumerate(self.structure.items()):
            self.update_progress(i, total_tables, f"Analizando tabla: {table_name}")
            
            if search_tables and keyword in table_name:
                found_tables.append(table_name)
            elif search_columns:
                # Buscar en columnas
                for column in columns:
                    if keyword in column['name']:
                        if table_name not in found_tables:
                            found_tables.append(table_name)
                        break
            
            # Pequeña pausa para mostrar el progreso
            if i % 100 == 0:
                time.sleep(0.01)
        
        # Mostrar resultados
        self.update_progress(total_tables, total_tables, 
                           f"Búsqueda completada. Encontradas {len(found_tables)} tablas.")
        
        for table_name in sorted(found_tables):
            self.tables_list.insert("", tk.END, values=(table_name,))
        
        # Rehabilitar botón
        self.search_button.configure(state='normal')
    
    def show_table_details(self, event):
        """Muestra los detalles de la tabla seleccionada"""
        selection = self.tables_list.selection()
        if not selection:
            return
        
        # Limpiar listas anteriores
        for item in self.fields_list.get_children():
            self.fields_list.delete(item)
            
        for item in self.data_list.get_children():
            self.data_list.delete(item)
        
        table_name = self.tables_list.item(selection[0])['values'][0]
        columns = self.structure.get(table_name, [])
        
        # Mostrar campos en la tabla de estructura
        for column in columns:
            # Determinar tipo de llave
            key_type = []
            if column['is_primary_key']:
                key_type.append("PK")
            if column['is_foreign_key']:
                key_type.append("FK")
            key_str = ", ".join(key_type) if key_type else ""
            
            # Formatear tipo de dato
            type_str = column['data_type']
            if column['max_length'] > 0:
                type_str += f"({column['max_length']})"
            
            # Formatear referencia
            ref_str = ""
            if column['is_foreign_key'] and column['referenced_table']:
                ref_str = f"{column['referenced_table']}.{column['referenced_column']}"
            
            # Insertar fila en la tabla
            self.fields_list.insert("", tk.END, values=(
                column['name'],
                type_str,
                "Sí" if column['is_nullable'] else "No",
                key_str,
                ref_str
            ))
        
        # Mostrar vista previa de datos
        try:
            if self.db.connect():
                # Configurar columnas en el TreeView de datos
                column_names = [col['name'] for col in columns]
                self.data_list['columns'] = column_names
                
                # Configurar encabezados y anchos
                for col in column_names:
                    self.data_list.heading(col, text=col)
                    self.data_list.column(col, width=200, minwidth=100)  # Ancho mínimo y predeterminado
                
                # Ejecutar consulta
                query = f"SELECT TOP 3 * FROM {table_name}"
                results = self.db.execute_query(query)
                
                if results:
                    for row in results:
                        # Convertir todos los valores a string para mostrar
                        values = [str(val) if val is not None else '' for val in row]
                        self.data_list.insert("", tk.END, values=values)
                
                self.db.close()
                self.status_var.set(f"Vista previa de {table_name} cargada")
            else:
                self.status_var.set("Error al conectar a la base de datos")
        except Exception as e:
            self.status_var.set(f"Error al cargar datos: {str(e)}")

def main():
    root = tk.Tk()
    app = TableStructureViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
