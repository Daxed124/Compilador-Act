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