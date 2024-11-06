from utils import a_star, heuristic

class RedGhost:
    def __init__(self):
        self.color = (255, 0, 0)
        self.position_x = 13
        self.position_y = 15
        self.speed = 0.07
        self.path = []
        self.current_zone = None
        self.target_position = None
        self.scatter_mode = False
        self.eaten = False
        self.direction = "right"
        self.animate_going_home = False

    def move(self, map_data, posiciones_4, pacman_grid_x, pacman_grid_y):
        # Identificar las posiciones de entrada y salida del túnel
        if self.eaten:
            self.position_x, self.position_y = (18, 13)
            self.eaten = False
        
        tuneles = []
        for pos in posiciones_4:
            tuneles.append((pos[2], pos[1]))
        
        # Movimiento hacia el siguiente paso en el camino al objetivo
        if self.path and len(self.path) != 0:
            next_x, next_y = self.path[1] if len(self.path) > 1 else self.path[0]  # La siguiente celda en el camino

            # Verificar que el siguiente paso es transitable
            if map_data[next_x][next_y] not in (8, -2):  # Evitar paredes y obstáculos
                # Movimiento gradual hacia la siguiente celda
                if (next_x, next_y) in tuneles:
                    self.position_x, self.position_y = (next_x, next_y)
                if abs(self.position_x - next_x) > self.speed:
                    self.position_x += self.speed if next_x > self.position_x else -self.speed
                elif abs(self.position_y - next_y) > self.speed:
                    if next_y > self.position_y:
                        self.position_y += self.speed
                        self.direction = "right" 
                    else:
                        self.position_y -= self.speed 
                        self.direction = "left" 
                # Cuando se alcanza la siguiente celda, ajustar la posición
                if (int(round(self.position_x)), int(round(self.position_y))) == (next_x, next_y):
                    self.last_cell = (int(round(self.position_x)), int(round(self.position_y)))  # Guarda la posición actual como última
                    self.position_x, self.position_y = next_x, next_y
                    del self.path[0]  # Elimina la celda completada del camino
        
        # Si el camino se vacía, recalcula hacia la posición actual de Pacman
        if not self.scatter_mode:
            if not self.path or len(self.path) == 0:
                self.path = a_star((int(self.position_x), int(self.position_y)), (int(pacman_grid_y), int(pacman_grid_x)), map_data, posiciones_4)
            
        if self.scatter_mode and not self.eaten:
            for pos in posiciones_4:
                if pos[0] == 4:
                    entrada_tunel = (pos[2], pos[1])
                elif pos[0] == -4:
                    salida_tunel = (pos[2], pos[1])
            if not self.path or len(self.path) == 0:
                if heuristic((int(self.position_x), int(self.position_y)), (5, 26), entrada_tunel, salida_tunel) > 2:
                    self.path = a_star((int(self.position_x), int(self.position_y)), (5, 26), map_data, posiciones_4)
                else:
                    self.path = a_star((int(self.position_x), int(self.position_y)), (9, 24), map_data, posiciones_4)
                if heuristic((int(self.position_x), int(self.position_y)), (9, 24), entrada_tunel, salida_tunel) > 2:
                    self.path = a_star((int(self.position_x), int(self.position_y)), (9, 24), map_data, posiciones_4)
                else:
                    self.path = a_star((int(self.position_x), int(self.position_y)), (5, 26), map_data, posiciones_4)
