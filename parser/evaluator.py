import os
from parser.grammar_parser import parse_yalp_file
from parser.slr import construir_tabla_slr, parsear_cadena, exportar_tabla_slr
from parser.visualizer import visualizar_lr0
from afd_serializer import cargar_afd_pickle
from lexer import lexer


def limpiar_mapping(mapping):
    limpio = {}
    for clave, valor in mapping.items():
        if isinstance(valor, str) and valor.startswith("return "):
            limpio[clave] = valor[7:]  # sin "return "
        else:
            limpio[clave] = valor
    return limpio


def solo_espacios(cadena):
    for c in cadena:
        if c not in [' ', '\t', '\n', '\r']:
            return False
    return True


def evaluar_archivo(path_txt, afd_path, yalp_path):
    afd, raw_mapping = cargar_afd_pickle(afd_path)
    mapping = limpiar_mapping(raw_mapping)

    tokens_yalp, producciones, ignore_tokens, start_symbol = parse_yalp_file(yalp_path)

    tabla, estados, transiciones = construir_tabla_slr(producciones, tokens_yalp)

    base = os.path.splitext(os.path.basename(yalp_path))[0]
    os.makedirs(base, exist_ok=True)

    log_path = os.path.join(base, f"{base}.txt")
    tabla_path = os.path.join(base, "tabla_slr.txt")
    visualizar_lr0(estados, transiciones, os.path.join(base, base))
    exportar_tabla_slr(tabla, tabla_path)

   
    with open(path_txt, "r", encoding="utf-8") as f:
        contenido = f.read()
        expresion = ""
        i = 0
        while i < len(contenido):
            c = contenido[i]
            expresion += c

            if c == ';':
                contiene_algo = False
                j = 0
                while j < len(expresion):
                    if expresion[j] not in [' ', '\t', '\n', '\r', ';']:
                        contiene_algo = True
                        break
                    j += 1

                if contiene_algo:
                    evaluar_expresion(
                        expresion, afd, mapping, tabla, producciones, log_path, ignore_tokens
                    )

                expresion = ""
            i += 1

def evaluar_expresion(expr, afd, mapping, tabla, producciones, log_path, ignore_tokens):
    try:
        print(f"\n🧪 Expresión: {expr.strip()}")
        tokens = lexer(expr, afd, mapping, debug=True)
        entrada = [tok for tok, _ in tokens if tok not in ignore_tokens]

        entrada.append('$')  # ✅ Agregar el símbolo de fin de entrada

        print(f"✅ Tokens que se enviarán al parser: {entrada}")
        print(f"🚫 Tokens ignorados: {ignore_tokens}")
        parsear_cadena(entrada, tabla, producciones, log_path)
    except Exception as e:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"❌ Error: {e}\n")
        print(f"❌ Error: {e}")