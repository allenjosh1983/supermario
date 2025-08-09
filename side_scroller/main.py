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
    width, height = surface.get_size()
    fade_surface = pygame.Surface((width, fade_height), pygame.SRCALPHA)
    for y in range(fade_height):
        alpha = int(255 * (1 - y / fade_height))
        pygame.draw.line(fade_surface, (255, 255, 255, alpha), (0, y), (width, y))
    bottom_part = surface.subsurface(pygame.Rect(0, height - fade_height, width, fade_height))
    bottom_part.blit(fade_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

apply_vertical_fade(clouds_cropped, fade_height=100)

# === Ground layer ===
ground_layer = pygame.image.load("assets/ground.png").convert_alpha()
ground_layer = pygame.transform.scale(ground_layer, (SCREEN_WIDTH, 100))
ground_draw_y = SCREEN_HEIGHT - ground_layer.get_height()
GROUND_SURFACE_OFFSET = 20
ground_surface_y = ground_draw_y + GROUND_SURFACE_OFFSET

# === Player setup ===
player_rect = pygame.Rect(100, 0, 50, 50)
velocity_y = 0
GRAVITY = 1500
JUMP_VELOCITY = -600

# Track player's position in world coordinates
player_world_x = 100  # start near beginning of level
player_rect.bottom = ground_surface_y

# === Level and scrolling setup ===
LEVEL_WIDTH = 2400  # total level width in pixels (3x screen width)
scroll_x = 0
SCROLL_SPEED = 5

LEFT_BOUNDARY = SCREEN_WIDTH * 0.4
RIGHT_BOUNDARY = SCREEN_WIDTH * 0.6

# === Define platforms across the level ===
platforms = [
    pygame.Rect(300, ground_surface_y - 100, 150, 20),
    pygame.Rect(700, ground_surface_y - 150, 200, 20),
    pygame.Rect(1200, ground_surface_y - 120, 180, 20),
    pygame.Rect(1800, ground_surface_y - 200, 220, 20),
    pygame.Rect(2350, ground_surface_y - 100, 160, 20),  # goal platform near right edge
]

# === Parallax scroll ratios ===
MOUNTAIN_SCROLL_RATIO = 0.3

# === Cloud drift variables ===
CLOUD_SCROLL_RATIO = 0.1
CLOUD_DRIFT_SPEED = 20
cloud_scroll_x = 0

# === Cloud oscillation variables ===
cloud_wave_time = 0
CLOUD_WAVE_SPEED = 0.5
CLOUD_WAVE_AMPLITUDE = 4

# Game success flag
level_complete = False

# Double jump tracking and jump pressed flag
jump_count = 0
jump_pressed = False

running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Horizontal movement using world x
    move_speed = SCROLL_SPEED
    if keys[pygame.K_RIGHT]:
        player_world_x += move_speed
    if keys[pygame.K_LEFT]:
        player_world_x -= move_speed

    # Clamp player_world_x to level bounds
    player_world_x = max(0, min(player_world_x, LEVEL_WIDTH - player_rect.width))

    # Update scroll_x to keep player within screen boundaries
    if player_world_x - scroll_x < LEFT_BOUNDARY:
        scroll_x = max(0, player_world_x - LEFT_BOUNDARY)
    elif player_world_x - scroll_x > RIGHT_BOUNDARY:
        scroll_x = min(player_world_x - RIGHT_BOUNDARY, LEVEL_WIDTH - SCREEN_WIDTH)

    # Update player's screen x position
    player_rect.x = player_world_x - scroll_x

    # Collision detection flag: player is on ground or platform
    player_on_ground_or_platform = False

    # Apply gravity before vertical movement
    velocity_y += GRAVITY * dt
    player_rect.y += velocity_y * dt

    # Collision with platforms
    collision_tolerance = 10
    for platform in platforms:
        platform_screen_rect = platform.copy()
        platform_screen_rect.x -= scroll_x

        if player_rect.colliderect(platform_screen_rect) and velocity_y >= 0:
            if (player_rect.bottom - velocity_y * dt) <= (platform_screen_rect.top + collision_tolerance):
                player_rect.bottom = platform_screen_rect.top
                velocity_y = 0
                player_on_ground_or_platform = True
                jump_count = 0  # reset jump count on landing
                break

    # Collision with ground if not on platform
    if not player_on_ground_or_platform:
        if player_rect.bottom > ground_surface_y:
            player_rect.bottom = ground_surface_y
            velocity_y = 0
            player_on_ground_or_platform = True
            jump_count = 0  # reset jump count on landing

    # Jumping with double jump support
    if keys[pygame.K_SPACE]:
        if not jump_pressed and jump_count < 2:
            velocity_y = JUMP_VELOCITY
            jump_count += 1
            jump_pressed = True
    else:
        jump_pressed = False

    # Cloud drift independent of player scroll
    cloud_scroll_x += CLOUD_DRIFT_SPEED * dt

    # Cloud oscillation and alpha pulsing
    cloud_wave_time += dt
    cloud_y_offset = CLOUD_WAVE_AMPLITUDE * math.sin(2 * math.pi * CLOUD_WAVE_SPEED * cloud_wave_time)
    cloud_alpha = 204 + 51 * math.sin(2 * math.pi * CLOUD_WAVE_SPEED * cloud_wave_time)
    cloud_alpha = max(0, min(255, int(cloud_alpha)))
    clouds_cropped.set_alpha(cloud_alpha)

    # Clear screen
    screen.fill((135, 206, 235))

    # Draw mountains with parallax
    mountain_width = mountains.get_width()
    mountain_offset = scroll_x * MOUNTAIN_SCROLL_RATIO
    x_rel_mountain = mountain_offset % mountain_width
    screen.blit(mountains, (-x_rel_mountain, 0))
    screen.blit(mountains, (-x_rel_mountain + mountain_width, 0))

    # Draw clouds
    cloud_width = clouds_cropped.get_width()
    x_rel_cloud = cloud_scroll_x % cloud_width
    screen.blit(clouds_cropped, (-x_rel_cloud, cloud_y_offset))
    screen.blit(clouds_cropped, (-x_rel_cloud + cloud_width, cloud_y_offset))

    # Draw ground with scrolling
    ground_width = ground_layer.get_width()
    ground_offset = scroll_x % ground_width
    screen.blit(ground_layer, (-ground_offset, ground_draw_y))
    screen.blit(ground_layer, (-ground_offset + ground_width, ground_draw_y))

    # Detect if player is standing on final platform (using world coords)
    goal_platform = platforms[-1]
    player_on_goal_platform = False

    player_bottom_world_y = player_rect.bottom
    platform_top_y = goal_platform.top

    player_right = player_world_x + player_rect.width
    player_left = player_world_x
    platform_right = goal_platform.right
    platform_left = goal_platform.left

    horizontal_overlap = (player_right > platform_left) and (player_left < platform_right)

    if horizontal_overlap:
        if 0 <= (player_bottom_world_y - platform_top_y) <= 15:
            player_on_goal_platform = True
            level_complete = True

    # Draw platforms, changing color if player is on goal platform
    for i, platform in enumerate(platforms):
        draw_rect = platform.copy()
        draw_rect.x -= scroll_x
        if i == len(platforms) - 1:
            color = (255, 0, 0) if player_on_goal_platform else (255, 215, 0)  # red if standing, gold otherwise
        else:
            color = (0, 128, 0)
        pygame.draw.rect(screen, color, draw_rect)

    # Draw player
    pygame.draw.rect(screen, (255, 0, 0), player_rect)

    # Show success message if level complete
    if level_complete:
        font = pygame.font.SysFont(None, 48)
        text = font.render("Level Complete!", True, (0, 0, 0))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 3))

    pygame.display.flip()

pygame.quit()
sys.exit()
