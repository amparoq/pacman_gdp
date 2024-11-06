from utils import a_star, heuristic

class BlueGhost:
    def __init__(self):
        self.color = (0, 255, 255)
        self.position_x = 17
        self.position_y = 11
        self.speed = 0.07
        self.path = []
        self.current_zone = None
        self.target_position = None
        self.scatter_mode = False
        self.in_house = True
        self.moving_down = True
        self.eaten = False
        self.direction = "right"
        self.animate_going_home = False

    def move(self, map_data, posiciones_4, pacman_grid_x, pacman_grid_y):
        if self.eaten:
            self.position_x, self.position_y = (18, 11)
            self.eaten = False
            
        if not self.in_house:
            tuneles = [(pos[2], pos[1]) for pos in posiciones_4]

            if self.path:
                next_x, next_y = self.path[1] if len(self.path) > 1 else self.path[0]

                if map_data[next_x][next_y] not in (8, -2):
                    if (next_x, next_y) in tuneles:
                        self.position_x, self.position_y = (next_x, next_y)
                    elif abs(self.position_x - next_x) < 0.1 and abs(self.position_y - next_y) < 0.1:
                        self.position_x, self.position_y = next_x, next_y
                        if self.path:
                            del self.path[0]
                    else:
                        if abs(self.position_x - next_x) > self.speed:
                            self.position_x += self.speed if next_x > self.position_x else -self.speed
                        elif abs(self.position_y - next_y) > self.speed:
                            if next_y > self.position_y:
                                self.position_y += self.speed
                                self.direction = "right" 
                            else:
                                self.position_y -= self.speed 
                                self.direction = "left" 

                    if (int(round(self.position_x)), int(round(self.position_y))) == (next_x, next_y):
                        self.last_cell = (int(round(self.position_x)), int(round(self.position_y)))
                        self.position_x, self.position_y = next_x, next_y
                        if self.path:
                            del self.path[0]
            
            # Si el camino se vacía y no estamos en modo de dispersión, recalcula el camino solo una vez
            if not self.scatter_mode and not self.path:
                self.path = a_star((int(self.position_x), int(self.position_y)), 
                                   (int(pacman_grid_y), int(pacman_grid_x)), 
                                   map_data, posiciones_4)

            if self.scatter_mode and not self.eaten:
                for pos in posiciones_4:
                    if pos[0] == 4:
                        entrada_tunel = (pos[2], pos[1])
                    elif pos[0] == -4:
                        salida_tunel = (pos[2], pos[1])
                
                if not self.path:
                    if heuristic((int(self.position_x), int(self.position_y)), (33, 26), entrada_tunel, salida_tunel) > 2:
                        self.path = a_star((int(self.position_x), int(self.position_y)), (33, 26), map_data, posiciones_4)
                    else:
                        self.path = a_star((int(self.position_x), int(self.position_y)), (27, 20), map_data, posiciones_4)
                    if heuristic((int(self.position_x), int(self.position_y)), (27, 20), entrada_tunel, salida_tunel) > 2:
                        self.path = a_star((int(self.position_x), int(self.position_y)), (27, 20), map_data, posiciones_4)
                    else:
                        self.path = a_star((int(self.position_x), int(self.position_y)), (33, 26), map_data, posiciones_4)
        
        else:
            if self.moving_down:
                next_x, next_y = 19, 11
            else:
                next_x, next_y = 17, 11

            if abs(self.position_x - next_x) < 0.1:
                self.position_x = next_x
            else:
                self.position_x += self.speed if next_x > self.position_x else -self.speed
            
            if abs(self.position_y - next_y) < 0.1:
                self.position_y = next_y
            else:
                self.position_y += self.speed if next_y > self.position_y else -self.speed

            if int(round(self.position_x)) == next_x and int(round(self.position_y)) == next_y:
                self.moving_down = not self.moving_down
