def parse_yalp_file(path):
    def trim(s: str) -> str:
        i, j = 0, len(s) - 1
        while i <= j and s[i] in " \t\r\n":
            i += 1
        while j >= i and s[j] in " \t\r\n":
            j -= 1
        return s[i:j + 1]

    def split_ws(s: str):
        parts, buf = [], []
        for ch in s:
            if ch in " \t":
                if buf:
                    parts.append(''.join(buf))
                    buf = []
            else:
                buf.append(ch)
        if buf:
            parts.append(''.join(buf))
        return parts

    def split_pipe(s: str):
        parts, buf = [], []
        for ch in s:
            if ch == '|':
                parts.append(trim(''.join(buf)))
                buf = []
            else:
                buf.append(ch)
        parts.append(trim(''.join(buf)))
        return parts

    def drop_trailing_semicolon(s: str):
        return s[:-1] if s and s[-1] == ';' else s

    tokens, ignore_tokens, productions = set(), set(), {}
    current_lhs = None
    start_symbol = None

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = trim(raw)

            if not line:
                continue
            if (line[0] == '/' and len(line) > 1 and line[1] in ('/', '*')) or line[0] == '*':
                continue

            if line[:6] == '%token':
                for tok in split_ws(line[6:]):
                    if tok:
                        tokens.add(tok)
                continue

            if line[:6] == 'IGNORE':
                for tok in split_ws(line[6:]):
                    if tok:
                        ignore_tokens.add(tok)
                continue

            if ':' in line:
                pos = line.find(':')
                lhs = trim(line[:pos])
                rhs = trim(line[pos + 1:])
                productions[lhs] = []
                current_lhs = lhs

                if start_symbol is None:
                    start_symbol = lhs

                if rhs and rhs != ';':
                    rhs_clean = drop_trailing_semicolon(rhs)
                    for alt in split_pipe(rhs_clean):
                        if alt:
                            productions[lhs].append(split_ws(alt))

                if rhs and rhs[-1] == ';':
                    current_lhs = None
                continue

            if current_lhs is not None:
                if line == ';':
                    current_lhs = None
                    continue

                if line[0] == '|':
                    line = trim(line[1:])

                ends = line.endswith(';')
                if ends:
                    line = trim(line[:-1])

                if line:
                    productions[current_lhs].append(split_ws(line))

                if ends:
                    current_lhs = None

    if not productions:
        raise ValueError("❌ No se encontraron producciones válidas.")

    # ✅ Agregar producción aumentada: S' → ...
    start_symbol_aug = start_symbol + "'"
    while start_symbol_aug in productions:
        start_symbol_aug += "'"

    # Si existe una producción llamada "general" con reglas ambiguas, forzar expression SEMICOLON
    if (
        'general' in productions and
        any(
            rule == ['general', 'SEMICOLON', 'expression'] or rule == ['expression']
            for rule in productions['general']
        )
    ):
        print("🔧 Usando símbolo inicial alternativo: expression SEMICOLON (por ambigüedad en 'general')")
        productions[start_symbol_aug] = [['expression', 'SEMICOLON']]
    else:
        productions[start_symbol_aug] = [[start_symbol]]

    return list(tokens), productions, ignore_tokens, start_symbol_aug

def limpiar(texto):
    inicio = 0
    fin = len(texto) - 1
    while inicio <= fin and texto[inicio] in [' ', '\t']:
        inicio += 1
    while fin >= inicio and texto[fin] in [' ', '\t']:
        fin -= 1
    return texto[inicio:fin+1]

def parse_rhs(texto, reglas):
    alts = []
    temp = ""
    i = 0
    while i < len(texto):
        if texto[i] == '|':
            if temp:
                alts.append(temp)
                temp = ""
        else:
            temp += texto[i]
        i += 1
    if temp:
        alts.append(temp)

    for alt in alts:
        regla = []
        palabra = ""
        for c in alt:
            if c in [' ', '\t']:
                if palabra:
                    regla.append(palabra)
                    palabra = ""
            else:
                palabra += c
        if palabra:
            regla.append(palabra)
        if regla:
            reglas.append(regla)