import os
from graphviz import Digraph

def visualizar_lr0(states, transitions, filename):
    
 
    
    dot = Digraph(format='png')
    dot.attr(rankdir='LR', size='10,8')
    dot.attr(dpi='300')
    
    for i, state in enumerate(states):
        label = f"I{i}\n"
        for lhs, rhs, dot_pos in state:
            rhs_str = list(rhs)
            rhs_str.insert(dot_pos, "•")
            label += f"{lhs} → {' '.join(rhs_str)}\n"
        dot.node(str(i), label, shape='box')

    for (i, symbol), j in transitions.items():
        dot.edge(str(i), str(j), label=symbol)

    dot.render(filename, cleanup=True)
    print(f"✅ Autómata LR(0) visualizado en '{filename}.png'")