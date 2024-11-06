import heapq

def create_map_matrix(map_txt):
    map_file = open(map_txt)
    map_data = []
    posiciones_4 = []  # Lista para almacenar las coordenadas de -4
    for fila, line in enumerate(map_file):
        map_row = []
        for columna, character in enumerate(line.strip()):
            if character == "X":
                map_row.append(8) # Paredes
            elif character == ".":
                map_row.append(1) # Espacios con pellets pequeños
            elif character == "+":
                map_row.append(2) # Espacios con pellets de power up
            elif character == "=":
                map_row.append(-1) # "Puertas" de espacio de fantasmas
            elif character == "G":
                map_row.append(3) # Espacios dentro de casa de fantasmas
            elif character == "T":
                map_row.append(4) # Entrada tunel derecho
                posiciones_4.append((4, columna // 2, fila)) 
            elif character == "t":
                map_row.append(-4) # Entrada tunel izquierdo
                posiciones_4.append((-4, columna // 2, fila))  # Agrega la posición de -4
            elif character == "E":
                map_row.append(0) # Espacio vacío
            elif character == "S":
                map_row.append(-2) # Espacios fuera del laberinto, aca pondremos score o solo son vacíos (fantasmas y jugador no pueden llegar aca)
        map_data.append(map_row)
    map_file.close()
    return map_data, posiciones_4

def matriz_a_pantalla(fila, columna, cell_size):
    x_pantalla = columna * cell_size
    y_pantalla = fila * cell_size
    return x_pantalla, y_pantalla

import heapq

def heuristic(a, b, posicion_tunel_derecha, posicion_tunel_izquierda):
    # Usamos la distancia de Manhattan como heurística
    dist_a_b = abs(a[0] - b[0]) + abs(a[1] - b[1])
    # Considerando los tuneles:
    if posicion_tunel_derecha:
        # 1. si entro por el tunel derecho y salgo por el izquierdo
        dist_a_tunel_derecha =  abs(a[0] - posicion_tunel_derecha[0]) + abs(a[1] - posicion_tunel_derecha[1])
        dist_a_tunel_izquierda = abs(b[0] - posicion_tunel_izquierda[0]) + abs(b[1] - posicion_tunel_izquierda[1])
        
        dist_a_b_di = dist_a_tunel_derecha + dist_a_tunel_izquierda
        # 2. si entro por el tunel izquierdp y salgo por el derecho
        dist_a_tunel_derecha =  abs(a[0] - posicion_tunel_izquierda[0]) + abs(a[1] - posicion_tunel_izquierda[1])
        dist_a_tunel_izquierda = abs(b[0] - posicion_tunel_derecha[0]) + abs(b[1] - posicion_tunel_derecha[1])
        
        dist_a_b_id = dist_a_tunel_derecha + dist_a_tunel_izquierda
        return min(dist_a_b, dist_a_b_di, dist_a_b_id)
    return dist_a_b

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()  # El camino se construye desde el objetivo hasta el inicio
    return path

def a_star(start, goal, matriz, posiciones_4):
    # Conjuntos abiertos y cerrados para almacenar y buscar nodos
    open_set = []
    heapq.heappush(open_set, (0, start))  # Usamos heapq para mantener la prioridad por fScore
    came_from = {}

    # gScore y fScore inicializados
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal, None, None)}

    # Identificar las posiciones de entrada y salida del túnel
    entrada_tunel = None
    salida_tunel = None
    for pos in posiciones_4:
        if pos[0] == 4:
            entrada_tunel = (pos[2], pos[1])
        elif pos[0] == -4:
            salida_tunel = (pos[2], pos[1])

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

        # Verificación de túnel: si current es una entrada o salida del túnel, agrega la otra como vecino
        if current == entrada_tunel:
            neighbors.append(salida_tunel)  # Agrega la salida del túnel como vecino
        elif current == salida_tunel:
            neighbors.append(entrada_tunel)  # Agrega la entrada del túnel como vecino

        for neighbor in neighbors:
            x, y = neighbor
            if 0 <= x < len(matriz) and 0 <= y < len(matriz[0]):  # Asegura que esté dentro de los límites
                if matriz[x][y] in (0, 1, 2, 4, -4, -1, 3):  # Verifica si la celda es transitable
                    # Coste de movimiento estándar
                    tentative_g_score = g_score[current] + 1

                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        # Registro de mejor camino conocido
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal, entrada_tunel, salida_tunel)

                        # Añadir a open_set si no está presente
                        if neighbor not in [i[1] for i in open_set]:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # Retornar None si no se encuentra un camino
    return None

# matriz, pos4 = create_map_matrix("maze1.txt")
# print(a_star((17, 14), (18, 23), matriz, pos4))

# total_pellets = 0
# for m in matriz: 
#     for mi in m:
#         if mi == 1:
#             total_pellets += mi

# print(total_pellets)