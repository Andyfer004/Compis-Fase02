import os
import pickle

def cargar_afd(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
    with open(ruta, 'rb') as f:
        return pickle.load(f)

def ascii_de(char):
    return str(ord(char))

def lexer(cadena, afd_dict, mapping, debug=True):
    pos = 0
    tokens = []
    while pos < len(cadena):
        estado_actual = afd_dict['initial']
        transiciones = afd_dict['transitions']
        aceptacion = set(afd_dict['accepted'])

        ultimo_estado_final = None
        ultimo_token_pos = pos
        recorrido = []

        i = pos
        while i < len(cadena):
            char = cadena[i]
            ascii_token_char = str(ord(char))
            if estado_actual in transiciones and ascii_token_char in transiciones[estado_actual]:
                siguiente = transiciones[estado_actual][ascii_token_char]
                recorrido.append((estado_actual, ascii_token_char, siguiente))
                estado_actual = siguiente
                i += 1
                if estado_actual in aceptacion:
                    ultimo_estado_final = estado_actual
                    ultimo_token_pos = i
            else:
                break

        if ultimo_estado_final is None:
            raise ValueError(f"❌ Error léxico: símbolo inesperado '{cadena[pos]}' en posición {pos}")

        lexema = cadena[pos:ultimo_token_pos]
        tag = afd_dict.get('state_tags', {}).get(ultimo_estado_final)

        token = mapping.get(tag, 'UNKNOWN')

        # if debug:
        #     print(f"✔️ Token: {token}, lexema: '{lexema}' (tag: {tag})")
        #     for est, sym, sig in recorrido:
        #         print(f"   {est} --{sym}--> {sig}")

        tokens.append((token, lexema))
        pos = ultimo_token_pos

    return tokens