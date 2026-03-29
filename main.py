import pygame, sys, os
from constants import *
import game, editor, ui, attacks as atk_module
import level1_runner, level1_script, custom_runner

# Створюємо вікно з можливістю зміни розміру
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
# Віртуальна поверхня, на якій малюємо все (завжди 1080p)
virtual_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

pygame.display.set_caption("Geometry Ball")
clock  = pygame.time.Clock()

pygame.mixer.init()
MUSIC_FILE   = os.path.join(os.path.dirname(__file__), "music_level1.mp3")
music_loaded = os.path.exists(MUSIC_FILE)
if music_loaded:
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(0.75)

def music_play():
    if music_loaded: pygame.mixer.music.play(0)
def music_stop():
    if music_loaded: pygame.mixer.music.stop()

BEAT       = 0.3482
LEVEL1_DUR = level1_script.get_level_end()

CUSTOM_GL  = editor.ED_LEFT
CUSTOM_GR  = editor.ED_RIGHT

state         = STATE_MENU
fullscreen    = False
ed_rects      = {}
lv_ed_btn     = None
playing_level = 1

editor.load_level()

def start_level_1():
    global playing_level
    playing_level = 1
    level1_runner.reset()
    game.reset(game_left=PANEL_W, game_right=BASE_WIDTH)
    music_play()

def start_custom():
    global playing_level
    playing_level = 0
    editor.load_level()
    sx, sy = editor.get_start_pos()
    tl = editor.get_scripted_timeline()
    custom_runner.reset(tl)
    game.reset(start_x=sx, start_y=sy,
               obstacles=editor.get_active_obstacles(),
               game_left=CUSTOM_GL, game_right=CUSTOM_GR)
    music_stop()

def respawn():
    if playing_level == 0:
        start_custom()
    else:
        start_level_1()

while True:
    dt = clock.tick(FPS) / 1000.0
    
    # Отримуємо реальний розмір вікна для масштабування
    curr_w, curr_h = screen.get_size()
    
    # Перераховуємо координати миші під віртуальний екран
    raw_mouse = pygame.mouse.get_pos()
    mouse = (raw_mouse[0] * (BASE_WIDTH / curr_w), raw_mouse[1] * (BASE_HEIGHT / curr_h))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            music_stop(); pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

        if state == STATE_EDITOR:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: state = STATE_LEVELS
                else: editor.handle_keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if editor.handle_click(*mouse, ed_rects):
                        editor.save_level(); start_custom(); state = STATE_CUSTOM
                elif event.button == 3: editor.handle_rightclick(*mouse)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                editor.handle_release(*mouse)

        elif state in (STATE_LEVEL, STATE_CUSTOM, STATE_EXPLODE, STATE_WIN):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music_stop()
                    state = STATE_EDITOR if playing_level == 0 else STATE_LEVELS
                if event.key == pygame.K_r and state == STATE_WIN:
                    game.deaths = 0; respawn()
                    state = STATE_CUSTOM if playing_level == 0 else STATE_LEVEL
                if state in (STATE_LEVEL, STATE_CUSTOM):
                    game.set_direction(event.key)
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == STATE_LEVELS: state = STATE_MENU
                else: music_stop(); pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU and ui.btn_play.collidepoint(mouse):
                    state = STATE_LEVELS
                elif state == STATE_LEVELS:
                    if ui.level_btn(1).collidepoint(mouse):
                        start_level_1(); state = STATE_LEVEL
                    if lv_ed_btn and lv_ed_btn.collidepoint(mouse):
                        music_stop(); state = STATE_EDITOR

    # ── Логика ──
    if state in (STATE_LEVEL, STATE_CUSTOM):
        is_custom = (state == STATE_CUSTOM)
        lvl_dur   = editor.custom_duration if is_custom else LEVEL1_DUR
        runner    = custom_runner if is_custom else level1_runner
        result = game.update(dt, lvl_dur, scripted_runner=runner)
        if result == "dead":  state = STATE_EXPLODE
        elif result == "win": music_stop(); state = STATE_WIN

    elif state == STATE_EXPLODE:
        if game.update_explode(dt):
            respawn()
            state = STATE_CUSTOM if playing_level == 0 else STATE_LEVEL

    # ── Рисование (на virtual_surface) ──
    virtual_surface.fill((0, 0, 0))
    
    if state == STATE_MENU:
        ui.draw_menu(virtual_surface)
    elif state == STATE_LEVELS:
        lv_ed_btn = ui.draw_level_select(virtual_surface)
    elif state == STATE_EDITOR:
        ed_rects = editor.draw(virtual_surface)
    elif state in (STATE_LEVEL, STATE_CUSTOM):
        is_custom = (state == STATE_CUSTOM)
        lvl_dur   = editor.custom_duration if is_custom else LEVEL1_DUR
        runner    = custom_runner if is_custom else level1_runner
        game.draw_level(virtual_surface, lvl_dur, is_custom,
                        editor.ed_objects if is_custom else None,
                        beat_interval=BEAT if not is_custom else None,
                        runner=runner)
    elif state == STATE_EXPLODE:
        game.draw_explode(virtual_surface, 0) # спрощено для віртуалізації
    elif state == STATE_WIN:
        ui.draw_win(virtual_surface, game.deaths)

    # Масштабування та вивід на реальний екран
    scaled_surf = pygame.transform.smoothscale(virtual_surface, (curr_w, curr_h))
    screen.blit(scaled_surf, (0, 0))
    pygame.display.flip()