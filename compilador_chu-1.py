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
