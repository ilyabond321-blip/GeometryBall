import pygame
pygame.init()

# Логічні розміри, на які розрахований код
BASE_WIDTH, BASE_HEIGHT = 1920, 1080
# Початкові розміри вікна (можна змінити на 1280x720 для старту)
WIDTH, HEIGHT = 1920, 1080 

FPS = 60
BALL_RADIUS = 28
SPEED = 6
PANEL_W = 240
PANEL_W2 = 300
SAVE_FILE = "my_level.json"
WARN_TIME = 2.0
LEVEL_DURATION = 30
EXPLODE_DUR = 1.2

BG_MENU     = (20, 20, 40)
BG_LEVEL    = (15, 15, 35)
BG_PANEL    = (10, 10, 28)
BALL_COLOR  = (233, 69, 96)
BALL_GLOW   = (255, 100, 130)
TRAIL_COLOR = (100, 30, 50)
YELLOW  = (255, 213, 0)
WHITE   = (255, 255, 255)
GRAY    = (100, 100, 130)
RED     = (220, 50, 50)
ORANGE  = (255, 140, 0)
GREEN   = (50, 200, 80)
CYAN    = (0, 220, 255)
PURPLE  = (180, 60, 255)
BLUE    = (60, 120, 220)
DARK    = (30, 30, 55)

STATE_MENU    = "menu"
STATE_LEVELS  = "levels"
STATE_LEVEL   = "level"
STATE_EXPLODE = "explode"
STATE_WIN     = "win"
STATE_EDITOR  = "editor"
STATE_CUSTOM  = "custom"

font_big  = pygame.font.SysFont("Arial", 100, bold=True)
font_med  = pygame.font.SysFont("Arial", 48,  bold=True)
font_warn = pygame.font.SysFont("Arial", 60,  bold=True)
font_sm   = pygame.font.SysFont("Arial", 28)
font_tiny = pygame.font.SysFont("Arial", 20)
font_ui   = pygame.font.SysFont("Arial", 18,  bold=True)
