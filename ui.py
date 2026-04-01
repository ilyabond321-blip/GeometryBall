import pygame, random, math
from constants import *
from lang import T

stars = [(random.randint(0,WIDTH), random.randint(0,HEIGHT), random.random()) for _ in range(220)]

# Кнопки (перераховуються в draw-функціях під поточний WIDTH/HEIGHT)
btn_play     = pygame.Rect(WIDTH//2-sc(160), HEIGHT//2+sc(40), sc(320), sc(80))
btn_settings = pygame.Rect(WIDTH//2-sc(160), HEIGHT//2+sc(140), sc(320), sc(70))

def level_btn(i):
    bw, bh, gap = sc(260), sc(120), sc(60)
    sx = WIDTH//2-(3*bw+2*gap)//2
    return pygame.Rect(sx+(i-1)*(bw+gap), HEIGHT//2-bh//2, bw, bh)

def _stars(screen):
    for sx2,sy2,br in stars:
        c = int(br*180)
        pygame.draw.circle(screen,(c,c,c+40),(sx2,sy2),1)

def _btn(screen, r, label, col_main, col_border, font=None):
    hov = r.collidepoint(pygame.mouse.get_pos())
    cm  = tuple(min(255,c+30) for c in col_main) if hov else col_main
    pygame.draw.rect(screen, cm, r, border_radius=sc(14))
    pygame.draw.rect(screen, col_border, r, sc(3), border_radius=sc(14))
    f   = font or font_med
    t   = f.render(label, True, WHITE)
    screen.blit(t,(r.centerx-t.get_width()//2, r.centery-t.get_height()//2))

def draw_menu(screen):
    screen.fill(BG_MENU); _stars(screen)

    # Тінь + заголовок
    sh = font_big.render("GEOMETRY BALL", True, (80,50,0))
    tx = font_big.render("GEOMETRY BALL", True, YELLOW)
    screen.blit(sh,(WIDTH//2-sh.get_width()//2+sc(5), HEIGHT//3-sc(30)+sc(5)))
    screen.blit(tx,(WIDTH//2-tx.get_width()//2,       HEIGHT//3-sc(30)))

    # Кнопка ГРАТИ
    _btn(screen, btn_play,
         T("play_btn"), (40,150,60),(80,220,100))

    # Кнопка НАЛАШТУВАННЯ
    _btn(screen, btn_settings,
         T("settings_btn"), (50,50,130),(100,100,200), font=font_sm)

    esc = font_tiny.render(T("exit_hint"), True, GRAY)
    screen.blit(esc,(WIDTH//2-esc.get_width()//2, HEIGHT-sc(40)))

def draw_level_select(screen):
    screen.fill(BG_MENU); _stars(screen)
    t = font_med.render(T("select_level"), True, YELLOW)
    screen.blit(t,(WIDTH//2-t.get_width()//2, HEIGHT//4-sc(30)))

    for i in range(1,4):
        btn   = level_btn(i); locked = i>1
        hov   = btn.collidepoint(pygame.mouse.get_pos()) and not locked
        col   = (40,40,60) if locked else ((60,120,200) if hov else (40,90,160))
        brd   = (70,70,100) if locked else ((120,180,255) if hov else (80,140,220))
        pygame.draw.rect(screen, col, btn, border_radius=sc(16))
        pygame.draw.rect(screen, brd, btn, sc(3), border_radius=sc(16))
        nm = font_med.render(T("level_n",i), True, WHITE if not locked else GRAY)
        screen.blit(nm,(btn.centerx-nm.get_width()//2, btn.centery-nm.get_height()//2-sc(12)))
        sub_str = T("soon") if locked else T("level_dur",98)
        sub = font_tiny.render(sub_str, True, GRAY if locked else (150,220,150))
        screen.blit(sub,(btn.centerx-sub.get_width()//2, btn.centery+sc(20)))

    ed_btn = pygame.Rect(WIDTH//2-sc(180), HEIGHT*3//4-sc(30), sc(360), sc(70))
    hov2   = ed_btn.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen,(80,50,160) if hov2 else (55,35,120), ed_btn, border_radius=sc(16))
    pygame.draw.rect(screen,(160,100,255) if hov2 else (120,70,200), ed_btn, sc(2), border_radius=sc(16))
    et = font_sm.render(T("editor_btn"), True, WHITE)
    screen.blit(et,(ed_btn.centerx-et.get_width()//2, ed_btn.centery-et.get_height()//2))

    esc = font_sm.render(T("back_hint"), True, GRAY)
    screen.blit(esc,(WIDTH//2-esc.get_width()//2, HEIGHT-sc(40)))
    return ed_btn

def draw_win(screen, deaths):
    screen.fill((5,25,5)); _stars(screen)
    t1 = font_big.render(T("win"), True, GREEN)
    screen.blit(t1,(WIDTH//2-t1.get_width()//2, HEIGHT//3))
    t2 = font_med.render(T("deaths_count",deaths), True, GRAY)
    screen.blit(t2,(WIDTH//2-t2.get_width()//2, HEIGHT//2))
    t3 = font_med.render(T("restart_hint"), True, GRAY)
    screen.blit(t3,(WIDTH//2-t3.get_width()//2, HEIGHT//2+sc(80)))

# ── ЕКРАН НАЛАШТУВАНЬ ─────────────────────────────────
class SettingsScreen:
    def __init__(self):
        self.music_vol = 0.75
        self.sfx_vol   = 0.80
        self.lang      = "ua"
        self._drag_music = False
        self._drag_sfx   = False
        self._rects      = {}

    def sync_from(self, cfg_get):
        self.music_vol = cfg_get("music_vol")
        self.sfx_vol   = cfg_get("sfx_vol")
        self.lang      = cfg_get("lang")

    def sync_to(self, cfg_set):
        cfg_set("music_vol", self.music_vol)
        cfg_set("sfx_vol",   self.sfx_vol)
        cfg_set("lang",      self.lang)

    def _slider(self, screen, label, val, sx, sy, sw, sh):
        """Малює слайдер, повертає pygame.Rect рейки."""
        t = font_sm.render(label, True, WHITE)
        screen.blit(t,(sx, sy-t.get_height()-sc(4)))
        track = pygame.Rect(sx, sy, sw, sh)
        pygame.draw.rect(screen,(40,40,80), track, border_radius=sh//2)
        fill  = pygame.Rect(sx, sy, int(sw*val), sh)
        pygame.draw.rect(screen, CYAN, fill, border_radius=sh//2)
        # Ручка
        kx = sx + int(sw*val)
        ky = sy + sh//2
        kr = sh+sc(4)
        pygame.draw.circle(screen, WHITE, (kx,ky), kr)
        pygame.draw.circle(screen, CYAN,  (kx,ky), kr-sc(3))
        # Відсоток
        pct = font_tiny.render(f"{int(val*100)}%", True, GRAY)
        screen.blit(pct,(sx+sw+sc(10), sy))
        return track

    def draw(self, screen):
        screen.fill(BG_MENU); _stars(screen)

        title = font_med.render(T("settings_title"), True, YELLOW)
        screen.blit(title,(WIDTH//2-title.get_width()//2, sc(40)))

        cx   = WIDTH//2
        sw   = sc(500)
        sx   = cx - sw//2
        sh   = sc(18)
        rects = {}

        # ── МОВА ──────────────────────────────────────
        y = sc(150)
        lbl = font_sm.render(T("language"), True, GRAY)
        screen.blit(lbl,(cx-lbl.get_width()//2, y)); y+=sc(44)

        bw  = sc(220)
        gap = sc(20)
        r_ua = pygame.Rect(cx-bw-gap//2, y, bw, sc(56))
        r_en = pygame.Rect(cx+gap//2,    y, bw, sc(56))

        for r, code, key in [(r_ua,"ua","lang_ua"),(r_en,"en","lang_en")]:
            active = (self.lang == code)
            hov    = r.collidepoint(pygame.mouse.get_pos())
            col    = (30,100,30) if active else ((40,40,80) if not hov else (50,50,100))
            brd    = GREEN if active else (80,80,140)
            pygame.draw.rect(screen, col, r, border_radius=sc(12))
            pygame.draw.rect(screen, brd, r, sc(3) if active else sc(2), border_radius=sc(12))
            t = font_sm.render(T(key), True, WHITE)
            screen.blit(t,(r.centerx-t.get_width()//2, r.centery-t.get_height()//2))
        rects["lang_ua"] = r_ua; rects["lang_en"] = r_en
        y += sc(80)

        # ── ГУЧНІСТЬ МУЗИКИ ───────────────────────────
        y += sc(20)
        tr_m = self._slider(screen, T("music_vol"),
                            self.music_vol, sx, y, sw, sh)
        rects["track_music"] = tr_m; y+=sc(70)

        # ── ГУЧНІСТЬ ЕФЕКТІВ ──────────────────────────
        tr_s = self._slider(screen, T("sfx_vol"),
                            self.sfx_vol, sx, y, sw, sh)
        rects["track_sfx"] = tr_s; y+=sc(80)

        # ── КНОПКИ ────────────────────────────────────
        r_apply = pygame.Rect(cx-sc(200), y, sc(180), sc(60))
        r_back  = pygame.Rect(cx+sc(20),  y, sc(180), sc(60))
        _btn(screen, r_apply, T("apply_btn"),(20,130,50),(60,200,80), font=font_sm)
        _btn(screen, r_back,  T("back_btn"), (80,30,30), (160,60,60), font=font_sm)
        rects["apply"] = r_apply; rects["back"] = r_back

        self._rects = rects
        return rects

    def handle_event(self, event):
        """Повертає 'back', 'apply' або None."""
        r = self._rects
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = event.pos
            if r.get("lang_ua") and r["lang_ua"].collidepoint(mx,my): self.lang="ua"
            if r.get("lang_en") and r["lang_en"].collidepoint(mx,my): self.lang="en"
            if r.get("apply")   and r["apply"].collidepoint(mx,my):   return "apply"
            if r.get("back")    and r["back"].collidepoint(mx,my):    return "back"
            # Слайдери — старт перетягування
            if r.get("track_music") and r["track_music"].collidepoint(mx,my):
                self._drag_music = True
            if r.get("track_sfx")   and r["track_sfx"].collidepoint(mx,my):
                self._drag_sfx   = True
        if event.type == pygame.MOUSEBUTTONUP:
            self._drag_music = False; self._drag_sfx = False
        if event.type == pygame.MOUSEMOTION:
            mx = event.pos[0]
            if self._drag_music and r.get("track_music"):
                tr = r["track_music"]
                self.music_vol = max(0.0,min(1.0,(mx-tr.x)/tr.w))
            if self._drag_sfx and r.get("track_sfx"):
                tr = r["track_sfx"]
                self.sfx_vol = max(0.0,min(1.0,(mx-tr.x)/tr.w))
        return None

settings_screen = SettingsScreen()
