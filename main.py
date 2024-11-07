import pygame
import gif_pygame
from utils import create_map_matrix, matriz_a_pantalla, a_star
from player import Player
from constants import cell_size, pacman_color, wall_color, point_color, background_color, door_color, red_ghost_color, pink_ghost_color, orange_ghost_color, blue_ghost_color, scatter_mode_color
from red_ghost import RedGhost
from pink_ghost import PinkGhost
from orange_ghost import OrangeGhost
from blue_ghost import BlueGhost
from collections import deque
import time
import os
import sys

def resource_path(relative_path):
    """Obtiene la ruta de un recurso empaquetado o en desarrollo"""
    if getattr(sys, 'frozen', False):
        # Ejecutable
        base_path = sys._MEIPASS
    else:
        # Código fuente
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

gifs_path = resource_path("gifs")
images_path = resource_path("menus")
sfx_path = resource_path("sfx")

#Cargar imagen de fondo
background_image = pygame.image.load(os.path.join(images_path, "game_over.png"))


#Cargar imagen de fondo
#background_image = pygame.image.load("game_over.png")
start_screen_image = pygame.image.load(os.path.join(images_path,"start.png"))


# Load sound effects
pygame.mixer.init()

death_sound = pygame.mixer.Sound(os.path.join(sfx_path, "death.mp3"))
ghost_eaten_sound = pygame.mixer.Sound(os.path.join(sfx_path, "ghost_eaten.mp3"))
ghost_eating_sound = pygame.mixer.Sound(os.path.join(sfx_path, "ghost_eating.mp3"))
power_pellet_sound = pygame.mixer.Sound(os.path.join(sfx_path, "power_pellet.mp3"))
waka_sound = pygame.mixer.Sound(os.path.join(sfx_path, "wakawakaish.mp3"))

GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)

# Dimensiones de los botones
START_BUTTON_X, START_BUTTON_Y = 110, 250
START_BUTTON_WIDTH, START_BUTTON_HEIGHT = 150, 50
EXIT_BUTTON_X, EXIT_BUTTON_Y = 280, 250
EXIT_BUTTON_WIDTH, EXIT_BUTTON_HEIGHT = 150, 50


#Constantes para el botón
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_X = 100
BUTTON_Y = 370

# Encuentra una posición inicial para Pacman en la cuadrícula
pacman_grid_x, pacman_grid_y = 14, 21

# Variables de Pacman
direction = None
next_direction = None
speed = 2.5  # Velocidad en píxeles por frame

# Inicialización de la posición de Pacman en la pantalla
pacman_screen_x = pacman_grid_x * cell_size
pacman_screen_y = pacman_grid_y * cell_size

ghost_captured = 0

# Función para verificar si Pacman puede moverse a una posición en la cuadrícula
def can_move(grid_x, grid_y):
    if 0 <= grid_y < len(map_data) and 0 <= grid_x < len(map_data[0]):
        return map_data[grid_y][grid_x] in (0, 1, 2, 4, -4)
    return False

# Función para mover un fantasma "comido" hacia la casa
def move_ghost_to_house(ghost, ghost_house_position, ghost_eaten_gif):
    if ghost.animate_going_home:
        target_y, target_x = ghost_house_position
        
        # Mover en línea recta hacia la posición de la casa
        if abs(ghost.position_x - target_x) > ghost.speed:
            ghost.position_x += ghost.speed if target_x > ghost.position_x else -ghost.speed
        if abs(ghost.position_y - target_y) > ghost.speed:
            ghost.position_y += ghost.speed if target_y > ghost.position_y else -ghost.speed
        
        # Dibujar el gif del fantasma comido
        ghost_eaten_gif.render(screen, (int(ghost.position_y * cell_size), int(ghost.position_x * cell_size)))
        # Verificar si el fantasma ha llegado a la casa
        if abs(ghost.position_x - target_x) <= ghost.speed and abs(ghost.position_y - target_y) <= ghost.speed:
            ghost.position_x, ghost.position_y = target_x, target_y  # Asegurar que llegue exactamente
            ghost.animate_going_home = False
            ghost.path = []  # Reiniciar su camino

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


def draw_hud():
    # Colores y fuentes para el HUD
    hud_background_color = (0, 0, 0)  # Fondo de la barra superior
    text_color = (255, 255, 255)  # Color de texto blanco
    font = pygame.font.Font(None, 36)

    # Dibuja el fondo de la barra de HUD
    pygame.draw.rect(screen, hud_background_color, (0, 0, screen_width, 3))

    # Renderiza el texto del puntaje
    score_text = font.render(f"Puntaje: {player.points}", True, text_color)
    score_rect = score_text.get_rect(topleft=(10, 10))
    screen.blit(score_text, score_rect)

    # Renderiza el texto del nivel
    level_text = font.render(f"Nivel: {player.level}", True, text_color)
    level_rect = level_text.get_rect(center=(screen_width // 2, 20))
    screen.blit(level_text, level_rect)

    # Renderiza el texto de las vidas
    lives_text = font.render(f"Vidas: {player.lives}", True, text_color)
    lives_rect = lives_text.get_rect(topright=(screen_width - 10, 10))
    screen.blit(lives_text, lives_rect)

#Funcion para dibujar el boton
def draw_button(text, x, y, width, height, color, hover_color):
    global player, map_data, posiciones_4, pacman_grid_x, pacman_grid_y, pacman_screen_x, pacman_screen_y
    global red_ghost, pink_ghost, orange_ghost, blue_ghost
    # Obtener la posición del ratón
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()  # Obtiene el estado de los botones del ratón
    
    # Detectar si el mouse está sobre el botón
    if x < mouse_pos[0] < x + width and y < mouse_pos[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if mouse_click[0] == 1:
            # Acción al hacer clic en el botón
            if text == "Volver a jugar":
                initialize_game()  # Reiniciar el juego usando la función global
            elif text == "Salir":
                # Salir del juego
                pygame.quit()
                exit()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    # Dibujar el texto del botón
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)



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
def initialize_game():
    global player, map_data, posiciones_4, pacman_grid_x, pacman_grid_y, pacman_screen_x, pacman_screen_y
    global red_ghost, pink_ghost, orange_ghost, blue_ghost
    global running, game_started, game_won
    
    # Bucle principal
    running = True
    game_started = False
    
    # Configuración inicial del juego
    player = Player()
    map_data, posiciones_4 = create_map_matrix(resource_path("maze1.txt"))
    
    # Posiciones iniciales de Pacman
    pacman_grid_x, pacman_grid_y = 14, 21
    pacman_screen_x, pacman_screen_y = pacman_grid_x * cell_size, pacman_grid_y * cell_size

    game_won = False

    # Inicializa los fantasmas
    red_ghost = RedGhost()
    pink_ghost = PinkGhost()
    orange_ghost = OrangeGhost()
    blue_ghost = BlueGhost()

# Llama a la función para inicializar el juego al comenzar
initialize_game()

# Tamaño de la pantalla
map_height = len(map_data)
map_width = len(map_data[0])
screen_width = map_width * cell_size
screen_height = map_height * cell_size

# Inicializa Pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

def draw_start_button(game_started):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # 1. Dibujar el botón "Iniciar"
    if START_BUTTON_X < mouse_pos[0] < START_BUTTON_X + START_BUTTON_WIDTH and START_BUTTON_Y < mouse_pos[1] < START_BUTTON_Y + START_BUTTON_HEIGHT:
        pygame.draw.rect(screen, DARK_GREEN, (START_BUTTON_X, START_BUTTON_Y, START_BUTTON_WIDTH, START_BUTTON_HEIGHT))
        if mouse_click[0] == 1:
            # Iniciar el juego
            game_started = True
    else:
        pygame.draw.rect(screen, GREEN, (START_BUTTON_X, START_BUTTON_Y, START_BUTTON_WIDTH, START_BUTTON_HEIGHT))

    # Dibujar el texto del botón "Iniciar"
    font = pygame.font.Font(None, 36)
    text_surface = font.render("Iniciar", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(START_BUTTON_X + START_BUTTON_WIDTH // 2, START_BUTTON_Y + START_BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    # 2. Dibujar el botón "Salir"
    if EXIT_BUTTON_X < mouse_pos[0] < EXIT_BUTTON_X + EXIT_BUTTON_WIDTH and EXIT_BUTTON_Y < mouse_pos[1] < EXIT_BUTTON_Y + EXIT_BUTTON_HEIGHT:
        pygame.draw.rect(screen, DARK_RED, (EXIT_BUTTON_X, EXIT_BUTTON_Y, EXIT_BUTTON_WIDTH, EXIT_BUTTON_HEIGHT))
        if mouse_click[0] == 1:
            # Salir del juego
            pygame.quit()
            sys.exit()  # Cierra el juego y la ventana
    else:
        pygame.draw.rect(screen, RED, (EXIT_BUTTON_X, EXIT_BUTTON_Y, EXIT_BUTTON_WIDTH, EXIT_BUTTON_HEIGHT))

    # Dibujar el texto del botón "Salir"
    text_surface = font.render("Salir", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(EXIT_BUTTON_X + EXIT_BUTTON_WIDTH // 2, EXIT_BUTTON_Y + EXIT_BUTTON_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    return game_started


# Animaciones:
pacman_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "pacman_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "pacman_left.gif")),
                     "down": gif_pygame.load(os.path.join(gifs_path,"pacman_down.gif")),
                     "up": gif_pygame.load(os.path.join(gifs_path,"pacman_up.gif"))}

red_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "red_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "red_ghost_left.gif"))}

pink_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "pink_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "pink_ghost_left.gif"))}

red_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "red_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "red_ghost_left.gif"))}

pink_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "pink_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "pink_ghost_left.gif"))}

orange_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "orange_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "orange_ghost_left.gif"))}

blue_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "blue_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "blue_ghost_left.gif"))}

scatter_ghost_animations = {"right": gif_pygame.load(os.path.join(gifs_path, "eatable_ghost_right.gif")), 
                     "left": gif_pygame.load(os.path.join(gifs_path, "eatable_ghost_left.gif"))}

pacman_death_gif = gif_pygame.load(os.path.join(gifs_path, "pacman_death.gif"))

ghost_eaten_gif = gif_pygame.load(os.path.join(gifs_path, "eaten_ghost.gif"))

scatter_ghost_animations_blinking = {"right": gif_pygame.load(os.path.join(gifs_path, "eatable_ghost_blinking_right.gif")), 
                                    "left": gif_pygame.load(os.path.join(gifs_path, "eatable_ghost_blinking_left.gif"))}

# Calcular el tiempo total de duración de la animación
death_animation_duration = sum(pacman_death_gif.get_durations())

red_ghost_house_position = (11, 18)
pink_ghost_house_position = (13, 18)
orange_ghost_house_position = (14, 18)
blue_ghost_house_position = (16, 18)

scatter_mode_start = 0

# Variables de control para la animación de muerte
player_eaten = False
death_animation_start_time = None
death_animation_playing = False

game_won = False

# Control de sonido para evitar reproducción desordenada
power_pellet_active = False
death_sound_played = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_started:
    # Dibujar el fondo del menú de inicio
        screen.blit(start_screen_image, (0, 0))
        
        # Dibujar el botón de inicio
        game_started=draw_start_button(game_started)        
        pygame.display.flip()
        clock.tick(30)

    
    if game_started:
        # Si Pacman ha sido comido, iniciar la animación de muerte
        if player_eaten and not death_animation_playing:
            death_animation_start_time = time.time()  # Registrar el tiempo de inicio de la animación
            death_animation_playing = True  # Activar el estado de animación
            pacman_death_gif.reset()  # Reiniciar el GIF al primer fotograma
            death_sound.play()
        # Reproduce la animación de muerte si está activa
        if death_animation_playing:
            pacman_death_gif.render(screen, (pacman_screen_x - 7, pacman_screen_y - 7))
            pygame.display.flip()

            # Controlar la duración de la animación
            if (time.time() - death_animation_start_time) >= death_animation_duration:
                # Finaliza la animación y reinicia el estado del juego
                death_animation_playing = False
                player_eaten = False
                player.lives -= 1

                if player.lives <= 0:
                    # Dibujar el fondo
                    screen.blit(background_image, (0, 0))
                    # Mostrar "Game Over" en el centro de la pantalla
                    font = pygame.font.SysFont(None, 72)  # Tamaño de la fuente más grande
                    game_over_text = font.render("Game Over", True, (255, 255, 0))
                    
                    # Muestra el puntaje total
                    score_text = font.render(f"Puntaje Total: {player.points}", True, (255, 255, 255))
                    score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
                    screen.blit(score_text, score_rect)
                    
                    # Obtener el tamaño del texto para centrarlo
                    text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 30))
                    
                    # Dibujar el texto en el centro
                    screen.blit(game_over_text, text_rect)
                    
                    # Dibujar los botones
                    draw_button("Volver a jugar", 50, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (0, 255, 0), (0, 200, 0))
                    draw_button("Salir", 300, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (255, 0, 0), (200, 0, 0))
                    
                    pygame.display.flip()
                    clock.tick(30)

                    continue  # Salir del bucle principal si no quedan vidas
                else:
                    # Reinicia posiciones de Pacman y fantasmas
                    direction = None
                    next_direction = None
                    pacman_grid_x, pacman_grid_y = 14, 21
                    pacman_screen_x, pacman_screen_y = pacman_grid_x * cell_size, pacman_grid_y * cell_size
                    direction = "right"
                    red_ghost.position_x, red_ghost.position_y = red_ghost_house_position
                    pink_ghost.position_x, pink_ghost.position_y = pink_ghost_house_position
                    orange_ghost.position_x, orange_ghost.position_y = orange_ghost_house_position
                    blue_ghost.position_x, blue_ghost.position_y = blue_ghost_house_position

                    # Limpiar el camino y poner a los fantasmas en modo normal
                    for ghost in [red_ghost, pink_ghost, orange_ghost, blue_ghost]:
                        ghost.path = []
                        ghost.eaten = True
                        ghost.animate_going_home = False
            else:
                # Continuar en el bucle mientras se reproduce la animación
                continue  # Saltar el resto del bucle actual para que solo se muestre la animación
        
        if game_won:
            # Dibujar el fondo
            screen.blit(background_image, (0, 0))
            # Mostrar "Game Over" en el centro de la pantalla
            font = pygame.font.SysFont(None, 72)  # Tamaño de la fuente más grande
            game_over_text = font.render("¡Has ganado!", True, (255, 255, 0))
            
            # Muestra el puntaje total
            score_text = font.render(f"Puntaje Total: {player.points}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(score_text, score_rect)
            
            # Obtener el tamaño del texto para centrarlo
            text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 40))
            
            # Dibujar el texto en el centro
            screen.blit(game_over_text, text_rect)
            
            # Dibujar los botones
            draw_button("Volver a jugar", 50, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (0, 255, 0), (0, 200, 0))
            draw_button("Salir", 300, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (255, 0, 0), (200, 0, 0))
            
            
            pygame.display.flip()
            clock.tick(30)

            continue  # Salir del bucle principal si no quedan vidas
        
        if player.lives <= 0:
            # Dibujar el fondo
            screen.blit(background_image, (0, 0))
            # Mostrar "Game Over" en el centro de la pantalla
            font = pygame.font.SysFont(None, 72)  # Tamaño de la fuente más grande
            game_over_text = font.render("Game Over", True, (255, 255, 0))
            
            # Muestra el puntaje total
            score_text = font.render(f"Puntaje Total: {player.points}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(score_text, score_rect)
            
            # Obtener el tamaño del texto para centrarlo
            text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 80))
            
            # Dibujar el texto en el centro
            screen.blit(game_over_text, text_rect)
            
            # Dibujar los botones
            draw_button("Volver a jugar", 50, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (0, 255, 0), (0, 200, 0))
            draw_button("Salir", 300, 370 + BUTTON_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT, (255, 0, 0), (200, 0, 0))
            
            pygame.display.flip()
            clock.tick(30)

            continue  # Salir del bucle principal si no quedan vidas
        
        if player.level == 1:
            scatter_mode_duration = 7 # 7 segundos
        if player.level == 2:
            scatter_mode_duration = 5 # 5 segundos
        if player.level == 3:
            scatter_mode_duration = 4 # 7 segundos  
            
        # Obtener el objetivo para el fantasma rosado
        pink_ghost_target = update_pink_ghost_target(pacman_grid_x, pacman_grid_y, next_direction)
        blue_ghost_target = update_blue_ghost_target(pacman_grid_x, pacman_grid_y, red_ghost, next_direction)

        # Mover fantasmas
        if not blue_ghost.animate_going_home:
            blue_ghost.move(map_data, posiciones_4, blue_ghost_target[0], blue_ghost_target[1])
        if not red_ghost.animate_going_home:
            red_ghost.move(map_data, posiciones_4, pacman_grid_x, pacman_grid_y)
        if not pink_ghost.animate_going_home:
            pink_ghost.move(map_data, posiciones_4, pink_ghost_target[0], pink_ghost_target[1])
        if not orange_ghost.animate_going_home:
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
            waka_sound.play()
            map_data[pacman_grid_y][pacman_grid_x] = 0 
            player.pellets_eaten += 1
            player.points += 10


        if map_data[pacman_grid_y][pacman_grid_x] == 2 and not power_pellet_active:
            power_pellet_sound.play()
            power_pellet_active = True  # Marcar que el sonido de power pellet está activo
        elif map_data[pacman_grid_y][pacman_grid_x] != 2 and power_pellet_active:
            power_pellet_active = False  # Restablecer si ya no está en el estado del power pellet


        if map_data[pacman_grid_y][pacman_grid_x] == 2:
            map_data[pacman_grid_y][pacman_grid_x] = 0 
            player.pellets_eaten += 1
            player.points += 50
            # Aca se maneja la logica del power up (fantasmas escapan y pueden comerse)
            red_ghost.scatter_mode = True
            pink_ghost.scatter_mode = True
            orange_ghost.scatter_mode = True
            blue_ghost.scatter_mode = True
            
            scatter_mode_start = time.time()
            power_pellet_sound.play()
        
        if red_ghost.scatter_mode and (time.time() - scatter_mode_start >= scatter_mode_duration):
            red_ghost.scatter_mode = False
            pink_ghost.scatter_mode = False
            orange_ghost.scatter_mode = False
            blue_ghost.scatter_mode = False
            red_ghost.path = []
            pink_ghost.path = []
            orange_ghost.path = []
            blue_ghost.path = []
            ghost_captured = 0
            
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

        # Cuando pacman come al menos 30 de los pellets se libera al fantasma azul
        if player.pellets_eaten >= 30:
            blue_ghost.in_house = False
        
        # Cuando pacman come al menos un tercio de los pellets (242) se libera al fantasma naranjo
        if player.pellets_eaten >= 80:
            orange_ghost.in_house = False
            orange_ghost.left_house = True
        
        if player.pellets_eaten == 246:
            print("¡Paso de nivel!")
            # Reinicio todo
            player.level += 1
            if player.level > 3:
                game_won = True
            
            player.pellets_eaten = 0
            
            map_data, posiciones_4 = create_map_matrix(resource_path("maze1.txt"))
            
            # Reiniciar posiciones de Pacman y fantasmas
            pacman_grid_x, pacman_grid_y = 14, 21
            pacman_screen_x, pacman_screen_y = pacman_grid_x * cell_size, pacman_grid_y * cell_size
            red_ghost.position_x, red_ghost.position_y = red_ghost_house_position
            pink_ghost.position_x, pink_ghost.position_y = pink_ghost_house_position
            orange_ghost.position_x, orange_ghost.position_y = orange_ghost_house_position
            blue_ghost.position_x, blue_ghost.position_y = blue_ghost_house_position

            # Aumento velocidades de fantasmas
            # Limpiar el camino y poner a los fantasmas en modo normal
            for ghost in [red_ghost, pink_ghost, orange_ghost, blue_ghost]:
                ghost.path = []
                ghost.eaten = True
                ghost.scatter_mode = False
                ghost.in_house = True
                ghost.animate_going_home = False
                ghost.speed *= 1.1

            # Pausar un momento para mostrar el paso de nivel
            pygame.display.flip()
            time.sleep(2)
            continue 
        
        # Dibujar a Pacman en la posición de pantalla correspondiente
        pacman_rect = pygame.Rect(int(pacman_screen_x), int(pacman_screen_y), cell_size, cell_size)
        if direction:
            pacman_gif = pacman_animations[direction]
        else:
            pacman_gif = pacman_animations["right"]
        pacman_gif.render(screen, (pacman_screen_x - 7, pacman_screen_y - 7))
        
        if not red_ghost.animate_going_home:
            red_ghost_rect = pygame.Rect(int(red_ghost_screen_x), int(red_ghost_screen_y), cell_size, cell_size)
            if red_ghost.direction in ("left", "right"):
                if not red_ghost.scatter_mode:
                    red_ghost_gif = red_ghost_animations[red_ghost.direction]
                else:
                    if time.time() - scatter_mode_start >= scatter_mode_duration - 2:
                       red_ghost_gif = scatter_ghost_animations_blinking[red_ghost.direction] 
                    else:
                        red_ghost_gif = scatter_ghost_animations[red_ghost.direction]
            red_ghost_gif.render(screen, (red_ghost_screen_x - 7, red_ghost_screen_y - 7))

        if not pink_ghost.animate_going_home:
            pink_ghost_rect = pygame.Rect(int(pink_ghost_screen_x), int(pink_ghost_screen_y), cell_size, cell_size)
            if pink_ghost.direction in ("left", "right"):
                if not pink_ghost.scatter_mode:
                    pink_ghost_gif = pink_ghost_animations[pink_ghost.direction]
                else:
                    if time.time() - scatter_mode_start >= scatter_mode_duration - 2:
                       pink_ghost_gif = scatter_ghost_animations_blinking[pink_ghost.direction] 
                    else:
                        pink_ghost_gif = scatter_ghost_animations[pink_ghost.direction]
            pink_ghost_gif.render(screen, (pink_ghost_screen_x - 7, pink_ghost_screen_y - 7))
            
        if not orange_ghost.animate_going_home:
            orange_ghost_rect = pygame.Rect(int(orange_ghost_screen_x), int(orange_ghost_screen_y), cell_size, cell_size)
            if orange_ghost.direction in ("left", "right"):
                if not orange_ghost.scatter_mode:
                    orange_ghost_gif = orange_ghost_animations[orange_ghost.direction]
                else:
                    if time.time() - scatter_mode_start >= scatter_mode_duration - 2:
                       orange_ghost_gif = scatter_ghost_animations_blinking[orange_ghost.direction] 
                    else:
                        orange_ghost_gif = scatter_ghost_animations[orange_ghost.direction]
            orange_ghost_gif.render(screen, (orange_ghost_screen_x - 7, orange_ghost_screen_y - 7))

        if not blue_ghost.animate_going_home:
            blue_ghost_rect = pygame.Rect(int(blue_ghost_screen_x), int(blue_ghost_screen_y), cell_size, cell_size)
            if blue_ghost.direction in ("left", "right"):
                if not blue_ghost.scatter_mode:
                    blue_ghost_gif = blue_ghost_animations[blue_ghost.direction]
                else:
                    if time.time() - scatter_mode_start >= scatter_mode_duration - 2:
                       blue_ghost_gif = scatter_ghost_animations_blinking[blue_ghost.direction]
                    else: 
                        blue_ghost_gif = scatter_ghost_animations[blue_ghost.direction]
            blue_ghost_gif.render(screen, (blue_ghost_screen_x - 7, blue_ghost_screen_y - 7))
            
        # Detectar colisiones entre Pacman y cada fantasma
        if pacman_rect.colliderect(red_ghost_rect):
            if red_ghost.scatter_mode:
                ghost_eating_sound.play()
                ghost_captured += 1
                player.points += 200 * ghost_captured
                red_ghost.animate_going_home = True
                red_ghost.path = []
            else:
                player_eaten = True
        if pacman_rect.colliderect(pink_ghost_rect):
            if pink_ghost.scatter_mode:
                ghost_captured += 1
                player.points += 200 * ghost_captured
                pink_ghost.animate_going_home = True
                pink_ghost.path = []
            else:
                player_eaten = True
        if pacman_rect.colliderect(orange_ghost_rect):
            if orange_ghost.scatter_mode:
                ghost_captured += 1
                player.points += 200 * ghost_captured
                orange_ghost.animate_going_home = True
                orange_ghost.path = []
            else:
                player_eaten = True
        if pacman_rect.colliderect(blue_ghost_rect):
            if blue_ghost.scatter_mode:
                ghost_captured += 1
                player.points += 200 * ghost_captured
                blue_ghost.animate_going_home = True
                blue_ghost.path = []
            else:
                player_eaten = True
                
        # En el bucle principal, mueve los fantasmas a la casa si están en modo "comido"
        if red_ghost.animate_going_home:
            move_ghost_to_house(red_ghost, red_ghost_house_position, ghost_eaten_gif)
            ghost_eaten_sound.play()
        if pink_ghost.animate_going_home:
            move_ghost_to_house(pink_ghost, pink_ghost_house_position, ghost_eaten_gif)
            ghost_eaten_sound.play()
        if orange_ghost.animate_going_home:
            move_ghost_to_house(orange_ghost, orange_ghost_house_position, ghost_eaten_gif)
            ghost_eaten_sound.play()
        if blue_ghost.animate_going_home:
            move_ghost_to_house(blue_ghost, blue_ghost_house_position, ghost_eaten_gif)
            ghost_eaten_sound.play()

        draw_hud()
        
        pygame.display.flip()
        clock.tick(30)

pygame.quit()
