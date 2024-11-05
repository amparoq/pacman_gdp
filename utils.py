import heapq

def create_map_matrix(map_txt):
    map_file = open(map_txt)
    map_data = []
    posiciones_4 = []  # Lista para almacenar las coordenadas de -4
    for fila, line in enumerate(map_file):
        map_row = []
        for columna, character in enumerate(line.strip()):
            if character == "X":
                map_row.append(8)
            elif character == ".":
                map_row.append(1)
            elif character == "+":
                map_row.append(2)
            elif character == "=":
                map_row.append(-1)
            elif character == "G":
                map_row.append(3)
            elif character == "T":
                map_row.append(4)
                posiciones_4.append((4, columna // 2, fila)) 
            elif character == "t":
                map_row.append(-4)
                posiciones_4.append((-4, columna // 2, fila))  # Agrega la posición de -4
            elif character == "E":
                map_row.append(0)
            elif character == "S":
                map_row.append(-2)
        map_data.append(map_row)
    map_file.close()
    return map_data, posiciones_4

def matriz_a_pantalla(fila, columna, cell_size):
    x_pantalla = columna * cell_size
    y_pantalla = fila * cell_size
    return x_pantalla, y_pantalla

def heuristic(a, b):
    # Usamos la distancia de Manhattan como heurística
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()  # El camino se construye desde el objetivo hasta el inicio
    return path

def a_star(start, goal, matriz):
    # Conjuntos abiertos y cerrados para almacenar y buscar nodos
    open_set = []
    heapq.heappush(open_set, (0, start))  # Usamos heapq para mantener la prioridad por fScore
    came_from = {}

    # gScore y fScore inicializados
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        # Nodo con el menor fScore
        current = heapq.heappop(open_set)[1]

        # Si llegamos al objetivo, reconstruimos el camino
        if current == goal:
            return reconstruct_path(came_from, current)

        # Vecinos y movimiento posible en las direcciones arriba, abajo, izquierda, derecha
        neighbors = [
            (current[0] + 1, current[1]),  # Abajo
            (current[0] - 1, current[1]),  # Arriba
            (current[0], current[1] + 1),  # Derecha
            (current[0], current[1] - 1)   # Izquierda
        ]

        for neighbor in neighbors:
            x, y = neighbor
            if 0 <= x < len(matriz) and 0 <= y < len(matriz[0]):  # Asegura que esté dentro de los límites
                if matriz[x][y] in (0, 1, 2):  # Verifica si la celda es transitable
                    tentative_g_score = g_score[current] + 1  # Suponemos coste 1 para cada movimiento

                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        # Registro de mejor camino conocido
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)

                        # Añadir a open_set si no está presente
                        if neighbor not in [i[1] for i in open_set]:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # Retornar None si no se encuentra un camino
    return None

# matriz, _ = create_map_matrix("maze1.txt")
# print(a_star((5, 1), (10, 9), matriz))