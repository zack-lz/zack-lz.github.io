import pygame
import os
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound system

# Constants
WIDTH, HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_HEIGHT = -15  # 调高跳跃高度

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Game")

# Load assets
def load_image(name):
    path = os.path.join("assets", name)
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"Error: {path} not found.")
        sys.exit()

# Load sounds
background_music = os.path.join("assets", "background.mp3")
jump_sound = pygame.mixer.Sound(os.path.join("assets", "jump.wav"))

# Play background music
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # Loop forever
pygame.mixer.music.set_volume(0.3)

player_img = load_image("mario.png")
background_img = load_image("background.png")
block_img = load_image("block.png")
red_enemy_img = load_image("enemy1.png")
blue_enemy_img = load_image("enemy2.png")

# Game objects
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(player_img, (40, 60))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.velocity_y = 0
        self.on_ground = False

    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Check for collision with platforms
        for block in blocks:
            if self.rect.colliderect(block.rect) and self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.velocity_y = 0
                self.on_ground = True
                break
        else:
            self.on_ground = False

        # Prevent falling through the floor
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.on_ground = True

        # Horizontal movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_HEIGHT
            self.on_ground = False
            jump_sound.play()

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(block_img, (60, 40))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed):
        super().__init__()
        self.image = pygame.transform.scale(image, (80, 80))  # 改成更矮的长方形
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.starting_position = (x, y)  # Store initial position
        self.speed = speed

    def reset_position(self):
        self.rect.topleft = self.starting_position
        self.speed = abs(self.speed)  # Reset speed direction to positive

    def update(self):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed = -self.speed  # Reverse direction

# Initialize game objects
player = Player(50, HEIGHT - 150)
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

blocks = pygame.sprite.Group()
platform_positions = [(200, 300), (400, 250), (600, 200)]
for pos in platform_positions:
    block = Block(*pos)
    blocks.add(block)
    all_sprites.add(block)

# Add enemies
red_enemy = Enemy(500, HEIGHT - 80, red_enemy_img, 2)  # Red enemy adjusted position
blue_enemy = Enemy(700, HEIGHT - 80, blue_enemy_img, 3)  # Blue enemy adjusted position

enemies = pygame.sprite.Group()
enemies.add(red_enemy, blue_enemy)
all_sprites.add(red_enemy, blue_enemy)

# Initialize score
score = 0
high_score = 0
font = pygame.font.Font(None, 36)

# Background scrolling
background_x = 0

# Function to display the game over screen
def game_over_screen():
    global high_score
    if score > high_score:
        high_score = score  # Update high score
    screen.fill((0, 0, 0))  # Black background
    game_over_text = font.render("Game Over", True, (255, 255, 255))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 60))
    screen.blit(high_score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
    screen.blit(restart_text, (WIDTH // 2 - 110, HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False  # Exit the game over screen

# Function to check if the player jumps over the enemy
def check_jump_over(enemy):
    global score
    if player.rect.bottom < enemy.rect.top and player.rect.right > enemy.rect.right and player.rect.left < enemy.rect.right and not hasattr(enemy, 'scored'):
        score += 1  # Increment score
        enemy.scored = True  # Mark enemy as scored to prevent double counting

# Reset scoring status for all enemies
def reset_enemy_scoring():
    for enemy in enemies:
        if hasattr(enemy, 'scored'):
            del enemy.scored

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    # Update all sprites
    all_sprites.update()

    # Check for collisions with enemies
    if pygame.sprite.spritecollideany(player, enemies):
        game_over_screen()  # Show game over screen
        player.rect.topleft = (50, HEIGHT - 150)  # Reset player position
        score = 0  # Reset score
        reset_enemy_scoring()  # Reset scoring status
        for enemy in enemies:
            enemy.reset_position()  # Reset enemy positions

    # Check if player jumps over enemies
    for enemy in enemies:
        check_jump_over(enemy)

    # Update background scrolling
    background_x -= 2
    if background_x <= -WIDTH:
        background_x = 0

    # Draw everything
    screen.blit(pygame.transform.scale(background_img, (WIDTH, HEIGHT)), (background_x, 0))
    screen.blit(pygame.transform.scale(background_img, (WIDTH, HEIGHT)), (background_x + WIDTH, 0))
    all_sprites.draw(screen)

    # Draw score and high score
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
