"""
Скриптованный runner уровня 1.
Новое: flying_spinner — палка вылетает со стены и летит, крутясь.
Эффекты: тряска, смена фона, красные ограды.
"""
import pygame, math, random
from constants import *
import attacks as atk_module
import level1_script as script

# Для кастомного уровня левая граница = 300 (PANEL_W2)
CUSTOM_GAME_LEFT = 300
CUSTOM_GAME_RIGHT = WIDTH - 6

_atk_idx  = 0   # следующая атака в TIMELINE
_eff_idx  = 0   # следующий эффект в EFFECTS
_pending  = []  # [{atk, fire_at}] — warn→active

# ── Состояние эффектов ────────────────────────────────
shake_timer     = 0.0
shake_intensity = 0
shake_offset    = (0, 0)

bg_color        = list(BG_LEVEL)    # текущий цвет фона (изменяется плавно)
bg_target       = list(BG_LEVEL)
bg_fade_speed   = 0.0               # единиц/сек на канал

barriers_active = False             # красные ограды по краям
BARRIER_W       = 38                # ширина барьера

def reset():
    global _atk_idx, _eff_idx, _pending
    global shake_timer, shake_intensity, shake_offset
    global bg_color, bg_target, bg_fade_speed, barriers_active
    _atk_idx = 0; _eff_idx = 0; _pending = []
    shake_timer = 0; shake_intensity = 0; shake_offset = (0, 0)
    bg_color   = list(BG_LEVEL); bg_target = list(BG_LEVEL); bg_fade_speed = 0.0
    barriers_active = False
    atk_module.reset_attacks()

# ── Построение атаки ──────────────────────────────────
def _build(entry, phase):
    t  = entry["type"]
    GW = WIDTH - PANEL_W

    if t == "laser_h":
        y = int(entry["y"] * HEIGHT)
        return {"type":"laser_h","phase":phase,"timer":0.0,
                "active_time":0.55,"data":{"y":y,"thick":sc(22)},"_eid":id(entry)}

    elif t == "laser_v":
        x = int(PANEL_W + entry["x"] * GW)
        return {"type":"laser_v","phase":phase,"timer":0.0,
                "active_time":0.55,"data":{"x":x,"thick":sc(22)},"_eid":id(entry)}

    elif t == "double_laser":
        y = int(entry["y"] * HEIGHT)
        x = int(PANEL_W + entry["x"] * GW)
        return {"type":"double_laser","phase":phase,"timer":0.0,
                "active_time":0.55,"data":{"y":y,"x":x,"thick":sc(20)},"_eid":id(entry)}

    elif t == "flying_spinner":
        # Палка вылетает со стороны side, летит поперёк экрана, крутится
        side    = entry["side"]
        cy      = int(entry["cy_frac"] * HEIGHT)
        sp_rot  = entry["speed"]         # скорость вращения рад/с
        L       = 120                    # длина
        thick   = 13

        if side == "left":
            cx  = PANEL_W - L            # начинает за левым краем
            vx  = sc(5.5)                    # летит вправо
            vy  = 0.0
        else:
            cx  = WIDTH + L              # начинает за правым краем
            vx  = -sc(5.5)                   # летит влево
            vy  = 0.0

        return {"type":"flying_spinner","phase":phase,"timer":0.0,
                "active_time":5.5,
                "data":{"cx":float(cx),"cy":float(cy),
                        "vx":vx,"vy":vy,
                        "angle":random.uniform(0, math.pi*2),
                        "speed":sp_rot, "length":L, "thick":thick},
                "_eid":id(entry)}

    elif t == "blocks":
        seg = (WIDTH - PANEL_W) // 10
        blocks = [{"x":PANEL_W+c*seg,"y":-sc(80),"vy":sc(9),"w":sc(72),"h":sc(72)} for c in entry["cols"]]
        return {"type":"blocks","phase":phase,"timer":0.0,
                "active_time":3.2,"data":{"blocks":blocks},"_eid":id(entry)}

    elif t == "circles":
        side = entry["side"]; GW2 = WIDTH-PANEL_W; circs = []
        for i in range(5):
            if side=="left":    cx,cy,vx,vy=PANEL_W-50,110+i*(HEIGHT//6),7,0
            elif side=="right": cx,cy,vx,vy=WIDTH+50,110+i*(HEIGHT//6),-7,0
            elif side=="top":   cx,cy,vx,vy=PANEL_W+160+i*((GW2-320)//5),-50,0,7
            else:               cx,cy,vx,vy=PANEL_W+160+i*((GW2-320)//5),HEIGHT+50,0,-7
            circs.append({"x":float(cx),"y":float(cy),"vx":vx,"vy":vy,"r":sc(28)})
        return {"type":"circles","phase":phase,"timer":0.0,
                "active_time":3.8,"data":{"side":side,"circs":circs},"_eid":id(entry)}
    return None

# ── Главный update ────────────────────────────────────
def update(dt, elapsed):
    global _atk_idx, _eff_idx, shake_timer, shake_intensity, shake_offset
    global bg_color, bg_target, bg_fade_speed, barriers_active

    tl = script.get_timeline()
    ef = script.get_effects()
    WARN = 2.0

    # 1. Запускаем warn для атак
    while _atk_idx < len(tl) and elapsed >= tl[_atk_idx][0]:
        warn_t, entry = tl[_atk_idx]
        atk = _build(entry, "warn")
        if atk:
            atk_module.attacks.append(atk)
            _pending.append({"atk": atk, "fire_at": warn_t + WARN})
        _atk_idx += 1

    # 2. Активируем атаки по fire_at
    for pw in _pending[:]:
        if elapsed >= pw["fire_at"]:
            a = pw["atk"]
            if a["phase"] == "warn":
                a["phase"] = "active"; a["timer"] = 0.0
            _pending.remove(pw)

    # 3. Запускаем эффекты
    while _eff_idx < len(ef) and elapsed >= ef[_eff_idx][0]:
        _, eff = ef[_eff_idx]
        et = eff["type"]
        if et == "shake":
            shake_timer     = eff["duration"]
            shake_intensity = eff["intensity"]
        elif et == "bg":
            bg_target    = list(eff["color"])
            total_diff   = max(1, max(abs(bg_target[i]-bg_color[i]) for i in range(3)))
            bg_fade_speed = total_diff / eff["fade_time"]
        elif et == "barriers":
            barriers_active = True
        _eff_idx += 1

    # 4. Обновляем тряску
    if shake_timer > 0:
        shake_timer = max(0, shake_timer - dt)
        si = int(shake_intensity * (shake_timer / max(0.01, shake_timer + 0.01)))
        shake_offset = (random.randint(-si, si), random.randint(-si, si)) if shake_timer > 0 else (0,0)
    else:
        shake_offset = (0, 0)

    # 5. Обновляем цвет фона
    for i in range(3):
        if bg_color[i] != bg_target[i]:
            diff = bg_target[i] - bg_color[i]
            step = bg_fade_speed * dt
            if abs(diff) <= step:
                bg_color[i] = bg_target[i]
            else:
                bg_color[i] += step * (1 if diff > 0 else -1)

    # 6. Обновляем физику атак
    for atk in atk_module.attacks:
        atk["timer"] += dt
        if atk["phase"] == "active" and atk["timer"] >= atk["active_time"]:
            atk["phase"] = "done"
            continue
        if atk["phase"] == "active":
            tp = atk["type"]
            if tp == "blocks":
                for b in atk["data"]["blocks"]: b["y"] += b["vy"]
            elif tp == "circles":
                for c in atk["data"]["circs"]: c["x"]+=c["vx"]; c["y"]+=c["vy"]
            elif tp == "flying_spinner":
                d = atk["data"]
                d["cx"]    += d["vx"]
                d["cy"]    += d["vy"]
                d["angle"] += d["speed"] * dt
                # Удаляем если улетела за экран
                if d["cx"] < PANEL_W - 300 or d["cx"] > WIDTH + 300:
                    atk["phase"] = "done"
            elif tp == "spinners":
                for sp in atk["data"]["spinners"]:
                    sp["angle"] += sp["speed"] * dt

    atk_module.attacks[:] = [a for a in atk_module.attacks if a["phase"] != "done"]

def get_shake():        return shake_offset
def get_bg_color():     return tuple(int(c) for c in bg_color)
def barriers_on():      return barriers_active
def get_barrier_w():    return BARRIER_W
