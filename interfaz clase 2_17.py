 #    ╔═══════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 2 <<<  (Líneas 52 – 130)          ║
    # ║                Jonathan Mizraim Olvera Diaz                   ║
    # ║                                                               ║
    # ╚═══════════════════════════════════════════════════════════════╝
# LÓGICA DEL COMPILADOR

class CompiladorLogic:

    @staticmethod
    def compilar_y_ejecutar(ruta_archivo_fuente):
        with open(ruta_archivo_fuente, 'r', encoding='utf-8') as archivo:
            codigo_fuente = archivo.read()

        tokens = CompiladorLogic.analisis_lexico(codigo_fuente)
        return tokens

    # LÉXICO

    @staticmethod
    def analisis_lexico(codigo):
        tokens = []
        palabra = ""
        linea = 1
        i = 0
        ultimo_tipo = None  # para contexto

        while i < len(codigo):
            c = codigo[i]

            if c == "\n":
                linea += 1

            if c.isalnum() or c == "_":
                palabra += c

            elif c == '"':
                if palabra:
                    CompiladorLogic._procesar_palabra(palabra, linea, tokens, ultimo_tipo)
                    ultimo_tipo = tokens[-1][0] if tokens else None
                    palabra = ""

                cadena = ""
                i += 1
                while i < len(codigo) and codigo[i] != '"':
                    if codigo[i] == "\n":
                        linea += 1
                    cadena += codigo[i]
                    i += 1

                tokens.append(("CADENA", f'"{cadena}"', linea))

            elif c == '.':
                # Si la palabra actual es un número y el siguiente char es dígito → decimal
                if palabra.isdigit() and i + 1 < len(codigo) and codigo[i + 1].isdigit():
                    palabra += c
                else:
                    # Es terminador de sentencia
                    if palabra:
                        CompiladorLogic._procesar_palabra(palabra, linea, tokens, ultimo_tipo)
                        ultimo_tipo = tokens[-1][0] if tokens else None
                        palabra = ""
                    tokens.append(("SIMBOLO", ".", linea))
                    ultimo_tipo = "SIMBOLO"

            else:
                if palabra:
                    CompiladorLogic._procesar_palabra(palabra, linea, tokens, ultimo_tipo)
                    ultimo_tipo = tokens[-1][0] if tokens else None
                    palabra = ""

                if i + 1 < len(codigo):
                    doble = c + codigo[i + 1]
                    if doble in OPERADORES_DOBLES:
                        tokens.append(("OPERADOR", doble, linea))
                        ultimo_tipo = "OPERADOR"
                        i += 2
                        continue

                if c in OPERADORES_SIMBOLO:
                    tokens.append(("OPERADOR", c, linea))
                    ultimo_tipo = "OPERADOR"
                elif c in SIMBOLOS:
                    tokens.append(("SIMBOLO", c, linea))
                    ultimo_tipo = "SIMBOLO"

            i += 1

        if palabra:
            CompiladorLogic._procesar_palabra(palabra, linea, tokens, ultimo_tipo)

        return tokens

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 2 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝
# ╔══════════════════════════════════════════════════════════════════╗
# ║          >>> INICIO MIEMBRO 3 <<<  (Líneas 139 – 295)            ║
# ║                Raul Castañeda Moreno                             ║
# ╚══════════════════════════════════════════════════════════════════╝

    @staticmethod
    def _procesar_palabra(palabra, linea, tokens, ultimo_tipo=None):
        # Si el token anterior fue 'definir', esta palabra es nombre de función
        es_nombre_funcion = (
            ultimo_tipo == "PALABRA_RESERVADA"
            and tokens
            and tokens[-1][1] == "definir"
        )
        if es_nombre_funcion:
            tokens.append(("IDENTIFICADOR", palabra, linea))
        elif palabra in PALABRAS_RESERVADAS:
            tokens.append(("PALABRA_RESERVADA", palabra, linea))
        elif palabra in TIPOS_DATO:
            tokens.append(("TIPO_DATO", palabra, linea))
        elif palabra in FUNCIONES_INTEGRADAS:
            tokens.append(("FUNCION_INTEGRADA", palabra, linea))
        elif palabra.replace('.', '', 1).isdigit():
            tokens.append(("NUMERO", palabra, linea))
        elif palabra in OPERADORES_PALABRA:
            tokens.append(("OPERADOR", palabra, linea))
        else:
            tokens.append(("IDENTIFICADOR", palabra, linea))

    # SINTÁCTICO

    @staticmethod
    def analisis_sintactico(tokens):
        errores = []
        i = 0
        pila_par = []   # pila de paréntesis
        pila_llave = [] # pila de llaves

        while i < len(tokens):
            tipo, valor, linea = tokens[i]

            # ── Paréntesis ──
            if valor == "(":
                pila_par.append(linea)
            elif valor == ")":
                if not pila_par:
                    errores.append(f"')' sin abrir en línea {linea}")
                else:
                    pila_par.pop()

            # ── Llaves ──
            if valor == "{":
                pila_llave.append(linea)
            elif valor == "}":
                if not pila_llave:
                    errores.append(f"'}}' sin abrir en línea {linea}")
                else:
                    pila_llave.pop()

            # ── Declaración de variable: TIPO_DATO ID == expr . ──
            # Solo aplica fuera de listas de parámetros (no dentro de definir(...))
            if tipo == "TIPO_DATO":
                # Detectar si estamos dentro de una lista de parámetros de 'definir'
                en_params = False
                for k in range(i - 1, -1, -1):
                    v = tokens[k][1]
                    if v == "(":
                        # Ver si antes del ( hay un IDENTIFICADOR seguido de 'definir'
                        if k >= 2 and tokens[k-1][0] == "IDENTIFICADOR" and tokens[k-2][1] == "definir":
                            en_params = True
                        break
                    if v in (")", "{", "}", "."):
                        break

                if not en_params:
                    if i + 3 >= len(tokens):
                        errores.append(f"Declaración incompleta en línea {linea}")
                    else:
                        if tokens[i+1][0] != "IDENTIFICADOR":
                            errores.append(f"Falta identificador después de tipo en línea {linea}")
                        elif tokens[i+2][1] != "==":
                            errores.append(f"Se esperaba '==' en línea {linea}, se encontró '{tokens[i+2][1]}'")
                        else:
                            j = i + 3
                            termina = False
                            while j < len(tokens):
                                if tokens[j][1] == ".":
                                    termina = True
                                    break
                                if tokens[j][1] in ("{", "}"):
                                    break
                                j += 1
                            if not termina:
                                errores.append(f"Falta '.' al final de la declaración en línea {linea}")

            # ── Función: definir nombre ( params ) { ──
            if valor == "definir":
                if i + 1 >= len(tokens):
                    errores.append(f"'definir' sin nombre de función en línea {linea}")
                elif tokens[i+1][0] != "IDENTIFICADOR":
                    errores.append(f"Se esperaba nombre de función después de 'definir' en línea {linea}")
                else:
                    nombre_fn = tokens[i+1][1]
                    if i + 2 >= len(tokens) or tokens[i+2][1] != "(":
                        errores.append(f"Falta '(' después del nombre '{nombre_fn}' en línea {linea}")
                    else:
                        # Buscar cierre de paréntesis y luego '{'
                        j = i + 3
                        while j < len(tokens) and tokens[j][1] != ")":
                            j += 1
                        if j >= len(tokens):
                            errores.append(f"Falta ')' en definición de '{nombre_fn}' en línea {linea}")
                        elif j + 1 >= len(tokens) or tokens[j+1][1] != "{":
                            errores.append(f"Falta '{{' después de parámetros en función '{nombre_fn}' en línea {linea}")

            # ── Ciclo mientras: mientras ( condicion ) { ──
            if valor == "mientras":
                if i + 1 >= len(tokens) or tokens[i+1][1] != "(":
                    errores.append(f"Se esperaba '(' después de 'mientras' en línea {linea}")
                else:
                    j = i + 2
                    while j < len(tokens) and tokens[j][1] != ")":
                        j += 1
                    if j >= len(tokens):
                        errores.append(f"Falta ')' en condición de 'mientras' en línea {linea}")
                    elif j + 1 >= len(tokens) or tokens[j+1][1] != "{":
                        errores.append(f"Falta '{{' después de condición 'mientras' en línea {linea}")

            # ── Ciclo para: para ( expr ) { ──
            if valor == "para":
                if i + 1 >= len(tokens) or tokens[i+1][1] != "(":
                    errores.append(f"Se esperaba '(' después de 'para' en línea {linea}")
                else:
                    j = i + 2
                    while j < len(tokens) and tokens[j][1] != ")":
                        j += 1
                    if j >= len(tokens):
                        errores.append(f"Falta ')' en condición de 'para' en línea {linea}")
                    elif j + 1 >= len(tokens) or tokens[j+1][1] != "{":
                        errores.append(f"Falta '{{' después de condición 'para' en línea {linea}")

            # ── regresar expr . ──
            if valor == "regresar":
                j = i + 1
                termina = False
                while j < len(tokens) and tokens[j][1] not in ("}", "{"):
                    if tokens[j][1] == ".":
                        termina = True
                        break
                    j += 1
                if not termina:
                    errores.append(f"Falta '.' después de 'regresar' en línea {linea}")

            i += 1

        if pila_par:
            errores.append(f"Paréntesis sin cerrar (abierto en línea {pila_par[-1]})")
        if pila_llave:
            errores.append(f"Llave sin cerrar (abierta en línea {pila_llave[-1]})")

        return errores

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 3 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

 #    ╔═══════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 8 <<<  (Líneas 913 – 1086)        ║
    # ║                Jonathan Mizraim Olvera Diaz                   ║
    # ║                                                               ║
    # ╚═══════════════════════════════════════════════════════════════╝
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

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 8 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

