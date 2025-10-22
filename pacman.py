import pygame
import sys
import random
import time

pygame.init()

# --- Параметри ---
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Fun Edition")

# --- Кольори ---
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)

GHOST_COLORS = [RED, BLUE, YELLOW, PINK, WHITE]

# --- Ігрові параметри ---
speed = 5
radius = 18
score = 0
last_spawn_time = time.time()
spawn_interval = 30  # кожні 30 секунд новий привид

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# --- СТІНИ ---
walls = [
    pygame.Rect(0, 0, 800, 20),
    pygame.Rect(0, 0, 20, 800),
    pygame.Rect(780, 0, 20, 800),
    pygame.Rect(0, 780, 800, 20),

    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 100, 20, 200),
    pygame.Rect(680, 100, 20, 200),
    pygame.Rect(200, 200, 400, 20),

    pygame.Rect(300, 300, 200, 20),
    pygame.Rect(300, 300, 20, 200),
    pygame.Rect(480, 300, 20, 200),
    pygame.Rect(300, 480, 200, 20),

    pygame.Rect(100, 580, 600, 20),
    pygame.Rect(100, 580, 20, 100),
    pygame.Rect(680, 580, 20, 100),
    pygame.Rect(200, 680, 400, 20),

    pygame.Rect(100, 350, 150, 20),
    pygame.Rect(550, 350, 150, 20),
    pygame.Rect(350, 150, 100, 20),
    pygame.Rect(350, 650, 100, 20),

    pygame.Rect(350, 360, 100, 100),  # зона спавну
]

# --- ПЕЛЕТИ ---
pellets = []
for i in range(40, WIDTH - 40, 40):
    for j in range(40, HEIGHT - 40, 40):
        pellet_rect = pygame.Rect(i - 4, j - 4, 8, 8)
        if not any(pellet_rect.colliderect(w) for w in walls):
            pellets.append(pellet_rect)
total_pellets = len(pellets)

# --- PAC-MAN ---
x, y = 60, 60

# --- Привиди ---
ghosts = []

# --- Малювання Pac-Man з обличчям ---
def draw_pacman(surface, x, y):
    pygame.draw.circle(surface, YELLOW, (x, y), radius)
    # рот (маленький трикутник)
    mouth_points = [(x, y), (x + radius, y - radius // 3), (x + radius, y + radius // 3)]
    pygame.draw.polygon(surface, BLACK, mouth_points)
    # очі
    pygame.draw.circle(surface, BLACK, (x - 5, y - 8), 3)

# --- Малювання Привида ---
def draw_ghost(surface, x, y, color):
    pygame.draw.rect(surface, color, (x - radius, y - radius, radius * 2, radius * 2))
    # очі
    pygame.draw.circle(surface, WHITE, (x - 6, y - 6), 4)
    pygame.draw.circle(surface, WHITE, (x + 6, y - 6), 4)
    pygame.draw.circle(surface, BLACK, (x - 6, y - 6), 2)
    pygame.draw.circle(surface, BLACK, (x + 6, y - 6), 2)

# --- Функція спавну нового привида ---
def spawn_ghost():
    color = GHOST_COLORS[len(ghosts) % len(GHOST_COLORS)]
    ghosts.append({
        "x": 400,
        "y": 400,
        "dir": random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
        "color": color
    })

spawn_ghost()  # перший привид одразу

# --- Головний цикл ---
while True:
    # --- Події ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Керування Pac-Man ---
    keys = pygame.key.get_pressed()
    new_x, new_y = x, y
    if keys[pygame.K_a]:
        new_x -= speed
    if keys[pygame.K_d]:
        new_x += speed
    if keys[pygame.K_w]:
        new_y -= speed
    if keys[pygame.K_s]:
        new_y += speed

    pac_rect = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
    if not any(pac_rect.colliderect(w) for w in walls):
        x, y = new_x, new_y

    # --- Збирання пелет ---
    collected = False
    new_pellets = []
    for p in pellets:
        if pac_rect.colliderect(p):
            collected = True
            continue
        new_pellets.append(p)
    if collected:
        score += 1
    pellets = new_pellets

    # --- Спавн нового привида кожні 30 секунд ---
    current_time = time.time()
    if current_time - last_spawn_time > spawn_interval:
        spawn_ghost()
        last_spawn_time = current_time

    # --- Рух привидів ---
    for g in ghosts:
        gx, gy = g["x"], g["y"]
        dx, dy = g["dir"]
        new_gx = gx + dx * 2
        new_gy = gy + dy * 2
        ghost_rect = pygame.Rect(new_gx - radius, new_gy - radius, radius * 2, radius * 2)

        if any(ghost_rect.colliderect(w) for w in walls):
            g["dir"] = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        else:
            g["x"], g["y"] = new_gx, new_gy

        # Перевірка зіткнення з Pac-Man
        if pac_rect.colliderect(ghost_rect):
            screen.fill(BLACK)
            game_over_text = font.render("💀 GAME OVER! 💀", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

    # --- Малювання ---
    screen.fill(BLACK)

    # Стіни
    for w in walls:
        pygame.draw.rect(screen, BLUE, w)

    # Пелети
    for p in pellets:
        pygame.draw.circle(screen, YELLOW, p.center, 4)

    # Привиди
    for g in ghosts:
        draw_ghost(screen, int(g["x"]), int(g["y"]), g["color"])

    # Pac-Man
    draw_pacman(screen, x, y)

    # Рахунок
    score_text = font.render(f"Score: {score}/{total_pellets}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
