import pygame
from utils import create_map_matrix, matriz_a_pantalla, a_star
from player import Player
from constants import cell_size, pacman_color, wall_color, point_color, background_color, door_color, red_ghost_color, pink_ghost_color, orange_ghost_color, blue_ghost_color
from red_ghost import RedGhost
from pink_ghost import PinkGhost
from orange_ghost import OrangeGhost
from blue_ghost import BlueGhost
from collections import deque

# Cargar el mapa desde un archivo de texto
map_data, posiciones_4 = create_map_matrix("maze1.txt")


# Tamaño de la pantalla
map_height = len(map_data)
map_width = len(map_data[0])
screen_width = map_width * cell_size
screen_height = map_height * cell_size

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Encuentra una posición inicial para Pacman en la cuadrícula
pacman_grid_x, pacman_grid_y = 14, 21

# Variables de Pacman
direction = None
next_direction = None
speed = 2.5  # Velocidad en píxeles por frame

# Inicialización de la posición de Pacman en la pantalla
pacman_screen_x = pacman_grid_x * cell_size
pacman_screen_y = pacman_grid_y * cell_size

# Función para verificar si Pacman puede moverse a una posición en la cuadrícula
def can_move(grid_x, grid_y):
    if 0 <= grid_y < len(map_data) and 0 <= grid_x < len(map_data[0]):
        return map_data[grid_y][grid_x] in (0, 1, 2, 4, -4)
    return False

# Ajustar el objetivo del fantasma rosado en función de la dirección de Pacman
def update_pink_ghost_target(pacman_x, pacman_y, next_direction):
    if next_direction:
        if next_direction == "up":
            possible_moves = [(pacman_x, pacman_y - 4), # straight up
                            (pacman_x + 1, pacman_y - 3), # straight up and one to the right
                            (pacman_x + 2, pacman_y - 2), # straight up and two to the right
                            (pacman_x + 3, pacman_y - 1), # straight up and thre to the right
                            (pacman_x - 1, pacman_y - 3), # straight up and one to the left
                            (pacman_x - 2, pacman_y - 2), # straight up and two to the left
                            (pacman_x - 3, pacman_y - 1) # straight up and three to the left
                            ]
        elif next_direction == "right":
            possible_moves = [(pacman_x + 4, pacman_y), # straight right
                            (pacman_x + 3, pacman_y - 1), # straight right and one up
                            (pacman_x + 2, pacman_y - 2), # straight up and two to the right
                            (pacman_x + 1, pacman_y - 3), # straight up and thre to the right
                            (pacman_x + 3, pacman_y + 3), # straight up and one to the left
                            (pacman_x + 2, pacman_y + 2), # straight up and two to the left
                            (pacman_x + 1, pacman_y + 1) # straight up and three to the left
                            ]
        elif next_direction == "left":
            possible_moves = [(pacman_x - 4, pacman_y), # straight right
                            (pacman_x - 3, pacman_y - 1), # straight right and one up
                            (pacman_x - 2, pacman_y - 2), # straight up and two to the right
                            (pacman_x - 1, pacman_y - 3), # straight up and thre to the right
                            (pacman_x - 3, pacman_y + 3), # straight up and one to the left
                            (pacman_x - 2, pacman_y + 2), # straight up and two to the left
                            (pacman_x - 1, pacman_y + 1) # straight up and three to the left
                            ]
        elif next_direction == "down":
            possible_moves = [(pacman_x, pacman_y + 4), # straight up
                            (pacman_x + 1, pacman_y + 3), # straight up and one to the right
                            (pacman_x + 2, pacman_y + 2), # straight up and two to the right
                            (pacman_x + 3, pacman_y + 1), # straight up and thre to the right
                            (pacman_x - 1, pacman_y + 3), # straight up and one to the left
                            (pacman_x - 2, pacman_y + 2), # straight up and two to the left
                            (pacman_x - 3, pacman_y + 1) # straight up and three to the left
                            ]
        for move in possible_moves:
            if move[0] < map_width and move[0] > 0 and move[1] < map_height and move[1] > 0:
                if map_data[move[1]][move[0]] in (0, 1, 2):
                    return move
    return pacman_x, pacman_y

# Ajustar el objetivo del fantasma rosado en función de la dirección de Pacman y el rojo
def is_transitable(x, y, map_data):
    # Verifica si la posición (x, y) es transitable en el mapa
    if 0 <= y < len(map_data) and 0 <= x < len(map_data[0]):
        return map_data[int(y)][int(x)] in (0, 1, 2, 4, -4)  # Solo considerar celdas transitables
    return False

def find_nearest_transitable(target, map_data, max_distance=10):
    x, y = target
    visited = set()
    queue = deque([(x, y, 0)])  # (posición x, posición y, distancia actual)
    
    while queue:
        current_x, current_y, distance = queue.popleft()
        
        # Si encontramos una celda transitable, la devolvemos
        if is_transitable(current_x, current_y, map_data):
            return current_x, current_y
        
        # Limitar la distancia máxima de búsqueda para evitar exploraciones excesivas
        if distance < max_distance:
            # Agregar vecinos en un radio mayor
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = current_x + dx, current_y + dy
                if (new_x, new_y) not in visited:
                    visited.add((new_x, new_y))
                    queue.append((new_x, new_y, distance + 1))
    
    # Si no se encuentra una celda transitable dentro del rango, devolver el objetivo original
    return target

def update_blue_ghost_target(pacman_x, pacman_y, red_ghost, next_direction):
    target = (pacman_x, pacman_y)  # Por defecto, ir a Pacman
    if next_direction == "up":
        target = (pacman_x, pacman_y - 2)
    elif next_direction == "right":
        target = (pacman_x + 2, pacman_y)
    elif next_direction == "left":
        target = (pacman_x - 2, pacman_y)
    elif next_direction == "down":
        target = (pacman_x, pacman_y + 2)

    # Calcular el objetivo basado en la posición de RedGhost
    final_target = abs(target[0] - red_ghost.position_x) * 2, abs(target[1] - red_ghost.position_y) * 2

    # Verificar si el final_target es transitable; de no serlo, buscar una posición cercana válida
    if not is_transitable(final_target[0], final_target[1], map_data):
        final_target = find_nearest_transitable(final_target, map_data)

    return final_target


# Creamos una instancia de jugador para manejar vidas, nivel y puntos:
player = Player()
red_ghost = RedGhost()
pink_ghost = PinkGhost()
orange_ghost = OrangeGhost()
blue_ghost = BlueGhost()

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # Obtener el objetivo para el fantasma rosado
    pink_ghost_target = update_pink_ghost_target(pacman_grid_x, pacman_grid_y, next_direction)
    blue_ghost_target = update_blue_ghost_target(pacman_grid_x, pacman_grid_y, red_ghost, next_direction)

    # Mover fantasmas
    blue_ghost.move(map_data, posiciones_4, blue_ghost_target[0], blue_ghost_target[1])
    red_ghost.move(map_data, posiciones_4, pacman_grid_x, pacman_grid_y)
    pink_ghost.move(map_data, posiciones_4, pink_ghost_target[0], pink_ghost_target[1])
    orange_ghost.move(map_data, posiciones_4, pacman_grid_x, pacman_grid_y)

    # Si PinkGhost está en su posición objetivo, asignarle un nuevo objetivo hacia Pacman
    if int(pink_ghost.position_x) == pink_ghost_target[0] and int(pink_ghost.position_y) == pink_ghost_target[1]:
        pink_ghost_target = update_pink_ghost_target(pacman_grid_x, pacman_grid_y, next_direction)
        pink_ghost.move(map_data, posiciones_4, pink_ghost_target[0], pink_ghost_target[1])
    
    if int(blue_ghost.position_x) == blue_ghost_target[0] and int(blue_ghost.position_y) == blue_ghost_target[1]:
        blue_ghost_target = update_blue_ghost_target(pacman_grid_x, pacman_grid_y, red_ghost, next_direction)
        blue_ghost.move(map_data, posiciones_4, blue_ghost_target[0], blue_ghost_target[1])

    # Obtener posiciones de pantalla para los fantasmas
    red_ghost_screen_x, red_ghost_screen_y = matriz_a_pantalla(red_ghost.position_x, red_ghost.position_y, cell_size)
    pink_ghost_screen_x, pink_ghost_screen_y = matriz_a_pantalla(pink_ghost.position_x, pink_ghost.position_y, cell_size)
    orange_ghost_screen_x, orange_ghost_screen_y = matriz_a_pantalla(orange_ghost.position_x, orange_ghost.position_y, cell_size)
    blue_ghost_screen_x, blue_ghost_screen_y = matriz_a_pantalla(blue_ghost.position_x, blue_ghost.position_y, cell_size)
    
    # Detecta las teclas presionadas para cambiar de dirección
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        next_direction = 'up'
    elif keys[pygame.K_DOWN]:
        next_direction = 'down'
    elif keys[pygame.K_LEFT]:
        next_direction = 'left'
    elif keys[pygame.K_RIGHT]:
        next_direction = 'right'

    # Movimiento en la cuadrícula solo si está alineado (si está en una intersección)
    if pacman_screen_x % cell_size == 0 and pacman_screen_y % cell_size == 0:
        pacman_grid_x = int(pacman_screen_x // cell_size)
        pacman_grid_y = int(pacman_screen_y // cell_size)

        # Cambia la dirección solo si la siguiente celda está libre
        if next_direction == 'up' and can_move(pacman_grid_x, pacman_grid_y - 1):
            direction = 'up'
        elif next_direction == 'down' and can_move(pacman_grid_x, pacman_grid_y + 1):
            direction = 'down'
        elif next_direction == 'left' and can_move(pacman_grid_x - 1, pacman_grid_y):
            direction = 'left'
        elif next_direction == 'right' and can_move(pacman_grid_x + 1, pacman_grid_y):
            direction = 'right'
        
        # Lógica del túnel
        if map_data[pacman_grid_y][pacman_grid_x] == 4 and direction == 'right':
            # Teletransportar al otro lado (celda -4)
            pacman_grid_x = 0  # Índice de -4 en el borde izquierdo
            pacman_screen_x = pacman_grid_x * cell_size
        elif map_data[pacman_grid_y][pacman_grid_x] == -4 and direction == 'left':
            # Teletransportar al otro lado (celda 4)
            pacman_grid_x = map_width - 1  # Índice de 4 en el borde derecho
            pacman_screen_x = pacman_grid_x * cell_size

    # Mueve a Pacman en la dirección actual si es posible
    if direction == 'up' and can_move(pacman_grid_x, pacman_grid_y - 1):
        pacman_screen_y -= speed
    elif direction == 'down' and can_move(pacman_grid_x, pacman_grid_y + 1):
        pacman_screen_y += speed
    elif direction == 'left' and can_move(pacman_grid_x - 1, pacman_grid_y):
        pacman_screen_x -= speed
    elif direction == 'right' and can_move(pacman_grid_x + 1, pacman_grid_y):
        pacman_screen_x += speed
    
    # Cambiar el map_data (la matriz) segun la posicion de pacman
    # Acá se come los pellets
    if map_data[pacman_grid_y][pacman_grid_x] == 1:
        map_data[pacman_grid_y][pacman_grid_x] = 0 
        player.points += 10
    if map_data[pacman_grid_y][pacman_grid_x] == 2:
        map_data[pacman_grid_y][pacman_grid_x] = 0 
        player.points += 50
        # Aca se maneja la logica del power up (fantasmas escapan y pueden comerse)
        red_ghost.scatter_mode = True
        pink_ghost.scatter_mode = True
        orange_ghost.scatter_mode = True
        blue_ghost.scatter_mode = True

    # Dibujar el mapa
    screen.fill(background_color)
    for row in range(len(map_data)):
        for col in range(len(map_data[row])):
            cell_value = map_data[row][col]
            cell_rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            
            if cell_value == 8:
                pygame.draw.rect(screen, wall_color, cell_rect)
            elif cell_value == 2:
                pygame.draw.circle(screen, point_color, cell_rect.center, cell_size // 4)
            elif cell_value == 1:
                pygame.draw.circle(screen, point_color, cell_rect.center, cell_size // 8)
            elif cell_value == -1:
                pygame.draw.rect(screen, door_color, cell_rect)

    # Dibujar a Pacman en la posición de pantalla correspondiente
    pacman_rect = pygame.Rect(int(pacman_screen_x), int(pacman_screen_y), cell_size, cell_size)
    pygame.draw.circle(screen, pacman_color, pacman_rect.center, cell_size // 2)
    
    red_ghost_rect = pygame.Rect(int(red_ghost_screen_x), int(red_ghost_screen_y), cell_size, cell_size)
    pygame.draw.circle(screen, red_ghost_color, red_ghost_rect.center, cell_size // 2)

    pink_ghost_rect = pygame.Rect(int(pink_ghost_screen_x), int(pink_ghost_screen_y), cell_size, cell_size)
    pygame.draw.circle(screen, pink_ghost_color, pink_ghost_rect.center, cell_size // 2)
    
    orange_ghost_rect = pygame.Rect(int(orange_ghost_screen_x), int(orange_ghost_screen_y), cell_size, cell_size)
    pygame.draw.circle(screen, orange_ghost_color, orange_ghost_rect.center, cell_size // 2)

    blue_ghost_rect = pygame.Rect(int(blue_ghost_screen_x), int(blue_ghost_screen_y), cell_size, cell_size)
    pygame.draw.circle(screen, blue_ghost_color, blue_ghost_rect.center, cell_size // 2)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
