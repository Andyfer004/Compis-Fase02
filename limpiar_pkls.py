import pickle
import os

def quitar_espacios(s):
    # Elimina espacios en blanco al inicio
    i = 0
    while i < len(s) and s[i].isspace():
        i += 1
    # Elimina espacios en blanco al final
    j = len(s) - 1
    while j >= 0 and s[j].isspace():
        j -= 1
    return s[i:j+1]

def limpiar_mapping(mapping_sucio):
    limpio = {}
    for clave, valor in mapping_sucio.items():
        if isinstance(valor, str) and valor.startswith("return "):
            aux = valor[len("return "):]
            limpio[clave] = quitar_espacios(aux)
        else:
            limpio[clave] = valor
    return limpio

def limpiar_pkl(path):
    try:
        with open(path, "rb") as f:
            contenido = pickle.load(f)

        if isinstance(contenido, tuple) and len(contenido) == 2:
            afd_dict, mapping = contenido
        else:
            print(f"❌ No es un .pkl válido con (afd_dict, mapping): {path}")
            return

        mapping_limpio = limpiar_mapping(mapping)

        with open(path, "wb") as f:
            pickle.dump((afd_dict, mapping_limpio), f)

        print(f"✅ Mapping limpiado y guardado: {path}")

    except Exception as e:
        print(f"❌ Error limpiando {path}: {e}")

if __name__ == "__main__":
    carpeta_input = "input"
    for archivo in os.listdir(carpeta_input):
        if archivo.endswith(".pkl"):
            ruta = os.path.join(carpeta_input, archivo)
            limpiar_pkl(ruta)