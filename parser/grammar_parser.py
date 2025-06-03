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

        if clean == '%%':
            in_productions = True
            continue

        if ':' in clean:
                # Guardar la producción anterior si la hay
            if current_lhs and accumulating_rules:
                productions[current_lhs] = accumulating_rules
                print(f"  ✅ Cerrando producción {current_lhs}: {accumulating_rules}")
            lhs, rhs = clean.split(':', 1)
            current_lhs = lhs.strip()
            in_productions = True
            accumulating_rules = []

            rhs = rhs.strip()
            if rhs:  # Si hay una regla en la misma línea
                rules = [r.strip().split() for r in rhs.split('|') if r.strip()]
                accumulating_rules.extend(rules)
                print(f"  📌 Nueva producción {current_lhs}: {rules}")
            else:
                print(f"  📌 Nueva producción {current_lhs}: [] (esperando reglas en siguientes líneas)")
            continue


        if clean.startswith('|'):
            rules = [r.strip().split() for r in clean.split('|') if r.strip()]
            accumulating_rules.extend(rules)
            print(f"  ➕ Reglas adicionales para {current_lhs}: {rules}")
            continue

        if clean == ';':
            if current_lhs:
                productions[current_lhs] = accumulating_rules
                print(f"  ✅ Cerrando producción {current_lhs}: {accumulating_rules}")
                current_lhs = None
                accumulating_rules = []
            continue

        if in_productions and current_lhs:
            rule = clean.split()
            if rule:
                accumulating_rules.append(rule)
                print(f"  ➕ Regla agregada suelta para {current_lhs}: {rule}")

    # Guardar última producción si quedó algo
    if current_lhs and accumulating_rules:
        productions[current_lhs] = accumulating_rules
        print(f"  ✅ Cerrando producción final {current_lhs}: {accumulating_rules}")

    if not productions:
        raise ValueError("❌ No se encontraron producciones válidas en el archivo .yalp")

    print("\n📦 Tokens finales:", tokens)
    print("📜 Producciones finales:", productions)
    return tokens, productions