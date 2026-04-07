# ╔══════════════════════════════════════════════════════════════════╗
# ║          >>> INICIO MIEMBRO 1 <<<  (Líneas 1 – 51)              ║
# ║  Sección: Imports, palabras reservadas, tipos de dato,          ║
# ║           operadores, símbolos y constantes de diseño           ║
# ╚══════════════════════════════════════════════════════════════════╝

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import ctypes

#Habilitar DPI Awareness para mejor resolución en Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

PALABRAS_RESERVADAS = {
    "si", "tons", "tonses", "mientras", "para", "roto", "reanuda", "mentira", "verdad",
    "nada", "y", "o", "nel", "definir", "regresar", "pasar", "clase", "de", "importar"
}
TIPOS_DATO = {"entero", "flota", "siono", "tecto"}
FUNCIONES_INTEGRADAS = {"afuera", "adentro", "read", "get", "count", "def"}

#Separadores por tipo

OPERADORES_PALABRA = {"suma", "resta", "multi", "divi"}
OPERADORES_SIMBOLO = {"%", "<", ">"}
OPERADORES_DOBLES = {"==", "!="}
SIMBOLOS = {"=", "(", ")", "{", "}", '"', ".", ",", "!"}
OPERADORES = OPERADORES_PALABRA | OPERADORES_SIMBOLO | OPERADORES_DOBLES

# Colores y estilos de la interfaz
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

# ╔══════════════════════════════════════════════════════════════════╗
# ║          >>> FIN MIEMBRO 1 <<<                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
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

#     ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 3 <<<  (Líneas 139 – 295)            ║
    # ║  Sección: _procesar_palabra + análisis sintáctico completo       ║
    # ║              Raul                                                ║
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
# ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 4 <<<  (Líneas 296 – 484)           ║
    # ║  Sección: Análisis semántico + construcción y                   ║
    # ║           visualización del AST                                 ║
    # ╚══════════════════════════════════════════════════════════════════╝

    # SEMÁNTICO

    @staticmethod
    def analisis_semantico(tokens):
        errores = []
        pila_ambitos = [{}]
        funciones = {}
        params_pendientes = {}  # params de función esperando al { siguiente
        i = 0

        def declarada(nombre):
            for ambito in reversed(pila_ambitos):
                if nombre in ambito:
                    return True
            return False

        while i < len(tokens):
            tipo, valor, linea = tokens[i]

            # Apertura de bloque → nuevo ámbito (con parámetros pendientes si los hay)
            if valor == "{":
                nuevo = dict(params_pendientes)
                params_pendientes.clear()
                pila_ambitos.append(nuevo)

            # Cierre de bloque → destruir ámbito
            elif valor == "}":
                if len(pila_ambitos) > 1:
                    pila_ambitos.pop()

            # Registro de función + parámetros como variables del ámbito
            elif valor == "definir":
                if i + 1 < len(tokens) and tokens[i+1][0] == "IDENTIFICADOR":
                    nombre_fn = tokens[i+1][1]
                    funciones[nombre_fn] = linea
                    # Registrar parámetros: buscar entre ( y )
                    j = i + 2
                    while j < len(tokens) and tokens[j][1] != "(":
                        j += 1
                    j += 1  # saltar (
                    while j < len(tokens) and tokens[j][1] != ")":
                        if tokens[j][0] == "TIPO_DATO" and j + 1 < len(tokens):
                            param_nombre = tokens[j+1][1]
                            # Se registra en el ámbito actual (el bloque { vendrá después)
                            pila_ambitos[-1][param_nombre] = tokens[j][1]
                        j += 1

            # Declaración de variable: TIPO_DATO ID == expr .
            elif tipo == "TIPO_DATO":
                if i + 1 < len(tokens):
                    nombre_var = tokens[i+1][1]
                    pila_ambitos[-1][nombre_var] = valor
                    i += 3
                    while i < len(tokens) and tokens[i][1] != ".":
                        if tokens[i][0] == "IDENTIFICADOR":
                            if not declarada(tokens[i][1]) and tokens[i][1] not in funciones:
                                errores.append(f"Variable '{tokens[i][1]}' no declarada (línea {tokens[i][2]})")
                        # CADENA es siempre válida como valor literal
                        i += 1

            # Asignación simple: ID == expr .  (dentro de ciclos/funciones)
            elif tipo == "IDENTIFICADOR":
                if i + 1 < len(tokens) and tokens[i+1][1] == "==":
                    if not declarada(valor):
                        errores.append(f"Variable '{valor}' no declarada en asignación (línea {linea})")
                    i += 2
                    while i < len(tokens) and tokens[i][1] != ".":
                        if tokens[i][0] == "IDENTIFICADOR":
                            if not declarada(tokens[i][1]) and tokens[i][1] not in funciones:
                                errores.append(f"Variable '{tokens[i][1]}' no declarada (línea {tokens[i][2]})")
                        i += 1

            i += 1

        return errores

    # AST

    @staticmethod
    def construir_ast(tokens):
        ast = []
        i = 0

        while i < len(tokens):
            tipo, valor, linea = tokens[i]

            # ── Declaración de variable ──
            if tipo == "TIPO_DATO":
                nodo = {
                    "tipo": "DECLARACION",
                    "dato": valor,
                    "id": tokens[i+1][1] if i+1 < len(tokens) else "?",
                    "expresion": [],
                    "linea": linea
                }
                i += 3
                while i < len(tokens) and tokens[i][1] != ".":
                    nodo["expresion"].append(tokens[i][1])
                    i += 1
                ast.append(nodo)

            # ── Función ──
            elif valor == "definir":
                nombre_fn = tokens[i+1][1] if i+1 < len(tokens) else "?"
                params = []
                j = i + 3
                while j < len(tokens) and tokens[j][1] != ")":
                    if tokens[j][0] in ("IDENTIFICADOR", "TIPO_DATO"):
                        params.append(tokens[j][1])
                    j += 1
                nodo = {
                    "tipo": "FUNCION",
                    "nombre": nombre_fn,
                    "params": params,
                    "linea": linea
                }
                ast.append(nodo)
                i = j

            # ── Ciclo mientras ──
            elif valor == "mientras":
                condicion = []
                j = i + 2
                while j < len(tokens) and tokens[j][1] != ")":
                    condicion.append(tokens[j][1])
                    j += 1
                nodo = {
                    "tipo": "MIENTRAS",
                    "condicion": condicion,
                    "linea": linea
                }
                ast.append(nodo)
                i = j

            # ── Ciclo para ──
            elif valor == "para":
                condicion = []
                j = i + 2
                while j < len(tokens) and tokens[j][1] != ")":
                    condicion.append(tokens[j][1])
                    j += 1
                nodo = {
                    "tipo": "PARA",
                    "condicion": condicion,
                    "linea": linea
                }
                ast.append(nodo)
                i = j

            # ── regresar ──
            elif valor == "regresar":
                expr = []
                j = i + 1
                while j < len(tokens) and tokens[j][1] != ".":
                    expr.append(tokens[j][1])
                    j += 1
                nodo = {
                    "tipo": "REGRESAR",
                    "expresion": expr,
                    "linea": linea
                }
                ast.append(nodo)
                i = j

            i += 1

        return ast

    @staticmethod
    def mostrar_ast(ast):
        salida = ["🌳 ÁRBOL SINTÁCTICO:\n"]

        for n in ast:
            t = n["tipo"]
            salida.append(f"└── {t}  (línea {n['linea']})")
            if t == "DECLARACION":
                salida.append(f"    ├── Tipo : {n['dato']}")
                salida.append(f"    ├── ID   : {n['id']}")
                salida.append(f"    └── Expr : {' '.join(n['expresion'])}\n")
            elif t == "FUNCION":
                salida.append(f"    ├── Nombre  : {n['nombre']}")
                salida.append(f"    └── Params  : {', '.join(n['params']) or 'ninguno'}\n")
            elif t in ("MIENTRAS", "PARA"):
                salida.append(f"    └── Condición: {' '.join(n['condicion'])}\n")
            elif t == "REGRESAR":
                salida.append(f"    └── Expr: {' '.join(n['expresion'])}\n")

        return "\n".join(salida)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 4 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

# ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 5 <<<  (Líneas 485 – 700)           ║
    # ║  Sección: Tabla de símbolos + generación de cuádruplos          ║
    # ║           (código intermedio) + mostrar_cuadruplos              ║
    # ╚══════════════════════════════════════════════════════════════════╝

    # TABLA

    @staticmethod
    def construir_tabla(tokens):
        tabla = {}
        i = 0

        while i < len(tokens):
            if tokens[i][0] == "TIPO_DATO":
                nombre = tokens[i+1][1]
                expr = []

                i += 3
                while i < len(tokens) and tokens[i][1] != ".":
                    expr.append(tokens[i][1])
                    i += 1

                tabla[nombre] = {
                    "tipo": tokens[i- len(expr)-3][1],
                    "expr": expr
                }

            i += 1

        return tabla

    @staticmethod
    def mostrar_tabla(tabla):
        salida = ["🧠 TABLA DE SÍMBOLOS:\n"]

        for k, v in tabla.items():
            salida.append(f"{k} -> Tipo: {v['tipo']} | Expr: {' '.join(v['expr'])}")

        return "\n".join(salida)

    # CÓDIGO INTERMEDIO (Cuádruplos)

    @staticmethod
    def generar_cuadruplos(tokens):
        cuadruplos = []
        temp_count = [0]
        label_count = [0]

        def nuevo_temp():
            t = f"t{temp_count[0]}"
            temp_count[0] += 1
            return t

        def nueva_label():
            l = f"L{label_count[0]}"
            label_count[0] += 1
            return l

        OP_MAP = {
            "suma": "+", "resta": "-", "multi": "*", "divi": "/",
            "%": "%", "<": "<", ">": ">", "!=": "!="
        }

        def eval_expr(expr_tokens):
            # Normalizar: si recibimos strings directos, convertir a tuplas ficticias
            norm = []
            for t in expr_tokens:
                if isinstance(t, tuple):
                    norm.append(t[1])  # extraer el valor del token
                else:
                    norm.append(t)
            vals = norm

            for op_sym in ("suma","resta","multi","divi","+","-","*","/","%","<",">","!="):
                if op_sym in vals:
                    idx = vals.index(op_sym)
                    izq_vals = vals[:idx]
                    der_vals = vals[idx+1:]
                    # Llamada recursiva con strings
                    izq = eval_expr(izq_vals)
                    der = eval_expr(der_vals)
                    res = nuevo_temp()
                    cuadruplos.append((OP_MAP.get(op_sym, op_sym), izq, der, res))
                    return res
            return vals[0] if vals else ""

        i = 0
        n = len(tokens)
        while i < n:
            tipo, valor, linea = tokens[i]

            # Declaración: TIPO id == expr .
            if tipo == "TIPO_DATO" and i+2 < n and tokens[i+2][1] == "==":
                nombre = tokens[i+1][1]
                expr_toks = []
                i += 3
                while i < n and tokens[i][1] != ".":
                    expr_toks.append(tokens[i])
                    i += 1
                res = eval_expr(expr_toks)
                cuadruplos.append(("=", res, "", nombre))

            # Asignación: id == expr .
            elif tipo == "IDENTIFICADOR" and i+1 < n and tokens[i+1][1] == "==":
                nombre = valor
                expr_toks = []
                i += 2
                while i < n and tokens[i][1] != ".":
                    expr_toks.append(tokens[i])
                    i += 1
                res = eval_expr(expr_toks)
                cuadruplos.append(("=", res, "", nombre))

            # afuera(expr)
            elif tipo == "FUNCION_INTEGRADA" and valor == "afuera":
                i += 2
                expr_toks = []
                while i < n and tokens[i][1] != ")":
                    expr_toks.append(tokens[i])
                    i += 1
                res = eval_expr(expr_toks)
                cuadruplos.append(("afuera", res, "", ""))

            # definir nombre(params) {
            elif valor == "definir":
                nombre_fn = tokens[i+1][1] if i+1 < n else "?"
                params = []
                j = i + 3
                while j < n and tokens[j][1] != ")":
                    if tokens[j][0] == "IDENTIFICADOR":
                        params.append(tokens[j][1])
                    j += 1
                cuadruplos.append(("func_inicio", nombre_fn, str(len(params)), ""))
                for p in params:
                    cuadruplos.append(("param", p, "", ""))
                i = j

            elif valor == "}":
                cuadruplos.append(("bloque_fin", "", "", ""))

            # regresar expr .
            elif valor == "regresar":
                expr_toks = []
                i += 1
                while i < n and tokens[i][1] != ".":
                    expr_toks.append(tokens[i])
                    i += 1
                res = eval_expr(expr_toks)
                cuadruplos.append(("regresar", res, "", ""))

            # mientras (cond) {
            elif valor == "mientras":
                label_ini = nueva_label()
                label_fin = nueva_label()
                cuadruplos.append(("label", label_ini, "", ""))
                i += 2
                cond_toks = []
                while i < n and tokens[i][1] != ")":
                    cond_toks.append(tokens[i])
                    i += 1
                cond_res = eval_expr(cond_toks)
                cuadruplos.append(("if_false", cond_res, "", label_fin))
                cuadruplos.append(("_loop_meta_", label_ini, label_fin, ""))

            # para (init , cond) {
            elif valor == "para":
                i += 2
                init_toks = []
                while i < n and tokens[i][1] != ",":
                    init_toks.append(tokens[i])
                    i += 1
                # Emitir init: puede ser  TIPO id == val  o  id == val
                if init_toks and init_toks[0][0] == "TIPO_DATO":
                    nombre_var = init_toks[1][1]
                    r = eval_expr(init_toks[3:])
                elif len(init_toks) >= 3 and init_toks[1][1] == "==":
                    nombre_var = init_toks[0][1]
                    r = eval_expr(init_toks[2:])
                else:
                    nombre_var = None; r = ""
                if nombre_var:
                    cuadruplos.append(("=", r, "", nombre_var))
                i += 1
                label_ini = nueva_label()
                label_fin = nueva_label()
                cuadruplos.append(("label", label_ini, "", ""))
                cond_toks = []
                while i < n and tokens[i][1] != ")":
                    cond_toks.append(tokens[i])
                    i += 1
                cond_res = eval_expr(cond_toks)
                cuadruplos.append(("if_false", cond_res, "", label_fin))
                cuadruplos.append(("_loop_meta_", label_ini, label_fin, ""))

            i += 1

        # Post-proceso: resolver _loop_meta_ en goto + label
        resultado = []
        loop_stack = []
        for c in cuadruplos:
            if c[0] == "_loop_meta_":
                loop_stack.append((c[1], c[2]))
            elif c[0] == "bloque_fin" and loop_stack:
                label_ini, label_fin = loop_stack.pop()
                resultado.append(("goto", label_ini, "", ""))
                resultado.append(("label", label_fin, "", ""))
            else:
                resultado.append(c)

        return resultado

    @staticmethod
    def mostrar_cuadruplos(cuadruplos):
        salida = ["⚙  CÓDIGO INTERMEDIO (Cuádruplos):\n"]
        salida.append(f"  {'#':<5} {'OP':<14} {'ARG1':<14} {'ARG2':<14} {'RES'}")
        salida.append("  " + "─" * 58)
        for idx, (op, a1, a2, res) in enumerate(cuadruplos):
            salida.append(f"  {idx:<5} {op:<14} {str(a1):<14} {str(a2):<14} {res}")
        return "\n".join(salida)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 5 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

# ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 6 <<<  (Líneas 701 – 816)           ║
    # ║  Sección: Intérprete (ejecuta cuádruplos en memoria virtual)    ║
    # ╚══════════════════════════════════════════════════════════════════╝

    # INTÉRPRETE

    @staticmethod
    def interpretar(cuadruplos, output_fn=None):
        if output_fn is None:
            output_fn = print

        labels = {}
        for idx, (op, a1, a2, res) in enumerate(cuadruplos):
            if op == "label":
                labels[a1] = idx

        memoria = {}
        MAX_ITER = 100_000

        def get(nombre):
            return memoria.get(nombre, 0)

        def set_(nombre, valor):
            memoria[nombre] = valor

        def evaluar(v):
            if v == "" or v is None:
                return 0
            # Si ya es string Python (resultado de concatenación), devolverlo tal cual
            if isinstance(v, str) and not v.startswith('"'):
                # Puede ser variable o temporal
                val_mem = get(v)
                if val_mem != 0 or v in memoria:
                    return val_mem
                # Intentar convertir a número
                try: return int(v)
                except (ValueError, TypeError): pass
                try: return float(v)
                except (ValueError, TypeError): pass
                return v
            if isinstance(v, str) and v.startswith('"'):
                return v[1:-1]  # quitar comillas
            return get(v)

        pc = 0
        iteraciones = 0

        while pc < len(cuadruplos):
            iteraciones += 1
            if iteraciones > MAX_ITER:
                output_fn("⚠ Límite de iteraciones alcanzado (posible bucle infinito).")
                break

            op, a1, a2, res = cuadruplos[pc]

            if op == "label":
                pass

            elif op == "=":
                set_(res, evaluar(a1))

            elif op in ("+", "-", "*", "/", "%"):
                v1, v2 = evaluar(a1), evaluar(a2)
                if op == "+":
                    # Concatenación si alguno es cadena
                    if isinstance(v1, str) or isinstance(v2, str):
                        r = str(v1) + str(v2)
                    else:
                        r = v1 + v2
                elif op == "-": r = v1 - v2
                elif op == "*": r = v1 * v2
                elif op == "/": r = (v1 / v2) if v2 != 0 else 0
                else:           r = v1 % v2
                set_(res, r)

            elif op in ("<", ">", "!="):
                v1, v2 = evaluar(a1), evaluar(a2)
                if   op == "<":  r = v1 < v2
                elif op == ">":  r = v1 > v2
                else:            r = v1 != v2
                set_(res, r)

            elif op == "if_false":
                if not evaluar(a1):
                    pc = labels.get(res, pc)
                    continue

            elif op == "goto":
                pc = labels.get(a1, pc)
                continue

            elif op == "afuera":
                val = evaluar(a1)
                if isinstance(val, float) and val == int(val):
                    val = int(val)
                # Limpiar comillas residuales si es cadena literal
                s = str(val)
                if s.startswith('"') and s.endswith('"'):
                    s = s[1:-1]
                output_fn(s)

            elif op == "func_inicio":
                # Saltar el cuerpo de la función al definirse
                depth = 1
                pc += 1
                while pc < len(cuadruplos) and depth > 0:
                    if cuadruplos[pc][0] == "func_inicio": depth += 1
                    if cuadruplos[pc][0] == "bloque_fin":  depth -= 1
                    pc += 1
                continue

            elif op in ("param", "bloque_fin"):
                pass

            elif op == "regresar":
                set_("_ret_", evaluar(a1))

            pc += 1

        return memoria


    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 6 <<<                                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

# ╔══════════════════════════════════════════════════════════════════╗
# ║          >>> INICIO MIEMBRO 7 <<<  (Líneas 817 – 912)           ║
# ║  Sección: Widget NumeroLinea + clase CompiladorApp              ║
# ║           (_configurar_ventana, _inicializar_variables,         ║
# ║            _configurar_estilos)                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

# WIDGET: Números de línea para el editor

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

# INTERFAZ GRÁFICA

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

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> FIN MIEMBRO 7 <<<                                   ║
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

# ╔══════════════════════════════════════════════════════════════════╗
    # ║          >>> INICIO MIEMBRO 9 <<<  (Líneas 1087 – 1254)         ║
    # ║  Sección: Métodos de la app: sincronización de scroll,          ║
    # ║           terminal, cerrar/abrir/guardar archivo,               ║
    # ║           compilar + punto de entrada __main__                  ║
    # ╚══════════════════════════════════════════════════════════════════╝

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

        try:
            tokens = CompiladorLogic.compilar_y_ejecutar(self.ruta_actual)

            # LÉXICO
            self.escribir_terminal(" ANÁLISIS LÉXICO:", "titulo")
            for t in tokens:
                tipo, valor, linea = t
                self.escribir_terminal(f"  [{linea}] {tipo:20s} → {valor}", "info")

            self.escribir_terminal("", None)

            # SINTÁCTICO
            self.escribir_terminal("📐 ANÁLISIS SINTÁCTICO:", "titulo")
            err_sin = CompiladorLogic.analisis_sintactico(tokens)
            if err_sin:
                for e in err_sin:
                    self.escribir_terminal(f"  ✖ {e}", "error")
                self.escribir_terminal("\n Compilación fallida en fase sintáctica.", "error")
                return
            else:
                self.escribir_terminal("   Sin errores sintácticos.", "exito")

            self.escribir_terminal("", None)

            # SEMÁNTICO
            self.escribir_terminal(" ANÁLISIS SEMÁNTICO:", "titulo")
            err_sem = CompiladorLogic.analisis_semantico(tokens)
            if err_sem:
                for e in err_sem:
                    self.escribir_terminal(f"  ✖ {e}", "error")
                self.escribir_terminal("\n Compilación fallida en fase semántica.", "error")
                return
            else:
                self.escribir_terminal("  ✔ Sin errores semánticos.", "exito")

            self.escribir_terminal("", None)

            # AST
            ast = CompiladorLogic.construir_ast(tokens)
            for l in CompiladorLogic.mostrar_ast(ast).split("\n"):
                self.escribir_terminal(l, "info")

            self.escribir_terminal("", None)

            # TABLA DE SÍMBOLOS
            tabla = CompiladorLogic.construir_tabla(tokens)
            for l in CompiladorLogic.mostrar_tabla(tabla).split("\n"):
                self.escribir_terminal(l, "info")

            self.escribir_terminal("", None)

            # CÓDIGO INTERMEDIO
            cuadruplos = CompiladorLogic.generar_cuadruplos(tokens)
            for l in CompiladorLogic.mostrar_cuadruplos(cuadruplos).split("\n"):
                self.escribir_terminal(l, "info")

            self.escribir_terminal("", None)

            # EJECUCIÓN / INTÉRPRETE
            self.escribir_terminal("▶  RESULTADO DE EJECUCIÓN:", "titulo")
            salida_ejecucion = []
            CompiladorLogic.interpretar(
                cuadruplos,
                output_fn=lambda msg: salida_ejecucion.append(msg)
            )
            if salida_ejecucion:
                for linea_out in salida_ejecucion:
                    self.escribir_terminal(f"  {linea_out}", "exito")
            else:
                self.escribir_terminal("  (sin salida en pantalla)", "warning")

            self.escribir_terminal("", None)
            self.escribir_terminal(" Compilación y ejecución exitosa.", "exito")

        except Exception as e:
            self.escribir_terminal(f"  ✖ Error interno: {e}", "error")

if __name__ == "__main__":
    app = CompiladorApp()
    app.mainloop()

# ╔══════════════════════════════════════════════════════════════════╗
# ║          >>> FIN MIEMBRO 9 <<<                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
