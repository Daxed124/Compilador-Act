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
