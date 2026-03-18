import tkinter as tk
from tkinter import messagebox, filedialog
import os

# Palabras clave y tokens del lenguaje
PALABRAS_RESERVADAS = {
    "si", "tons", "tonses", "mientras", "para", "roto", "reanuda", "mentira", "verdad",
    "nada", "y", "o", "nel", "definir", "regresar", "pasar", "clase", "de", "importar"
}
TIPOS_DATO = {"entero", "flota", "siono", "tecto"}
FUNCIONES_INTEGRADAS = {"afuera", "adentro", "read", "get", "count", "def"}
SIMBOLOS = {"=", "(", ")", "{", "}", '"', ";", ","}
OPERADORES = {"suma", "resta", "multi", "divi", "%", "<", ">", "==", "!="}

# Colores y estilos de la interfaz
COLOR_FONDO = "black"
COLOR_BOTONES = "navajoWhite"
COLOR_BOTON_GUARDAR = "orange"
COLOR_BOTON_COMPILAR = "light green"
COLOR_TERMINAL_BG = "black"
COLOR_TERMINAL_FG = "light green"
FONT_EDITOR = ("Consolas", 11)
FONT_TERMINAL = ("Consolas", 10)



# LÓGICA DEL COMPILADOR

class CompiladorLogic:
    
    @staticmethod
    def compilar_y_ejecutar(ruta_archivo_fuente):
        """
        Simula el flujo de compilación: 
        1. Leer archivo
        2. Análisis léxico
        """
        with open(ruta_archivo_fuente, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()
            
        tokens = CompiladorLogic.analisis_lexico(codigo_fuente)
        return tokens

    @staticmethod
    def analisis_lexico(codigo):
        """Analiza el código y retorna una lista de tokens."""
        tokens = []
        palabra = ""
        linea = 1

        # Iterar carácter por carácter
        for i, c in enumerate(codigo):
            if c == ".":
                linea += 1
                
            if c.isalnum() or c == "_":
                palabra += c
            else:
                if palabra:
                    CompiladorLogic._procesar_palabra(palabra, linea, tokens)
                    palabra = ""

                if c in SIMBOLOS:
                    tokens.append(("SIMBOLO", c, linea))
                elif c in OPERADORES:
                    tokens.append(("OPERADOR", c, linea))
                # Ignoramos espacios en blanco, tabs, etc.

        # Procesar la última palabra si existe
        if palabra:
             CompiladorLogic._procesar_palabra(palabra, linea, tokens)

        return tokens

    @staticmethod
    def _procesar_palabra(palabra, linea, tokens):

        if palabra in PALABRAS_RESERVADAS:
            tokens.append(("PALABRA_RESERVADA", palabra, linea))
        elif palabra in TIPOS_DATO:
            tokens.append(("TIPO_DATO", palabra, linea))
        elif palabra in FUNCIONES_INTEGRADAS:
            tokens.append(("FUNCION_INTEGRADA", palabra, linea))
        elif palabra.isdigit():
            tokens.append(("NUMERO", palabra, linea))
        else:
            tokens.append(("IDENTIFICADOR", palabra, linea))


# INTERFAZ GRÁFICA

class CompiladorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._configurar_ventana()
        self._inicializar_variables()
        self._crear_interfaz()

    def _configurar_ventana(self):
        self.title("Compilador: Cuchurrumin FC")
        self.state("zoomed")
        self.minsize(900, 500)
        self.configure(bg=COLOR_FONDO)

    def _inicializar_variables(self):
        self.archivo_actual = "Ninguno"
        self.ruta_actual = None

    def _crear_interfaz(self):
        # Barra superior
        self._crear_barra_herramientas()
        
        # Contenedor principal (Split View)
        self.contenedor = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6)
        self.contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        # Paneles
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()

    def _crear_barra_herramientas(self):
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", pady=5)

        self._crear_boton(barra, "📂 Abrir", COLOR_BOTONES, self.abrir_archivo)
        self._crear_boton(barra, "💾 Guardar", COLOR_BOTON_GUARDAR, self.guardar_archivo)
        self._crear_boton(barra, "⚙ Compilar", COLOR_BOTON_COMPILAR, self.compilar)

    def _crear_boton(self, padre, texto, color, comando):
        btn = tk.Button(padre, text=texto, bg=color, fg="black", width=12, command=comando)
        btn.pack(side="left", padx=5)

    def _crear_panel_izquierdo(self):
        self.panel_izquierdo = tk.Frame(self.contenedor, bg="#2b2b2b", width=200)
        self.contenedor.add(self.panel_izquierdo, minsize=180)

        # Titulo
        tk.Label(self.panel_izquierdo, text="📁 Archivo abierto",
                bg="black", fg="white",
                font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # Etiqueta de archivo
        self.lbl_archivo = tk.Label(self.panel_izquierdo,
                                    text=self.archivo_actual,
                                    bg="black", fg="cyan",
                                    wraplength=160, justify="left")
        self.lbl_archivo.pack(anchor="w", padx=10)

        # Boton cerrar
        tk.Button(self.panel_izquierdo, text="❌ Cerrar archivo",
                bg="gray", fg="white",
                command=self.cerrar_archivo).pack(anchor="w", padx=10, pady=10)

    def _crear_panel_derecho(self):
        self.panel_derecho = tk.PanedWindow(self.contenedor, orient=tk.VERTICAL, sashwidth=6)
        self.contenedor.add(self.panel_derecho)

        # Editor de Código
        frame_editor = tk.Frame(self.panel_derecho)
        self.panel_derecho.add(frame_editor, minsize=300)
        
        scrollbar_editor = tk.Scrollbar(frame_editor)
        scrollbar_editor.pack(side="right", fill="y")
        
        self.text_area = tk.Text(frame_editor, wrap="word", font=FONT_EDITOR,
                                yscrollcommand=scrollbar_editor.set)
        self.text_area.pack(expand=True, fill="both")
        scrollbar_editor.config(command=self.text_area.yview)

        # Terminal de Salida
        frame_terminal = tk.Frame(self.panel_derecho)
        self.panel_derecho.add(frame_terminal, minsize=150)
        
        scrollbar_terminal = tk.Scrollbar(frame_terminal)
        scrollbar_terminal.pack(side="right", fill="y")
        
        self.terminal = tk.Text(frame_terminal, wrap="word", font=FONT_TERMINAL,
                                bg=COLOR_TERMINAL_BG, fg=COLOR_TERMINAL_FG,
                                yscrollcommand=scrollbar_terminal.set)
        self.terminal.pack(expand=True, fill="both")
        scrollbar_terminal.config(command=self.terminal.yview)


    def escribir_terminal(self, mensaje):
        self.terminal.insert(tk.END, mensaje + "\n")
        self.terminal.see(tk.END)

    def cerrar_archivo(self):
        self.text_area.delete("1.0", tk.END)
        self.terminal.delete("1.0", tk.END)
        self.archivo_actual = "Ninguno"
        self.ruta_actual = None
        self.lbl_archivo.config(text=self.archivo_actual)
        self.escribir_terminal("Archivo cerrado.")

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Text Document", ".chu"), ("Todos", "*.*")]
        )

        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read()
                
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, contenido)
                self.ruta_actual = ruta
                self.archivo_actual = os.path.basename(ruta)
                self.lbl_archivo.config(text=self.archivo_actual)
                self.escribir_terminal(f"Archivo abierto: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar_archivo(self):
        if self.ruta_actual:
            ruta = self.ruta_actual
        else:
            ruta = filedialog.asksaveasfilename(
                title="Guardar archivo",
                defaultextension=".chu",
                filetypes=[("Archivos CHU", "*.chu")]
            )

        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as archivo:
                    archivo.write(self.text_area.get("1.0", tk.END))
                
                self.ruta_actual = ruta
                self.archivo_actual = os.path.basename(ruta)
                self.lbl_archivo.config(text=self.archivo_actual)
                self.escribir_terminal(f"Archivo guardado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def compilar(self):
        self.terminal.delete("1.0", tk.END)
        
        # Guardar antes de compila
        if not self.ruta_actual:
            respuesta = messagebox.askyesno("Guardar", "Para compilar, primero debes guardar el archivo. ¿Deseas guardarlo ahora?")
            if respuesta:
                self.guardar_archivo()
            else:
                self.escribir_terminal("⚠ Compilación cancelada: El archivo debe guardarse primero.")
                return

        # Si aún después de intentar guardar no hay ruta (usuario canceló en el diálogo de archivo), salimos
        if not self.ruta_actual:
            return

        # SE ASegura que contenido en disco sea el mismo que en el editor
        try:
             with open(self.ruta_actual, "w", encoding="utf-8") as archivo:
                    archivo.write(self.text_area.get("1.0", tk.END))
        except Exception as e:
             self.escribir_terminal(f"⚠ Advertencia: No se pudo auto-guardar cambios recientes: {e}")


        # 1. Llamada a la función solicitada
        self.escribir_terminal(f"🔵 Compilando {self.archivo_actual}...")
        
        try:
            tokens = CompiladorLogic.compilar_y_ejecutar(self.ruta_actual)

            for tipo, valor, linea in tokens:
                self.escribir_terminal(f"   [{tipo}] -> '{valor}' (ln {linea})")
            
            self.escribir_terminal(f"✔ Léxico finalizado. {len(tokens)} tokens encontrados.\n")

        except Exception as e:
            self.escribir_terminal(f"❌ Error durante la compilación: {e}")


if __name__ == "__main__":
    app = CompiladorApp()
    app.mainloop()
