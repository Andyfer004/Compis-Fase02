from collections import defaultdict
import os

def compute_first(productions):
    first = defaultdict(set)
    changed = True
    while changed:
        changed = False
        for nt, rules in productions.items():
            for rule in rules:
                if not rule:
                    continue
                symbol = rule[0]
                if symbol not in productions:
                    if symbol not in first[nt]:
                        first[nt].add(symbol)
                        changed = True
                else:
                    for f in first[symbol]:
                        if f not in first[nt]:
                            first[nt].add(f)
                            changed = True
    return dict(first)

def compute_follow(productions, first, start_symbol):
    follow = defaultdict(set)
    follow[start_symbol].add('$')
    changed = True
    while changed:
        changed = False
        for nt, rules in productions.items():
            for rule in rules:
                for i in range(len(rule)):
                    B = rule[i]
                    if B in productions:
                        rest = rule[i+1:i+2]
                        if rest:
                            first_rest = first[rest[0]] if rest[0] in productions else {rest[0]}
                            for f in first_rest:
                                if f != 'ε' and f not in follow[B]:
                                    follow[B].add(f)
                                    changed = True
                        else:
                            for f in follow[nt]:
                                if f not in follow[B]:
                                    follow[B].add(f)
                                    changed = True
    return dict(follow)

def augment_grammar(productions):
    start = list(productions.keys())[0]
    #print(f"🚩 Símbolo inicial detectado: {start}")  # ← AGREGA ESTA LÍNEA
    new_start = start + "'"
    return {new_start: [[start]], **productions}, new_start


def closure(items, productions):
    closure_set = set(items)
    added = True
    while added:
        added = False
        new_items = set()
        for lhs, rhs, dot_pos in closure_set:
            if dot_pos < len(rhs):
                B = rhs[dot_pos]
                if B in productions:
                    for prod in productions[B]:
                        new_items.add((B, tuple(prod), 0))
        if not new_items.issubset(closure_set):
            closure_set |= new_items
            added = True
    return frozenset(closure_set)

def goto(items, symbol, productions):
    goto_set = set()
    for lhs, rhs, dot_pos in items:
        if dot_pos < len(rhs) and rhs[dot_pos] == symbol:
            goto_set.add((lhs, rhs, dot_pos + 1))
    return closure(goto_set, productions)

def construct_states(productions, start_symbol):
    C = []
    initial = closure({(start_symbol, tuple(productions[start_symbol][0]), 0)}, productions)
    C.append(initial)
    transitions = {}
    symbols = set(s for rules in productions.values() for r in rules for s in r)

    while True:
        added = False
        for I in C:
            for X in symbols:
                goto_I = goto(I, X, productions)
                if goto_I and goto_I not in C:
                    C.append(goto_I)
                    added = True
                if goto_I:
                    transitions[(C.index(I), X)] = C.index(goto_I)
        if not added:
            break
    return C, transitions

def construir_tabla_slr(productions, tokens):
    augmented, start = augment_grammar(productions)
    states, transitions = construct_states(augmented, start)
    first = compute_first(augmented)
    follow = compute_follow(augmented, first, start)
    action = defaultdict(dict)
    goto_table = defaultdict(dict)
    conflictos = []

    for i, I in enumerate(states):
        for lhs, rhs, dot in I:
            if dot < len(rhs):
                a = rhs[dot]
                if a in tokens:
                    j = transitions.get((i, a))
                    if j is not None:
                        existente = action[i].get(a)
                        nueva = ('shift', j)
                        if existente and existente != nueva:
                            conflictos.append((i, a, existente, nueva))
                        action[i][a] = nueva
            else:
                if lhs == start:
                    existente = action[i].get('$')
                    nueva = ('accept',)
                    if existente and existente != nueva:
                        conflictos.append((i, '$', existente, nueva))
                    action[i]['$'] = nueva
                else:
                    for a in follow[lhs]:
                        existente = action[i].get(a)
                        nueva = ('reduce', lhs, rhs)
                        if existente and existente != nueva:
                            conflictos.append((i, a, existente, nueva))
                        action[i][a] = nueva

        for A in productions:
            j = transitions.get((i, A))
            if j is not None:
                goto_table[i][A] = j


    return {'action': dict(action), 'goto': dict(goto_table)}, states, transitions

def parsear_cadena(tokens, tabla, producciones, log_path):
    """
    Analiza la lista de tokens con la tabla SLR.
    • Guarda el trace paso a paso en log_path_trace.txt
    • Guarda el resultado (aceptado o error) en log_path_resultado.txt
    """

    pila = [0]
    tokens = tokens + ['$']
    i = 0

    # Obtener directorio y base del path
    base_path = os.path.splitext(log_path)[0]
    trace_path = base_path + "_trace.txt"
    resultado_path = base_path + "_resultado.txt"

    with open(trace_path, 'w', encoding='utf-8') as trace, \
         open(resultado_path, 'w', encoding='utf-8') as resultado:

        trace.write("=== TRACE SLR(1) ===\n")

        while True:
            estado = pila[-1]
            t = tokens[i]
            accion = tabla['action'].get(estado, {}).get(t)

            trace.write(f"STACK {pila} | INPUT {tokens[i:]} | ACTION {accion}\n")

            if accion is None:
                msg = (f"❌ Cadena no aceptada: '{t}' inesperado en posición {i}.\n"
                f"   → Tokens restantes: {tokens[i:]}\n")
                resultado.write(msg)
                raise SyntaxError(f"Token inesperado: '{t}' en posición {i}")

            if accion[0] == 'shift':
                pila.append(accion[1])
                i += 1
                continue

            if accion[0] == 'reduce':
                lhs, rhs = accion[1], accion[2]
                for _ in rhs:
                    pila.pop()
                goto_estado = tabla['goto'][pila[-1]][lhs]
                pila.append(goto_estado)
                trace.write(f"   ↳ reduce {lhs} -> {' '.join(rhs)} "
                            f"(goto {goto_estado})\n")
                continue

            if accion[0] == 'accept':
                resultado.write("✅ Cadena aceptada.\n")
                print("✅ Cadena aceptada.")
                return
        
def exportar_tabla_slr(tabla, filename='tabla_slr.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("🔽 TABLA SLR(1)\n\n")

        f.write("📌 ACTION:\n")
        for estado in sorted(tabla['action']):
            for simbolo in sorted(tabla['action'][estado]):
                accion = tabla['action'][estado][simbolo]
                f.write(f"  ACTION[{estado}, {simbolo}] = {accion}\n")

        f.write("\n📌 GOTO:\n")
        for estado in sorted(tabla['goto']):
            for simbolo in sorted(tabla['goto'][estado]):
                destino = tabla['goto'][estado][simbolo]
                f.write(f"  GOTO[{estado}, {simbolo}] = {destino}\n")