import pygame
from utils import create_map_matrix

# Cargar el mapa desde un archivo de texto
map_data, posiciones_4 = create_map_matrix("maze1.txt")

# Configuración
cell_size = 20
pacman_color = (255, 255, 0)
wall_color = (0, 0, 255)
point_color = (255, 255, 255)
background_color = (0, 0, 0)
door_color = (255, 255, 255)

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
pacman_grid_x, pacman_grid_y = 0, 0
for row in range(map_height):
    for col in range(map_width):
        if map_data[row][col] == 0:
            pacman_grid_x, pacman_grid_y = col, row
            break
    else:
        continue
    break

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

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
