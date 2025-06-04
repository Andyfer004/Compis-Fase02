def parse_yalp_file(filepath):
    tokens = set()
    productions = {}
    ignore_tokens = set()
    current_lhs = [None]
    accumulating_rules = []
    in_productions = [False]

    def es_espacio(c):
        return c in [' ', '\t']

    def dividir_palabras(texto):
        palabra = ''
        palabras = []
        for c in texto:
            if es_espacio(c):
                if palabra:
                    palabras.append(palabra)
                    palabra = ''
            else:
                palabra += c
        if palabra:
            palabras.append(palabra)
        return palabras

    def limpiar_fin_linea(linea):
        return ''.join(c for c in linea if c not in ['\r', '\n'])

    def agregar_reglas(rhs_texto):
        alternativas = [alt for alt in rhs_texto.split('|') if alt]
        for alt in alternativas:
            palabras = dividir_palabras(alt)
            if palabras:
                accumulating_rules.append(palabras)

    def process_line(linea, linea_num):
        linea = limpiar_fin_linea(linea)

        if not linea or linea.startswith('/*'):
            return

        if linea.startswith('%token'):
            contenido = linea[len('%token'):]
            nuevos_tokens = dividir_palabras(contenido)
            print(f"[Línea {linea_num}] ➕ Tokens encontrados: {nuevos_tokens}")
            tokens.update(nuevos_tokens)
            return

        if linea.startswith('IGNORE'):
            partes = dividir_palabras(linea)
            if len(partes) == 2:
                token_ignorado = partes[1]
                ignore_tokens.add(token_ignorado)
                print(f"[Línea {linea_num}] 🧽 Token a ignorar: {token_ignorado}")
            return

        if linea == '%%':
            in_productions[0] = True
            print(f"[Línea {linea_num}] ➖ Inicio de producciones")
            return

        if ':' in linea:
            if current_lhs[0] and accumulating_rules:
                productions[current_lhs[0]] = accumulating_rules[:]
                print(f"[Línea {linea_num}] ✅ Cerrando producción {current_lhs[0]}: {accumulating_rules}")
            lhs, rhs = linea.split(':', 1)
            lhs = lhs.strip()
            current_lhs[0] = lhs
            accumulating_rules.clear()
            agregar_reglas(rhs)
            print(f"[Línea {linea_num}] 📌 Nueva producción {lhs}: {accumulating_rules}")
            return

        if linea.lstrip().startswith('|'):
            contenido = linea.lstrip()[1:]
            agregar_reglas(contenido)
            print(f"[Línea {linea_num}] ➕ Reglas alternativas para {current_lhs[0]}: {contenido}")
            return

        if linea == ';':
            if current_lhs[0]:
                productions[current_lhs[0]] = accumulating_rules[:]
                print(f"[Línea {linea_num}] ✅ Cerrando producción {current_lhs[0]}: {accumulating_rules}")
                current_lhs[0] = None
                accumulating_rules.clear()
            return

        if in_productions[0] and current_lhs[0]:
            agregar_reglas(linea)
            print(f"[Línea {linea_num}] ➕ Regla agregada suelta para {current_lhs[0]}: {linea}")

    with open(filepath, 'r', encoding='utf-8') as f:
        buffer = ''
        linea_actual = 1
        while True:
            c = f.read(1)
            if not c:
                break
            if c == '\n':
                process_line(buffer, linea_actual)
                buffer = ''
                linea_actual += 1
            else:
                buffer += c
        if buffer:
            process_line(buffer, linea_actual)

    if current_lhs[0] and accumulating_rules:
        productions[current_lhs[0]] = accumulating_rules[:]
        print(f"[Final] ✅ Cerrando producción final {current_lhs[0]}: {accumulating_rules}")

    if not productions:
        raise ValueError("❌ No se encontraron producciones válidas en el archivo .yalp")

    print("\n📦 Tokens finales:", tokens)
    print("📜 Producciones finales:", productions)
    print("🧽 Tokens ignorados:", ignore_tokens)

    return tokens, productions, ignore_tokens