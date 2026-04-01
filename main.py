import pygame, sys, os
from constants import *
import settings, lang
from lang import T, set_lang

# ── Завантажуємо налаштування до всього іншого ────────
settings.load()
set_lang(settings.get("lang"))

import game, editor, ui, attacks as atk_module
import level1_runner, level1_script, custom_runner

# ── Вікно — повноекранний, розмір монітора ─────────────
screen    = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Geometry Ball")
clock     = pygame.time.Clock()

# ── Музика ─────────────────────────────────────────────
pygame.mixer.init()
MUSIC_FILE   = os.path.join(os.path.dirname(__file__), "music_level1.mp3")
music_loaded = os.path.exists(MUSIC_FILE)
if music_loaded:
    pygame.mixer.music.load(MUSIC_FILE)

def _apply_volumes():
    mv = settings.get("music_vol")
    if music_loaded:
        pygame.mixer.music.set_volume(mv)

_apply_volumes()

def music_play():
    if music_loaded: pygame.mixer.music.play(0)
def music_stop():
    if music_loaded: pygame.mixer.music.stop()

BEAT       = 0.3482
LEVEL1_DUR = level1_script.get_level_end()

# Межі ігрової зони для кастомного рівня (з editor)
CUSTOM_GL  = editor.PANEL_W_ED
CUSTOM_GR  = WIDTH

state         = STATE_MENU
fullscreen    = True
ed_rects      = {}
lv_ed_btn     = None
playing_level = 1

editor.load_level()
ui.settings_screen.sync_from(settings.get)

# ── Функції старту ─────────────────────────────────────
def start_level_1():
    global playing_level
    playing_level = 1
    level1_runner.reset()
    game.reset(game_left=PANEL_W, game_right=WIDTH)
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
        sx, sy = editor.get_start_pos()
        tl = editor.get_scripted_timeline()
        custom_runner.reset(tl)
        game.reset(start_x=sx, start_y=sy,
                   obstacles=editor.get_active_obstacles(),
                   game_left=CUSTOM_GL, game_right=CUSTOM_GR)
    else:
        level1_runner.reset()
        game.reset(game_left=PANEL_W, game_right=WIDTH)
        music_play()

# ══════════════════════════════════════════════════════
while True:
    dt    = clock.tick(FPS) / 1000.0
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            music_stop(); settings.save(); pygame.quit(); sys.exit()

        # F11 — переключення вікно/повноекран
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullscreen = not fullscreen
            screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN) \
                     if fullscreen else \
                     pygame.display.set_mode((min(WIDTH,1280), min(HEIGHT,720)))

        # ── РЕДАКТОР ──────────────────────────────────
        if state == STATE_EDITOR:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = STATE_LEVELS
                else:
                    editor.handle_keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if editor.handle_click(*mouse, ed_rects):
                        editor.save_level(); start_custom(); state = STATE_CUSTOM
                elif event.button == 3:
                    editor.handle_rightclick(*mouse)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                editor.handle_release(*mouse)

        # ── ГРА / ЗАГИБЕЛЬ / ПЕРЕМОГА ─────────────────
        elif state in (STATE_LEVEL, STATE_CUSTOM, STATE_EXPLODE, STATE_WIN):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    music_stop()
                    state = STATE_EDITOR if playing_level==0 else STATE_LEVELS
                if event.key == pygame.K_r and state == STATE_WIN:
                    game.deaths = 0; respawn()
                    state = STATE_CUSTOM if playing_level==0 else STATE_LEVEL
                if state in (STATE_LEVEL, STATE_CUSTOM):
                    game.set_direction(event.key)

        # ── НАЛАШТУВАННЯ ──────────────────────────────
        elif state == STATE_SETTINGS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU
            result = ui.settings_screen.handle_event(event)
            if result == "back":
                state = STATE_MENU
            elif result == "apply":
                ui.settings_screen.sync_to(settings.set)
                settings.save()
                set_lang(settings.get("lang"))
                _apply_volumes()
                state = STATE_MENU

        # ── МЕНЮ / ВИБІР РІВНЯ ────────────────────────
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == STATE_LEVELS: state = STATE_MENU
                else: music_stop(); settings.save(); pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == STATE_MENU:
                    if ui.btn_play.collidepoint(mouse):
                        state = STATE_LEVELS
                    elif ui.btn_settings.collidepoint(mouse):
                        ui.settings_screen.sync_from(settings.get)
                        state = STATE_SETTINGS
                elif state == STATE_LEVELS:
                    if ui.level_btn(1).collidepoint(mouse):
                        start_level_1(); state = STATE_LEVEL
                    if lv_ed_btn and lv_ed_btn.collidepoint(mouse):
                        music_stop(); state = STATE_EDITOR

    # ── Логіка ─────────────────────────────────────────
    if state in (STATE_LEVEL, STATE_CUSTOM):
        is_custom = (state == STATE_CUSTOM)
        lvl_dur   = editor.custom_duration if is_custom else LEVEL1_DUR
        runner    = custom_runner if is_custom else level1_runner

        result = game.update(dt, lvl_dur, scripted_runner=runner)

        if result == "dead":  state = STATE_EXPLODE
        elif result == "win": music_stop(); state = STATE_WIN
        elif is_custom and game.check_finish(editor.ed_objects): state = STATE_WIN

    elif state == STATE_EXPLODE:
        if game.update_explode(dt):
            respawn()
            state = STATE_CUSTOM if playing_level==0 else STATE_LEVEL

    # ── Малювання ──────────────────────────────────────
    if state == STATE_MENU:
        ui.draw_menu(screen)
    elif state == STATE_LEVELS:
        lv_ed_btn = ui.draw_level_select(screen)
    elif state == STATE_EDITOR:
        ed_rects = editor.draw(screen)
    elif state == STATE_SETTINGS:
        ui.settings_screen.draw(screen)
    elif state in (STATE_LEVEL, STATE_CUSTOM):
        is_custom = (state == STATE_CUSTOM)
        lvl_dur   = editor.custom_duration if is_custom else LEVEL1_DUR
        runner    = custom_runner if is_custom else level1_runner
        game.draw_level(screen, lvl_dur, is_custom,
                        editor.ed_objects if is_custom else None,
                        beat_interval=BEAT if not is_custom else None,
                        runner=runner)
    elif state == STATE_EXPLODE:
        is_custom = (playing_level == 0)
        lvl_dur   = editor.custom_duration if is_custom else LEVEL1_DUR
        runner    = custom_runner if is_custom else level1_runner
        game.draw_explode(screen, lvl_dur, runner=runner)
    elif state == STATE_WIN:
        ui.draw_win(screen, game.deaths)

    pygame.display.flip()
