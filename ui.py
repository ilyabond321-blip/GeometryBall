import pygame
import random
from constants import *

stars = [(random.randint(0, BASE_WIDTH), random.randint(0, BASE_HEIGHT), random.random()) for _ in range(200)]
btn_play = pygame.Rect(BASE_WIDTH//2-160, BASE_HEIGHT//2+40, 320, 80)

def level_btn(i):
    bw, bh, gap = 260, 120, 60
    sx = BASE_WIDTH//2-(3*bw+2*gap)//2
    return pygame.Rect(sx+(i-1)*(bw+gap), BASE_HEIGHT//2-bh//2, bw, bh)

def _stars(screen):
    for sx,sy,br in stars:
        c = int(br*180)
        pygame.draw.circle(screen, (c,c,c+40), (sx,sy), 1)

def draw_menu(screen):
    screen.fill(BG_MENU); _stars(screen)
    # Текст та кнопки малюються як зазвичай, але screen тут - це virtual_surface
    sh = font_big.render("GEOMETRY BALL", True, (80,50,0))
    tx = font_big.render("GEOMETRY BALL", True, YELLOW)
    screen.blit(sh, (BASE_WIDTH//2-sh.get_width()//2+5, BASE_HEIGHT//3-30+5))
    screen.blit(tx, (BASE_WIDTH//2-tx.get_width()//2,   BASE_HEIGHT//3-30))
    
    # Використовуємо глобальну змінну миші, яку ми вирахували в main.py
    # Оскільки ui.py не бачить змінну mouse з циклу main, 
    # в ідеалі передати її як аргумент, або перерахувати тут:
    mx, my = pygame.mouse.get_pos()
    sw, sh_real = pygame.display.get_surface().get_size()
    vmouse = (mx * (BASE_WIDTH/sw), my * (BASE_HEIGHT/sh_real))
    
    hov = btn_play.collidepoint(vmouse)
    pygame.draw.rect(screen, (60,180,80) if hov else (40,150,60), btn_play, border_radius=18)
    pt = font_med.render("▶  ГРАТИ", True, WHITE)
    screen.blit(pt, (btn_play.centerx-pt.get_width()//2, btn_play.centery-pt.get_height()//2))

def draw_level_select(screen):
    screen.fill(BG_MENU); _stars(screen)
    mx, my = pygame.mouse.get_pos()
    sw, sh_real = pygame.display.get_surface().get_size()
    vmouse = (mx * (BASE_WIDTH/sw), my * (BASE_HEIGHT/sh_real))
    
    t = font_med.render("ВИБІР РІВНЯ", True, YELLOW)
    screen.blit(t, (BASE_WIDTH//2-t.get_width()//2, BASE_HEIGHT//4-30))
    for i in range(1, 4):
        btn = level_btn(i); locked = i > 1
        hov = btn.collidepoint(vmouse) and not locked
        col = (60,120,200) if hov else (40,90,160)
        if locked: col = (40,40,60)
        pygame.draw.rect(screen, col, btn, border_radius=16)
        num = font_med.render(f"Уровень {i}", True, WHITE if not locked else GRAY)
        screen.blit(num, (btn.centerx-num.get_width()//2, btn.centery-num.get_height()//2))

    ed_btn = pygame.Rect(BASE_WIDTH//2-180, BASE_HEIGHT*3//4-30, 360, 70)
    pygame.draw.rect(screen, (80,50,160), ed_btn, border_radius=16)
    et = font_sm.render("✏️  Редактор рівнів", True, WHITE)
    screen.blit(et, (ed_btn.centerx-et.get_width()//2, ed_btn.centery-et.get_height()//2))
    return ed_btn

def draw_win(screen, deaths):
    screen.fill((5,25,5)); _stars(screen)
    t1 = font_big.render("Перемога!", True, GREEN)
    screen.blit(t1, (BASE_WIDTH//2-t1.get_width()//2, BASE_HEIGHT//3))
