"""
==================================================================
 Ejemplo aplicado: DFS y backtracking para resolver un laberinto
==================================================================

Idea del ejemplo:
------------------
Un laberinto se puede representar como un GRAFO: cada casilla libre
es un nodo, y hay una arista entre dos casillas libres si son vecinas
(arriba, abajo, izquierda o derecha) y no hay una pared entre ellas.

A diferencia de un arbol, un laberinto SI puede tener varios caminos
posibles entre dos casillas, por eso aqui se representa como un grafo
general con NetworkX. Aun asi, el algoritmo de recorrido es el mismo
DFS visto en la presentacion, solo que ahora con BACKTRACKING
explicito: si una rama no lleva a la salida, el algoritmo "retrocede"
y prueba otro camino.

Este es el uso que menciona la diapositiva de "Aplicaciones en el
mundo real": Resolucion de laberintos -> DFS.

Librerias usadas:
    - networkx  -> para representar el laberinto como grafo
    - matplotlib -> para dibujar el laberinto y la solucion
    - numpy     -> para representar el laberinto como matriz numerica
    - pandas    -> para mostrar el registro paso a paso del DFS
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd


# ------------------------------------------------------------------
# 1. Definicion del laberinto
# ------------------------------------------------------------------
# '#' = pared, '.' = camino libre, 'S' = inicio (start), 'E' = salida (exit)
laberinto_texto = [
    "S.#.....",
    ".#.###.#",
    ".#.....#",
    ".#.###.#",
    "...#...#",
    "###.#.#.",
    "#...#..E",
    "#.######",
]

filas = len(laberinto_texto)
columnas = len(laberinto_texto[0])

# Ubicar el inicio (S) y la salida (E) dentro de la cuadricula
inicio = None
salida = None
for f in range(filas):
    for c in range(columnas):
        if laberinto_texto[f][c] == "S":
            inicio = (f, c)
        elif laberinto_texto[f][c] == "E":
            salida = (f, c)


# ------------------------------------------------------------------
# 2. Construir el grafo del laberinto con NetworkX
# ------------------------------------------------------------------
G = nx.Graph()  # grafo NO dirigido: se puede ir y volver entre celdas vecinas

for f in range(filas):
    for c in range(columnas):
        if laberinto_texto[f][c] != "#":          # si la celda no es pared
            G.add_node((f, c))
            # Revisamos el vecino de abajo y el vecino de la derecha
            # (con eso cubrimos todas las conexiones sin repetir)
            for df, dc in [(1, 0), (0, 1)]:
                vecino = (f + df, c + dc)
                if (0 <= vecino[0] < filas and 0 <= vecino[1] < columnas
                        and laberinto_texto[vecino[0]][vecino[1]] != "#"):
                    G.add_edge((f, c), vecino)


# ------------------------------------------------------------------
# 3. DFS con backtracking para encontrar un camino de S a E
# ------------------------------------------------------------------
def dfs_laberinto(grafo, actual, destino, visitados, camino, orden_exploracion):
    """
    DFS recursivo con backtracking:
      - Si la celda actual es el destino, ya encontramos la salida.
      - Si no, probamos cada vecino no visitado.
      - Si NINGUN vecino lleva a la salida, esta celda se elimina del
        camino (backtracking) y devolvemos False para que el nivel
        anterior siga probando otras opciones.
    """
    visitados.add(actual)
    orden_exploracion.append(actual)
    camino.append(actual)

    if actual == destino:
        return True

    for vecino in grafo.neighbors(actual):
        if vecino not in visitados:
            if dfs_laberinto(grafo, vecino, destino, visitados, camino, orden_exploracion):
                return True

    # Backtracking: ninguna de las rutas desde 'actual' llego a la salida
    camino.pop()
    return False


visitados = set()
camino_solucion = []
orden_exploracion = []

encontrado = dfs_laberinto(G, inicio, salida, visitados, camino_solucion, orden_exploracion)

print(f"Salida encontrada: {encontrado}")
print(f"Casillas exploradas en total (incluyendo retrocesos): {len(orden_exploracion)}")
print(f"Longitud del camino final (sin retrocesos): {len(camino_solucion)} casillas")
print("\nCamino final de S a E:")
print(camino_solucion)


# ------------------------------------------------------------------
# 4. Interpretacion practica
# ------------------------------------------------------------------
# El DFS explora una rama del laberinto hasta el fondo. Si llega a un
# callejon sin salida, HACE BACKTRACKING: retrocede a la ultima
# decision que tomo y prueba otro camino, sin volver a repetir
# casillas ya visitadas. Notese que "casillas exploradas" es mayor
# que "longitud del camino final", porque incluye los callejones sin
# salida que el algoritmo tuvo que descartar.


# ------------------------------------------------------------------
# 5. Visualizacion del laberinto y la solucion
# ------------------------------------------------------------------
# Convertimos el laberinto a una matriz numerica para dibujarlo:
#   0 = pared
#   1 = camino libre (no visitado por el DFS)
#   2 = camino explorado pero descartado (backtracking)
#   3 = camino final (la solucion)
#   4 = inicio
#   5 = salida
matriz = np.zeros((filas, columnas), dtype=int)
for f in range(filas):
    for c in range(columnas):
        matriz[f, c] = 0 if laberinto_texto[f][c] == "#" else 1

for celda in orden_exploracion:
    if matriz[celda] == 1:
        matriz[celda] = 2  # fue explorada

for celda in camino_solucion:
    matriz[celda] = 3  # forma parte del camino final

matriz[inicio] = 4
matriz[salida] = 5

colores = ["#2b2d42", "#f8f9fa", "#ffd6a5", "#8ac926", "#1982c4", "#ff595e"]
cmap = mcolors.ListedColormap(colores)

plt.figure(figsize=(8, 8))
plt.imshow(matriz, cmap=cmap, vmin=0, vmax=5)
plt.title("Laberinto resuelto con DFS + backtracking (S = inicio, E = salida)")
plt.xticks([])
plt.yticks([])

# Leyenda manual para explicar los colores
parches = [
    plt.Rectangle((0, 0), 1, 1, color=colores[0], label="Pared"),
    plt.Rectangle((0, 0), 1, 1, color=colores[1], label="Camino libre"),
    plt.Rectangle((0, 0), 1, 1, color=colores[2], label="Explorado y descartado"),
    plt.Rectangle((0, 0), 1, 1, color=colores[3], label="Camino final"),
    plt.Rectangle((0, 0), 1, 1, color=colores[4], label="Inicio (S)"),
    plt.Rectangle((0, 0), 1, 1, color=colores[5], label="Salida (E)"),
]
plt.legend(handles=parches, bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("laberinto_dfs.png", dpi=150, bbox_inches="tight")
print("\nImagen guardada como 'laberinto_dfs.png'")
plt.show()  # abre una ventana con la imagen al ejecutar el script


# ------------------------------------------------------------------
# 6. Registro paso a paso con pandas
# ------------------------------------------------------------------
tabla = pd.DataFrame({
    "Paso": range(1, len(orden_exploracion) + 1),
    "Casilla visitada (fila, columna)": orden_exploracion,
    "Forma parte del camino final": [c in camino_solucion for c in orden_exploracion],
})

print("\nRegistro de exploracion del DFS:")
print(tabla.to_string(index=False))

tabla.to_csv("registro_dfs_laberinto.csv", index=False)
print("\nTabla guardada como 'registro_dfs_laberinto.csv'")