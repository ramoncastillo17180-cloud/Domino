"""Búsquedas sobre una matriz discreta; sin dependencias de la interfaz."""
from collections import deque
from dataclasses import dataclass
from time import perf_counter


@dataclass
class Result:
    algorithm: str
    order: list
    levels: dict
    parents: dict
    seconds: float


def search(matrix, start, algorithm="BFS", target=None, stop_at_target=False):
    """BFS mide distancias mínimas; DFS registra profundidad de exploración."""
    if algorithm not in ("BFS", "DFS"):
        raise ValueError("Algoritmo desconocido")
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("La matriz debe ser rectangular y no vacía")
    rows, cols = len(matrix), len(matrix[0])
    if start is None or not (0 <= start[0] < rows and 0 <= start[1] < cols) or not matrix[start[0]][start[1]]:
        raise ValueError("Selecciona una ficha inicial válida")
    if target is not None and not (0 <= target[0] < rows and 0 <= target[1] < cols and matrix[target[0]][target[1]]):
        raise ValueError("La meta debe estar sobre una ficha")
    begin = perf_counter()
    frontier = deque([(start, None, 0)]) if algorithm == "BFS" else [(start, None, 0)]
    parents, levels, order, visited = {}, {}, [], set()
    queued = {start}
    while frontier:
        node, parent, depth = frontier.popleft() if algorithm == "BFS" else frontier.pop()
        if node in visited:
            continue
        visited.add(node)
        parents[node], levels[node] = parent, depth
        order.append(node)
        if stop_at_target and node == target:
            break
        r, c = node
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        for other in neighbors if algorithm == "BFS" else reversed(neighbors):
            y, x = other
            if not (0 <= y < rows and 0 <= x < cols and matrix[y][x]) or other in visited:
                continue
            # BFS descubre al insertar; DFS fija el padre al extraer para profundizar.
            if algorithm == "BFS" and other in queued:
                continue
            queued.add(other)
            frontier.append((other, node, depth + 1))
    return Result(algorithm, order, levels, parents, perf_counter() - begin)


def bfs(matrix, start):
    return search(matrix, start, "BFS")


def dfs(matrix, start):
    return search(matrix, start, "DFS")


def reconstruct_path(result, target):
    if target not in result.parents:
        return []
    path = []
    while target is not None:
        path.append(target)
        target = result.parents[target]
    return path[::-1]


def compare(matrix, start, target=None):
    """Misma terminación: extraer meta; sin meta, agotar el componente."""
    return tuple(search(matrix, start, name, target, True) for name in ("BFS", "DFS"))


SCENARIOS = ("Cadena recta", "Zigzag", "Bifurcación", "Fichas aisladas", "Laberinto de dominós")


def scenario(name):
    """Devuelve una matriz nueva y selecciones válidas para cada ejemplo."""
    start, target = (3, 1), (3, 10)
    if name == SCENARIOS[0]:
        cells = [(3, c) for c in range(1, 11)]
    elif name == SCENARIOS[1]:
        cells = [(1, c) for c in range(1, 5)] + [(r, 4) for r in range(2, 4)] + [(3, c) for c in range(5, 9)] + [(r, 8) for r in range(4, 7)]
        start, target = (1, 1), (6, 8)
    elif name in SCENARIOS[2:4]:
        cells = [(3, c) for c in range(1, 11)] + [(r, 5) for r in range(1, 7)]
        target = (1, 5)
        if name == SCENARIOS[3]: cells += [(0, 0), (7, 11), (0, 10)]
    elif name == SCENARIOS[4]:
        cells = [(r, c) for r in range(1, 7) for c in range(1, 11) if r in (1, 3, 6) or c in (1, 5, 10)]
        start, target = (3, 1), (3, 10)
    else:
        raise ValueError("Escenario desconocido")
    matrix = [[0]*12 for _ in range(8)]
    for r, c in cells: matrix[r][c] = 1
    return matrix, start, target
