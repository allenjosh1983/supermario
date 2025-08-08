import pygame
import sys
import math

pygame.init()

# === Screen setup ===
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SideScroller")
clock = pygame.time.Clock()

# === Load and scale backgrounds ===
clouds_full = pygame.image.load("assets/clouds.png").convert_alpha()
clouds_full = pygame.transform.scale(clouds_full, (SCREEN_WIDTH, SCREEN_HEIGHT))

mountains = pygame.image.load("assets/mountains.png").convert_alpha()
mountains = pygame.transform.scale(mountains, (SCREEN_WIDTH, SCREEN_HEIGHT))

# === Crop top part of clouds (350 pixels) for layering above mountains ===
CLOUDS_CROP_HEIGHT = 350
clouds_cropped = pygame.Surface((SCREEN_WIDTH, CLOUDS_CROP_HEIGHT), pygame.SRCALPHA)
clouds_cropped.blit(clouds_full, (0, 0), (0, 0, SCREEN_WIDTH, CLOUDS_CROP_HEIGHT))

def apply_vertical_fade(surface, fade_height):
    """Apply a vertical alpha gradient fade on the bottom fade_height pixels using an alpha mask."""
    width, height = surface.get_size()
    fade_surface = pygame.Surface((width, fade_height), pygame.SRCALPHA)
    for y in range(fade_height):
        alpha = int(255 * (1 - y / fade_height))
        pygame.draw.line(fade_surface, (255, 255, 255, alpha), (0, y), (width, y))
    # Cut the bottom fade_height part of surface
    bottom_part = surface.subsurface(pygame.Rect(0, height - fade_height, width, fade_height))
    # Multiply alpha by fade mask
    bottom_part.blit(fade_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# Apply fade to bottom 100 pixels of clouds_cropped
apply_vertical_fade(clouds_cropped, fade_height=100)

# === Ground layer ===
ground_layer = pygame.image.load("assets/ground.png").convert_alpha()
ground_layer = pygame.transform.scale(ground_layer, (SCREEN_WIDTH, 100))
ground_draw_y = SCREEN_HEIGHT - ground_layer.get_height()
GROUND_SURFACE_OFFSET = 20
ground_surface_y = ground_draw_y + GROUND_SURFACE_OFFSET

# === Player setup ===
player_rect = pygame.Rect(100, 0, 50, 50)
player_rect.bottom = ground_surface_y

# === Scrolling ===
scroll_x = 0
SCROLL_SPEED = 5

# === Parallax scroll ratios ===
MOUNTAIN_SCROLL_RATIO = 0.3

# === Cloud drift variables ===
CLOUD_SCROLL_RATIO = 0.1
CLOUD_DRIFT_SPEED = 20  # pixels per second
cloud_scroll_x = 0

# === Cloud oscillation variables (softened) ===
cloud_wave_time = 0
CLOUD_WAVE_SPEED = 0.5  # slower oscillation (half cycle per second)
CLOUD_WAVE_AMPLITUDE = 4  # smaller vertical movement (4 pixels)

running = True
while running:
    dt = clock.tick(60) / 1000  # seconds elapsed this frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === Input handling ===
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        scroll_x += SCROLL_SPEED
        player_rect.x += 5
    elif keys[pygame.K_LEFT]:
        scroll_x -= SCROLL_SPEED
        player_rect.x -= 5

    # === Update cloud drift independently of player scroll ===
    cloud_scroll_x += CLOUD_DRIFT_SPEED * dt

    # === Update cloud vertical oscillation and alpha pulsing ===
    cloud_wave_time += dt
    cloud_y_offset = CLOUD_WAVE_AMPLITUDE * math.sin(2 * math.pi * CLOUD_WAVE_SPEED * cloud_wave_time)
    cloud_alpha = 204 + 51 * math.sin(2 * math.pi * CLOUD_WAVE_SPEED * cloud_wave_time)  # 204 = 0.8*255, 255 max
    cloud_alpha = max(0, min(255, int(cloud_alpha)))  # clamp between 0-255
    clouds_cropped.set_alpha(cloud_alpha)

    # === Clear screen with sky blue ===
    screen.fill((135, 206, 235))

    # === Draw mountains with parallax scrolling ===
    mountain_width = mountains.get_width()
    mountain_offset = scroll_x * MOUNTAIN_SCROLL_RATIO
    x_rel_mountain = mountain_offset % mountain_width
    screen.blit(mountains, (-x_rel_mountain, 0))
    screen.blit(mountains, (-x_rel_mountain + mountain_width, 0))

    # === Draw cropped clouds with fade drifting and soft oscillation ===
    cloud_width = clouds_cropped.get_width()
    x_rel_cloud = cloud_scroll_x % cloud_width
    screen.blit(clouds_cropped, (-x_rel_cloud, cloud_y_offset))
    screen.blit(clouds_cropped, (-x_rel_cloud + cloud_width, cloud_y_offset))

    # === Draw ground ===
    ground_width = ground_layer.get_width()
    ground_offset = scroll_x % ground_width
    screen.blit(ground_layer, (-ground_offset, ground_draw_y))
    screen.blit(ground_layer, (-ground_offset + ground_width, ground_draw_y))

    # === Draw player ===
    pygame.draw.rect(screen, (255, 0, 0), player_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
