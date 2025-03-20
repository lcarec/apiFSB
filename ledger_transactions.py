import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime
from typing import List, Dict, Any
from db_connection import SQLServerConnection
import pandas as pd
from tkinter.filedialog import asksaveasfilename
from collections import defaultdict

class LedgerTransactionViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visor de Transacciones Contables")
        self.root.geometry("1400x800")
        
        # Inicializar conexión a la base de datos
        self.db = SQLServerConnection(
            "192.168.10.191",
            "consultor",
            "Consultor1",
            "DynamicsAx1_PRODUCTIVO"
        )
        
        # Variable para controlar la cancelación
        self.cancel_search = False
        
        # Variable para la empresa seleccionada
        self.selected_company = tk.StringVar(value="FSB")
        
        # Variable para comprobantes descuadrados
        self.unbalanced_only = tk.BooleanVar(value=False)
        
        # Variable para la búsqueda de cuentas
        self.account_search_var = tk.StringVar()
        self.account_search_var.trace('w', self.on_account_search_change)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame para filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="5")
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Frame para empresas
        company_frame = ttk.LabelFrame(filter_frame, text="Filtros principales", padding="5")
        company_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Botones de radio para empresas
        ttk.Radiobutton(company_frame, text="FSB", value="FSB",
                       variable=self.selected_company).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(company_frame, text="ASB", value="ASB",
                       variable=self.selected_company).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(company_frame, text="FES", value="FES",
                       variable=self.selected_company).grid(row=0, column=2, padx=10)
        
        # Checkbox para comprobantes descuadrados
        ttk.Checkbutton(company_frame, text="Solo comprobantes descuadrados",
                       variable=self.unbalanced_only).grid(row=0, column=3, padx=20)
        
        # Frame para filtros adicionales
        additional_filters_frame = ttk.Frame(filter_frame)
        additional_filters_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        # Búsqueda de cuenta
        ttk.Label(additional_filters_frame, text="Buscar cuenta:").grid(row=0, column=0, padx=5)
        self.account_entry = ttk.Entry(additional_filters_frame, textvariable=self.account_search_var, width=30)
        self.account_entry.grid(row=0, column=1, padx=5)
        
        # Lista de cuentas sugeridas
        self.account_listbox = tk.Listbox(additional_filters_frame, height=5, width=50)
        self.account_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        self.account_listbox.grid_remove()  # Inicialmente oculto
        
        # Vincular eventos de doble clic y Enter a la lista de cuentas
        self.account_listbox.bind('<Double-Button-1>', self.on_account_select)
        self.account_listbox.bind('<Return>', self.on_account_select)
        
        # Filtro de comprobante
        ttk.Label(additional_filters_frame, text="Comprobante:").grid(row=0, column=2, padx=5)
        self.voucher_var = tk.StringVar()
        self.voucher_entry = ttk.Entry(additional_filters_frame, textvariable=self.voucher_var, width=15)
        self.voucher_entry.grid(row=0, column=3, padx=5)
        
        # Selector de fechas
        date_frame = ttk.Frame(additional_filters_frame)
        date_frame.grid(row=0, column=4, columnspan=4, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(date_frame, text="Fecha inicial:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(date_frame, text="Fecha final:").grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(date_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5)
        
        # Frame para botones
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        # Botón de búsqueda
        self.search_button = ttk.Button(button_frame, text="Buscar",
                                      command=self.search_transactions)
        self.search_button.grid(row=0, column=0, padx=5)
        
        # Botón de cancelar
        self.cancel_button = ttk.Button(button_frame, text="Cancelar",
                                      command=self.cancel_search_process,
                                      state='disabled')
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Botón de exportar
        self.export_button = ttk.Button(button_frame, text="Exportar a Excel",
                                      command=self.export_to_excel)
        self.export_button.grid(row=0, column=2, padx=5)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(filter_frame, 
                                      variable=self.progress_var,
                                      maximum=100,
                                      mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=6, sticky=(tk.W, tk.E),
                          padx=5, pady=5)
        
        # Etiqueta de estado
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(filter_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=6)
        
        # Frame para resultados
        results_frame = ttk.LabelFrame(main_frame, text="Transacciones", padding="5")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # TreeView para mostrar los resultados
        columns = ("Fecha", "Comprobante", "Cuenta", "Nombre", "Glosa", "Debe", "Haber", "TipoMov")
        
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
        
        # Configurar columnas
        column_widths = {
            "Fecha": 100,
            "Comprobante": 120,
            "Cuenta": 120,
            "Nombre": 250,
            "Glosa": 300,
            "Debe": 120,
            "Haber": 120,
            "TipoMov": 80
        }
        
        column_alignments = {
            "Fecha": "center",
            "Comprobante": "w",
            "Cuenta": "w",
            "Nombre": "w",
            "Glosa": "w",
            "Debe": "e",
            "Haber": "e",
            "TipoMov": "center"
        }
        
        # Configurar nombres y propiedades de columnas
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ["Debe", "Haber"]:
                # Usar un espacio adicional para simular padding
                self.tree.column(col, width=column_widths[col], minwidth=50, anchor=column_alignments[col], stretch=False)
            else:
                self.tree.column(col, width=column_widths[col], minwidth=50, anchor=column_alignments[col])
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid de la tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
    def cancel_search_process(self):
        """Cancela el proceso de búsqueda"""
        self.cancel_search = True
        self.status_var.set("Cancelando búsqueda...")
        
    def on_account_search_change(self, *args):
        """Maneja los cambios en la búsqueda de cuentas"""
        search_text = self.account_search_var.get().strip()
        
        if len(search_text) < 2:
            self.account_listbox.grid_remove()
            return
        
        try:
            if not self.db.connect():
                return
            
            query = """
            SELECT DISTINCT TOP 10 ACCOUNTNUM, ACCOUNTNAME
            FROM LEDGERTABLE
            WHERE (ACCOUNTNUM LIKE ? OR ACCOUNTNAME LIKE ?)
                AND DATAAREAID = ?
            ORDER BY ACCOUNTNUM
            """
            
            search_pattern = f"%{search_text}%"
            results = self.db.execute_query(query, (search_pattern, search_pattern, self.selected_company.get()))
            
            self.account_listbox.delete(0, tk.END)
            
            if results:
                self.account_listbox.grid()  # Mostrar la lista
                for account_num, account_name in results:
                    self.account_listbox.insert(tk.END, f"{account_num} - {account_name}")
            else:
                self.account_listbox.grid_remove()
                
        except Exception as e:
            print(f"Error en la búsqueda de cuentas: {str(e)}")
        finally:
            self.db.close()

    def on_account_select(self, event):
        """Maneja la selección de una cuenta por doble clic o Enter"""
        selection = self.account_listbox.curselection()
        if selection:
            account = self.account_listbox.get(selection[0])
            self.account_search_var.set(account)
            self.account_listbox.grid_remove()
    
    def search_transactions(self):
        """Busca transacciones según las fechas seleccionadas"""
        try:
            # Limpiar mensaje de estado
            self.status_var.set("")
            
            # Reiniciar estado de cancelación
            self.cancel_search = False
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener fechas y filtros
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            selected_company = self.selected_company.get()
            voucher_filter = self.voucher_var.get().strip()
            account_filter = self.account_search_var.get().strip()
            
            # Validar fechas
            if start_date > end_date:
                messagebox.showerror("Error", "La fecha inicial no puede ser mayor que la fecha final")
                return
            
            # Asegurar que las fechas estén en el formato correcto para SQL Server
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            self.status_var.set("Buscando transacciones...")
            self.search_button.configure(state='disabled')
            self.cancel_button.configure(state='normal')
            self.progress_var.set(0)
            self.root.update_idletasks()
            
            # Ejecutar consulta
            if not self.db.connect():
                raise Exception("No se pudo conectar a la base de datos")
            
            # Si hay filtro de cuenta, primero obtenemos los comprobantes que la contienen
            vouchers_with_account = []
            if account_filter:
                account_num = account_filter.split(' - ')[0] if ' - ' in account_filter else account_filter
                account_query = """
                SELECT DISTINCT lt.VOUCHER
                FROM LEDGERTRANS lt
                LEFT JOIN LEDGERTABLE ltb ON lt.ACCOUNTNUM = ltb.ACCOUNTNUM
                    AND ltb.DATAAREAID = lt.DATAAREAID
                WHERE lt.DATAAREAID = ?
                AND CAST(lt.TRANSDATE AS DATE) >= CAST(? AS DATE)
                AND CAST(lt.TRANSDATE AS DATE) <= CAST(? AS DATE)
                AND (lt.ACCOUNTNUM LIKE ? OR ltb.ACCOUNTNAME LIKE ?)
                """
                account_params = [selected_company, start_date_str, end_date_str,
                                f"%{account_num}%", f"%{account_filter}%"]
                vouchers = self.db.execute_query(account_query, tuple(account_params))
                if vouchers:
                    vouchers_with_account = [v[0] for v in vouchers]
                else:
                    self.status_var.set("No se encontraron transacciones")
                    return
            
            # Construir la consulta base con subconsulta para detectar comprobantes descuadrados
            if self.unbalanced_only.get():
                query = """
                WITH VoucherTotals AS (
                    SELECT 
                        VOUCHER,
                        SUM(CASE WHEN CREDITING = 0 THEN ABS(ROUND(AMOUNTMST, 0)) ELSE 0 END) as TotalDebe,
                        SUM(CASE WHEN CREDITING = 1 THEN ABS(ROUND(AMOUNTMST, 0)) ELSE 0 END) as TotalHaber
                    FROM LEDGERTRANS
                    WHERE DATAAREAID = ?
                    AND CAST(TRANSDATE AS DATE) >= CAST(? AS DATE)
                    AND CAST(TRANSDATE AS DATE) <= CAST(? AS DATE)
                    GROUP BY VOUCHER
                    HAVING SUM(CASE WHEN CREDITING = 0 THEN ABS(ROUND(AMOUNTMST, 0)) ELSE 0 END) <>
                           SUM(CASE WHEN CREDITING = 1 THEN ABS(ROUND(AMOUNTMST, 0)) ELSE 0 END)
                )
                """
            else:
                query = ""
            
            query += """
            SELECT 
                lt.TRANSDATE as Fecha,
                lt.VOUCHER as Comprobante,
                lt.ACCOUNTNUM as Cuenta,
                ltb.ACCOUNTNAME as Nombre,
                lt.TXT as Glosa,
                CAST(CASE WHEN lt.CREDITING = 0 THEN ABS(ROUND(lt.AMOUNTMST, 0)) ELSE 0 END AS BIGINT) as Debe,
                CAST(CASE WHEN lt.CREDITING = 1 THEN ABS(ROUND(lt.AMOUNTMST, 0)) ELSE 0 END AS BIGINT) as Haber,
                lt.PERIODCODE as TipoMov
            FROM LEDGERTRANS lt
            LEFT JOIN LEDGERTABLE ltb ON lt.ACCOUNTNUM = ltb.ACCOUNTNUM
                AND ltb.DATAAREAID = lt.DATAAREAID
            """
            
            if self.unbalanced_only.get():
                query += " INNER JOIN VoucherTotals vt ON lt.VOUCHER = vt.VOUCHER"
            
            query += """
            WHERE CAST(lt.TRANSDATE AS DATE) >= CAST(? AS DATE) 
            AND CAST(lt.TRANSDATE AS DATE) <= CAST(? AS DATE)
            AND lt.DATAAREAID = ?
            AND lt.PERIODCODE IN (0, 1)
            """
            
            # Parámetros base
            params = []
            if self.unbalanced_only.get():
                params.extend([selected_company, start_date_str, end_date_str])
            params.extend([start_date_str, end_date_str, selected_company])
            
            # Agregar filtros adicionales
            if voucher_filter:
                query += " AND lt.VOUCHER LIKE ?"
                params.append(f"%{voucher_filter}%")
            elif vouchers_with_account:  # Si estamos filtrando por cuenta
                placeholders = ','.join(['?' for _ in vouchers_with_account])
                query += f" AND lt.VOUCHER IN ({placeholders})"
                params.extend(vouchers_with_account)
            
            # Ordenar primero por comprobante para mantener las transacciones agrupadas
            query += " ORDER BY lt.VOUCHER, lt.TRANSDATE"
            
            results = self.db.execute_query(query, tuple(params))
            
            if not results:
                self.status_var.set("No se encontraron transacciones")
                return
            
            # Diccionario para almacenar totales por comprobante
            totals_by_voucher = defaultdict(lambda: {'debe': 0, 'haber': 0})
            
            # Insertar resultados
            total_rows = len(results)
            current_voucher = None
            voucher_rows = []
            
            for i, row in enumerate(results):
                # Verificar si se canceló la búsqueda
                if self.cancel_search:
                    self.status_var.set("Búsqueda cancelada")
                    break
                
                # Convertir fechas a string y formatear números
                row_data = list(row)
                for j, value in enumerate(row_data):
                    if isinstance(value, datetime):
                        row_data[j] = value.strftime('%d-%m-%Y')
                    elif isinstance(value, (int, float)) and j in [5, 6]:  # Columnas Debe y Haber
                        row_data[j] = "{:,}".format(abs(int(value))) if value != 0 else "0"
                    elif j == 7:  # Columna TipoMov
                        row_data[j] = "Apertura" if value == 0 else "Normal"
                    elif value is None:
                        row_data[j] = '0' if j in [5, 6] else ''
                
                voucher = row_data[1]  # Índice del comprobante
                
                # Si cambia el comprobante, insertar las filas acumuladas y el total
                if current_voucher is not None and current_voucher != voucher:
                    # Insertar todas las filas del comprobante anterior
                    for saved_row in voucher_rows:
                        self.tree.insert("", tk.END, values=saved_row)
                    
                    # Insertar el total del comprobante anterior
                    self.insert_voucher_total(current_voucher, totals_by_voucher[current_voucher])
                    
                    # Limpiar las filas acumuladas
                    voucher_rows = []
                    
                # Actualizar totales del comprobante actual
                debe = int(str(row_data[5]).replace(',', '')) if row_data[5] else 0
                haber = int(str(row_data[6]).replace(',', '')) if row_data[6] else 0
                totals_by_voucher[voucher]['debe'] += debe
                totals_by_voucher[voucher]['haber'] += haber
                
                # Guardar la fila para insertarla después
                voucher_rows.append(row_data)
                current_voucher = voucher
                
                # Actualizar progreso
                progress = ((i + 1) / total_rows) * 100
                self.progress_var.set(progress)
                if i % 100 == 0:
                    self.root.update_idletasks()
            
            # Insertar las últimas filas y el total del último comprobante
            if voucher_rows:
                for row in voucher_rows:
                    self.tree.insert("", tk.END, values=row)
                self.insert_voucher_total(current_voucher, totals_by_voucher[current_voucher])
            
            if not self.cancel_search:
                self.status_var.set(f"Se encontraron {total_rows} transacciones")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar transacciones: {str(e)}")
            self.status_var.set("Error en la búsqueda")
        
        finally:
            self.search_button.configure(state='normal')
            self.cancel_button.configure(state='disabled')
            self.db.close()
    
    def insert_voucher_total(self, voucher, totals):
        """Inserta una fila de total para un comprobante"""
        total_row = [
            "",  # Fecha
            f"Total {voucher}",  # Comprobante
            "",  # Cuenta
            "",  # Nombre
            "TOTAL COMPROBANTE",  # Glosa
            "{:,}".format(totals['debe']),  # Debe
            "{:,}".format(totals['haber']),  # Haber
            ""  # TipoMov
        ]
        item_id = self.tree.insert("", tk.END, values=total_row, tags=('total',))
        self.tree.tag_configure('total', background='#f0f0f0', font=('Arial', 9, 'bold'))
    
    def export_to_excel(self):
        """Exporta los resultados a un archivo Excel"""
        try:
            if not self.tree.get_children():
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            filename = asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Guardar como..."
            )
            
            if not filename:
                return
            
            # Obtener datos del TreeView
            data = []
            columns = self.tree["columns"]
            
            for item in self.tree.get_children():
                values = self.tree.item(item)["values"]
                # Convertir los valores de texto a números para las columnas Debe y Haber
                row_data = list(values)
                for i, value in enumerate(row_data):
                    if i in [5, 6]:  # Columnas Debe y Haber
                        # Remover las comas y convertir a entero, usar 0 si está vacío
                        row_data[i] = int(str(value).replace(",", "")) if value and value != "0" else 0
                data.append(row_data)
            
            # Crear DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Guardar a Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                
                # Obtener la hoja de trabajo
                worksheet = writer.sheets['Sheet1']
                
                # Formato de números para las columnas Debe y Haber
                for col in ['F', 'G']:  # Columnas F y G son Debe y Haber
                    for row in range(2, len(data) + 2):  # Empezar desde la fila 2 (después del encabezado)
                        cell = worksheet[f"{col}{row}"]
                        cell.number_format = '#,##0'
            
            messagebox.showinfo("Éxito", "Datos exportados correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

def main():
    root = tk.Tk()
    app = LedgerTransactionViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
