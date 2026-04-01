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

