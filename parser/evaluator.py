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
        '=': 'EQ'
    }

    # Mapping final usado por el lexer
    mapping = {**original_mapping, **manual_mapping}

    print("\n📦 Mapping final:")
    for tag, tok in mapping.items():
        print(f"  {tag} => {tok}")

    # Cargar tokens y producciones desde el archivo .yalp
    tokens_yalp, producciones = parse_yalp_file(yalp_path)
    print(f"Tokens leídos: {tokens_yalp}")
    print(f"Producciones leídas: {producciones}")

    base_filename = os.path.splitext(os.path.basename(yalp_path))[0]
    output_dir = base_filename  # o, si prefieres: os.path.join('output', base_filename)
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, f'{base_filename}.txt')
    filename = os.path.join(output_dir, base_filename)


    # Construir tabla SLR y visualizar el autómata
    tabla, estados, transiciones = construir_tabla_slr(producciones, tokens_yalp)
    visualizar_lr0(estados, transiciones,filename)
    tabla_txt_path = os.path.join(output_dir, 'tabla_slr.txt')
    exportar_tabla_slr(tabla, tabla_txt_path)

    # Leer archivo de entrada y evaluar cada línea
    with open(path_txt, 'r') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                lista_tokens = lexer(linea, afd, mapping, debug=False)
                entrada = [t for t, _ in lista_tokens if t != 'WHITESPACE']
                # print(f"\nEvaluando: {linea}")
                mensaje = f"\nEvaluando: {linea}"
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(mensaje + '\n')
                parsear_cadena(entrada, tabla, producciones,log_path)
            except Exception as e:
                print(f"❌ Error: {e}")