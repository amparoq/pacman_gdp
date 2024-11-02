
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
                posiciones_4.append((4, fila, columna)) 
            elif character == "t":
                map_row.append(-4)
                posiciones_4.append((-4, fila, columna))  # Agrega la posición de -4
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
