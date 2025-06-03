# SLR Parser Generator

Este proyecto implementa un **parser SLR(1)** en Python capaz de:

* Leer gramáticas desde archivos `.yalp`
* Construir tablas SLR automáticamente
* Visualizar el autómata LR(0)
* Analizar cadenas de entrada con un lexer personalizado
* Guardar resultados y autómatas generados en carpetas por proyecto

## Estructura del Proyecto

```
.
├── afd_serializer.py
├── evaluator.py
├── lexer.py
├── parser/
│   ├── grammar_parser.py
│   ├── slr.py
│   └── visualizer.py
├── input/
│   ├── <archivos .yalp>
│   └── <archivos de entrada .txt>
├── output/
│   └── <carpetas por archivo .yalp>
│       ├── <archivo>.png   # Imagen del autómata
│       └── <archivo>.txt   # Resultados de evaluación
```

## Instalación

Requiere Python 3.8 o superior y los siguientes paquetes:

* `graphviz`
* `pickle` (incluido en la stdlib)
* `os` (incluido en la stdlib)

Puedes instalar Graphviz con:

```sh
pip install graphviz
```

**Importante:**
Asegúrate de tener instalado [Graphviz](https://graphviz.gitlab.io/download/) en tu sistema (además del paquete de Python).

## Uso

1. **Prepara tus archivos**:

   * Gramática: `input/tu_gramatica.yalp`
   * AFD serializado: `afd.pkl`
   * Archivo de pruebas: `input/entradas.txt`

2. **Ejecuta el evaluador**:

```python
from evaluator import evaluar_archivo

evaluar_archivo(
    path_txt='input/entradas.txt',
    afd_path='afd.pkl',
    yalp_path='input/tu_gramatica.yalp'
)
```

3. **Resultados**:

   * Se creará una carpeta por cada gramática utilizada (ej. `slr-4/`).
   * Ahí encontrarás:

     * El autómata LR(0) como imagen PNG.
     * Un log `.txt` con los resultados de cada evaluación.

## Ejemplo de archivo `.yalp`

```yalp
%token ID NUMBER PLUS MINUS TIMES DIV LPAREN RPAREN SEMICOLON ASSIGNOP LT EQ

%%
S : E SEMICOLON ;
E : E PLUS T
  | E MINUS T
  | T ;
T : T TIMES F
  | T DIV F
  | F ;
F : LPAREN E RPAREN
  | ID
  | NUMBER ;
```

---
