import pygame
import sys

pygame.init()

# === Screen setup ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SideScroller")
clock = pygame.time.Clock()

# === Background layers (far to near) ===
bg_files = ["sky.png", "clouds.png", "mountains.png"]
scroll_ratios = [0, 0.1, 0.3]  # Parallax scroll speeds

bg_layers = []
for name in bg_files:
    img = pygame.image.load(f"assets/{name}").convert_alpha()
    img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))  # <-- FORCE 800x600
    bg_layers.append(img)

# === Ground layer ===
ground_layer = pygame.image.load("assets/ground.png").convert_alpha()
ground_layer = pygame.transform.scale(ground_layer, (SCREEN_WIDTH, 100))

# Ground is drawn at the bottom of the screen
ground_draw_y = SCREEN_HEIGHT - ground_layer.get_height()  # = 500 if ground is 100px tall

# Adjust player to land visually on top of the grass part of ground
GROUND_SURFACE_OFFSET = 20  # ← Tweak this depending on where the grass line is
ground_surface_y = ground_draw_y + GROUND_SURFACE_OFFSET

# === Player setup ===
player_rect = pygame.Rect(100, 0, 50, 50)
player_rect.bottom = ground_surface_y  # Align player visually on top of ground

# === Scrolling ===
scroll_x = 0
SCROLL_SPEED = 5

# === Game loop ===
running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === Input ===
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        scroll_x += SCROLL_SPEED
        player_rect.x += 5
    elif keys[pygame.K_LEFT]:
        scroll_x -= SCROLL_SPEED
        player_rect.x -= 5

    # === Draw background layers ===
    for img, ratio in zip(bg_layers, scroll_ratios):
        width = img.get_width()
        offset = scroll_x * ratio
        x_rel = offset % width
        screen.blit(img, (-x_rel, 0))
        screen.blit(img, (-x_rel + width, 0))

    # === Draw ground ===
    ground_width = ground_layer.get_width()
    x_ground = scroll_x % ground_width
    screen.blit(ground_layer, (-x_ground, ground_draw_y))
    screen.blit(ground_layer, (-x_ground + ground_width, ground_draw_y))

    # === Draw player ===
    pygame.draw.rect(screen, (255, 0, 0), player_rect)

    # === Debug: Draw line at surface
    pygame.draw.line(screen, (255, 0, 0), (0, ground_surface_y), (SCREEN_WIDTH, ground_surface_y), 2)

    # === Update display ===
    pygame.display.flip()

pygame.quit()
sys.exit()
