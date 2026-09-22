"""
==================================================================
 Ejemplo aplicado: Arboles, DFS y BFS en un rastreador web
 (web crawler)
==================================================================

Idea del ejemplo:
------------------
Un rastreador web (el programa que usan buscadores como Google) parte
de una PAGINA SEMILLA y va descubriendo paginas nuevas siguiendo los
enlaces que encuentra en cada una. Si ignoramos los enlaces que
regresan a paginas ya visitadas, ese recorrido se puede representar
como un ARBOL:

    - La raiz es la PAGINA SEMILLA (la pagina inicial del rastreo).
    - Cada hijo es una PAGINA enlazada directamente desde su padre.
    - Los "nietos" son paginas enlazadas desde esas paginas, y asi
      sucesivamente.

Se reutiliza la MISMA clase Nodo y las MISMAS funciones de recorrido
(dfs_recursivo, dfs_iterativo, bfs) de la presentacion "Arboles, DFS
y BFS", aplicadas ahora a un caso real de rastreo web, tal como lo
menciona la diapositiva "Aplicaciones en el mundo real": Rastreadores
web -> BFS (exploracion de paginas por niveles de enlaces).

Librerias usadas:
    - networkx  -> para representar el arbol como grafo y dibujarlo
    - matplotlib -> para graficar el arbol de rastreo
    - pandas    -> para mostrar el orden de rastreo con su "profundidad"
"""

from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd


# ------------------------------------------------------------------
# 1. Clase Nodo (igual a la de la presentacion)
# ------------------------------------------------------------------
class Nodo:
    """Cada nodo guarda su valor (la URL o nombre de pagina) y sus hijos."""

    def __init__(self, valor):
        self.valor = valor
        self.hijos = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)


# ------------------------------------------------------------------
# 2. Construccion del arbol: Pagina semilla -> Paginas enlazadas
# ------------------------------------------------------------------
semilla = Nodo("Pagina de inicio (blog.com)")

# Paginas enlazadas directamente desde la pagina de inicio (nivel 1)
pagina_blog = Nodo("/blog")
pagina_nosotros = Nodo("/sobre-nosotros")
pagina_contacto = Nodo("/contacto")

semilla.agregar_hijo(pagina_blog)
semilla.agregar_hijo(pagina_nosotros)
semilla.agregar_hijo(pagina_contacto)

# Paginas enlazadas desde /blog (nivel 2)
pagina_blog.agregar_hijo(Nodo("/blog/articulo-arboles"))
pagina_blog.agregar_hijo(Nodo("/blog/articulo-grafos"))

# Paginas enlazadas desde /sobre-nosotros (nivel 2)
pagina_nosotros.agregar_hijo(Nodo("/sobre-nosotros/equipo"))

# Paginas enlazadas desde /contacto (nivel 2)
pagina_contacto.agregar_hijo(Nodo("/contacto/soporte"))
pagina_contacto.agregar_hijo(Nodo("/contacto/ventas"))


# ------------------------------------------------------------------
# 3. Recorridos DFS y BFS (mismas funciones de la presentacion)
# ------------------------------------------------------------------
def dfs_recursivo(nodo, visitados=None):
    """DFS usando la pila de llamadas de Python (recursion)."""
    if visitados is None:
        visitados = []
    visitados.append(nodo.valor)
    for hijo in nodo.hijos:
        dfs_recursivo(hijo, visitados)
    return visitados


def dfs_iterativo(raiz):
    """DFS usando una pila explicita (lista con pop())."""
    visitados = []
    pila = [raiz]
    while pila:
        nodo = pila.pop()
        visitados.append(nodo.valor)
        for hijo in reversed(nodo.hijos):
            pila.append(hijo)
    return visitados


def bfs(raiz):
    """BFS usando una cola (deque) -> comportamiento FIFO."""
    visitados = []
    cola = deque([raiz])
    while cola:
        nodo = cola.popleft()
        visitados.append(nodo.valor)
        for hijo in nodo.hijos:
            cola.append(hijo)
    return visitados


orden_dfs = dfs_recursivo(semilla)
orden_bfs = bfs(semilla)

print("Orden de rastreo DFS (profundidad primero):")
print(orden_dfs)
print()
print("Orden de rastreo BFS (por niveles de enlaces):")
print(orden_bfs)


# ------------------------------------------------------------------
# 4. Interpretacion practica
# ------------------------------------------------------------------
# BFS: es el que usan la mayoria de los rastreadores web reales,
#      porque primero termina de descubrir TODAS las paginas enlazadas
#      directamente desde la semilla (nivel 1) antes de entrar a
#      revisar sus enlaces (nivel 2). Esto evita que el rastreador se
#      "pierda" siguiendo un solo hilo de enlaces muy profundo,
#      dejando de lado el resto del sitio.
#
# DFS: tambien se usa en algunos casos, por ejemplo cuando se quiere
#      explorar rapidamente una seccion completa del sitio (como
#      /blog y todos sus articulos) antes de pasar a otra seccion.


# ------------------------------------------------------------------
# 5. Pasar el arbol de Nodo a un grafo de NetworkX (para dibujarlo)
# ------------------------------------------------------------------
G = nx.DiGraph()  # grafo dirigido: cada arista va de pagina padre -> pagina hija


def agregar_al_grafo(nodo, grafo):
    """Recorre el arbol (con DFS) y agrega cada arista padre-hijo."""
    for hijo in nodo.hijos:
        grafo.add_edge(nodo.valor, hijo.valor)
        agregar_al_grafo(hijo, grafo)


G.add_node(semilla.valor)  # aseguramos que la raiz quede en el grafo
agregar_al_grafo(semilla, G)


# ------------------------------------------------------------------
# 6. Calcular una posicion "por niveles" (profundidad de rastreo)
#    sin depender de librerias externas como graphviz
# ------------------------------------------------------------------
def posiciones_arbol(grafo, raiz):
    niveles = {raiz: 0}
    cola = deque([raiz])
    while cola:
        actual = cola.popleft()
        for hijo in grafo.successors(actual):
            niveles[hijo] = niveles[actual] + 1
            cola.append(hijo)

    nodos_por_nivel = {}
    for nodo, nivel in niveles.items():
        nodos_por_nivel.setdefault(nivel, []).append(nodo)

    posiciones = {}
    for nivel, nodos in nodos_por_nivel.items():
        cantidad = len(nodos)
        for i, nodo in enumerate(nodos):
            x = (i - (cantidad - 1) / 2)
            y = -nivel
            posiciones[nodo] = (x, y)
    return posiciones, niveles


pos, niveles = posiciones_arbol(G, semilla.valor)

# Colores segun la profundidad de rastreo (0 = semilla, 1, 2, ...)
paleta_por_nivel = {0: "#264653", 1: "#2a9d8f", 2: "#e9c46a"}
colores = [paleta_por_nivel.get(niveles[nodo], "#e76f51") for nodo in G.nodes()]

plt.figure(figsize=(12, 6))
nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=colores,
    node_size=2600,
    font_size=7,
    font_weight="bold",
    edge_color="#555555",
    arrows=True,
    arrowsize=15,
)
plt.title("Arbol de rastreo web (BFS explora primero todo un nivel de enlaces)")
plt.axis("off")
plt.tight_layout()
plt.savefig("rastreador_web_bfs.png", dpi=150)
print("\nImagen guardada como 'rastreador_web_bfs.png'")


# ------------------------------------------------------------------
# 7. Tabla del orden de rastreo con su profundidad (pandas)
# ------------------------------------------------------------------
tabla = pd.DataFrame({
    "Paso": range(1, len(orden_bfs) + 1),
    "Pagina rastreada (BFS)": orden_bfs,
    "Profundidad (nivel de enlace)": [niveles[p] for p in orden_bfs],
})

print("\nOrden de rastreo BFS con su profundidad:")
print(tabla.to_string(index=False))

tabla.to_csv("rastreo_bfs_paginas.csv", index=False)
print("\nTabla guardada como 'rastreo_bfs_paginas.csv'")