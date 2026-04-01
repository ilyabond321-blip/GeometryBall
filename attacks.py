import pygame
import random
import math
import time
from constants import *

attacks = []
atk_cooldown = 2.0
custom_atk_enabled = {
    "laser_h": True, "laser_v": True,
    "blocks": True,  "circles": True,
    "double_laser": True, "spinners": True,
}

def reset_attacks():
    global attacks, atk_cooldown
    attacks.clear()
    atk_cooldown = 2.0

# ── Фабрики атак ──────────────────────────────────────
def mk_laser_h():
    y = random.randint(100, HEIGHT - 100)
    return {"type": "laser_h", "phase": "warn", "timer": 0.0,
            "active_time": 1.2, "data": {"y": y, "thick": sc(22)}}

def mk_laser_v():
    x = random.randint(PANEL_W + 100, WIDTH - 100)
    return {"type": "laser_v", "phase": "warn", "timer": 0.0,
            "active_time": 1.2, "data": {"x": x, "thick": sc(22)}}

def mk_blocks():
    cols = random.sample(range(1, 9), random.randint(4, 6))
    blocks = [{"x": PANEL_W + c * ((WIDTH - PANEL_W) // 10),
               "y": -sc(70), "vy": sc(8), "w": sc(70), "h": sc(70)} for c in cols]
    return {"type": "blocks", "phase": "warn", "timer": 0.0,
            "active_time": 3.5, "data": {"blocks": blocks}}

def mk_circles():
    side = random.choice(["left", "right", "top", "bottom"])
    circs = []
    for i in range(5):
        if side == "left":    cx, cy, vx, vy = PANEL_W-sc(40), sc(120)+i*(HEIGHT//6), sc(6), 0
        elif side == "right": cx, cy, vx, vy = WIDTH+sc(40),  sc(120)+i*(HEIGHT//6), -sc(6), 0
        elif side == "top":   cx, cy, vx, vy = PANEL_W+sc(150)+i*((WIDTH-PANEL_W-300)//5), -sc(40), 0, sc(6)
        else:                 cx, cy, vx, vy = PANEL_W+sc(150)+i*((WIDTH-PANEL_W-300)//5), HEIGHT+sc(40), 0, -sc(6)
        circs.append({"x": float(cx), "y": float(cy), "vx": vx, "vy": vy, "r": sc(28)})
    return {"type": "circles", "phase": "warn", "timer": 0.0,
            "active_time": 4.0, "data": {"side": side, "circs": circs}}

def mk_double_laser():
    """Два лазера одновременно: горизонтальный + вертикальный."""
    y = random.randint(120, HEIGHT - 120)
    x = random.randint(PANEL_W + 120, WIDTH - 120)
    return {"type": "double_laser", "phase": "warn", "timer": 0.0,
            "active_time": 1.4, "data": {"y": y, "x": x, "thick": sc(20)}}

def mk_spinners():
    """Крутящиеся палки в 3 случайных точках экрана."""
    gap_x = (WIDTH - PANEL_W) // 3
    positions = [
        (PANEL_W + gap_x // 2,            HEIGHT // 3),
        (PANEL_W + gap_x // 2,            HEIGHT * 2 // 3),
        (PANEL_W + gap_x + gap_x // 2,    HEIGHT // 2),
        (PANEL_W + gap_x*2 + gap_x // 2,  HEIGHT // 3),
        (PANEL_W + gap_x*2 + gap_x // 2,  HEIGHT * 2 // 3),
    ]
    chosen = random.sample(positions, 3)
    spinners = []
    for (px, py) in chosen:
        speed = random.choice([-2.0, -1.5, 1.5, 2.0])
        spinners.append({
            "cx": px, "cy": py,
            "angle": random.uniform(0, math.pi * 2),
            "speed": speed,
            "length": random.randint(sc(100), sc(150)),
            "thick": sc(14),
        })
    return {"type": "spinners", "phase": "warn", "timer": 0.0,
            "active_time": 5.0, "data": {"spinners": spinners}}

ATK_MAKERS = {
    "laser_h":      mk_laser_h,
    "laser_v":      mk_laser_v,
    "blocks":       mk_blocks,
    "circles":      mk_circles,
    "double_laser": mk_double_laser,
    "spinners":     mk_spinners,
}

# Пул атак для уровня 1 (только новые + лазеры)
LEVEL1_ATK_POOL = ["laser_h", "laser_v", "double_laser", "spinners", "blocks", "circles"]

def spawn_attack(pool=None):
    if pool:
        chosen_key = random.choice(pool)
        attacks.append(ATK_MAKERS[chosen_key]())
    else:
        p = [fn for k, fn in ATK_MAKERS.items() if custom_atk_enabled.get(k, True)]
        if p: attacks.append(random.choice(p)())

def update_attacks(dt, level_start_time, freq=1.0, pool=None):
    global atk_cooldown
    atk_cooldown -= dt
    elapsed = time.time() - level_start_time
    interval = max(1.5, (5.0 / freq) - elapsed * 0.04)
    if atk_cooldown <= 0:
        spawn_attack(pool)
        atk_cooldown = interval

    for atk in attacks:
        atk["timer"] += dt
        if atk["phase"] == "warn" and atk["timer"] >= WARN_TIME:
            atk["phase"] = "active"; atk["timer"] = 0.0
        elif atk["phase"] == "active" and atk["timer"] >= atk["active_time"]:
            atk["phase"] = "done"
        if atk["phase"] == "active":
            if atk["type"] == "blocks":
                for b in atk["data"]["blocks"]: b["y"] += b["vy"]
            elif atk["type"] == "circles":
                for c in atk["data"]["circs"]:
                    c["x"] += c["vx"]; c["y"] += c["vy"]
            elif atk["type"] == "spinners":
                for sp in atk["data"]["spinners"]:
                    sp["angle"] += sp["speed"] * dt

    attacks[:] = [a for a in attacks if a["phase"] != "done"]

def _spinner_segments(sp):
    """Возвращает две точки концов палки."""
    cx, cy = sp["cx"], sp["cy"]
    L = sp["length"]
    dx = math.cos(sp["angle"]) * L
    dy = math.sin(sp["angle"]) * L
    return (cx + dx, cy + dy), (cx - dx, cy - dy)

def _point_segment_dist(px, py, ax, ay, bx, by):
    """Расстояние от точки до отрезка."""
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
    return math.hypot(px - (ax + t*dx), py - (ay + t*dy))

def check_hit(bx, by, active_obstacles):
    br = pygame.Rect(bx-BALL_RADIUS, by-BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)
    for obs in active_obstacles:
        r  = obs["rect"]
        bt = obs.get("btype","block")
        if bt == "half":
            r = pygame.Rect(r.x, r.y+r.h//2, r.w, r.h//2)
        if br.colliderect(r): return True
    for atk in attacks:
        if atk["phase"] != "active": continue
        t, d = atk["type"], atk["data"]
        if t == "laser_h":
            if br.colliderect(pygame.Rect(0, d["y"]-d["thick"], WIDTH, d["thick"]*2)): return True
        elif t == "laser_v":
            if br.colliderect(pygame.Rect(d["x"]-d["thick"], 0, d["thick"]*2, HEIGHT)): return True
        elif t == "double_laser":
            if br.colliderect(pygame.Rect(0, d["y"]-d["thick"], WIDTH, d["thick"]*2)): return True
            if br.colliderect(pygame.Rect(d["x"]-d["thick"], 0, d["thick"]*2, HEIGHT)): return True
        elif t == "blocks":
            for b in d["blocks"]:
                if br.colliderect(pygame.Rect(b["x"]-b["w"]//2, int(b["y"]), b["w"], b["h"])): return True
        elif t == "circles":
            for c in d["circs"]:
                if math.hypot(bx-c["x"], by-c["y"]) < BALL_RADIUS + c["r"]: return True
        elif t == "spinners":
            for sp in d["spinners"]:
                p1, p2 = _spinner_segments(sp)
                dist = _point_segment_dist(bx, by, p1[0], p1[1], p2[0], p2[1])
                if dist < BALL_RADIUS + sp["thick"] // 2 + 4: return True
        elif t == "flying_spinner":
            cx2, cy2 = d["cx"], d["cy"]
            L2 = d["length"]; ang = d["angle"]
            p1 = (cx2+math.cos(ang)*L2, cy2+math.sin(ang)*L2)
            p2 = (cx2-math.cos(ang)*L2, cy2-math.sin(ang)*L2)
            if _point_segment_dist(bx,by,p1[0],p1[1],p2[0],p2[1]) < BALL_RADIUS + d["thick"]//2 + 4: return True
    return False

def draw_attacks(screen):
    for atk in attacks:
        t, d, ph = atk["type"], atk["data"], atk["phase"]
        pulse = 0.5 + 0.5 * math.sin(atk["timer"] * 10)

        if ph == "warn":
            wc  = (255, int(50 + 150*pulse), 0)
            alp = int(40 + 80*pulse)

            if t == "laser_h":
                wr = pygame.Rect(PANEL_W, d["y"]-d["thick"], WIDTH-PANEL_W, d["thick"]*2)
                s = pygame.Surface((wr.w, wr.h), pygame.SRCALPHA); s.fill((*ORANGE, alp))
                screen.blit(s, wr.topleft); pygame.draw.rect(screen, wc, wr, 2)
                ex = font_warn.render("!", True, wc)
                screen.blit(ex, (PANEL_W+10, wr.centery-ex.get_height()//2))
                screen.blit(ex, (WIDTH-40,   wr.centery-ex.get_height()//2))

            elif t == "laser_v":
                wr = pygame.Rect(d["x"]-d["thick"], 0, d["thick"]*2, HEIGHT)
                s = pygame.Surface((wr.w, wr.h), pygame.SRCALPHA); s.fill((*ORANGE, alp))
                screen.blit(s, wr.topleft); pygame.draw.rect(screen, wc, wr, 2)
                ex = font_warn.render("!", True, wc)
                screen.blit(ex, (wr.centerx-ex.get_width()//2, 10))
                screen.blit(ex, (wr.centerx-ex.get_width()//2, HEIGHT-55))

            elif t == "double_laser":
                # Горизонтальный
                wr = pygame.Rect(PANEL_W, d["y"]-d["thick"], WIDTH-PANEL_W, d["thick"]*2)
                s = pygame.Surface((wr.w, wr.h), pygame.SRCALPHA); s.fill((*ORANGE, alp))
                screen.blit(s, wr.topleft); pygame.draw.rect(screen, wc, wr, 2)
                # Вертикальный
                wr2 = pygame.Rect(d["x"]-d["thick"], 0, d["thick"]*2, HEIGHT)
                s2 = pygame.Surface((wr2.w, wr2.h), pygame.SRCALPHA); s2.fill((*ORANGE, alp))
                screen.blit(s2, wr2.topleft); pygame.draw.rect(screen, wc, wr2, 2)
                ex = font_warn.render("!", True, wc)
                screen.blit(ex, (PANEL_W+10, wr.centery-ex.get_height()//2))
                screen.blit(ex, (WIDTH-40,   wr.centery-ex.get_height()//2))
                screen.blit(ex, (wr2.centerx-ex.get_width()//2, 10))
                screen.blit(ex, (wr2.centerx-ex.get_width()//2, HEIGHT-55))

            elif t == "blocks":
                for b in d["blocks"]:
                    wr = pygame.Rect(b["x"]-b["w"]//2, 0, b["w"], HEIGHT)
                    s = pygame.Surface((wr.w, wr.h), pygame.SRCALPHA); s.fill((*RED, alp//2))
                    screen.blit(s, wr.topleft); pygame.draw.rect(screen, wc, wr, 2)
                    ex = font_warn.render("!", True, wc)
                    screen.blit(ex, (wr.centerx-ex.get_width()//2, 10))

            elif t == "circles":
                side = d["side"]
                wr = {"left":   pygame.Rect(PANEL_W, 0, 35, HEIGHT),
                      "right":  pygame.Rect(WIDTH-35, 0, 35, HEIGHT),
                      "top":    pygame.Rect(PANEL_W, 0, WIDTH-PANEL_W, 35),
                      "bottom": pygame.Rect(PANEL_W, HEIGHT-35, WIDTH-PANEL_W, 35)}[side]
                s = pygame.Surface((wr.w, wr.h), pygame.SRCALPHA); s.fill((*PURPLE, alp))
                screen.blit(s, wr.topleft); pygame.draw.rect(screen, wc, wr, 2)
                ex = font_warn.render("!", True, wc)
                screen.blit(ex, (wr.centerx-ex.get_width()//2, wr.centery-ex.get_height()//2))

            elif t == "spinners":
                for sp in d["spinners"]:
                    # Мигающий круг на месте будущей палки
                    pygame.draw.circle(screen, wc, (sp["cx"], sp["cy"]), 30, 3)
                    ex = font_warn.render("!", True, wc)
                    screen.blit(ex, (sp["cx"]-ex.get_width()//2, sp["cy"]-ex.get_height()//2))

        elif ph == "active":
            if t == "laser_h":
                y2, thk = d["y"], d["thick"]
                for r in range(thk+16, thk, -5):
                    gs = pygame.Surface((WIDTH, r*2), pygame.SRCALPHA); gs.fill((*CYAN, 15))
                    screen.blit(gs, (0, y2-r))
                pygame.draw.rect(screen, CYAN,  (0, y2-thk, WIDTH, thk*2))
                pygame.draw.rect(screen, WHITE, (0, y2-3, WIDTH, 6))

            elif t == "laser_v":
                x2, thk = d["x"], d["thick"]
                for r in range(thk+16, thk, -5):
                    gs = pygame.Surface((r*2, HEIGHT), pygame.SRCALPHA); gs.fill((*CYAN, 15))
                    screen.blit(gs, (x2-r, 0))
                pygame.draw.rect(screen, CYAN,  (x2-thk, 0, thk*2, HEIGHT))
                pygame.draw.rect(screen, WHITE, (x2-3, 0, sc(6), HEIGHT))

            elif t == "double_laser":
                # Горизонтальный — жёлто-красный
                y2, x2, thk = d["y"], d["x"], d["thick"]
                for r in range(thk+16, thk, -5):
                    gs = pygame.Surface((WIDTH, r*2), pygame.SRCALPHA); gs.fill((*YELLOW, 12))
                    screen.blit(gs, (0, y2-r))
                pygame.draw.rect(screen, YELLOW, (0, y2-thk, WIDTH, thk*2))
                pygame.draw.rect(screen, WHITE,  (0, y2-3,   WIDTH, 6))
                # Вертикальный — жёлто-красный
                for r in range(thk+16, thk, -5):
                    gs = pygame.Surface((r*2, HEIGHT), pygame.SRCALPHA); gs.fill((*YELLOW, 12))
                    screen.blit(gs, (x2-r, 0))
                pygame.draw.rect(screen, YELLOW, (x2-thk, 0, thk*2, HEIGHT))
                pygame.draw.rect(screen, WHITE,  (x2-3,   0, 6,     HEIGHT))

            elif t == "blocks":
                for b in d["blocks"]:
                    r = pygame.Rect(b["x"]-b["w"]//2, int(b["y"]), b["w"], b["h"])
                    pygame.draw.rect(screen, RED, r, border_radius=sc(8))
                    pygame.draw.rect(screen, (255,120,120), r, 2, border_radius=sc(8))
                    pygame.draw.line(screen, WHITE, r.topleft, r.bottomright, 2)
                    pygame.draw.line(screen, WHITE, r.topright, r.bottomleft, 2)

            elif t == "circles":
                for c in d["circs"]:
                    cx2, cy2, cr = int(c["x"]), int(c["y"]), c["r"]
                    for gr in range(cr+10, cr, -4):
                        gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
                        pygame.draw.circle(gs, (*PURPLE, 22), (gr, gr), gr)
                        screen.blit(gs, (cx2-gr, cy2-gr))
                    pygame.draw.circle(screen, PURPLE, (cx2, cy2), cr)
                    pygame.draw.circle(screen, (220,150,255), (cx2, cy2), cr, 2)

            elif t == "spinners":
                for sp in d["spinners"]:
                    p1, p2 = _spinner_segments(sp)
                    cx, cy = sp["cx"], sp["cy"]
                    thk = sp["thick"]
                    # Свечение
                    for glow in range(thk+8, thk, -3):
                        pygame.draw.line(screen, (*ORANGE, 0),
                            (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), glow)
                    # Палка
                    pygame.draw.line(screen, ORANGE,
                        (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), thk)
                    pygame.draw.line(screen, WHITE,
                        (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), 3)
                    # Центр
                    pygame.draw.circle(screen, WHITE, (cx, cy), 8)
                    pygame.draw.circle(screen, ORANGE, (cx, cy), 6)

def draw_flying_spinner(screen, atk):
    """Отрисовка летящей палки — отдельная функция, вызывается из game.py."""
    d   = atk["data"]
    ph  = atk["phase"]
    cx  = int(d["cx"]); cy = int(d["cy"])
    L   = d["length"];  angle = d["angle"]; thk = d["thick"]
    p1  = (int(cx + math.cos(angle)*L), int(cy + math.sin(angle)*L))
    p2  = (int(cx - math.cos(angle)*L), int(cy - math.sin(angle)*L))

    if ph == "warn":
        # Мигающий контур там где палка появится
        pulse = 0.5 + 0.5 * math.sin(atk["timer"] * 10)
        wc = (255, int(50+150*pulse), 0)
        pygame.draw.circle(screen, wc, (cx, cy), sc(22), sc(3))
        t2 = font_warn.render("!", True, wc)
        screen.blit(t2, (cx - t2.get_width()//2, cy - t2.get_height()//2))
        return

    # Активная: рисуем летящую палку с огненным следом
    # Свечение
    for glow in range(thk+10, thk, -4):
        try:
            pygame.draw.line(screen, (*RED, 0), p1, p2, glow)
        except Exception:
            pass
    # Основная палка — красно-оранжевая (отличается от статичных оранжевых)
    pygame.draw.line(screen, (255, 80, 20), p1, p2, thk)
    pygame.draw.line(screen, (255, 200, 100), p1, p2, 3)
    # Центральная точка — белая с огнём
    pygame.draw.circle(screen, (255, 200, 100), (cx, cy), 9)
    pygame.draw.circle(screen, WHITE, (cx, cy), 5)
