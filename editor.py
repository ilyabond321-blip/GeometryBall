"""
Редактор уровней — Geometry Ball
Вкладки: БЛОКИ | АТАКИ | ДЕКОР(TODO) | ТРИГГЕРЫ(TODO)
Зум: колёсико мыши или кнопки +/-
Контроль атак: позиция, тип, сторона
"""
import pygame, math, json, os, copy
from constants import *
from lang import T
import attacks as atk_module

# ═══════════════════════════════════════════════════════
#  КОНСТАНТЫ
# ═══════════════════════════════════════════════════════
PANEL_W_ED  = sc(300)          # ширина левой панели
ED_L0       = PANEL_W_ED   # базовая левая граница игровой зоны (без зума)
ED_R0       = WIDTH        # базовая правая граница
ED_T0       = 0
ED_B0       = HEIGHT

GRID_BASE   = sc(40)           # базовый шаг сетки в мировых координатах

BLOCK_TYPES = ("block", "half", "dark")
BLOCK_STYLE = {
    "block": {"fill":(155,28,28),  "border":(255,110,110), "cross":True,  "hatch":False, "label":T("block")},
    "half":  {"fill":(155,85,15),  "border":(255,185,75),  "cross":False, "hatch":False, "label":"Полублок"},
    "dark":  {"fill":(14,14,14),   "border":(65,65,65),    "cross":False, "hatch":True,  "label":"Тёмный"},
}

ATK_TYPES = ["laser_h","laser_v","double_laser","flying_spinner","blocks","circles"]
ATK_LABEL = {
    "laser_h":        T("laser_h"),
    "laser_v":        T("laser_v"),
    "double_laser":   "2 Лазера",
    "flying_spinner": "Палка",
    "blocks":         T("blocks"),
    "circles":        "Круги",
}
ATK_COL = {
    "laser_h":        (0,170,210),
    "laser_v":        (0,150,190),
    "double_laser":   (20,110,230),
    "flying_spinner": (230,110,0),
    "blocks":         (210,80,0),
    "circles":        (170,0,210),
}

TABS = ["БЛОКИ", "АТАКИ"]   # ДЕКОР и ТРИГГЕРЫ — потом
TAB_LOCKED = {"БЛОКИ":False,"АТАКИ":False}

# ═══════════════════════════════════════════════════════
#  СОСТОЯНИЕ
# ═══════════════════════════════════════════════════════
# Вкладка
active_tab      = "БЛОКИ"

# Инструмент
ed_tool         = "block"     # "block"/"half"/"dark"/"start"/"finish"/"erase"

# Зум / камера
zoom            = 1.0         # 0.5 .. 3.0
cam_x           = 0.0         # смещение камеры в мировых координатах
cam_y           = 0.0

# Объекты уровня
ed_objects      = []          # [{type, rect}] или [{type, x, y}]
ed_attacks      = []          # [{time, atk_type, params...}]

# Состояние редактирования
ed_dragging     = False
ed_drag_start   = (0, 0)
ed_drag_type    = "block"
ed_pan_active   = False
ed_pan_origin   = (0, 0)
ed_cam_origin   = (0.0, 0.0)

# Настройки уровня
custom_duration = 60

# Выбранная атака для редактирования
sel_atk_type    = "laser_h"
sel_atk_idx     = -1          # индекс выбранной атаки в списке (-1 = ничего)
atk_input       = ""
atk_input_focus = False

# ─── Вычисляемые границы ─────────────────────────────
@property
def _ed_left():  return PANEL_W_ED
def ed_left():   return PANEL_W_ED

def game_rect_screen():
    """Прямоугольник игровой зоны на экране."""
    return pygame.Rect(PANEL_W_ED, 0, WIDTH - PANEL_W_ED, HEIGHT)

# ═══════════════════════════════════════════════════════
#  ТРАНСФОРМАЦИИ МИРОВЫЕ ↔ ЭКРАННЫЕ
# ═══════════════════════════════════════════════════════
def world_to_screen(wx, wy):
    """Мировые координаты → экранные (с учётом зума и камеры)."""
    gw = WIDTH - PANEL_W_ED
    gh = HEIGHT
    # центр игровой зоны
    cx = PANEL_W_ED + gw / 2
    cy = gh / 2
    sx = cx + (wx - cam_x - gw/2) * zoom
    sy = cy + (wy - cam_y - gh/2) * zoom
    return sx, sy

def screen_to_world(sx, sy):
    gw = WIDTH - PANEL_W_ED
    gh = HEIGHT
    cx = PANEL_W_ED + gw / 2
    cy = gh / 2
    wx = (sx - cx) / zoom + cam_x + gw/2
    wy = (sy - cy) / zoom + cam_y + gh/2
    return wx, wy

def snap_world(wx, wy=None):
    """Привязка к сетке в мировых координатах."""
    if wy is None:
        return round(wx / GRID_BASE) * GRID_BASE
    return (round(wx / GRID_BASE) * GRID_BASE,
            round(wy / GRID_BASE) * GRID_BASE)

# ═══════════════════════════════════════════════════════
#  СОХРАНЕНИЕ / ЗАГРУЗКА
# ═══════════════════════════════════════════════════════
def save_level():
    obs = []
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r = o["rect"]
            obs.append({"type":o["type"],"x":r.x,"y":r.y,"w":r.w,"h":r.h})
        else:
            obs.append({"type":o["type"],"x":o["x"],"y":o["y"]})
    json.dump({
        "objects":  obs,
        "attacks":  ed_attacks,
        "duration": custom_duration,
        "atk_enabled": atk_module.custom_atk_enabled,
        "atk_freq": 2,
    }, open(SAVE_FILE, "w"))

def load_level():
    global ed_objects, ed_attacks, custom_duration
    if not os.path.exists(SAVE_FILE): return
    data = json.load(open(SAVE_FILE))
    ed_objects = []
    for o in data.get("objects", []):
        bt = o["type"]
        if bt not in BLOCK_TYPES and bt not in ("start","finish"):
            bt = "block"
        if bt in BLOCK_TYPES:
            ed_objects.append({"type":bt,
                                "rect":pygame.Rect(o["x"],o["y"],o["w"],o["h"])})
        else:
            ed_objects.append({"type":bt,"x":o["x"],"y":o["y"]})
    ed_attacks       = data.get("attacks", [])
    custom_duration  = data.get("duration", 60)
    atk_module.custom_atk_enabled = data.get(
        "atk_enabled", atk_module.custom_atk_enabled).copy()

def get_active_obstacles():
    res = []
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r = o["rect"]
            # Мировые → экранные при zoom=1
            res.append({"rect":  pygame.Rect(r.x + PANEL_W_ED, r.y, r.w, r.h),
                        "btype": o["type"]})
    return res

def get_start_pos():
    for o in ed_objects:
        if o["type"] == "start":
            return o["x"] + PANEL_W_ED, o["y"]
    return (PANEL_W_ED + WIDTH) // 2, HEIGHT // 2

def get_scripted_timeline():
    GW = WIDTH - PANEL_W_ED
    tl = []
    for a in sorted(ed_attacks, key=lambda x: x["time"]):
        t_warn = max(0.0, a["time"] - 2.0)
        at     = a["atk_type"]
        if at == "laser_h":
            entry = {"type":"laser_h",  "y": a.get("y_frac", 0.5)}
        elif at == "laser_v":
            entry = {"type":"laser_v",  "x": a.get("x_frac", 0.5)}
        elif at == "double_laser":
            entry = {"type":"double_laser",
                     "y": a.get("y_frac", 0.3), "x": a.get("x_frac", 0.7)}
        elif at == "flying_spinner":
            entry = {"type":"flying_spinner",
                     "side":    a.get("side","left"),
                     "cy_frac": a.get("cy_frac", 0.5),
                     "speed":   a.get("speed", 3.0)}
        elif at == "blocks":
            entry = {"type":"blocks", "cols": a.get("cols",[3,7])}
        elif at == "circles":
            entry = {"type":"circles", "side": a.get("side","left")}
        else:
            continue
        tl.append((t_warn, entry))
    return tl

# ═══════════════════════════════════════════════════════
#  РИСОВАНИЕ БЛОКА
# ═══════════════════════════════════════════════════════
def _draw_block_world(surface, btype, wx, wy, ww, wh, alpha=255):
    """Рисует блок в мировых координатах (с применением зума)."""
    sx, sy = world_to_screen(wx, wy)
    sw     = ww * zoom
    sh     = wh * zoom
    _draw_block_screen(surface, btype, int(sx), int(sy), int(sw), int(sh), alpha)

def _draw_block_screen(surface, btype, rx, ry, rw, rh, alpha=255):
    st = BLOCK_STYLE[btype]
    if btype == "half":
        ry += rh // 2
        rh  = max(1, rh // 2)
    r = pygame.Rect(rx, ry, max(1,rw), max(1,rh))

    if alpha < 255:
        s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        s.fill((*st["fill"], alpha))
        pygame.draw.rect(s, (*st["border"], alpha), (0,0,r.w,r.h), 2, border_radius=sc(4))
        surface.blit(s, r.topleft)
        return

    pygame.draw.rect(surface, st["fill"],   r, border_radius=sc(4))
    pygame.draw.rect(surface, st["border"], r, 2, border_radius=sc(4))
    if st["cross"]:
        pygame.draw.line(surface, (255,90,90), r.topleft,  r.bottomright, 2)
        pygame.draw.line(surface, (255,90,90), r.topright, r.bottomleft,  2)
    if st["hatch"]:
        for ox in range(0, rw+rh, 18):
            x1 = min(rx+ox, rx+rw-1)
            y1 = ry if rx+ox <= rx+rw-1 else ry+(rx+ox-(rx+rw-1))
            x2 = rx if ox <= rh else rx+(ox-rh)
            y2 = min(ry+ox, ry+rh-1)
            pygame.draw.line(surface, (50,50,50), (x1,y1), (x2,y2), 1)

# ═══════════════════════════════════════════════════════
#  СЕТКА
# ═══════════════════════════════════════════════════════
def _draw_grid(surface):
    G  = PANEL_W_ED
    clip = pygame.Rect(G, 0, WIDTH-G, HEIGHT)
    surface.set_clip(clip)

    # шаг сетки в экранных пикселях
    grid_px = GRID_BASE * zoom

    # начало сетки — выравниваем по cam_x/cam_y
    sx0, sy0 = world_to_screen(0, 0)

    x = sx0 % grid_px + G
    while x < WIDTH:
        col = (48,48,95) if abs(x - (sx0 % grid_px + G) - round(4*grid_px)*
                                  round((x-(sx0%grid_px+G))/(4*grid_px+0.001))) < 1 else (28,28,55)
        # каждые 4 клетки жирнее
        is_major = round((x - sx0) / grid_px) % 4 == 0
        c = (50,50,95) if is_major else (28,28,55)
        pygame.draw.line(surface, c, (int(x),0), (int(x),HEIGHT), 2 if is_major else 1)
        x += grid_px

    y = sy0 % grid_px
    while y < HEIGHT:
        is_major = round((y - sy0) / grid_px) % 4 == 0
        c = (50,50,95) if is_major else (28,28,55)
        pygame.draw.line(surface, c, (G, int(y)), (WIDTH, int(y)), 2 if is_major else 1)
        y += grid_px

    surface.set_clip(None)
    pygame.draw.rect(surface, (70,70,150),
                     pygame.Rect(G,0,WIDTH-G,HEIGHT), 2)

# ═══════════════════════════════════════════════════════
#  ВРЕМЕННАЯ ШКАЛА
# ═══════════════════════════════════════════════════════
TLINE_H  = 58
TLINE_Y  = HEIGHT - TLINE_H - 22   # оставляем место для подсказки

def _draw_timeline(surface):
    bx, by = PANEL_W_ED, TLINE_Y
    bw, bh = WIDTH - PANEL_W_ED, TLINE_H

    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    s.fill((8,8,28,210))
    surface.blit(s, (bx, by))
    pygame.draw.rect(surface, (55,55,120), (bx,by,bw,bh), 1)

    if custom_duration > 0:
        step = 5 if custom_duration <= 60 else 10
        for t in range(0, int(custom_duration)+1, step):
            tx = bx + int(t/custom_duration*bw)
            pygame.draw.line(surface,(50,50,95),(tx,by),(tx,by+bh),1)
            lbl = font_tiny.render(f"{t}s",True,(75,75,120))
            surface.blit(lbl,(tx+2,by+2))

    # Атаки
    for i, a in enumerate(ed_attacks):
        if custom_duration <= 0: break
        tx = bx + int(a["time"]/custom_duration*bw)
        c  = ATK_COL.get(a["atk_type"], PURPLE)
        thick = 5 if i == sel_atk_idx else 3
        pygame.draw.line(surface, c, (tx,by+2), (tx,by+bh-2), thick)
        if i == sel_atk_idx:
            pygame.draw.circle(surface, WHITE, (tx, by+bh//2), 6, 2)
        abbr = ATK_LABEL.get(a["atk_type"],"?")[:4]
        lbl  = font_tiny.render(abbr, True, c)
        surface.blit(lbl,(tx+3, by+bh-18))

    hint = font_tiny.render(
        "ЛКМ — добавить атаку   ПКМ — удалить   Клик на линию — выбрать и редактировать",
        True,(65,65,105))
    surface.blit(hint,(bx+6, by+bh+4))

# ═══════════════════════════════════════════════════════
#  ПАНЕЛЬ ВКЛАДОК
# ═══════════════════════════════════════════════════════
def _btn(surf, r, label, active=False, col=None, font=None):
    mx, my = pygame.mouse.get_pos()
    base   = col if col else ((28,75,155) if active else (28,28,58))
    if r.collidepoint(mx,my): base = tuple(min(255,c+38) for c in base)
    pygame.draw.rect(surf, base, r, border_radius=sc(6))
    pygame.draw.rect(surf, (95,155,255) if active else (50,50,105), r, 2, border_radius=sc(6))
    f  = font or font_ui
    t  = f.render(label, True, WHITE)
    surf.blit(t, (r.centerx-t.get_width()//2, r.centery-t.get_height()//2))

def _tiny(surf, r, label, active=False, col=None):
    mx,my = pygame.mouse.get_pos()
    base  = col if col else ((28,75,155) if active else (22,22,48))
    if r.collidepoint(mx,my): base = tuple(min(255,c+35) for c in base)
    pygame.draw.rect(surf, base, r, border_radius=sc(4))
    pygame.draw.rect(surf,(85,85,135) if not active else (95,155,255),r,1,border_radius=sc(4))
    t = font_tiny.render(label, True, WHITE)
    surf.blit(t,(r.centerx-t.get_width()//2, r.centery-t.get_height()//2))

def _draw_tabs(surf, y):
    """Рисует строку вкладок, возвращает dict {name: rect}."""
    PW   = PANEL_W_ED
    tw   = (PW-8) // len(TABS)
    rects = {}
    for i,name in enumerate(TABS):
        r = pygame.Rect(4+i*(tw+2), y, tw, 30)
        locked = name not in ("БЛОКИ","АТАКИ")
        col    = (28,75,155) if (name==active_tab and not locked) else \
                 (18,18,38)  if locked else (22,22,50)
        lbl    = name + (" 🔒" if locked else "")
        _btn(surf, r, lbl, active=(name==active_tab), col=col, font=font_tiny)
        rects[name] = r
    return rects

# ═══════════════════════════════════════════════════════
#  СОДЕРЖИМОЕ ВКЛАДОК
# ═══════════════════════════════════════════════════════
def _draw_tab_blocks(surf, y):
    """Вкладка БЛОКИ: инструменты, зум."""
    PW  = PANEL_W_ED
    rects = {}
    tool_rects = {}

    lbl = font_tiny.render(T("blocks_lbl"), True, GRAY)
    surf.blit(lbl,(PW//2-lbl.get_width()//2,y)); y+=18

    bw3 = (PW-12)//3
    for i, bt in enumerate(["block","half","dark"]):
        r = pygame.Rect(4+i*(bw3+2), y, bw3, 38)
        _btn(surf, r, BLOCK_STYLE[bt]["label"],
             active=(ed_tool==bt),
             col={"block":(110,20,20),"half":(110,60,5),"dark":(18,18,18)}[bt] if ed_tool==bt else None)
        tool_rects[bt] = r
    y += 44

    lbl2 = font_tiny.render("── ПРОЧЕЕ ──", True, GRAY)
    surf.blit(lbl2,(PW//2-lbl2.get_width()//2,y)); y+=18

    for tool, label, col in [
        ("start",  T("start_tool"),  (18,95,38)),
        ("finish", "5 Финиш 🏁", (0,75,95)),
        ("erase",  "6 Стереть",  (50,50,68)),
    ]:
        r = pygame.Rect(4, y, PW-8, 34)
        _btn(surf, r, label, active=(ed_tool==tool),
             col=col if ed_tool==tool else None)
        tool_rects[tool] = r; y += 40
    rects["tools"] = tool_rects

    # Зум
    y += 8
    lbl3 = font_tiny.render("── МАСШТАБ ──", True, GRAY)
    surf.blit(lbl3,(PW//2-lbl3.get_width()//2,y)); y+=18
    zoom_pct = font_ui.render(f"{int(zoom*100)}%", True, WHITE)
    surf.blit(zoom_pct,(PW//2-zoom_pct.get_width()//2,y))
    rz_m = pygame.Rect(4, y, 44, 28); rz_p = pygame.Rect(PW-48,y,44,28)
    _btn(surf,rz_m," − "); _btn(surf,rz_p," + ")
    rects["zoom_minus"] = rz_m; rects["zoom_plus"] = rz_p; y+=34

    rz_r = pygame.Rect(4, y, PW-8, 26)
    _tiny(surf, rz_r, "Сбросить масштаб")
    rects["zoom_reset"] = rz_r; y+=32

    # Подсказка панорамирования
    hint = font_tiny.render("ПКМ — панорама  Колесо — зум", True, (60,60,100))
    surf.blit(hint,(4,y)); y+=18

    return rects, y

def _draw_tab_attacks(surf, y):
    """Вкладка АТАКИ: тип, параметры выбранной атаки, список."""
    global sel_atk_idx
    PW    = PANEL_W_ED
    rects = {}

    lbl = font_tiny.render(T("atk_lbl"), True, GRAY)
    surf.blit(lbl,(PW//2-lbl.get_width()//2,y)); y+=18
    bw2 = (PW-12)//2
    atk_sel = {}
    for i, ak in enumerate(ATK_TYPES):
        r = pygame.Rect(4+(i%2)*(bw2+4), y+(i//2)*32, bw2, 28)
        _tiny(surf, r, ATK_LABEL[ak],
              active=(sel_atk_type==ak),
              col=ATK_COL[ak] if sel_atk_type==ak else None)
        atk_sel[ak] = r
    y += (len(ATK_TYPES)//2)*32 + 8
    rects["atk_sel"] = atk_sel

    # Поле ввода времени
    lbl2 = font_tiny.render("Время (сек):", True, GRAY)
    surf.blit(lbl2,(4,y)); y+=16
    inp_r = pygame.Rect(4, y, PW-58, 26)
    pygame.draw.rect(surf,(30,60,30) if atk_input_focus else (20,20,45),inp_r,border_radius=sc(5))
    pygame.draw.rect(surf,(70,190,70) if atk_input_focus else (50,50,95),inp_r,2,border_radius=sc(5))
    disp = (atk_input+"|") if atk_input_focus else (atk_input or "0.0")
    surf.blit(font_ui.render(disp,True,WHITE),(inp_r.x+5,inp_r.y+4))
    rects["atk_input"] = inp_r
    r_add = pygame.Rect(PW-52, y, 48, 26)
    _btn(surf, r_add, "+Доб.", col=(18,75,18))
    rects["atk_add"] = r_add; y+=32

    # ── Параметры выбранной атаки ──────────────────────
    if 0 <= sel_atk_idx < len(ed_attacks):
        a   = ed_attacks[sel_atk_idx]
        at  = a["atk_type"]
        lbl3 = font_tiny.render(f"── Ред.: {ATK_LABEL[at]} @ {a['time']:.1f}s ──", True, YELLOW)
        surf.blit(lbl3,(4,y)); y+=18

        param_rects = {}
        if at in ("laser_h", "double_laser"):
            y_frac = a.get("y_frac", 0.5)
            txt = font_tiny.render(f"Y: {int(y_frac*100)}%  (верх→низ)", True, GRAY)
            surf.blit(txt,(4,y)); y+=16
            r_yd = pygame.Rect(4,y,40,24); r_yu = pygame.Rect(50,y,40,24)
            r_yc = pygame.Rect(95,y,60,24)
            _tiny(surf,r_yd,"- Y"); _tiny(surf,r_yu,"+ Y")
            _tiny(surf,r_yc,f"{int(y_frac*HEIGHT)}px",col=(40,40,80))
            param_rects["y_down"]=r_yd; param_rects["y_up"]=r_yu; y+=30

        if at in ("laser_v", "double_laser"):
            x_frac = a.get("x_frac", 0.5)
            txt = font_tiny.render(f"X: {int(x_frac*100)}%  (лево→право)", True, GRAY)
            surf.blit(txt,(4,y)); y+=16
            r_xd = pygame.Rect(4,y,40,24); r_xu = pygame.Rect(50,y,40,24)
            _tiny(surf,r_xd,"- X"); _tiny(surf,r_xu,"+ X")
            param_rects["x_down"]=r_xd; param_rects["x_up"]=r_xu; y+=30

        if at == "flying_spinner":
            side = a.get("side","left"); spd = a.get("speed",3.0)
            cy_f = a.get("cy_frac",0.5)
            txt = font_tiny.render(f"Сторона: {side}  Скор:{spd:.1f}", True, GRAY)
            surf.blit(txt,(4,y)); y+=16
            rl = pygame.Rect(4,y,70,24); rr = pygame.Rect(80,y,70,24)
            _tiny(surf,rl,"◀ Лево", active=(side=="left"))
            _tiny(surf,rr,"Право ▶", active=(side=="right"))
            param_rects["side_left"]=rl; param_rects["side_right"]=rr; y+=30

            txt2 = font_tiny.render(f"Y: {int(cy_f*100)}%", True, GRAY)
            surf.blit(txt2,(4,y)); y+=16
            r_sd=pygame.Rect(4,y,40,24); r_su=pygame.Rect(50,y,40,24)
            r_ssd=pygame.Rect(100,y,40,24); r_ssu=pygame.Rect(146,y,40,24)
            _tiny(surf,r_sd,"- Y"); _tiny(surf,r_su,"+ Y")
            _tiny(surf,r_ssd,"- V"); _tiny(surf,r_ssu,"+ V")
            param_rects["cy_down"]=r_sd;param_rects["cy_up"]=r_su
            param_rects["spd_down"]=r_ssd;param_rects["spd_up"]=r_ssu; y+=30

        if at == "blocks":
            cols = a.get("cols",[3,7])
            txt = font_tiny.render(f"Колонки: {cols}", True, GRAY)
            surf.blit(txt,(4,y)); y+=16
            # Кнопки для колонок 1-10
            bw_c = (PW-8)//10
            col_rects = {}
            for ci in range(1,11):
                rc2 = pygame.Rect(4+(ci-1)*bw_c, y, bw_c-1, sc(24))
                _tiny(surf,rc2,str(ci),active=(ci in cols),
                      col=(100,50,0) if ci in cols else None)
                col_rects[ci] = rc2
            param_rects["cols"] = col_rects; y+=30

        if at == "circles":
            side = a.get("side","left")
            txt = font_tiny.render("Откуда летят:", True, GRAY)
            surf.blit(txt,(4,y)); y+=16
            sides = ["left","right","top","bottom"]
            labels = ["◀ Лево","Право ▶","▲ Верх","▼ Низ"]
            side_rects = {}
            bw4 = (PW-8)//2
            for si2,(sd,lb) in enumerate(zip(sides,labels)):
                rs = pygame.Rect(4+(si2%2)*(bw4+4),y+(si2//2)*28,bw4,24)
                _tiny(surf,rs,lb,active=(side==sd))
                side_rects[sd]=rs
            param_rects["circle_side"]=side_rects; y+=(len(sides)//2)*28+4

        rects["params"] = param_rects

    # ── Список атак ────────────────────────────────────
    y += 4
    lbl4 = font_tiny.render("── Список атак ──", True, GRAY)
    surf.blit(lbl4,(4,y)); y+=18
    atk_del = {}
    for i, a in enumerate(sorted(enumerate(ed_attacks),key=lambda x:x[1]["time"])):
        orig_i, av = a
        if y > HEIGHT-200: break
        selected = (orig_i == sel_atk_idx)
        r = pygame.Rect(4, y, PW-38, sc(22))
        c = ATK_COL.get(av["atk_type"],PURPLE)
        bg = (30,30,55) if not selected else (40,60,90)
        pygame.draw.rect(surf,bg,r,border_radius=3)
        pygame.draw.rect(surf,c,r,2 if selected else 1,border_radius=3)
        txt = f"{av['time']:.1f}s  {ATK_LABEL.get(av['atk_type'],'?')[:10]}"
        surf.blit(font_tiny.render(txt,True,c),(r.x+3,r.y+4))
        rd = pygame.Rect(PW-32,y,26,22)
        _tiny(surf,rd,"✕",col=(75,12,12))
        atk_del[orig_i] = rd; y+=26
    rects["atk_del"] = atk_del
    rects["atk_list_bounds"] = (4, y)   # чтобы знать до куда нарисовали

    return rects, y

# ═══════════════════════════════════════════════════════
#  ГЛАВНАЯ ОТРИСОВКА
# ═══════════════════════════════════════════════════════
def draw(screen):
    screen.fill(BG_LEVEL)
    _draw_grid(screen)

    # Клип игровой зоны
    gr = game_rect_screen()
    screen.set_clip(gr)

    # Объекты
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r  = o["rect"]
            sx, sy = world_to_screen(r.x, r.y)
            _draw_block_screen(screen, o["type"],
                               int(sx), int(sy),
                               int(r.w*zoom), int(r.h*zoom))
        elif o["type"] in ("start","finish"):
            sx, sy = world_to_screen(o["x"], o["y"])
            col = GREEN if o["type"]=="start" else CYAN
            r_px = max(8, int(22*zoom))
            pygame.draw.circle(screen, col, (int(sx),int(sy)), r_px)
            pygame.draw.circle(screen, WHITE,(int(sx),int(sy)), r_px, 2)
            lbl = font_ui.render("S" if o["type"]=="start" else "F", True, WHITE)
            screen.blit(lbl,(int(sx)-lbl.get_width()//2, int(sy)-lbl.get_height()//2))

    # Превью
    mx, my = pygame.mouse.get_pos()
    in_game = gr.collidepoint(mx,my) and my < TLINE_Y

    if ed_dragging and ed_drag_type in BLOCK_TYPES:
        wx0,wy0 = ed_drag_start
        wx1,wy1 = snap_world(*screen_to_world(mx,my))
        rwx = min(wx0,wx1); rwy = min(wy0,wy1)
        rww = max(GRID_BASE, abs(wx1-wx0))
        rwh = max(GRID_BASE, abs(wy1-wy0))
        sx,sy = world_to_screen(rwx,rwy)
        _draw_block_screen(screen, ed_drag_type,
                           int(sx),int(sy),int(rww*zoom),int(rwh*zoom), alpha=80)
        dim = font_tiny.render(f"{int(rww//GRID_BASE)}×{int(rwh//GRID_BASE)}", True, WHITE)
        screen.blit(dim,(mx+12,my-18))
    elif in_game:
        wx,wy = snap_world(*screen_to_world(mx,my))
        sx,sy = world_to_screen(wx,wy)
        cz = int(GRID_BASE*zoom)
        if ed_tool in BLOCK_TYPES:
            pygame.draw.rect(screen,(220,220,255),
                             pygame.Rect(int(sx),int(sy),cz,cz),1,border_radius=2)
            _draw_block_screen(screen, ed_tool, int(sx),int(sy), cz, cz, alpha=60)
        elif ed_tool in ("start","finish"):
            col = GREEN if ed_tool=="start" else CYAN
            s2 = pygame.Surface((48,48),pygame.SRCALPHA)
            pygame.draw.circle(s2,(*col,90),(24,24),22)
            screen.blit(s2,(int(sx)-24,int(sy)-24))
        elif ed_tool == "erase":
            pygame.draw.rect(screen,(220,50,50),
                             pygame.Rect(mx-22,my-22,44,44),2,border_radius=sc(4))

    screen.set_clip(None)
    _draw_timeline(screen)

    # Панели
    screen.fill(BG_PANEL, pygame.Rect(0,0,PANEL_W_ED,HEIGHT))
    pygame.draw.line(screen,(60,60,130),(PANEL_W_ED,0),(PANEL_W_ED,HEIGHT),2)

    return _draw_left_panel(screen)

# ═══════════════════════════════════════════════════════
#  ЛЕВАЯ ПАНЕЛЬ
# ═══════════════════════════════════════════════════════
def _draw_left_panel(surf):
    PW = PANEL_W_ED
    y  = 8
    rects = {}

    t = font_med.render("РЕДАКТОР", True, YELLOW)
    surf.blit(t,(PW//2-t.get_width()//2,y)); y+=42

    # Вкладки
    tab_rects = _draw_tabs(surf, y); y+=36
    rects["tabs"] = tab_rects

    # Содержимое вкладки
    if active_tab == "БЛОКИ":
        tab_r, y = _draw_tab_blocks(surf, y)
    elif active_tab == "АТАКИ":
        tab_r, y = _draw_tab_attacks(surf, y)
    else:
        tab_r = {}
        txt = font_tiny.render("Скоро...", True, GRAY)
        surf.blit(txt,(PW//2-txt.get_width()//2, y+20))
        y += 60
    rects.update(tab_r)

    # ── Нижние кнопки (всегда видны) ──────────────────
    y = max(y+8, HEIGHT - 158)
    lbl4 = font_tiny.render(f"Длит.: {custom_duration} сек", True, GRAY)
    surf.blit(lbl4,(4,y)); y+=16
    rm=pygame.Rect(4,y,40,26); rp=pygame.Rect(PW-44,y,40,26)
    tv = font_ui.render(str(custom_duration),True,WHITE)
    surf.blit(tv,(PW//2-tv.get_width()//2,y+3))
    _btn(surf,rm," − "); _btn(surf,rp," + ")
    rects["dur_minus"]=rm; rects["dur_plus"]=rp; y+=34

    half = (PW-12)//2
    rc=pygame.Rect(4,y,half,30); rs=pygame.Rect(PW//2+2,y,half,30)
    _btn(surf,rc,"🗑 Очистить",col=(65,10,10))
    _btn(surf,rs,"💾 Сохранить",col=(10,65,10))
    rects["clear"]=rc; rects["save"]=rs; y+=38

    rplay=pygame.Rect(4,y,PW-8,48)
    hov=rplay.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surf,(38,118,238) if hov else (22,82,182),rplay,border_radius=sc(10))
    pygame.draw.rect(surf,(88,168,255),rplay,3,border_radius=sc(10))
    pt=font_med.render("▶ ИГРАТЬ!",True,WHITE)
    surf.blit(pt,(rplay.centerx-pt.get_width()//2,rplay.centery-pt.get_height()//2))
    rects["play"]=rplay

    et=font_tiny.render(T("esc_back"),True,GRAY)
    surf.blit(et,(PW//2-et.get_width()//2,HEIGHT-18))
    return rects

# ═══════════════════════════════════════════════════════
#  ОБРАБОТКА СОБЫТИЙ
# ═══════════════════════════════════════════════════════
def handle_keydown(event):
    global ed_tool, atk_input, atk_input_focus, active_tab
    if atk_input_focus:
        k=event.key
        if k in (pygame.K_RETURN,pygame.K_ESCAPE): atk_input_focus=False
        elif k==pygame.K_BACKSPACE: atk_input=atk_input[:-1]
        elif event.unicode in "0123456789.": atk_input+=event.unicode
        return
    hk={pygame.K_1:"block",pygame.K_2:"half",pygame.K_3:"dark",
        pygame.K_4:"start",pygame.K_5:"finish",pygame.K_6:"erase"}
    if event.key in hk:
        ed_tool=hk[event.key]
        if hk[event.key] in BLOCK_TYPES: active_tab="БЛОКИ"

def handle_scroll(dy, mx, my):
    """Колёсико мыши — зум."""
    global zoom, cam_x, cam_y
    gr = game_rect_screen()
    if not gr.collidepoint(mx, my): return
    # Масштабируем относительно позиции курсора
    wx, wy = screen_to_world(mx, my)
    zoom = max(0.3, min(3.5, zoom * (1.12 if dy > 0 else 0.88)))
    # Корректируем камеру чтобы под курсором осталась та же точка
    wx2, wy2 = screen_to_world(mx, my)
    cam_x -= wx2 - wx
    cam_y -= wy2 - wy

def handle_click(mx, my, rects):
    global ed_tool, ed_dragging, ed_drag_start, ed_drag_type
    global custom_duration, sel_atk_type, sel_atk_idx
    global atk_input, atk_input_focus, active_tab, zoom, cam_x, cam_y

    # Поле ввода
    if rects.get("atk_input") and rects["atk_input"].collidepoint(mx,my):
        atk_input_focus=True; return False
    atk_input_focus=False

    gr     = game_rect_screen()
    on_tl  = gr.collidepoint(mx,my) and my >= TLINE_Y
    in_gm  = gr.collidepoint(mx,my) and my < TLINE_Y

    # Клик на временную шкалу
    if on_tl and custom_duration > 0:
        bx,bw = PANEL_W_ED, WIDTH-PANEL_W_ED
        t_val  = (mx-bx)/bw*custom_duration
        # Выбрать существующую атаку?
        for i,a in enumerate(ed_attacks):
            tx = bx+int(a["time"]/custom_duration*bw)
            if abs(tx-mx)<10:
                sel_atk_idx=i; active_tab="АТАКИ"; return False
        # Добавить новую
        _add_attack(round(t_val,1)); sel_atk_idx=len(ed_attacks)-1
        active_tab="АТАКИ"; return False

    if in_gm:
        wx,wy = snap_world(*screen_to_world(mx,my))
        if ed_tool in BLOCK_TYPES:
            ed_dragging=True; ed_drag_start=(wx,wy); ed_drag_type=ed_tool
        elif ed_tool in ("start","finish"):
            ed_objects[:] = [o for o in ed_objects if o["type"]!=ed_tool]
            ed_objects.append({"type":ed_tool,"x":int(wx),"y":int(wy)})
        elif ed_tool=="erase":
            _erase_at_world(*screen_to_world(mx,my))
        return False

    # Панель
    if mx >= PANEL_W_ED: return False

    # Вкладки
    for name,r in rects.get("tabs",{}).items():
        if r.collidepoint(mx,my) and name in ("БЛОКИ","АТАКИ"):
            active_tab=name

    # Инструменты (вкладка БЛОКИ)
    for t2,r in rects.get("tools",{}).items():
        if r.collidepoint(mx,my): ed_tool=t2

    # Зум
    if rects.get("zoom_minus") and rects["zoom_minus"].collidepoint(mx,my):
        zoom=max(0.3,zoom-0.1)
    if rects.get("zoom_plus") and rects["zoom_plus"].collidepoint(mx,my):
        zoom=min(3.5,zoom+0.1)
    if rects.get("zoom_reset") and rects["zoom_reset"].collidepoint(mx,my):
        zoom=1.0; cam_x=0.0; cam_y=0.0

    # Тип атаки
    for ak,r in rects.get("atk_sel",{}).items():
        if r.collidepoint(mx,my): sel_atk_type=ak

    # Добавить атаку
    if rects.get("atk_add") and rects["atk_add"].collidepoint(mx,my):
        try: tv=float(atk_input) if atk_input else 0.0
        except: tv=0.0
        _add_attack(round(tv,1)); sel_atk_idx=len(ed_attacks)-1

    # Параметры выбранной атаки
    if 0<=sel_atk_idx<len(ed_attacks):
        a  = ed_attacks[sel_atk_idx]
        at = a["atk_type"]
        pr = rects.get("params",{})

        def _click(key,action):
            if pr.get(key) and pr[key].collidepoint(mx,my): action()

        if at in ("laser_h","double_laser"):
            _click("y_up",   lambda: a.update({"y_frac":min(0.95,a.get("y_frac",0.5)+0.05)}))
            _click("y_down", lambda: a.update({"y_frac":max(0.05,a.get("y_frac",0.5)-0.05)}))
        if at in ("laser_v","double_laser"):
            _click("x_up",   lambda: a.update({"x_frac":min(0.95,a.get("x_frac",0.5)+0.05)}))
            _click("x_down", lambda: a.update({"x_frac":max(0.05,a.get("x_frac",0.5)-0.05)}))
        if at=="flying_spinner":
            _click("side_left",  lambda: a.update({"side":"left"}))
            _click("side_right", lambda: a.update({"side":"right"}))
            _click("cy_up",   lambda: a.update({"cy_frac":min(0.95,a.get("cy_frac",0.5)+0.05)}))
            _click("cy_down", lambda: a.update({"cy_frac":max(0.05,a.get("cy_frac",0.5)-0.05)}))
            _click("spd_up",  lambda: a.update({"speed":min(8.0,a.get("speed",3.0)+0.5)}))
            _click("spd_down",lambda: a.update({"speed":max(0.5,a.get("speed",3.0)-0.5)}))
        if at=="blocks":
            for ci,rc2 in pr.get("cols",{}).items():
                if rc2.collidepoint(mx,my):
                    cols=list(a.get("cols",[3,7]))
                    if ci in cols: cols.remove(ci)
                    else: cols.append(ci)
                    a["cols"]=sorted(cols)
        if at=="circles":
            for sd,rs in pr.get("circle_side",{}).items():
                if rs.collidepoint(mx,my): a["side"]=sd

    # Удаление атак из списка
    for orig_i,rd in rects.get("atk_del",{}).items():
        if rd.collidepoint(mx,my):
            if 0<=orig_i<len(ed_attacks):
                ed_attacks.pop(orig_i)
                if sel_atk_idx>=len(ed_attacks): sel_atk_idx=len(ed_attacks)-1

    # Длительность
    if rects.get("dur_minus") and rects["dur_minus"].collidepoint(mx,my):
        custom_duration=max(10,custom_duration-5)
    if rects.get("dur_plus") and rects["dur_plus"].collidepoint(mx,my):
        custom_duration=min(300,custom_duration+5)

    if rects.get("clear") and rects["clear"].collidepoint(mx,my):
        ed_objects.clear(); ed_attacks.clear(); sel_atk_idx=-1
    if rects.get("save") and rects["save"].collidepoint(mx,my):
        save_level()

    return rects.get("play") and rects["play"].collidepoint(mx,my)

def handle_rightclick(mx, my):
    global sel_atk_idx, ed_pan_active
    gr = game_rect_screen()
    if gr.collidepoint(mx,my) and my >= TLINE_Y and custom_duration>0:
        bx,bw = PANEL_W_ED, WIDTH-PANEL_W_ED
        for a in ed_attacks[:]:
            tx=bx+int(a["time"]/custom_duration*bw)
            if abs(tx-mx)<12:
                ed_attacks.remove(a)
                if sel_atk_idx>=len(ed_attacks): sel_atk_idx=len(ed_attacks)-1
                return
    if gr.collidepoint(mx,my) and my < TLINE_Y:
        _erase_at_world(*screen_to_world(mx,my))

def handle_rightdown(mx, my):
    global ed_pan_active, ed_pan_origin, ed_cam_origin
    gr = game_rect_screen()
    if gr.collidepoint(mx,my) and my < TLINE_Y:
        ed_pan_active  = True
        ed_pan_origin  = (mx, my)
        ed_cam_origin  = (cam_x, cam_y)

def handle_rightup():
    global ed_pan_active
    if ed_pan_active:
        ed_pan_active = False
        # Если почти не двигались — это клик, не панорама
        # (логика в handle_rightclick)

def handle_pan(mx, my):
    global cam_x, cam_y
    if not ed_pan_active: return
    dx = (mx - ed_pan_origin[0]) / zoom
    dy = (my - ed_pan_origin[1]) / zoom
    cam_x = ed_cam_origin[0] - dx
    cam_y = ed_cam_origin[1] - dy

def handle_release(mx, my):
    global ed_dragging
    if not ed_dragging: return
    ed_dragging=False
    wx1,wy1 = snap_world(*screen_to_world(mx,my))
    wx0,wy0 = ed_drag_start
    rx,ry   = int(min(wx0,wx1)), int(min(wy0,wy1))
    rw      = max(GRID_BASE, int(abs(wx1-wx0)))
    rh      = max(GRID_BASE, int(abs(wy1-wy0)))
    ed_objects.append({"type":ed_drag_type, "rect":pygame.Rect(rx,ry,rw,rh)})

def _erase_at_world(wx, wy):
    r = 28/zoom   # радиус стирания в мировых координатах
    ed_objects[:] = [
        o for o in ed_objects
        if not (o["type"] in BLOCK_TYPES and
                pygame.Rect(o["rect"].x, o["rect"].y,
                            o["rect"].w, o["rect"].h)
                .colliderect(pygame.Rect(wx-r,wy-r,r*2,r*2)))
        and not (o["type"] in ("start","finish") and
                 math.hypot(o["x"]-wx, o["y"]-wy) < r*1.5)
    ]

def _add_attack(time_val):
    a = {"time":time_val,"atk_type":sel_atk_type}
    if sel_atk_type=="laser_h":          a.update({"y_frac":0.5})
    elif sel_atk_type=="laser_v":         a.update({"x_frac":0.5})
    elif sel_atk_type=="double_laser":    a.update({"y_frac":0.3,"x_frac":0.7})
    elif sel_atk_type=="flying_spinner":  a.update({"side":"left","cy_frac":0.5,"speed":3.0})
    elif sel_atk_type=="blocks":          a.update({"cols":[3,7]})
    elif sel_atk_type=="circles":         a.update({"side":"left"})
    ed_attacks.append(a)
