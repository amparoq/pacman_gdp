
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
    return x_pantalla, y_pantalla, fila, columna


def handle_tunnel(map_data, posiciones_4, grid_x, grid_y, direction):
    if map_data[grid_y][grid_x] == 4 and direction == 'right':  # Túnel derecho a izquierdo
        for posi in posiciones_4:
            if posi[0] == -4:
                return posi[1], posi[2]
    elif map_data[grid_y][grid_x] == -4 and direction == 'left':  # Túnel izquierdo a derecho
        for posi in posiciones_4:
            if posi[0] == 4:
                print(posi[1], posi[2])
                return posi[1], posi[2]
    return grid_x, grid_y