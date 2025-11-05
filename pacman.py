import pygame
import sys
import random
import time
import math

pygame.init()

# --- ПАРАМЕТРИ ---
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Ultimate Edition")

# --- КОЛЬОРИ ---
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
LIGHTBLUE = (0, 180, 255)
ORANGE = (255, 165, 0)

GHOST_COLORS = [RED, PINK, LIGHTBLUE, ORANGE, WHITE]

# --- ПАРАМЕТРИ ГРИ ---
speed = 5
GHOST_SPEED = 2 
GHOST_CHASE_DISTANCE = 150 
radius = 18
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)

# --- ПОДІЇ ТА ТАЙМЕРИ ---
# Таймер на 15 секунд для спавну нового привида
NEW_GHOST_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_GHOST_EVENT, 15000) 

# --- СТІНИ ---
walls = [
    # межі
    pygame.Rect(0, 0, 800, 20),
    pygame.Rect(0, 0, 20, 800),
    pygame.Rect(780, 0, 20, 800),
    pygame.Rect(0, 780, 800, 20),

    # основні коридори
    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 100, 20, 200),
    pygame.Rect(680, 100, 20, 200),
    pygame.Rect(200, 200, 400, 20),

    # Середній і нижній регіони
    pygame.Rect(100, 580, 600, 20),
    pygame.Rect(100, 580, 20, 100),
    pygame.Rect(680, 580, 20, 100),
    pygame.Rect(200, 680, 400, 20),

    pygame.Rect(100, 350, 150, 20),
    pygame.Rect(550, 350, 150, 20),
    pygame.Rect(350, 150, 100, 20),
    pygame.Rect(350, 650, 100, 20),

    # НОВІ СТІНИ (сині плюсики)
    pygame.Rect(200, 400, 20, 80),  # Ліва вертикальна
    pygame.Rect(580, 400, 20, 80),  # Права вертикальна
    
    # Центральні стінки, позначені хрестиком, тут відсутні.
]

# Координати зони спавну для привидів (центр екрана)
SPAWN_POINT = (WIDTH // 2, HEIGHT // 2)

# --- ФУНКЦІЇ ---

def draw_pacman(surface, x, y):
    pygame.draw.circle(surface, YELLOW, (x, y), radius)
    # рот
    mouth = [(x, y), (x + radius, y - radius // 3), (x + radius, y + radius // 3)]
    pygame.draw.polygon(surface, BLACK, mouth)
    # очі
    pygame.draw.circle(surface, BLACK, (x - 5, y - 8), 3)

def draw_ghost(surface, x, y, color):
    # Тіло
    pygame.draw.rect(surface, color, (x - radius, y - radius, radius * 2, radius * 2))
    pygame.draw.circle(surface, color, (x, y - radius), radius)
    # Очі
    pygame.draw.circle(surface, WHITE, (x - 6, y - 6), 4)
    pygame.draw.circle(surface, WHITE, (x + 6, y - 6), 4)
    pygame.draw.circle(surface, BLACK, (x - 6, y - 6), 2)
    pygame.draw.circle(surface, BLACK, (x + 6, y - 6), 2)

def create_pellets():
    pellets = []
    for i in range(40, WIDTH - 40, 40):
        for j in range(40, HEIGHT - 40, 40):
            pellet = pygame.Rect(i - 4, j - 4, 8, 8)
            if not any(pellet.colliderect(w) for w in walls):
                pellets.append(pellet)
    return pellets

def spawn_new_ghost(ghosts, color_index):
    """Створює і додає ОДНОГО нового привида до списку."""
    color = GHOST_COLORS[color_index % len(GHOST_COLORS)]
    ghosts.append({
        "x": SPAWN_POINT[0], 
        "y": SPAWN_POINT[1],
        "dir": random.choice([(1,0), (-1,0), (0,1), (0,-1)]),
        "color": color
    })

def spawn_initial_ghosts():
    """Створює лише 1 привид на старті."""
    ghosts = []
    spawn_new_ghost(ghosts, 0) # Початковий привид має перший колір
    return ghosts

def random_free_position():
    while True:
        x = random.randint(40, WIDTH - 40)
        y = random.randint(40, HEIGHT - 40)
        rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        if not any(rect.colliderect(w) for w in walls):
            return x, y

def game_over_screen(message):
    button_restart = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 100, 40)
    button_quit = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 100, 40)

    while True:
        screen.fill(BLACK)
        text = font.render(message, True, YELLOW)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

        pygame.draw.rect(screen, BLUE, button_restart)
        pygame.draw.rect(screen, RED, button_quit)

        restart_text = font.render("Restart", True, WHITE)
        quit_text = font.render("Quit", True, WHITE)

        screen.blit(restart_text, (button_restart.x + 5, button_restart.y + 5))
        screen.blit(quit_text, (button_quit.x + 20, button_quit.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_restart.collidepoint(event.pos):
                    # Повертаємо True для чистого перезапуску
                    return True 
                elif button_quit.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def move_ghost(g, pac_x, pac_y):
    gx, gy = g["x"], g["y"]
    
    # 1. Перевірка дистанції для переслідування
    distance = math.sqrt((pac_x - gx)**2 + (pac_y - gy)**2)
    chase = distance < GHOST_CHASE_DISTANCE

    if chase:
        dx_to_pac = pac_x - gx
        dy_to_pac = pac_y - gy
        
        # Визначаємо пріоритетний напрямок (горизонтальний або вертикальний)
        potential_dir = (0, 0)
        if abs(dx_to_pac) > abs(dy_to_pac):
            potential_dir = (1, 0) if dx_to_pac > 0 else (-1, 0)
        else:
            potential_dir = (0, 1) if dy_to_pac > 0 else (0, -1)

        # Перевіряємо, чи дозволяє стіна рухатись у напрямку переслідування
        new_gx_chase = gx + potential_dir[0] * GHOST_SPEED
        new_gy_chase = gy + potential_dir[1] * GHOST_SPEED
        ghost_rect_chase = pygame.Rect(new_gx_chase - radius, new_gy_chase - radius, radius * 2, radius * 2)
        
        if not any(ghost_rect_chase.colliderect(w) for w in walls):
            # Якщо стін немає, встановлюємо напрямок переслідування
            g["dir"] = potential_dir

    # 2. Рух у поточному напрямку (або новому напрямку переслідування)
    dx, dy = g["dir"]
    new_gx = gx + dx * GHOST_SPEED
    new_gy = gy + dy * GHOST_SPEED
    ghost_rect = pygame.Rect(new_gx - radius, new_gy - radius, radius * 2, radius * 2)

    # 3. Перевірка зіткнення зі стіною (для режиму блукання або якщо не вдалось переслідувати)
    if any(ghost_rect.colliderect(w) for w in walls):
        # Якщо привид вперся в стіну, вибираємо новий випадковий напрямок
        g["dir"] = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        
        # Спроба руху в новому випадковому напрямку (щоб не стояти на місці)
        new_gx = gx + g["dir"][0] * GHOST_SPEED
        new_gy = gy + g["dir"][1] * GHOST_SPEED
    
    # 4. Встановлення нових координат
    g["x"], g["y"] = new_gx, new_gy


def main_game():
    x, y = 60, 60
    direction = None
    pellets = create_pellets()
    total_pellets = len(pellets)
    ghosts = spawn_initial_ghosts() 
    next_ghost_color_index = 1 
    score = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Обробка таймера спавну: 1 привид кожні 15 секунд
            if event.type == NEW_GHOST_EVENT:
                spawn_new_ghost(ghosts, next_ghost_color_index)
                next_ghost_color_index += 1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: direction = (0, -1)
                if event.key == pygame.K_s: direction = (0, 1)
                if event.key == pygame.K_a: direction = (-1, 0)
                if event.key == pygame.K_d: direction = (1, 0)

        # Рух Pac-Man
        if direction:
            new_x = x + direction[0] * speed
            new_y = y + direction[1] * speed
            rect = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
            if not any(rect.colliderect(w) for w in walls):
                x, y = new_x, new_y

        pac_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

        # Збір пелет
        initial_pellets_count = len(pellets)
        pellets = [p for p in pellets if not pac_rect.colliderect(p)]
        score += initial_pellets_count - len(pellets)

        # Перевірка виграшу
        if not pellets:
            if game_over_screen("🎉 YOU WIN! 🎉"):
                return 
            else:
                pygame.quit()
                sys.exit()

        # Рух та перевірка зіткнень привидів
        for g in ghosts:
            move_ghost(g, x, y) 
            
            # Використовуємо округлені координати для Rect
            ghost_rect = pygame.Rect(int(g["x"]) - radius, int(g["y"]) - radius, radius * 2, radius * 2) 
            if pac_rect.colliderect(ghost_rect):
                if game_over_screen("💀 GAME OVER 💀"):
                    return 
                else:
                    pygame.quit()
                    sys.exit()

        # Малювання
        screen.fill(BLACK)
        for w in walls:
            pygame.draw.rect(screen, BLUE, w)
        for p in pellets:
            pygame.draw.circle(screen, YELLOW, p.center, 4)
        for g in ghosts:
            draw_ghost(screen, int(g["x"]), int(g["y"]), g["color"])
        draw_pacman(screen, int(x), int(y))
        score_text = font.render(f"Score: {score}/{total_pellets}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

# --- ЗАПУСК ---
if __name__ == '__main__':
    while True:
        # Цикл для чистого перезапуску гри
        main_game()