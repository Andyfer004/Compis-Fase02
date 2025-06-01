import pickle
import os

def guardar_afd_pickle(afd_dict, mapping, ruta):
    """
    Guarda el AFD y su mapping en un .pkl
    """
    try:
        with open(ruta, 'wb') as f:
            pickle.dump({'afd': afd_dict, 'mapping': mapping}, f)
        print(f"✅ AFD + mapping guardados en: {ruta}")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")

def cargar_afd_pickle(ruta):
    """
    Carga el AFD y su mapping desde un .pkl
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"❌ El archivo no existe: {ruta}")

    try:
        with open(ruta, 'rb') as f:
            data = pickle.load(f)

        afd_dict = data.get('afd')
        mapping = data.get('mapping')

        if not afd_dict or not mapping:
            raise ValueError("❌ El archivo no contiene AFD o mapping válidos.")

        print(f"✅ AFD cargado correctamente desde: {ruta}")
        print(f"   Estados: {len(afd_dict['transitions'])}, Estados de aceptación: {len(afd_dict['accepted'])}")
        return afd_dict, mapping

    except Exception as e:
        raise RuntimeError(f"❌ Error al cargar el AFD: {e}")