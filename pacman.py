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

NEW_GHOST_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_GHOST_EVENT, 15000)

# --- СТІНИ (нижню 3-тю стінку прибрано!) ---
walls = [
    pygame.Rect(0, 0, 800, 20),
    pygame.Rect(0, 0, 20, 800),
    pygame.Rect(780, 0, 20, 800),
    pygame.Rect(0, 780, 800, 20),

    pygame.Rect(100, 100, 600, 20),
    pygame.Rect(100, 100, 20, 200),
    pygame.Rect(680, 100, 20, 200),
    pygame.Rect(200, 200, 400, 20),

    # <<< СТІНКА ЗНИЗУ ВИДАЛЕНА >>>
    # pygame.Rect(100, 580, 600, 20),

    pygame.Rect(100, 580, 20, 100),
    pygame.Rect(680, 580, 20, 100),
    pygame.Rect(200, 680, 400, 20),

    pygame.Rect(100, 350, 150, 20),
    pygame.Rect(550, 350, 150, 20),
    pygame.Rect(350, 150, 100, 20),
    pygame.Rect(350, 650, 100, 20),

    pygame.Rect(200, 400, 20, 80),
    pygame.Rect(580, 400, 20, 80),
]

SPAWN_POINT = (WIDTH // 2, HEIGHT // 2)

def draw_pacman(surface, x, y):
    pygame.draw.circle(surface, YELLOW, (x, y), radius)
    mouth = [(x, y), (x + radius, y - radius // 3), (x + radius, y + radius // 3)]
    pygame.draw.polygon(surface, BLACK, mouth)
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

def spawn_new_ghost(ghosts, color_index):
    color = GHOST_COLORS[color_index % len(GHOST_COLORS)]
    ghosts.append({"x": SPAWN_POINT[0], "y": SPAWN_POINT[1], "dir": random.choice([(1,0),(-1,0),(0,1),(0,-1)]), "color": color})

def spawn_initial_ghosts():
    ghosts = []
    spawn_new_ghost(ghosts, 0)
    return ghosts

def game_over_screen(message):
    button_restart = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 100, 40)
    button_quit = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, 100, 40)

    while True:
        screen.fill(BLACK)
        text = font.render(message, True, YELLOW)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

        pygame.draw.rect(screen, BLUE, button_restart)
        pygame.draw.rect(screen, RED, button_quit)
        screen.blit(font.render("Restart", True, WHITE), (button_restart.x + 5, button_restart.y + 5))
        screen.blit(font.render("Quit", True, WHITE), (button_quit.x + 20, button_quit.y + 5))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_restart.collidepoint(event.pos): return True
                if button_quit.collidepoint(event.pos): pygame.quit(); sys.exit()

def move_ghost(g, pac_x, pac_y):
    gx, gy = g["x"], g["y"]
    distance = math.dist((gx,gy),(pac_x,pac_y))
    if distance < GHOST_CHASE_DISTANCE:
        if abs(pac_x-gx) > abs(pac_y-gy):
            g["dir"] = (1,0) if pac_x>gx else (-1,0)
        else:
            g["dir"] = (0,1) if pac_y>gy else (0,-1)

    dx,dy=g["dir"]
    new_gx,new_gy=gx+dx*GHOST_SPEED,gy+dy*GHOST_SPEED
    ghost_rect=pygame.Rect(new_gx-radius,new_gy-radius,radius*2,radius*2)
    if any(ghost_rect.colliderect(w) for w in walls):
        g["dir"]=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
    else:
        g["x"],g["y"]=new_gx,new_gy

def main_game():
    x,y=60,60
    direction=None
    pellets=create_pellets()
    total_pellets=len(pellets)
    ghosts=spawn_initial_ghosts()
    next_color=1
    score=0

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==NEW_GHOST_EVENT:
                spawn_new_ghost(ghosts,next_color); next_color+=1
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_w: direction=(0,-1)
                if event.key==pygame.K_s: direction=(0,1)
                if event.key==pygame.K_a: direction=(-1,0)
                if event.key==pygame.K_d: direction=(1,0)

        if direction:
            new_x,new_y=x+direction[0]*speed,y+direction[1]*speed
            rect=pygame.Rect(new_x-radius,new_y-radius,radius*2,radius*2)
            if not any(rect.colliderect(w) for w in walls): x,y=new_x,new_y

        pac_rect=pygame.Rect(x-radius,y-radius,radius*2,radius*2)
        pellets=[p for p in pellets if not pac_rect.colliderect(p)]
        score=total_pellets-len(pellets)

        if not pellets:
            if game_over_screen("🎉 YOU WIN! 🎉"): return

        for g in ghosts:
            move_ghost(g,x,y)
            if pac_rect.colliderect(pygame.Rect(g["x"]-radius,g["y"]-radius,radius*2,radius*2)):
                if game_over_screen("💀 GAME OVER 💀"): return

        screen.fill(BLACK)
        for w in walls: pygame.draw.rect(screen,BLUE,w)
        for p in pellets: pygame.draw.circle(screen,YELLOW,p.center,4)
        for g in ghosts: draw_ghost(screen,int(g["x"]),int(g["y"]),g["color"])
        draw_pacman(screen,int(x),int(y))
        screen.blit(font.render(f"Score: {score}/{total_pellets}",True,WHITE),(10,10))
        pygame.display.flip()
        clock.tick(60)

if __name__=='__main__':
    while True:
        main_game()
