import pygame
import os
import sys

# 使用虚拟音频设备
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# 初始化 pygame
pygame.init()
pygame.mixer.init()  # Initialize sound system

# Constants
WIDTH, HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.5
PLAYER_SPEED = 5
PINK = (255, 182, 193)
WHITE = (255, 255, 255)
BUTTON_COLOR = (0, 150, 200)
BUTTON_HOVER_COLOR = (0, 200, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
JUMP_HEIGHT = -15  # 调高跳跃高度

# Set up display
# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumpio")


# Load assets
def load_image(name):
    path = os.path.join("assets", name)
    try:
        return pygame.image.load(path)
    except FileNotFoundError:
        print(f"Error: {path} not found.")
        sys.exit()

jumpio_logo = load_image("Jumpio.png")
# Load sounds
background_music = os.path.join("assets", "background.mp3")
jump_sound = pygame.mixer.Sound(os.path.join("assets", "jump.wav"))
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)
# Button function
def draw_button(text, x, y, width, height, hover=False):
    button_color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, (x, y, width, height), border_radius=12)
    button_text = small_font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(button_text, text_rect)

def start_screen():
    running = True
    button_x, button_y = WIDTH // 2 - 100, HEIGHT // 2 + 50
    button_y_offset = 20 
    button_width, button_height = 200, 50

    while running:
        screen.fill(PINK)
        
        # Draw logo
        logo_rect = jumpio_logo.get_rect(center=(WIDTH // 2 , HEIGHT // 2 - 50 ))
        screen.blit(jumpio_logo, logo_rect.topleft)

        
        # Get mouse position and check hover
        button_y = logo_rect.bottom + button_y_offset 
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovering = button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height

        # Draw start button
        draw_button("Start Game", button_x, button_y, button_width, button_height, hover=is_hovering)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and is_hovering:
                running = False  # Exit start screen

        pygame.display.flip()

# Start screen logic before main game loop
start_screen()

# Main game logic (this would be your existing game loop here)
print("Game Started!")  # Replace this with your game's main loop logic

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
        self.image = pygame.transform.scale(image, (90, 90))  # 改成更矮的长方形
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

# 改进后的函数：检测玩家是否跳跃过敌人
def check_jump_over(enemy):
    global score
    # 若玩家处于敌人上方（即玩家的底部高于敌人的顶部）
    if player.rect.bottom < enemy.rect.top:
        # 当玩家的水平中心已经超过敌人的右侧，并且该敌人此次跳跃还未计分，则加一分
        if player.rect.centerx > enemy.rect.right and not getattr(enemy, 'scored', False):
            score += 1
            enemy.scored = True
    else:
        # 当玩家不在敌人上方时，重置计分标记，使后续再次跳跃时能重新计分
        enemy.scored = False

# 重置所有敌人的计分标记（例如在游戏结束后重置）
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

    # 检测与敌人的碰撞（碰到敌人即游戏结束）
    if pygame.sprite.spritecollideany(player, enemies):
        game_over_screen()  # Show game over screen
        player.rect.topleft = (50, HEIGHT - 150)  # Reset player position
        score = 0  # Reset score
        reset_enemy_scoring()  # Reset scoring status
        for enemy in enemies:
            enemy.reset_position()  # Reset enemy positions

    # 检测是否跳跃过敌人
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