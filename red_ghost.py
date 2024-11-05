from utils import a_star

class RedGhost:
    def __init__(self):
        self.position_x = 13
        self.position_y = 15
        self.speed = 0.1  # Velocidad lenta para un movimiento controlado y gradual
        self.path = []
        self.current_zone = None
        self.target_position = None  # Punto objetivo según la zona de Pacman

    def define_zona(self, pacman_x, pacman_y):
        """ Define la zona en función de la posición de Pacman. """
        if pacman_y < 10:
            return 'top' if pacman_x < 14 else 'top_right'
        elif pacman_y >= 10 and pacman_y < 20:
            return 'middle' if pacman_x < 14 else 'middle_right'
        else:
            return 'bottom' if pacman_x < 14 else 'bottom_right'

    def obtener_objetivo(self, zona):
        """ Asigna un punto objetivo según la zona en la que se encuentra Pacman. """
        objetivos = {
            'top': (5, 5),
            'top_right': (5, 23),
            'middle': (15, 6),
            'middle_right': (15, 21),
            'bottom': (25, 6),
            'bottom_right': (25, 21)
        }
        return objetivos.get(zona, (13, 15))  # Posición central por defecto si no hay zona

    def move(self, map_data, pacman_grid_x, pacman_grid_y):
        # Define la zona actual de Pacman y obtiene el objetivo
        zona_actual = self.define_zona(pacman_grid_x, pacman_grid_y)
        self.current_zone = self.define_zona(self.position_x, self.position_y)
        
        if zona_actual != self.current_zone:
            self.target_position = self.obtener_objetivo(zona_actual)
            # Calcula el nuevo camino solo si cambia de zona
            self.path = a_star((int(self.position_y), int(self.position_x)), self.target_position, map_data)

        # Movimiento hacia el siguiente paso en el camino al objetivo
        if self.path and len(self.path) > 1:
            next_x, next_y = self.path[1]  # La siguiente celda en el camino hacia el objetivo

            # Verificar que el siguiente paso es transitable
            if map_data[next_y][next_x] not in (8, -1):  # Evitar paredes y obstáculos
                # Movimiento gradual hacia la siguiente celda
                if abs(self.position_x - next_x) > self.speed:
                    self.position_x += self.speed if next_x > self.position_x else -self.speed
                elif abs(self.position_y - next_y) > self.speed:
                    self.position_y += self.speed if next_y > self.position_y else -self.speed

                # Cuando se alcanza la siguiente celda, ajustar la posición a la siguiente en el camino
                if (int(round(self.position_x)), int(round(self.position_y))) == (next_x, next_y):
                    self.position_x, self.position_y = next_x, next_y
                    del self.path[0]  # Elimina la celda completada del camino
        else:
            # Si el camino está vacío o no se encuentra, espera hasta que haya un camino válido
            print("Esperando nuevo camino...")
