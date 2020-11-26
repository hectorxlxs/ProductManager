from tkinter import *
from tkinter import ttk
import sqlite3

maindb_dir = "databases/database.db"


class UI:
    def __init__(self, window):

        self.window = window

        # CONFIGURACIÓN DE VENTANA
        self.window.title("Gestión Productos")
        self.window.resizable(1, 1)
        self.window.wm_iconbitmap("resources/icon.ico")

        # CONFIGURACIÓN DEL FRAME
        self.frame = LabelFrame(window, text="Registrar nuevo producto")
        self.frame.grid(row=0, column=0, columnspan=3, sticky="ns", pady=(10, 0))

        # ENTRADA DE TEXTO NOMBRE DE PRODUCTO
        self.name_label = Label(self.frame, text="Nombre")
        self.name_label.grid(row=1, column=0)

        self.entry_name = Entry(self.frame)
        self.entry_name.focus()
        self.entry_name.grid(row=1, column=1)

        # ENTRADA DE TEXTO PARA PRECIO
        self.price_label = Label(self.frame, text="Precio")
        self.price_label.grid(row=2, column=0)

        self.entry_price = Entry(self.frame)
        self.entry_price.grid(row=2, column=1)

        # BOTÓN PARA AÑADIR PRODUCTO
        self.add_button = ttk.Button(self.frame, text="Añadir producto", command=self.add_product)
        self.add_button.grid(row=3, columnspan=2, sticky=E+W)

        # MENSAJE DE ERROR
        self.error_msg = Label(window, text='', fg='red')
        self.error_msg.grid(row=4, column=0, columnspan=2)

        # TABLA PARA VISUALIZACIÓN DE PRODUCTOS
        style = ttk.Style()
        style.configure("mystyle.Treeview", font=("Calibri", 11))
        style.configure("mystyle.Treeview.Heading", font=("Calibri", 13, "bold"))

        self.table = ttk.Treeview(height=20, columns=("name", "price"), style="mystyle.Treeview")
        self.table.grid(row=5, column=0, columnspan=2, sticky=E+W+N+S)

        # PARA QUE NO SE VEA LA PRIMERA COLUMNA QUE PONE AAUTOMATICAMENTE TKINTER PARA LOS ID'S
        self.table["show"] = "headings"

        self.table.column("name", anchor="center")
        self.table.heading("name", text="Nombre")

        self.table.column("price", anchor="center")
        self.table.heading("price", text="Precio")

        self.delete_button = ttk.Button(window, text="ELIMINAR", command=self.delete_product)
        self.delete_button.grid(row=6, column=0, sticky=E+W)

        self.edit_button = ttk.Button(window, text="EDITAR", command=self.edit_product)
        self.edit_button.grid(row=6, column=1, sticky=E+W)

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(5, weight=1)

        self.fill_table()

    def clear_table(self):
        for child in self.table.get_children():
            self.table.delete(child)

    def fill_table(self):
        self.table.delete()
        registros = get_productos()
        for row in registros:
            self.table.insert('', 0, text=row[0], values=(row[1], row[2]))

    def add_product(self):

        name = self.entry_name.get()
        price = self.entry_price.get()

        self.error_msg["text"] = valid_product_error(name, price, True)

        if self.error_msg["text"] == "":

            self.entry_name.delete(0, END)
            self.entry_price.delete(0, END)

            query = "INSERT INTO productos VALUES(NULL, ?, ?)"
            params = (name, price)
            db_execute(query, params)

            # hago esto para coger el id del elemento introducido ya que no he encontrado una forma mejor
            query = "SELECT * FROM productos WHERE nombre=?"
            params = (name,)
            resultado = db_execute(query, params).fetchall()

            self.table.insert('', 0, text=resultado[0][0], values=(resultado[0][1], resultado[0][2]))

    def delete_product(self):

        for tkinter_item_id in self.table.selection():

            item = self.table.item(tkinter_item_id)

            query = "DELETE FROM productos WHERE id=?"
            params = (item["text"],)
            db_execute(query, params)

            self.table.delete(tkinter_item_id)

    def edit_product(self):

        tkinter_item_id_list = self.table.selection()

        if len(tkinter_item_id_list) == 1:

            item = self.table.item(tkinter_item_id_list[0])
            item_id = item["text"]
            item_name = item["values"][0]
            item_price = item["values"][1]

            edit_window = EditWindow(self.table, tkinter_item_id_list[0], item_id, item_name, item_price)
            

def get_productos():
    consulta="SELECT * FROM productos ORDER BY nombre DESC"
    return db_execute(consulta)


def db_execute(consulta, parametros=()):
    with sqlite3.connect(maindb_dir) as conexion:
        cursor = conexion.cursor()
        resultado = cursor.execute(consulta, parametros)
        conexion.commit()
    return resultado


# devuelve null si los datos pasados son válidos, sino, devuelve el mensaje de error correspondiente
def valid_product_error(name, price, check_duplicates):

    try:
        name = str(name)
        price = float(price)

        if len(name) == 0:
            return "El nombre es obligatorio"

        if price <= 0:
            return "El precio debe ser mayor que 0"

        if(check_duplicates):
            # Lo busco en la base de datos para ver si ya existe otro producto cno el mismo nombre
            query = "SELECT * FROM productos WHERE nombre=?"
            params = (name,)
            resultado = db_execute(query, params).fetchall()

            if len(resultado) > 0:
                return "El producto introducido ya existe"

        return ""

    except ValueError:
        return "Error de formato en precio"


class EditWindow(Toplevel):

    def __init__(self, table, tkinter_item_id, id, name, price):

        Toplevel.__init__(self)

        self.table = table
        self.tkinter_item_id = tkinter_item_id
        self.id = id
        self.name = name
        self.price = price

        # CONFIGURACIÓN DE VENTANA
        self.title("Editar Producto")
        self.resizable(1, 1)
        self.wm_iconbitmap("resources/icon.ico")

        # CREACIÓN DEL FRAME
        self.frame = Frame(self)
        self.frame.grid(row=0, column=0, columnspan=3, sticky=E+W+N+S, padx=15, pady=(10, 0))

        # INDICADOR DE TEXTO NOMBRE ANTERIOR
        Label(self.frame, text="Nombre anterior:").grid(row=1, column=1, sticky=W)
        Label(self.frame, text=self.name).grid(row=1, column=2, sticky=W+E)

        # MODIFICADOR DE PRECIO
        Label(self.frame, text="Nuevo Nombre:").grid(row=2, column=1, sticky=W)

        self.name_entry = Entry(self.frame)
        self.name_entry.grid(row=2, column=2, sticky=W+E)

        # INDICADOR DE TEXTO PARA PRECIO ANTERIOR
        Label(self.frame, text="Precio anterior").grid(row=3, column=1, sticky=W)
        Label(self.frame, text=str(self.price)).grid(row=3, column=2, sticky=W+E)

        # MODIFICADOR DE PRECIO
        Label(self.frame, text="Nuevo Precio").grid(row=4, column=1, sticky=W)

        self.price_entry = Entry(self.frame)
        self.price_entry.grid(row=4, column=2, sticky=W+E)

        # BOTÓN PARA GUARDAR CAMBIOS
        ttk.Button(self.frame, text="Guardar cambios", command=self.mod_product).\
            grid(column=0, row=5, columnspan=3, sticky=E + W, pady=(5, 0))

        # MENSAJE DE ERROR
        self.error_msg = Label(self, text='', fg='red')
        self.error_msg.grid(column=0, row=6, columnspan=3)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def mod_product(self):

        name = self.name_entry.get()
        if len(name) == 0:
            name = self.name

        price = self.price_entry.get()
        if len(price) == 0:
            price = self.price

        self.error_msg["text"] = valid_product_error(name, price, False)

        if self.error_msg["text"] == "":

            query = "UPDATE productos SET nombre=?, precio=? WHERE nombre=? AND precio=?"
            params = (name, float(price), self.name, self.price)

            # MODIFICA LA INFORMACIÓN DEL TREEVIEW
            self.table.item(self.tkinter_item_id, values=(name, float(price)))

            db_execute(query, params)

            self.destroy()


if __name__ == '__main__':

    root = Tk()
    ui = UI(root)

    root.mainloop()

