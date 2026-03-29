import pygame, math, json, os
from constants import *
import attacks as atk_module

# ── Константы редактора ───────────────────────────────
GRID       = 40
ED_LEFT    = 270          # ширина панели (немного шире старой 240)
ED_RIGHT   = WIDTH - 270  # симметрично! одинаковые поля с обеих сторон
GAME_RECT  = pygame.Rect(ED_LEFT, 0, ED_RIGHT - ED_LEFT, HEIGHT)

BLOCK_TYPES = ("block", "half", "dark")

BLOCK_STYLE = {
    "block": {"fill":(160,30,30),  "border":(255,120,120), "cross":True,  "hatch":False},
    "half":  {"fill":(160,90,20),  "border":(255,190,80),  "cross":False, "hatch":False},
    "dark":  {"fill":(18,18,18),   "border":(70,70,70),    "cross":False, "hatch":True},
}

ATK_TYPES  = ["laser_h","laser_v","double_laser","flying_spinner","blocks","circles"]
ATK_LABEL  = {"laser_h":"Лазер →","laser_v":"Лазер ↓","double_laser":"2 Лазера",
               "flying_spinner":"Палка","blocks":"Ящики","circles":"Круги"}
ATK_COL    = {"laser_h":(0,160,200),"laser_v":(0,140,180),"double_laser":(0,100,220),
               "flying_spinner":(220,110,0),"blocks":(200,80,0),"circles":(160,0,200)}

# ── Состояние ─────────────────────────────────────────
ed_tool          = "block"
ed_objects       = []       # блоки + старт/финиш
ed_attacks       = []       # [{time, atk_type}]
ed_dragging      = False
ed_drag_start    = (0, 0)
ed_drag_type     = "block"
custom_duration  = 60
sel_atk          = "laser_h"
atk_input        = ""       # текстовое поле ввода времени
atk_input_focus  = False

def snap(v): return round(v / GRID) * GRID

# ── Сохранение / загрузка ─────────────────────────────
def save_level():
    obs = []
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r = o["rect"]
            obs.append({"type":o["type"],"x":r.x,"y":r.y,"w":r.w,"h":r.h})
        else:
            obs.append({"type":o["type"],"x":o["x"],"y":o["y"]})
    json.dump({"objects":obs,"attacks":ed_attacks,"duration":custom_duration,
               "atk_enabled":atk_module.custom_atk_enabled,"atk_freq":2},
              open(SAVE_FILE,"w"))

def load_level():
    global ed_objects, ed_attacks, custom_duration
    if not os.path.exists(SAVE_FILE): return
    data = json.load(open(SAVE_FILE))
    ed_objects = []
    for o in data.get("objects",[]):
        bt = o["type"]
        # обратная совместимость: старый "block" → "block"
        if bt not in BLOCK_TYPES and bt != "start" and bt != "finish":
            bt = "block"
        if bt in BLOCK_TYPES:
            ed_objects.append({"type":bt,"rect":pygame.Rect(o["x"],o["y"],o["w"],o["h"])})
        else:
            ed_objects.append({"type":bt,"x":o["x"],"y":o["y"]})
    ed_attacks       = data.get("attacks", [])
    custom_duration  = data.get("duration", 60)
    atk_module.custom_atk_enabled = data.get("atk_enabled",
                                              atk_module.custom_atk_enabled).copy()

def get_active_obstacles():
    res = []
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r = o["rect"]
            res.append({"rect": pygame.Rect(r.x+ED_LEFT, r.y, r.w, r.h),
                        "btype": o["type"]})
    return res

def get_start_pos():
    for o in ed_objects:
        if o["type"] == "start":
            return o["x"]+ED_LEFT, o["y"]
    return (ED_LEFT+ED_RIGHT)//2, HEIGHT//2

def get_scripted_timeline():
    """Таймлайн для custom_runner в формате [(warn_time, entry)]."""
    tl = []
    GW = ED_RIGHT - ED_LEFT
    for a in sorted(ed_attacks, key=lambda x: x["time"]):
        t_warn = max(0.0, a["time"] - 2.0)
        at     = a["atk_type"]
        if at == "laser_h":
            entry = {"type":"laser_h","y":a.get("y_frac",0.5)}
        elif at == "laser_v":
            entry = {"type":"laser_v","x":a.get("x_frac",0.5)}
        elif at == "double_laser":
            entry = {"type":"double_laser","y":a.get("y_frac",0.3),"x":a.get("x_frac",0.7)}
        elif at == "flying_spinner":
            entry = {"type":"flying_spinner","side":a.get("side","left"),
                     "cy_frac":a.get("cy_frac",0.5),"speed":a.get("speed",3.0)}
        elif at == "blocks":
            entry = {"type":"blocks","cols":a.get("cols",[3,7])}
        elif at == "circles":
            entry = {"type":"circles","side":a.get("side","left")}
        else:
            continue
        tl.append((t_warn, entry))
    return tl

# ── Кнопка ───────────────────────────────────────────
def _btn(screen, r, label, active=False, col=None):
    mx, my = pygame.mouse.get_pos()
    base   = col if col else ((30,80,160) if active else (30,30,60))
    hover  = r.collidepoint(mx, my)
    if hover: base = tuple(min(255,c+40) for c in base)
    pygame.draw.rect(screen, base, r, border_radius=6)
    pygame.draw.rect(screen, (100,160,255) if active else (55,55,110), r, 2, border_radius=6)
    t = font_ui.render(label, True, WHITE)
    screen.blit(t, (r.centerx-t.get_width()//2, r.centery-t.get_height()//2))

def _tiny(screen, r, label, active=False, col=None):
    mx, my = pygame.mouse.get_pos()
    base   = col if col else ((30,80,160) if active else (30,30,60))
    if r.collidepoint(mx, my): base = tuple(min(255,c+40) for c in base)
    pygame.draw.rect(screen, base, r, border_radius=4)
    pygame.draw.rect(screen, (80,80,140) if not active else (100,160,255), r, 1, border_radius=4)
    t = font_tiny.render(label, True, WHITE)
    screen.blit(t, (r.centerx-t.get_width()//2, r.centery-t.get_height()//2))

# ── Рисование блока (с учётом типа) ──────────────────
def _draw_block_at(screen, btype, rx, ry, rw, rh, alpha=255):
    st = BLOCK_STYLE[btype]
    # полублок — нижняя половина
    if btype == "half":
        ry += rh // 2
        rh  = rh // 2
    r = pygame.Rect(rx, ry, rw, rh)
    if alpha < 255:
        s = pygame.Surface((rw, rh), pygame.SRCALPHA)
        s.fill((*st["fill"], alpha))
        pygame.draw.rect(s, (*st["border"], alpha), (0,0,rw,rh), 2, border_radius=4)
        screen.blit(s, (rx, ry))
        return
    pygame.draw.rect(screen, st["fill"],   r, border_radius=4)
    pygame.draw.rect(screen, st["border"], r, 2, border_radius=4)
    if st["cross"]:
        pygame.draw.line(screen, (255,90,90), r.topleft,  r.bottomright, 2)
        pygame.draw.line(screen, (255,90,90), r.topright, r.bottomleft,  2)
    if st["hatch"]:
        for ox in range(0, rw+rh, 18):
            x1 = min(rx+ox, rx+rw-1);  y1 = ry if rx+ox <= rx+rw-1 else ry+(rx+ox-(rx+rw-1))
            x2 = rx if ox <= rh else rx+(ox-rh); y2 = min(ry+ox, ry+rh-1)
            pygame.draw.line(screen, (50,50,50), (x1,y1), (x2,y2), 1)

# ── Сетка ─────────────────────────────────────────────
def _draw_grid(screen):
    # тонкая (40px)
    for x in range(ED_LEFT, ED_RIGHT+1, GRID):
        pygame.draw.line(screen, (28,28,55), (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT+1, GRID):
        pygame.draw.line(screen, (28,28,55), (ED_LEFT,y), (ED_RIGHT,y))
    # жирная (160px = 4 клетки)
    for x in range(ED_LEFT, ED_RIGHT+1, GRID*4):
        pygame.draw.line(screen, (48,48,90), (x,0), (x,HEIGHT))
    for y in range(0, HEIGHT+1, GRID*4):
        pygame.draw.line(screen, (48,48,90), (ED_LEFT,y), (ED_RIGHT,y))
    # рамка
    pygame.draw.rect(screen, (70,70,150),
                     pygame.Rect(ED_LEFT,0,ED_RIGHT-ED_LEFT,HEIGHT), 2)

# ── Временная шкала ───────────────────────────────────
def _draw_timeline(screen):
    bx, by = ED_LEFT, HEIGHT - 62
    bw, bh = ED_RIGHT - ED_LEFT, 56
    # фон
    s = pygame.Surface((bw,bh), pygame.SRCALPHA); s.fill((8,8,28,200))
    screen.blit(s, (bx,by))
    pygame.draw.rect(screen, (55,55,120), (bx,by,bw,bh), 1)
    # отметки каждые 5с
    if custom_duration > 0:
        step = 5 if custom_duration <= 60 else 10
        for t in range(0, custom_duration+1, step):
            tx = bx + int(t/custom_duration*bw)
            pygame.draw.line(screen,(55,55,100),(tx,by),(tx,by+bh),1)
            lbl = font_tiny.render(f"{t}s", True, (80,80,130))
            screen.blit(lbl, (tx+2, by+2))
    # атаки
    for a in ed_attacks:
        if custom_duration > 0:
            tx = bx + int(a["time"]/custom_duration*bw)
            c  = ATK_COL.get(a["atk_type"], PURPLE)
            pygame.draw.line(screen, c, (tx,by+2), (tx,by+bh-2), 4)
            abbr = ATK_LABEL.get(a["atk_type"],"?")[:3]
            lbl  = font_tiny.render(abbr, True, c)
            screen.blit(lbl, (tx+3, by+bh-20))
    # подсказка
    hint = font_tiny.render("ЛКМ на шкалу — поставити атаку  |  ПКМ / інструменти Стерти — видалити", True, (70,70,110))
    screen.blit(hint, (bx+6, by+bh+4))

# ── Главная отрисовка ─────────────────────────────────
def draw(screen):
    screen.fill(BG_LEVEL)
    _draw_grid(screen)

    # объекты
    for o in ed_objects:
        if o["type"] in BLOCK_TYPES:
            r = o["rect"]
            _draw_block_at(screen, o["type"], r.x+ED_LEFT, r.y, r.w, r.h)
        elif o["type"] == "start":
            pygame.draw.circle(screen, GREEN, (o["x"]+ED_LEFT, o["y"]), 22)
            pygame.draw.circle(screen, WHITE,  (o["x"]+ED_LEFT, o["y"]), 22, 2)
            t = font_ui.render("S", True, WHITE)
            screen.blit(t,(o["x"]+ED_LEFT-t.get_width()//2, o["y"]-t.get_height()//2))
        elif o["type"] == "finish":
            pygame.draw.circle(screen, CYAN,  (o["x"]+ED_LEFT, o["y"]), 22)
            pygame.draw.circle(screen, WHITE, (o["x"]+ED_LEFT, o["y"]), 22, 2)
            t = font_ui.render("F", True, WHITE)
            screen.blit(t,(o["x"]+ED_LEFT-t.get_width()//2, o["y"]-t.get_height()//2))

    # превью курсора
    mx, my = pygame.mouse.get_pos()
    in_game = GAME_RECT.collidepoint(mx, my) and my < HEIGHT - 62
    if ed_dragging and ed_drag_type in BLOCK_TYPES:
        gx0, gy0 = ed_drag_start
        gx1 = snap(mx - ED_LEFT); gy1 = snap(my)
        rx = min(gx0,gx1); ry = min(gy0,gy1)
        rw = max(GRID, abs(gx1-gx0)); rh = max(GRID, abs(gy1-gy0))
        _draw_block_at(screen, ed_drag_type, rx+ED_LEFT, ry, rw, rh, alpha=80)
        # показываем размер
        lbl = font_tiny.render(f"{rw//GRID}×{rh//GRID}", True, WHITE)
        screen.blit(lbl, (mx+12, my-20))
    elif in_game:
        gx = snap(mx - ED_LEFT); gy = snap(my)
        if ed_tool in BLOCK_TYPES:
            # яркая рамка клетки под курсором
            cell = pygame.Rect(gx+ED_LEFT, gy, GRID, GRID)
            pygame.draw.rect(screen, (255,255,255), cell, 1, border_radius=2)
            _draw_block_at(screen, ed_tool, gx+ED_LEFT, gy, GRID, GRID, alpha=65)
        elif ed_tool in ("start","finish"):
            c = GREEN if ed_tool=="start" else CYAN
            s2 = pygame.Surface((48,48), pygame.SRCALPHA)
            pygame.draw.circle(s2,(*c,100),(24,24),22)
            screen.blit(s2,(gx+ED_LEFT-24, gy-24))
        elif ed_tool == "erase":
            pygame.draw.rect(screen,(220,50,50),pygame.Rect(mx-20,my-20,40,40),2,border_radius=4)
        elif ed_tool == "attack" and custom_duration > 0:
            # вертикальная линия на шкале
            tx = ED_LEFT + int(mx/WIDTH * (ED_RIGHT-ED_LEFT))  # грубо

    _draw_timeline(screen)

    # панели
    screen.fill(BG_PANEL, pygame.Rect(0,0,ED_LEFT,HEIGHT))
    pygame.draw.line(screen,(60,60,130),(ED_LEFT,0),(ED_LEFT,HEIGHT),2)
    screen.fill(BG_PANEL, pygame.Rect(ED_RIGHT,0,WIDTH-ED_RIGHT,HEIGHT))
    pygame.draw.line(screen,(60,60,130),(ED_RIGHT,0),(ED_RIGHT,HEIGHT),2)

    return _draw_left_panel(screen)

# ── Левая панель ──────────────────────────────────────
def _draw_left_panel(screen):
    rects = {}
    PW = ED_LEFT
    y  = 10

    t = font_med.render("РЕДАКТОР", True, YELLOW)
    screen.blit(t,(PW//2-t.get_width()//2,y)); y+=46

    # ── БЛОКИ (3 в ряд) ──────────────────────────────
    lbl = font_tiny.render("── БЛОКИ ──", True, GRAY)
    screen.blit(lbl,(PW//2-lbl.get_width()//2,y)); y+=18
    bw3 = (PW-12)//3
    tool_rects = {}
    for i, bt in enumerate(["block","half","dark"]):
        names = {"block":"Блок","half":"Напів","dark":"Темний"}
        cols  = {"block":(110,20,20),"half":(110,60,5),"dark":(18,18,18)}
        r = pygame.Rect(4+i*(bw3+2), y, bw3, 38)
        _btn(screen, r, names[bt], active=(ed_tool==bt), col=cols[bt])
        tool_rects[bt] = r
    y += 44

    # ── ПРОЧИЕ ИНСТРУМЕНТЫ ───────────────────────────
    for tool, label, col in [
        ("start",  "4 Старт ▶",  (20,100,40)),
        ("finish", "5 Финиш 🏁", (0,80,100)),
        ("erase",  "6 Стереть",  (50,50,70)),
        ("attack", "7 Атака ⚡",  (90,20,110)),
    ]:
        r = pygame.Rect(4, y, PW-8, 36)
        _btn(screen, r, label, active=(ed_tool==tool), col=col if ed_tool==tool else None)
        tool_rects[tool] = r; y += 42
    rects["tools"] = tool_rects

    # ── АТАКИ ────────────────────────────────────────
    y += 4
    lbl = font_tiny.render("── ТИП АТАКИ ──", True, GRAY)
    screen.blit(lbl,(PW//2-lbl.get_width()//2,y)); y+=18
    bw2 = (PW-12)//2
    atk_sel_rects = {}
    for i, ak in enumerate(ATK_TYPES):
        r = pygame.Rect(4+(i%2)*(bw2+4), y+(i//2)*34, bw2, 30)
        _tiny(screen, r, ATK_LABEL[ak],
              active=(sel_atk==ak), col=ATK_COL[ak] if sel_atk==ak else None)
        atk_sel_rects[ak] = r
    y += (len(ATK_TYPES)//2)*34 + 6
    rects["atk_sel"] = atk_sel_rects

    # ── ПОЛЕ ВВОДА ВРЕМЕНИ ───────────────────────────
    lbl2 = font_tiny.render("Час атаки (сек):", True, GRAY)
    screen.blit(lbl2,(4,y)); y+=16
    inp_r = pygame.Rect(4, y, PW-58, 28)
    pygame.draw.rect(screen,(35,70,35) if atk_input_focus else (22,22,48), inp_r, border_radius=5)
    pygame.draw.rect(screen,(80,200,80) if atk_input_focus else (55,55,100), inp_r,2,border_radius=5)
    disp = (atk_input+"|") if atk_input_focus else (atk_input or "0.0")
    screen.blit(font_ui.render(disp,True,WHITE),(inp_r.x+5,inp_r.y+5))
    rects["atk_input"] = inp_r
    r_add = pygame.Rect(PW-52, y, 48, 28)
    _btn(screen, r_add, "+Додати", col=(20,80,20))
    rects["atk_add"] = r_add; y += 34

    # ── СПИСОК АТАК ──────────────────────────────────
    lbl3 = font_tiny.render("Список атак:", True, GRAY)
    screen.blit(lbl3,(4,y)); y+=16
    atk_del = {}
    for i, a in enumerate(sorted(ed_attacks, key=lambda x:x["time"])):
        if y > HEIGHT-180: break
        r = pygame.Rect(4, y, PW-38, 22)
        c = ATK_COL.get(a["atk_type"],PURPLE)
        pygame.draw.rect(screen,(16,16,35),r,border_radius=3)
        pygame.draw.rect(screen,c,r,1,border_radius=3)
        txt = f"{a['time']:.1f}s {ATK_LABEL.get(a['atk_type'],'?')[:8]}"
        screen.blit(font_tiny.render(txt,True,c),(r.x+3,r.y+4))
        rd = pygame.Rect(PW-32, y, 26, 22)
        _tiny(screen, rd, "✕", col=(80,15,15)); atk_del[i]=rd; y+=26
    rects["atk_del"] = atk_del

    # ── ДЛИНА УРОВНЯ ─────────────────────────────────
    y = max(y+4, HEIGHT-152)
    lbl4 = font_tiny.render(f"Длит.: {custom_duration} сек", True, GRAY)
    screen.blit(lbl4,(4,y)); y+=16
    rm = pygame.Rect(4, y, 40, 26); rp = pygame.Rect(PW-44,y,40,26)
    tv = font_ui.render(str(custom_duration),True,WHITE)
    screen.blit(tv,(PW//2-tv.get_width()//2,y+3))
    _btn(screen,rm," − "); _btn(screen,rp," + ")
    rects["dur_minus"]=rm; rects["dur_plus"]=rp; y+=34

    # ── КНОПКИ ───────────────────────────────────────
    half = (PW-12)//2
    rc = pygame.Rect(4,y,half,32); rs = pygame.Rect(PW//2+2,y,half,32)
    _btn(screen,rc,"🗑 Очистити",col=(70,12,12))
    _btn(screen,rs,"💾 Зберегти",col=(12,70,12))
    rects["clear"]=rc; rects["save"]=rs; y+=40

    rp2 = pygame.Rect(4,y,PW-8,50)
    hov = rp2.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen,(40,120,240) if hov else (22,85,185), rp2, border_radius=10)
    pygame.draw.rect(screen,(90,170,255),rp2,3,border_radius=10)
    pt = font_med.render("▶ ГРАТИ!", True, WHITE)
    screen.blit(pt,(rp2.centerx-pt.get_width()//2,rp2.centery-pt.get_height()//2))
    rects["play"] = rp2

    et = font_tiny.render("ESC — назад", True, GRAY)
    screen.blit(et,(PW//2-et.get_width()//2,HEIGHT-20))
    return rects

# ── Обработка клавиш ──────────────────────────────────
def handle_keydown(event):
    global ed_tool, atk_input, atk_input_focus
    if atk_input_focus:
        k = event.key
        if k in (pygame.K_RETURN, pygame.K_ESCAPE):
            atk_input_focus = False
        elif k == pygame.K_BACKSPACE:
            atk_input = atk_input[:-1]
        elif event.unicode in "0123456789.":
            atk_input += event.unicode
        return
    hk = {pygame.K_1:"block",pygame.K_2:"half",pygame.K_3:"dark",
          pygame.K_4:"start",pygame.K_5:"finish",pygame.K_6:"erase",pygame.K_7:"attack"}
    if event.key in hk:
        ed_tool = hk[event.key]

# ── Обработка кликов ──────────────────────────────────
def handle_click(mx, my, rects):
    global ed_tool, ed_dragging, ed_drag_start, ed_drag_type
    global custom_duration, sel_atk, atk_input, atk_input_focus

    # Поле ввода времени
    if rects.get("atk_input") and rects["atk_input"].collidepoint(mx,my):
        atk_input_focus = True
        return False
    atk_input_focus = False

    in_game  = GAME_RECT.collidepoint(mx,my) and my < HEIGHT-62
    on_tline = GAME_RECT.collidepoint(mx,my) and my >= HEIGHT-62

    # Клик по временной шкале — добавить атаку
    if on_tline and custom_duration > 0:
        t_val = (mx - ED_LEFT) / (ED_RIGHT - ED_LEFT) * custom_duration
        _add_attack(round(t_val, 1))
        return False

    if in_game:
        gx = snap(mx - ED_LEFT); gy = snap(my)
        if ed_tool in BLOCK_TYPES:
            ed_dragging  = True
            ed_drag_start = (gx, gy)
            ed_drag_type  = ed_tool
        elif ed_tool in ("start","finish"):
            ed_objects[:] = [o for o in ed_objects if o["type"] != ed_tool]
            ed_objects.append({"type":ed_tool,"x":gx,"y":gy})
        elif ed_tool == "erase":
            hit = pygame.Rect(mx-22,my-22,44,44)
            ed_objects[:] = [
                o for o in ed_objects
                if not (o["type"] in BLOCK_TYPES and
                        pygame.Rect(o["rect"].x+ED_LEFT,o["rect"].y,
                                    o["rect"].w,o["rect"].h).colliderect(hit))
                and not (o["type"] in ("start","finish") and
                         math.hypot(o["x"]+ED_LEFT-mx, o["y"]-my) < 30)
            ]
        elif ed_tool == "attack" and custom_duration > 0:
            t_val = (mx - ED_LEFT) / (ED_RIGHT - ED_LEFT) * custom_duration
            _add_attack(round(t_val, 1))
        return False

    # Правая панель — ничего, только левая
    if mx >= ED_RIGHT:
        return False

    # Левая панель
    for t2, r in rects.get("tools",{}).items():
        if r.collidepoint(mx,my): ed_tool = t2
    for ak, r in rects.get("atk_sel",{}).items():
        if r.collidepoint(mx,my): sel_atk = ak
    if rects.get("atk_add") and rects["atk_add"].collidepoint(mx,my):
        try: t_val = float(atk_input) if atk_input else 0.0
        except: t_val = 0.0
        _add_attack(round(t_val,1))
    for i, r in rects.get("atk_del",{}).items():
        if r.collidepoint(mx,my):
            sl = sorted(ed_attacks,key=lambda x:x["time"])
            if i < len(sl): ed_attacks.remove(sl[i])
    if rects.get("dur_minus") and rects["dur_minus"].collidepoint(mx,my):
        custom_duration = max(10, custom_duration-5)
    if rects.get("dur_plus") and rects["dur_plus"].collidepoint(mx,my):
        custom_duration = min(300, custom_duration+5)
    if rects.get("clear") and rects["clear"].collidepoint(mx,my):
        ed_objects.clear(); ed_attacks.clear()
    if rects.get("save") and rects["save"].collidepoint(mx,my):
        save_level()
    return rects.get("play") and rects["play"].collidepoint(mx,my)

def handle_rightclick(mx, my):
    """ПКМ — удалить атаку на шкале или блок."""
    if GAME_RECT.collidepoint(mx,my) and my >= HEIGHT-62 and custom_duration>0:
        for a in ed_attacks[:]:
            tx = ED_LEFT + int(a["time"]/custom_duration*(ED_RIGHT-ED_LEFT))
            if abs(tx-mx) < 14:
                ed_attacks.remove(a); return
    if GAME_RECT.collidepoint(mx,my):
        hit = pygame.Rect(mx-22,my-22,44,44)
        ed_objects[:] = [
            o for o in ed_objects
            if not (o["type"] in BLOCK_TYPES and
                    pygame.Rect(o["rect"].x+ED_LEFT,o["rect"].y,
                                o["rect"].w,o["rect"].h).colliderect(hit))
            and not (o["type"] in ("start","finish") and
                     math.hypot(o["x"]+ED_LEFT-mx,o["y"]-my)<30)
        ]

def _add_attack(time_val):
    a = {"time": time_val, "atk_type": sel_atk}
    if sel_atk == "laser_h":          a.update({"y_frac":0.5})
    elif sel_atk == "laser_v":         a.update({"x_frac":0.5})
    elif sel_atk == "double_laser":    a.update({"y_frac":0.3,"x_frac":0.7})
    elif sel_atk == "flying_spinner":  a.update({"side":"left","cy_frac":0.5,"speed":3.0})
    elif sel_atk == "blocks":          a.update({"cols":[3,7]})
    elif sel_atk == "circles":         a.update({"side":"left"})
    ed_attacks.append(a)

def handle_release(mx, my):
    global ed_dragging
    if not ed_dragging: return
    ed_dragging = False
    gx1 = snap(mx - ED_LEFT); gy1 = snap(my)
    gx0, gy0 = ed_drag_start
    rx,ry = min(gx0,gx1), min(gy0,gy1)
    rw = max(GRID, abs(gx1-gx0)); rh = max(GRID, abs(gy1-gy0))
    ed_objects.append({"type": ed_drag_type, "rect": pygame.Rect(rx,ry,rw,rh)})
