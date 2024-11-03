class RedGhost:
    def __init__(self):
        self.position_x = 13
        self.position_y = 15
        self.speed = 2.5
    
    def decide_direction(self, map_data, pacman_grid_x, pacman_grid_y):
        # Movimientos posibles con sus respectivas nuevas posiciones
        possible_moves = {
            'right': (self.position_x + 1, self.position_y),
            'left': (self.position_x - 1, self.position_y),
            'down': (self.position_x, self.position_y + 1),
            'up': (self.position_x, self.position_y - 1)
        }
        
        # Filtrar movimientos válidos (sin paredes)
        valid_moves = {
            direction: (x, y)
            for direction, (x, y) in possible_moves.items()
            if 0 <= y < len(map_data) and 0 <= x < len(map_data[0]) and map_data[y][x] not in (-1, -2, 3, 8)
        }
        
        # Calcular la distancia de Manhattan para cada movimiento válido
        min_distance = float('inf')
        best_move = (self.position_x, self.position_y)
        
        for (new_x, new_y) in valid_moves.values():
            distance = abs(pacman_grid_x - new_x) + abs(pacman_grid_y - new_y)
            if distance < min_distance:
                min_distance = distance
                best_move = (new_x, new_y)
        
        # Actualizar la posición
        self.position_x, self.position_y = best_move
