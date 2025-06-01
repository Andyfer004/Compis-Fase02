def parse_yalp_file(filepath):
    tokens = set()
    productions = {}
    current_lhs = None
    accumulating_rules = []

    with open(filepath, 'r') as file:
        lines = file.readlines()

    in_productions = False

    for idx, line in enumerate(lines, 1):
        clean = line.strip()
        print(f"[Línea {idx}] --> '{clean}'")

        if not clean or clean.startswith('/*'):
            continue

        if clean.startswith('%token'):
            new_tokens = clean.replace('%token', '').strip().split()
            print(f"  ➕ Tokens encontrados: {new_tokens}")
            tokens.update(new_tokens)
            continue

        if ':' in clean:
            in_productions = True
            if current_lhs and accumulating_rules:
                productions[current_lhs] = accumulating_rules
                print(f"  ✅ Cerrando producción {current_lhs}: {accumulating_rules}")
            lhs, rhs = clean.split(':', 1)
            current_lhs = lhs.strip()
            rules = [r.strip().split() for r in rhs.split('|')]
            accumulating_rules = rules
            print(f"  📌 Nueva producción {current_lhs}: {rules}")
            continue

        if clean.startswith('|'):
            rules = [r.strip().split() for r in clean.split('|') if r.strip()]
            accumulating_rules.extend(rules)
            print(f"  ➕ Reglas adicionales para {current_lhs}: {rules}")
            continue

        if clean.endswith(';'):
            if current_lhs:
                productions[current_lhs] = accumulating_rules
                print(f"  ✅ Cerrando producción {current_lhs}: {accumulating_rules}")
                accumulating_rules = []
                current_lhs = None
            continue

        # 🚨 Si está dentro de producciones, debe tratarse como regla suelta (como 'expression PLUS term')
        if in_productions and current_lhs:
            rule = clean.strip().split()
            if rule:
                accumulating_rules.append(rule)
                print(f"  ➕ Regla agregada suelta para {current_lhs}: {rule}")

    if current_lhs and accumulating_rules:
        productions[current_lhs] = accumulating_rules
        print(f"  ✅ Cerrando producción final {current_lhs}: {accumulating_rules}")

    if not productions:
        raise ValueError("❌ No se encontraron producciones válidas en el archivo .yalp")

    print("\n📦 Tokens finales:", tokens)
    print("📜 Producciones finales:", productions)
    return tokens, productions