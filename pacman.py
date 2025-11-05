import pygame
import sys
import random
import time
import math
pygame.mixer.init()
pygame.init()


ghost_spawn_sound = pygame.mixer.Sound("privid.mp3")
win_sound = pygame.mixer.Sound("peremoga.mp3")
lose_sound = pygame.mixer.Sound("lose.mp3")


WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Ultimate Edition")


BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)
LIGHTBLUE = (0, 180, 255)
ORANGE = (255, 165, 0)

GHOST_COLORS = [RED, PINK, LIGHTBLUE, ORANGE, WHITE]

speed = 5
GHOST_SPEED = 2
GHOST_CHASE_DISTANCE = 150
radius = 18
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)


NEW_GHOST_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_GHOST_EVENT, 15000)

walls = [
    pygame.Rect(0, 0, 800, 20),
    pygame.Rect(0, 0, 20, 800),
    pygame.Rect(780, 0, 20, 800),
    pygame.Rect(0, 780, 800, 20),

    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 100, 20, 200),
    pygame.Rect(680, 100, 20, 200),
    pygame.Rect(200, 200, 400, 20),

    pygame.Rect(100, 580, 20, 100),
    pygame.Rect(680, 580, 20, 100),
    pygame.Rect(200, 680, 400, 20),

    pygame.Rect(100, 350, 150, 20),
    pygame.Rect(550, 350, 150, 20),
    pygame.Rect(350, 150, 100, 20),
    pygame.Rect(350, 650, 100, 20),

    pygame.Rect(200, 400, 20, 80),
    pygame.Rect(580, 400, 20, 80)
]

SPAWN_POINT = (WIDTH // 2, HEIGHT // 2)

def draw_pacman(surface, x, y):
    pygame.draw.circle(surface, YELLOW, (x, y), radius)
    pygame.draw.polygon(surface, BLACK, [(x, y), (x + radius, y - 6), (x + radius, y + 6)])
    pygame.draw.circle(surface, BLACK, (x - 5, y - 8), 3)

def draw_ghost(surface, x, y, color):
    pygame.draw.rect(surface, color, (x - radius, y - radius, radius * 2, radius * 2))
    pygame.draw.circle(surface, color, (x, y - radius), radius)
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

def spawn_new_ghost(ghosts, index):
    color = GHOST_COLORS[index % len(GHOST_COLORS)]
    ghosts.append({"x": SPAWN_POINT[0], "y": SPAWN_POINT[1], "dir": random.choice([(1,0),(-1,0),(0,1),(0,-1)]), "color": color})
    ghost_spawn_sound.play()

def move_ghost(g, px, py):
    gx, gy = g["x"], g["y"]
    dist = math.dist((gx, gy), (px, py))
    if dist < GHOST_CHASE_DISTANCE:
        g["dir"] = (1 if px > gx else -1, 0) if abs(px-gx) > abs(py-gy) else (0, 1 if py > gy else -1)
    nx, ny = gx + g["dir"][0] * GHOST_SPEED, gy + g["dir"][1] * GHOST_SPEED
    if any(pygame.Rect(nx - radius, ny - radius, radius*2, radius*2).colliderect(w) for w in walls):
        g["dir"] = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    else:
        g["x"], g["y"] = nx, ny

def game_over_screen(message):
    button_restart = pygame.Rect(260, 420, 120, 50)
    button_quit = pygame.Rect(420, 420, 120, 50)

    while True:
        screen.fill(BLACK)
        screen.blit(font.render(message, True, YELLOW), (280, 300))
        pygame.draw.rect(screen, BLUE, button_restart)
        pygame.draw.rect(screen, RED, button_quit)
        screen.blit(font.render("Restart", True, WHITE), (270, 430))
        screen.blit(font.render("Quit", True, WHITE), (455, 430))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_restart.collidepoint(event.pos): return True
                if button_quit.collidepoint(event.pos): pygame.quit(); sys.exit()


def main_game():
    x, y = 60, 60
    pellets = create_pellets()
    total = len(pellets)
    score = 0

    ghosts = []
    spawn_new_ghost(ghosts, 0)
    next_ghost = 1

    direction = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == NEW_GHOST_EVENT:
                spawn_new_ghost(ghosts, next_ghost); next_ghost += 1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: direction = (0,-1)
                if event.key == pygame.K_s: direction = (0,1)
                if event.key == pygame.K_a: direction = (-1,0)
                if event.key == pygame.K_d: direction = (1,0)

        if direction:
            nx, ny = x + direction[0]*speed, y + direction[1]*speed
            if not any(pygame.Rect(nx-radius, ny-radius, radius*2, radius*2).colliderect(w) for w in walls):
                x, y = nx, ny

        pac_rect = pygame.Rect(x-radius, y-radius, radius*2, radius*2)

        before = len(pellets)
        pellets = [p for p in pellets if not pac_rect.colliderect(p)]
        if len(pellets) < before:
            score += 1

        if not pellets:
            win_sound.play()
            pygame.time.delay(600)
            if game_over_screen("🎉 YOU WIN! 🎉"): return

        for g in ghosts:
            move_ghost(g, x, y)
            if pac_rect.colliderect(pygame.Rect(int(g["x"])-radius,int(g["y"])-radius,radius*2,radius*2)):
                lose_sound.play()
                pygame.time.delay(600)
                if game_over_screen("💀 GAME OVER 💀"): return

        screen.fill(BLACK)
        for w in walls: pygame.draw.rect(screen, BLUE, w)
        for p in pellets: pygame.draw.circle(screen, YELLOW, p.center, 4)
        for g in ghosts: draw_ghost(screen, int(g["x"]), int(g["y"]), g["color"])
        draw_pacman(screen, int(x), int(y))
        screen.blit(font.render(f"Score: {score}/{total}", True, WHITE), (10, 10))
        pygame.display.flip()
        clock.tick(60)

while True:
    main_game()

