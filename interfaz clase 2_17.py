import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import ctypes

# --- Habilitar DPI Awareness para mejor resolución en Windows ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

# Palabras clave y tokens del lenguaje
PALABRAS_RESERVADAS = {
    "si", "tons", "tonses", "mientras", "para", "roto", "reanuda", "mentira", "verdad",
    "nada", "y", "o", "nel", "definir", "regresar", "pasar", "clase", "de", "importar"
}
TIPOS_DATO = {"entero", "flota", "siono", "tecto"}
FUNCIONES_INTEGRADAS = {"afuera", "adentro", "read", "get", "count", "def"}

# Separar operadores por tipo para un análisis correcto
OPERADORES_PALABRA = {"suma", "resta", "multi", "divi"}
OPERADORES_SIMBOLO = {"%", "<", ">"}
OPERADORES_DOBLES = {"==", "!="}
SIMBOLOS = {"=", "(", ")", "{", "}", '"', ";", ",", "!"}
OPERADORES = OPERADORES_PALABRA | OPERADORES_SIMBOLO | OPERADORES_DOBLES

# Colores y estilos de la interfaz (paleta profesional)
COLOR_FONDO = "#1a1a2e"
COLOR_FONDO_PANEL = "#16213e"
COLOR_FONDO_EDITOR = "#0f0f1a"
COLOR_TEXTO_EDITOR = "#e0e0e0"
COLOR_TERMINAL_BG = "#0a0a14"
COLOR_TERMINAL_FG = "#00ff88"
COLOR_ACENTO = "#00d4aa"
COLOR_ACENTO_HOVER = "#00f0c0"
COLOR_NARANJA = "#ff8c42"
COLOR_NARANJA_HOVER = "#ffa566"
COLOR_VERDE = "#00e676"
COLOR_VERDE_HOVER = "#66ffa6"
COLOR_TEXTO_CLARO = "#c8d6e5"
COLOR_TEXTO_DIM = "#636e72"
COLOR_BORDE = "#2d3436"
COLOR_LINEAS = "#1e2a3a"
COLOR_NUM_LINEA_FG = "#4a6785"
FONT_EDITOR = ("Cascadia Code", 11)
FONT_TERMINAL = ("Cascadia Code", 10)
FONT_TITULO = ("Segoe UI", 11, "bold")
FONT_BOTON = ("Segoe UI", 10, "bold")
FONT_NUMLINEA = ("Cascadia Code", 11)


# ═══════════════════════════════════════════════════════════════
# LÓGICA DEL COMPILADOR
# ═══════════════════════════════════════════════════════════════

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
        i = 0

        while i < len(codigo):
            c = codigo[i]

            # FIX Error 1: Contar saltos de línea, no puntos
            if c == "\n":
                linea += 1

            if c.isalnum() or c == "_":
                palabra += c
            elif c == '"':
                # FIX Error 5: Manejar cadenas de texto
                if palabra:
                    CompiladorLogic._procesar_palabra(palabra, linea, tokens)
                    palabra = ""
                cadena = ""
                i += 1
                while i < len(codigo) and codigo[i] != '"':
                    if codigo[i] == "\n":
                        linea += 1
                    cadena += codigo[i]
                    i += 1
                tokens.append(("CADENA", f'"{cadena}"', linea))
                # i se incrementa al final del while
            elif c == '.' and i + 1 < len(codigo) and codigo[i + 1].isdigit() and palabra.isdigit():
                # FIX Error 6: Manejar números decimales
                palabra += c
            else:
                if palabra:
                    CompiladorLogic._procesar_palabra(palabra, linea, tokens)
                    palabra = ""

                # FIX Error 3: Verificar operadores de dos caracteres
                if i + 1 < len(codigo):
                    doble = c + codigo[i + 1]
                    if doble in OPERADORES_DOBLES:
                        tokens.append(("OPERADOR", doble, linea))
                        i += 2
                        continue

                if c in OPERADORES_SIMBOLO:
                    tokens.append(("OPERADOR", c, linea))
                elif c in SIMBOLOS:
                    tokens.append(("SIMBOLO", c, linea))
                # Ignoramos espacios en blanco, tabs, etc.

            i += 1

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
        # FIX Error 2: Detectar operadores de palabra
        elif palabra in OPERADORES_PALABRA:
            tokens.append(("OPERADOR", palabra, linea))
        elif palabra.replace('.', '', 1).isdigit():
            # Soporta enteros y decimales
            tokens.append(("NUMERO", palabra, linea))
        else:
            tokens.append(("IDENTIFICADOR", palabra, linea))


# ═══════════════════════════════════════════════════════════════
# WIDGET: Números de línea para el editor
# ═══════════════════════════════════════════════════════════════

class NumeroLinea(tk.Canvas):
    """Canvas que muestra los números de línea junto al editor."""

    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind("<<Modified>>", self._on_modify)
        self.text_widget.bind("<Configure>", self._on_modify)
        self.text_widget.bind("<KeyRelease>", self._on_modify)
        self.text_widget.bind("<MouseWheel>", self._on_scroll)

    def _on_scroll(self, event=None):
        self.after(5, self.actualizar)

    def _on_modify(self, event=None):
        self.after_idle(self.actualizar)

    def actualizar(self):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            num = str(i).split(".")[0]
            self.create_text(
                self.winfo_width() - 8, y,
                anchor="ne", text=num,
                fill=COLOR_NUM_LINEA_FG,
                font=FONT_NUMLINEA
            )
            i = self.text_widget.index(f"{i}+1line")
            if int(i.split(".")[0]) > int(self.text_widget.index("end").split(".")[0]):
                break


# ═══════════════════════════════════════════════════════════════
# INTERFAZ GRÁFICA
# ═══════════════════════════════════════════════════════════════

class CompiladorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self._configurar_ventana()
        self._inicializar_variables()
        self._configurar_estilos()
        self._crear_interfaz()

    def _configurar_ventana(self):
        self.title("⚡ Compilador: Cuchurrumin FC")
        self.state("zoomed")
        self.minsize(1000, 600)
        self.configure(bg=COLOR_FONDO)

    def _inicializar_variables(self):
        self.archivo_actual = "Ninguno"
        self.ruta_actual = None

    def _configurar_estilos(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Estilo general
        self.style.configure(".", background=COLOR_FONDO, foreground=COLOR_TEXTO_CLARO)
        self.style.configure("TFrame", background=COLOR_FONDO)
        self.style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO_CLARO)
        self.style.configure("TPanedwindow", background=COLOR_FONDO)

        # Botones personalizados
        self.style.configure("Abrir.TButton",
                             font=FONT_BOTON, padding=(14, 8),
                             background=COLOR_ACENTO, foreground="#000")
        self.style.map("Abrir.TButton",
                       background=[("active", COLOR_ACENTO_HOVER)])

        self.style.configure("Guardar.TButton",
                             font=FONT_BOTON, padding=(14, 8),
                             background=COLOR_NARANJA, foreground="#000")
        self.style.map("Guardar.TButton",
                       background=[("active", COLOR_NARANJA_HOVER)])

        self.style.configure("Compilar.TButton",
                             font=FONT_BOTON, padding=(14, 8),
                             background=COLOR_VERDE, foreground="#000")
        self.style.map("Compilar.TButton",
                       background=[("active", COLOR_VERDE_HOVER)])

        self.style.configure("Cerrar.TButton",
                             font=("Segoe UI", 9), padding=(10, 6),
                             background="#e74c3c", foreground="white")
        self.style.map("Cerrar.TButton",
                       background=[("active", "#ff6b6b")])

    def _crear_interfaz(self):
        # Barra superior
        self._crear_barra_herramientas()

        # Contenedor principal (Split View)
        self.contenedor = tk.PanedWindow(
            self, orient=tk.HORIZONTAL, sashwidth=4,
            bg=COLOR_BORDE, sashrelief="flat"
        )
        self.contenedor.pack(expand=True, fill="both", padx=12, pady=(0, 12))

        # Paneles
        self._crear_panel_izquierdo()
        self._crear_panel_derecho()

    def _crear_barra_herramientas(self):
        barra = tk.Frame(self, bg=COLOR_FONDO, pady=8)
        barra.pack(fill="x", padx=12)

        # Logo / Título
        titulo = tk.Label(
            barra, text="⚡ Cuchurrumin FC",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_FONDO, fg=COLOR_ACENTO
        )
        titulo.pack(side="left", padx=(5, 20))

        # Separador visual
        sep = tk.Frame(barra, bg=COLOR_BORDE, width=2, height=30)
        sep.pack(side="left", padx=10, fill="y")

        # Botones
        btn_abrir = ttk.Button(barra, text="📂 Abrir", style="Abrir.TButton", command=self.abrir_archivo)
        btn_abrir.pack(side="left", padx=5)

        btn_guardar = ttk.Button(barra, text="💾 Guardar", style="Guardar.TButton", command=self.guardar_archivo)
        btn_guardar.pack(side="left", padx=5)

        btn_compilar = ttk.Button(barra, text="⚙ Compilar", style="Compilar.TButton", command=self.compilar)
        btn_compilar.pack(side="left", padx=5)

    def _crear_panel_izquierdo(self):
        self.panel_izquierdo = tk.Frame(
            self.contenedor, bg=COLOR_FONDO_PANEL,
            width=220, highlightthickness=1,
            highlightbackground=COLOR_BORDE
        )
        self.contenedor.add(self.panel_izquierdo, minsize=200)

        # Título del panel
        header = tk.Frame(self.panel_izquierdo, bg=COLOR_FONDO_PANEL)
        header.pack(fill="x", padx=12, pady=(14, 0))

        tk.Label(
            header, text="📁 EXPLORADOR",
            bg=COLOR_FONDO_PANEL, fg=COLOR_ACENTO,
            font=FONT_TITULO
        ).pack(anchor="w")

        # Línea decorativa
        linea_dec = tk.Frame(self.panel_izquierdo, bg=COLOR_ACENTO, height=2)
        linea_dec.pack(fill="x", padx=12, pady=(6, 12))

        # Etiqueta "Archivo abierto"
        tk.Label(
            self.panel_izquierdo, text="Archivo abierto:",
            bg=COLOR_FONDO_PANEL, fg=COLOR_TEXTO_DIM,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=14)

        # Nombre del archivo
        self.lbl_archivo = tk.Label(
            self.panel_izquierdo,
            text=self.archivo_actual,
            bg=COLOR_FONDO_PANEL, fg="#00d4ff",
            wraplength=180, justify="left",
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_archivo.pack(anchor="w", padx=14, pady=(2, 0))

        # Botón cerrar
        btn_frame = tk.Frame(self.panel_izquierdo, bg=COLOR_FONDO_PANEL)
        btn_frame.pack(anchor="w", padx=12, pady=14)

        ttk.Button(
            btn_frame, text="❌ Cerrar archivo",
            style="Cerrar.TButton",
            command=self.cerrar_archivo
        ).pack()

    def _crear_panel_derecho(self):
        self.panel_derecho = tk.PanedWindow(
            self.contenedor, orient=tk.VERTICAL,
            sashwidth=4, bg=COLOR_BORDE, sashrelief="flat"
        )
        self.contenedor.add(self.panel_derecho)

        # ── Editor de Código ──
        frame_editor_wrapper = tk.Frame(self.panel_derecho, bg=COLOR_FONDO_EDITOR)
        self.panel_derecho.add(frame_editor_wrapper, minsize=300)

        # Etiqueta del editor
        editor_header = tk.Frame(frame_editor_wrapper, bg="#111125")
        editor_header.pack(fill="x")
        tk.Label(
            editor_header, text="  📝 EDITOR DE CÓDIGO",
            bg="#111125", fg=COLOR_TEXTO_DIM,
            font=("Segoe UI", 9, "bold"), pady=5
        ).pack(anchor="w")

        # Contenedor del editor con números de línea
        frame_editor = tk.Frame(frame_editor_wrapper, bg=COLOR_FONDO_EDITOR)
        frame_editor.pack(expand=True, fill="both")

        # Text area
        scrollbar_editor = tk.Scrollbar(frame_editor, troughcolor=COLOR_FONDO_EDITOR)
        scrollbar_editor.pack(side="right", fill="y")

        self.text_area = tk.Text(
            frame_editor, wrap="none", font=FONT_EDITOR,
            bg=COLOR_FONDO_EDITOR, fg=COLOR_TEXTO_EDITOR,
            insertbackground=COLOR_ACENTO,
            selectbackground="#264f78", selectforeground="white",
            borderwidth=0, padx=8, pady=8,
            undo=True, tabs=("4c",),
            yscrollcommand=self._sync_scroll_editor
        )

        # Números de línea
        self.num_linea = NumeroLinea(
            frame_editor, self.text_area,
            bg=COLOR_LINEAS, width=50,
            highlightthickness=0, borderwidth=0
        )
        self.num_linea.pack(side="left", fill="y")

        self.text_area.pack(side="left", expand=True, fill="both")
        scrollbar_editor.config(command=self._on_editor_scroll)

        # ── Terminal de Salida ──
        frame_terminal_wrapper = tk.Frame(self.panel_derecho, bg=COLOR_TERMINAL_BG)
        self.panel_derecho.add(frame_terminal_wrapper, minsize=150)

        # Etiqueta de terminal
        terminal_header = tk.Frame(frame_terminal_wrapper, bg="#0d0d18")
        terminal_header.pack(fill="x")
        tk.Label(
            terminal_header, text="  💻 TERMINAL DE SALIDA",
            bg="#0d0d18", fg=COLOR_TEXTO_DIM,
            font=("Segoe UI", 9, "bold"), pady=5
        ).pack(anchor="w")

        frame_terminal = tk.Frame(frame_terminal_wrapper, bg=COLOR_TERMINAL_BG)
        frame_terminal.pack(expand=True, fill="both")

        scrollbar_terminal = tk.Scrollbar(frame_terminal, troughcolor=COLOR_TERMINAL_BG)
        scrollbar_terminal.pack(side="right", fill="y")

        self.terminal = tk.Text(
            frame_terminal, wrap="word", font=FONT_TERMINAL,
            bg=COLOR_TERMINAL_BG, fg=COLOR_TERMINAL_FG,
            insertbackground=COLOR_TERMINAL_FG,
            borderwidth=0, padx=10, pady=8,
            yscrollcommand=scrollbar_terminal.set
        )
        self.terminal.pack(expand=True, fill="both")
        scrollbar_terminal.config(command=self.terminal.yview)

        # Tags de colores para la terminal
        self.terminal.tag_configure("exito", foreground="#00e676")
        self.terminal.tag_configure("error", foreground="#ff5252")
        self.terminal.tag_configure("info", foreground="#40c4ff")
        self.terminal.tag_configure("warning", foreground="#ffab40")
        self.terminal.tag_configure("titulo", foreground="#00d4aa", font=("Cascadia Code", 11, "bold"))

    def _sync_scroll_editor(self, *args):
        """Sincroniza scroll del editor con números de línea."""
        self.num_linea.actualizar()
        return args

    def _on_editor_scroll(self, *args):
        self.text_area.yview(*args)
        self.num_linea.actualizar()

    def escribir_terminal(self, mensaje, tag=None):
        if tag:
            self.terminal.insert(tk.END, mensaje + "\n", tag)
        else:
            self.terminal.insert(tk.END, mensaje + "\n")
        self.terminal.see(tk.END)

    def cerrar_archivo(self):
        self.text_area.delete("1.0", tk.END)
        self.terminal.delete("1.0", tk.END)
        self.archivo_actual = "Ninguno"
        self.ruta_actual = None
        self.lbl_archivo.config(text=self.archivo_actual)
        self.escribir_terminal("📋 Archivo cerrado.", "info")
        self.num_linea.actualizar()

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=[("Archivos CHU", "*.chu"), ("Todos", "*.*")]
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
                self.escribir_terminal(f"📂 Archivo abierto: {ruta}", "info")
                self.num_linea.actualizar()
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
                self.escribir_terminal(f"💾 Archivo guardado: {ruta}", "exito")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def compilar(self):
        self.terminal.delete("1.0", tk.END)

        # Guardar antes de compilar
        if not self.ruta_actual:
            respuesta = messagebox.askyesno(
                "Guardar",
                "Para compilar, primero debes guardar el archivo. ¿Deseas guardarlo ahora?"
            )
            if respuesta:
                self.guardar_archivo()
            else:
                self.escribir_terminal("⚠ Compilación cancelada: El archivo debe guardarse primero.", "warning")
                return

        # Si aún después de intentar guardar no hay ruta, salimos
        if not self.ruta_actual:
            return

        # Asegurar que el contenido en disco sea el mismo que en el editor
        try:
            with open(self.ruta_actual, "w", encoding="utf-8") as archivo:
                archivo.write(self.text_area.get("1.0", tk.END))
        except Exception as e:
            self.escribir_terminal(f"⚠ No se pudo auto-guardar cambios recientes: {e}", "warning")

        # Compilar
        self.escribir_terminal(f"🔵 Compilando {self.archivo_actual}...", "titulo")
        self.escribir_terminal("─" * 50)

        try:
            tokens = CompiladorLogic.compilar_y_ejecutar(self.ruta_actual)

            for tipo, valor, linea in tokens:
                self.escribir_terminal(f"   [{tipo}] -> '{valor}' (ln {linea})")

            self.escribir_terminal("─" * 50)
            self.escribir_terminal(f"✔ Léxico finalizado. {len(tokens)} tokens encontrados.\n", "exito")

        except Exception as e:
            self.escribir_terminal(f"❌ Error durante la compilación: {e}", "error")


if __name__ == "__main__":
    app = CompiladorApp()
    app.mainloop()
