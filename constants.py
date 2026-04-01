import pygame
pygame.init()

# ── Розмір монітора — підлаштовуємось автоматично ─────
_info        = pygame.display.Info()
_SW, _SH     = _info.current_w, _info.current_h

# Базова роздільна здатність (для масштабування констант)
_BASE_W, _BASE_H = 1920, 1080

WIDTH  = _SW
HEIGHT = _SH

# Масштабний коефіцієнт (відносно бази 1080p)
SX = WIDTH  / _BASE_W
SY = HEIGHT / _BASE_H
S  = min(SX, SY)   # рівномірний масштаб

def sc(v):
    """Масштабує значення відносно базової роздільної здатності."""
    return max(1, int(v * S))

FPS         = 60
BALL_RADIUS = sc(28)
SPEED       = max(3, int(6 * S))
SAVE_FILE   = "my_level.json"
WARN_TIME   = 2.0
EXPLODE_DUR = 1.2

# Панелі — масштабовані
PANEL_W  = sc(240)
PANEL_W2 = sc(300)

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

STATE_MENU     = "menu"
STATE_LEVELS   = "levels"
STATE_LEVEL    = "level"
STATE_EXPLODE  = "explode"
STATE_WIN      = "win"
STATE_EDITOR   = "editor"
STATE_CUSTOM   = "custom"
STATE_SETTINGS = "settings"

# ── Шрифти — масштабовані ─────────────────────────────
def _f(name, size, bold=False):
    # Пробуємо шрифти що підтримують кирилицю
    for fname in [name, "DejaVu Sans", "FreeSans", "Liberation Sans", "Arial Unicode MS", None]:
        try:
            if fname:
                return pygame.font.SysFont(fname, sc(size), bold=bold)
            else:
                return pygame.font.Font(None, sc(size))
        except Exception:
            continue
    return pygame.font.Font(None, sc(size))

font_big  = _f("Arial", 100, bold=True)
font_med  = _f("Arial", 48,  bold=True)
font_warn = _f("Arial", 60,  bold=True)
font_sm   = _f("Arial", 28)
font_tiny = _f("Arial", 20)
font_ui   = _f("Arial", 18,  bold=True)
