from parser.grammar_parser import parse_yalp_file
from parser.slr import construir_tabla_slr, parsear_cadena,exportar_tabla_slr
from parser.visualizer import visualizar_lr0
from afd_serializer import cargar_afd_pickle
from lexer import lexer
import os

def limpiar_mapping(mapping):
    """
    Elimina 'return ' al inicio de los valores del mapping si lo tiene.
    """
    return {
        k: v.replace("return ", "").strip()
        if isinstance(v, str) and v.startswith("return ")
        else v
        for k, v in mapping.items()
    }

def evaluar_archivo(path_txt, afd_path, yalp_path):
    afd, mapping_archivo = cargar_afd_pickle(afd_path)

    # Mapping limpio desde el pickle
    original_mapping = limpiar_mapping(mapping_archivo)

    # Mapeo manual de símbolos a tokens esperados por el parser
    manual_mapping = {
        'id': 'ID',
        'number': 'NUMBER',
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'TIMES',
        '/': 'DIV',
        '(': 'LPAREN',
        ')': 'RPAREN',
        ';': 'SEMICOLON',
        ':=': 'ASSIGNOP',
        '<': 'LT',
        '=': 'EQ',
        'WHITESPACE': 'ws'  # 🔧 Corrección aquí para alinear con IGNORE ws
    }

    # Mapping final usado por el lexer
    mapping = {**original_mapping, **manual_mapping}

    print("\n📦 Mapping final:")
    for tag, tok in mapping.items():
        print(f"  {tag} => {tok}")

    # Cargar tokens y producciones desde el archivo .yalp
    tokens_yalp, producciones, ignore_tokens = parse_yalp_file(yalp_path)
    print(f"Tokens leídos: {tokens_yalp}")
    print(f"Producciones leídas: {producciones}")
    print(f"Tokens a ignorar: {ignore_tokens}")

    base_filename = os.path.splitext(os.path.basename(yalp_path))[0]
    output_dir = base_filename
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, f'{base_filename}.txt')
    filename = os.path.join(output_dir, base_filename)

    # Construir tabla SLR y visualizar el autómata
    tabla, estados, transiciones = construir_tabla_slr(producciones, tokens_yalp)
    visualizar_lr0(estados, transiciones, filename)
    tabla_txt_path = os.path.join(output_dir, 'tabla_slr.txt')
    exportar_tabla_slr(tabla, tabla_txt_path)

    # Lectura manual de líneas desde archivo de entrada
    with open(path_txt, 'r', encoding='utf-8') as f:
        buffer = ''
        while True:
            c = f.read(1)
            if not c:  # EOF
                if buffer:
                    evaluar_linea(buffer, afd, mapping, tabla, producciones, log_path, ignore_tokens)
                break
            if c == '\n':
                if buffer and not solo_espacios(buffer):
                    evaluar_linea(buffer, afd, mapping, tabla, producciones, log_path, ignore_tokens)
                buffer = ''
            else:
                buffer += c


def solo_espacios(texto):
    for c in texto:
        if c not in [' ', '\t', '\r', '\n']:
            return False
    return True


def evaluar_linea(linea, afd, mapping, tabla, producciones, log_path, ignore_tokens):
    try:
        lista_tokens = lexer(linea, afd, mapping, debug=False)
        entrada = [
            mapping.get(t, t)
            for t, _ in lista_tokens
            if mapping.get(t, t) not in ignore_tokens
        ]
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\nEvaluando: {linea}\n")
        parsear_cadena(entrada, tabla, producciones, log_path)
    except Exception as e:
        print(f"❌ Error al evaluar línea: {e}")