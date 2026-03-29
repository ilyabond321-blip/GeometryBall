import pygame
import random
import math
import time
from constants import *
import attacks as atk_module

# ── Состояние ─────────────────────────────────────────
bx, by   = WIDTH//2, HEIGHT//2
bdx, bdy = SPEED, 0
trail    = []
deaths   = 0
active_obstacles  = []
level_start_time  = 0.0
particles         = []
explode_timer     = 0.0

stars = [(random.randint(0,WIDTH), random.randint(0,HEIGHT), random.random()) for _ in range(200)]

_game_left  = PANEL_W
_game_right = WIDTH

def reset(start_x=None, start_y=None, obstacles=None, game_left=None, game_right=None):
    global bx, by, bdx, bdy, trail, particles, active_obstacles, level_start_time
    global _game_left, _game_right
    _game_left  = game_left  if game_left  is not None else PANEL_W
    _game_right = game_right if game_right is not None else WIDTH
    bx = start_x if start_x is not None else (_game_left+_game_right)//2
    by = start_y if start_y is not None else HEIGHT//2
    bdx, bdy = SPEED, 0
    trail = []; particles = []
    active_obstacles = obstacles if obstacles is not None else []
    atk_module.reset_attacks()
    level_start_time = time.time()

def get_elapsed():
    return time.time() - level_start_time

# ── Обновление ────────────────────────────────────────
def update(dt, lvl_dur, freq=1.0, pool=None, scripted_runner=None):
    global bx, by, bdx, bdy

    bx += bdx; by += bdy

    GL = _game_left; GR = _game_right
    if bx - BALL_RADIUS <= GL:   bx = GL+BALL_RADIUS;  bdx =  abs(bdx)
    elif bx + BALL_RADIUS >= GR:  bx = GR-BALL_RADIUS;  bdx = -abs(bdx)
    if by - BALL_RADIUS <= 0:     by = BALL_RADIUS;      bdy =  abs(bdy)
    elif by + BALL_RADIUS >= HEIGHT: by = HEIGHT-BALL_RADIUS; bdy = -abs(bdy)

    if scripted_runner and scripted_runner.barriers_on():
        bw = scripted_runner.get_barrier_w()
        if bx - BALL_RADIUS <= GL + bw: bx = GL+bw+BALL_RADIUS; bdx = abs(bdx)
        if bx + BALL_RADIUS >= GR - bw: bx = GR-bw-BALL_RADIUS; bdx = -abs(bdx)
        if by - BALL_RADIUS <= bw:      by = bw+BALL_RADIUS;     bdy = abs(bdy)
        if by + BALL_RADIUS >= HEIGHT-bw: by=HEIGHT-bw-BALL_RADIUS; bdy=-abs(bdy)

    if scripted_runner:
        scripted_runner.update(dt, get_elapsed())
    else:
        atk_module.update_attacks(dt, level_start_time, freq, pool=pool)

    if atk_module.check_hit(bx, by, active_obstacles):
        global deaths
        deaths += 1
        spawn_explosion(bx, by)
        global explode_timer
        explode_timer = 0.0
        return "dead"

    trail.append((bx, by))
    if len(trail) > 35: trail.pop(0)

    if time.time() - level_start_time >= lvl_dur:
        return "win"
    return None

def check_finish(ed_objects):
    for o in ed_objects:
        if o["type"] == "finish":
            if math.hypot(bx-(o["x"]+PANEL_W), by-o["y"]) < 36:
                return True
    return False

def update_explode(dt):
    global explode_timer
    explode_timer += dt
    for p in particles:
        p["x"] += p["vx"]; p["y"] += p["vy"]
        p["vy"] += 0.2;    p["vx"] *= 0.97; p["age"] += dt
    return explode_timer >= EXPLODE_DUR

def spawn_explosion(x, y):
    global particles
    particles = []
    cols = [BALL_COLOR, BALL_GLOW, YELLOW, WHITE, ORANGE, (255,80,80)]
    for _ in range(80):
        a = random.uniform(0, 2*math.pi); spd = random.uniform(2, 11)
        particles.append({"x":float(x),"y":float(y),
            "vx":math.cos(a)*spd,"vy":math.sin(a)*spd,
            "size":random.randint(4,14),"lifetime":random.uniform(0.5,1.3),
            "age":0.0,"color":random.choice(cols)})

def set_direction(key):
    global bdx, bdy
    if key == pygame.K_LEFT:    bdx, bdy = -SPEED, 0
    elif key == pygame.K_RIGHT: bdx, bdy =  SPEED, 0
    elif key == pygame.K_UP:    bdx, bdy = 0, -SPEED
    elif key == pygame.K_DOWN:  bdx, bdy = 0,  SPEED

# ── Отрисовка ─────────────────────────────────────────
def draw_stars(screen):
    for sx,sy,br in stars:
        c = int(br*180)
        pygame.draw.circle(screen, (c,c,c+40), (sx,sy), 1)

def draw_grid(screen, ox=None, color=(25,25,50)):
    if ox is None: ox = _game_left
    for gx in range(ox, WIDTH, 80):
        pygame.draw.line(screen, color, (gx,0), (gx,HEIGHT))
    for gy in range(0, HEIGHT, 80):
        pygame.draw.line(screen, color, (ox,gy), (WIDTH,gy))

def draw_ball(screen, x, y):
    for r in range(BALL_RADIUS+16, BALL_RADIUS, -4):
        gs = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*BALL_GLOW,28), (r,r), r)
        screen.blit(gs, (x-r, y-r))
    pygame.draw.circle(screen, BALL_COLOR, (x,y), BALL_RADIUS)
    pygame.draw.circle(screen, BALL_GLOW,  (x,y), BALL_RADIUS, 3)
    pygame.draw.circle(screen, (255,180,190), (x-9,y-9), 8)

def draw_trail(screen):
    for i,(tx2,ty2) in enumerate(trail):
        rad = int(BALL_RADIUS * 0.5 * (i/max(len(trail),1)))
        if rad > 0:
            s = pygame.Surface((rad*2,rad*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*TRAIL_COLOR, int(180*(i/len(trail)))), (rad,rad), rad)
            screen.blit(s, (tx2-rad, ty2-rad))

def draw_particles_fx(screen):
    for p in particles:
        a = max(0.0, 1-p["age"]/p["lifetime"])
        pygame.draw.circle(screen,
            tuple(int(p["color"][i]*a) for i in range(3)),
            (int(p["x"]),int(p["y"])), max(1,int(p["size"]*a)))

def draw_obs(screen):
    for obs in active_obstacles:
        r    = obs["rect"]
        bt   = obs.get("btype","block")
        if bt == "half":
            r = pygame.Rect(r.x, r.y+r.h//2, r.w, r.h//2)
        if bt == "dark":
            pygame.draw.rect(screen, (18,18,18), r, border_radius=4)
            pygame.draw.rect(screen, (70,70,70), r, 2, border_radius=4)
            for ox in range(0, r.w+r.h, 18):
                x1=min(r.x+ox,r.x+r.w-1); y1=r.y if r.x+ox<=r.x+r.w-1 else r.y+(r.x+ox-(r.x+r.w-1))
                x2=r.x if ox<=r.h else r.x+(ox-r.h); y2=min(r.y+ox,r.y+r.h-1)
                pygame.draw.line(screen,(50,50,50),(x1,y1),(x2,y2),1)
        else:
            col = RED if bt=="block" else ORANGE
            bcol= (255,120,120) if bt=="block" else (255,190,80)
            pygame.draw.rect(screen, col, r, border_radius=4)
            pygame.draw.rect(screen, bcol, r, 2, border_radius=4)
            if bt == "block":
                pygame.draw.line(screen, (255,90,90), r.topleft, r.bottomright, 2)
                pygame.draw.line(screen, (255,90,90), r.topright, r.bottomleft, 2)

def draw_barriers(screen, runner):
    """Красные ограды по краям — появляются навсегда после ~66с."""
    bw = runner.get_barrier_w()
    elapsed = get_elapsed()
    # Плавное появление (первые 1.5с после активации)
    barrier_start_t = 66.0
    alpha = min(1.0, max(0.0, (elapsed - barrier_start_t) / 1.5))
    alp = int(alpha * 220)
    if alp <= 0:
        return

    # Пульс угрозы
    pulse = 0.5 + 0.5 * math.sin(elapsed * 6)
    glow_col = (int(180+60*pulse), 20, 20)

    rects = [
        pygame.Rect(PANEL_W, 0,          bw, HEIGHT),   # левый
        pygame.Rect(WIDTH-bw, 0,         bw, HEIGHT),   # правый
        pygame.Rect(PANEL_W, 0,          WIDTH-PANEL_W, bw),   # верхний
        pygame.Rect(PANEL_W, HEIGHT-bw,  WIDTH-PANEL_W, bw),   # нижний
    ]
    for r in rects:
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        s.fill((*glow_col, alp))
        screen.blit(s, r.topleft)
        pygame.draw.rect(screen, (*glow_col, min(255, alp+30)), r, 3)

def draw_hud(screen, lvl_dur, beat_interval=None):
    left = max(0.0, lvl_dur-(time.time()-level_start_time))
    bw2  = int((left/lvl_dur)*(WIDTH-PANEL_W-60))
    pygame.draw.rect(screen, (40,40,70), (PANEL_W+30,18,WIDTH-PANEL_W-60,20), border_radius=10)
    bar_col = GREEN if left>10 else ORANGE if left>5 else RED
    if bw2 > 0:
        pygame.draw.rect(screen, bar_col, (PANEL_W+30,18,bw2,20), border_radius=10)
    t = font_sm.render(f"⏱ {left:.1f} с   💀 {deaths}", True, WHITE)
    screen.blit(t, ((PANEL_W+WIDTH)//2-t.get_width()//2, 46))

    if beat_interval:
        elapsed = time.time() - level_start_time
        beat_phase = (elapsed % beat_interval) / beat_interval
        pulse = max(0.0, 1.0 - beat_phase * 4)
        if pulse > 0:
            rp = int(14 + pulse * 10)
            gs = pygame.Surface((rp*2, rp*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*YELLOW, int(pulse*220)), (rp,rp), rp)
            screen.blit(gs, (PANEL_W+14-rp, 28-rp))
        pygame.draw.circle(screen, YELLOW, (PANEL_W+14, 28), 10, 2)

    hint = font_tiny.render("Стрелки — направление   ESC — меню   F11 — оконный режим", True, GRAY)
    screen.blit(hint, (PANEL_W+20, HEIGHT-30))

def draw_finish_marker(screen, ed_objects):
    for o in ed_objects:
        if o["type"] == "finish":
            pulse = 0.5+0.5*math.sin(time.time()*4)
            fx, fy = o["x"]+PANEL_W, o["y"]
            pygame.draw.circle(screen, CYAN, (fx,fy), int(26+6*pulse), 4)
            ft = font_ui.render("ФИНИШ", True, CYAN)
            screen.blit(ft, (fx-ft.get_width()//2, fy-44))

def _draw_attacks_with_flying(screen):
    """Рисуем все атаки — обычные через attacks.draw_attacks,
       flying_spinner отдельно чтобы не менять attacks.py сложно."""
    # Разделяем: обычные и flying
    normal = [a for a in atk_module.attacks if a["type"] != "flying_spinner"]
    flying = [a for a in atk_module.attacks if a["type"] == "flying_spinner"]

    # Временно подменяем список для draw_attacks
    orig = atk_module.attacks[:]
    atk_module.attacks[:] = normal
    atk_module.draw_attacks(screen)
    atk_module.attacks[:] = orig

    # Рисуем летящие палки
    for atk in flying:
        attacks_mod_draw_flying(screen, atk)

def attacks_mod_draw_flying(screen, atk):
    d   = atk["data"]
    ph  = atk["phase"]
    cx  = int(d["cx"]); cy = int(d["cy"])
    L   = d["length"];  angle = d["angle"]; thk = d["thick"]
    p1  = (int(cx + math.cos(angle)*L), int(cy + math.sin(angle)*L))
    p2  = (int(cx - math.cos(angle)*L), int(cy - math.sin(angle)*L))

    if ph == "warn":
        pulse = 0.5 + 0.5 * math.sin(atk["timer"] * 10)
        wc = (255, int(50+150*pulse), 0)
        pygame.draw.circle(screen, wc, (cx, cy), 22, 3)
        return

    # Огненное свечение
    for glow in range(thk+12, thk, -4):
        s = pygame.Surface((abs(p2[0]-p1[0])+glow*2+4, abs(p2[1]-p1[1])+glow*2+4), pygame.SRCALPHA)
        ox = min(p1[0],p2[0]) - glow - 2
        oy = min(p1[1],p2[1]) - glow - 2
        pygame.draw.line(s, (255,80,20,18),
            (p1[0]-ox, p1[1]-oy), (p2[0]-ox, p2[1]-oy), glow)
        screen.blit(s, (ox, oy))

    pygame.draw.line(screen, (255, 80, 20),  p1, p2, thk)
    pygame.draw.line(screen, (255, 210, 80), p1, p2, 3)
    pygame.draw.circle(screen, (255,210,80), (cx,cy), 9)
    pygame.draw.circle(screen, WHITE,        (cx,cy), 5)

def draw_level(screen, lvl_dur, is_custom=False, ed_objects=None,
               beat_interval=None, runner=None):
    # Цвет фона
    bg = runner.get_bg_color() if runner else BG_LEVEL
    # Тряска
    sx, sy = runner.get_shake() if runner else (0, 0)

    screen.fill(bg)

    # Смещение всего кроме HUD
    if sx or sy:
        tmp = pygame.Surface((WIDTH, HEIGHT))
        tmp.fill(bg)
        _draw_game_content(tmp, lvl_dur, is_custom, ed_objects, beat_interval, runner)
        screen.blit(tmp, (sx, sy))
        # Закрашиваем полоски от тряски
        screen.fill(bg, pygame.Rect(0, 0, sx if sx>0 else 0, HEIGHT))
        screen.fill(bg, pygame.Rect(WIDTH+sx if sx<0 else WIDTH-1, 0, abs(sx)+1, HEIGHT))
        screen.fill(bg, pygame.Rect(0, 0, WIDTH, sy if sy>0 else 0))
        screen.fill(bg, pygame.Rect(0, HEIGHT+sy if sy<0 else HEIGHT-1, WIDTH, abs(sy)+1))
    else:
        _draw_game_content(screen, lvl_dur, is_custom, ed_objects, beat_interval, runner)

    draw_hud(screen, lvl_dur, beat_interval)

def _draw_game_content(surface, lvl_dur, is_custom, ed_objects, beat_interval, runner):
    bg = runner.get_bg_color() if runner else BG_LEVEL
    # Цвет сетки светлее на красном фоне
    grid_c = (45, 15, 15) if bg[0] > 20 else (25,25,50)
    draw_grid(surface, PANEL_W, grid_c)
    draw_obs(surface)
    if is_custom and ed_objects:
        draw_finish_marker(surface, ed_objects)
    if runner and runner.barriers_on():
        draw_barriers(surface, runner)
    _draw_attacks_with_flying(surface)
    draw_trail(surface)
    draw_ball(surface, bx, by)

def draw_explode(screen, lvl_dur, runner=None):
    bg = runner.get_bg_color() if runner else BG_LEVEL
    screen.fill(bg)
    draw_grid(screen, PANEL_W)
    draw_obs(screen)
    if runner and runner.barriers_on():
        draw_barriers(screen, runner)
    _draw_attacks_with_flying(screen)
    draw_particles_fx(screen)
    if int(explode_timer*4) % 2 == 0:
        t = font_med.render("💀  УМЕР!", True, RED)
        screen.blit(t, (WIDTH//2-t.get_width()//2, HEIGHT//2-30))
    draw_hud(screen, lvl_dur)
