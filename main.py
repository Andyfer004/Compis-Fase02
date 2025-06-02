from parser.evaluator import evaluar_archivo

print("🔎 Variable expressions (Parser 1)")
evaluar_archivo(
    "input/variable_expressions.txt",
    "input/afd_min.pkl",
    "input/slr-2.yalp"
)
