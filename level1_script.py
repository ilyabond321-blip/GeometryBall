# BPM=172.3  BEAT=0.3482s  BAR=1.3929s  offset=0.025s
WARN_TIME = 2.0
LEVEL_END = 98.0

EFFECTS = [
    (41.0,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (44.4,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (47.8,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (51.2,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (54.6,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (58.0,  {"type": "shake", "duration": 0.25, "intensity": 6}),
    (66.0,  {"type": "shake", "duration": 1.2,  "intensity": 18}),
    (66.0,  {"type": "bg",    "color": (35, 5, 5), "fade_time": 1.5}),
    (66.0,  {"type": "barriers"}),
    (68.4,  {"type": "shake", "duration": 0.3, "intensity": 10}),
    (71.8,  {"type": "shake", "duration": 0.3, "intensity": 10}),
    (75.2,  {"type": "shake", "duration": 0.3, "intensity": 10}),
    (78.6,  {"type": "shake", "duration": 0.3, "intensity": 10}),
    (82.0,  {"type": "shake", "duration": 0.2, "intensity": 7}),
    (85.4,  {"type": "shake", "duration": 0.2, "intensity": 7}),
    (88.8,  {"type": "shake", "duration": 0.15, "intensity": 5}),
    (92.2,  {"type": "shake", "duration": 0.15, "intensity": 5}),
]

TIMELINE = [
    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 1: 5-16с — лазеры ЧЕРЕДУЮТСЯ: край / центр / край / центр
    # ══════════════════════════════════════════════════
    (3.60,  {"type": "laser_h", "y": 0.15}),    # край
    (4.99,  {"type": "laser_v", "x": 0.5}),     # центр
    (6.38,  {"type": "laser_h", "y": 0.85}),    # край
    (7.77,  {"type": "laser_v", "x": 0.12}),    # край
    (9.17,  {"type": "laser_h", "y": 0.5}),     # центр
    (10.56, {"type": "laser_v", "x": 0.88}),    # край
    (11.95, {"type": "laser_h", "y": 0.2}),     # край
    (13.35, {"type": "laser_v", "x": 0.5}),     # центр

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 2: 16-26с — лазеры по краям + 2 ящика
    # ══════════════════════════════════════════════════
    (14.74, {"type": "laser_h", "y": 0.1}),
    (15.44, {"type": "laser_v", "x": 0.1}),
    (16.13, {"type": "laser_h", "y": 0.9}),
    (16.83, {"type": "laser_v", "x": 0.9}),
    (17.52, {"type": "laser_h", "y": 0.15}),
    (18.22, {"type": "blocks",  "cols": [4]}),       # 1 ящик по центру
    (18.92, {"type": "laser_h", "y": 0.85}),
    (19.61, {"type": "laser_v", "x": 0.15}),
    (20.31, {"type": "laser_h", "y": 0.1}),
    (21.01, {"type": "laser_v", "x": 0.9}),
    (21.70, {"type": "laser_h", "y": 0.9}),
    (22.40, {"type": "blocks",  "cols": [3, 7]}),    # 2 ящика
    (23.09, {"type": "laser_h", "y": 0.2}),
    (23.79, {"type": "laser_v", "x": 0.8}),
    (25.18, {"type": "laser_h", "y": 0.8}),
    (25.88, {"type": "laser_v", "x": 0.2}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 3: 26-39с — 1 палка за раз + лазеры края + ящики
    # ══════════════════════════════════════════════════
    (26.58, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.3,  "speed": 2.2}),
    (27.27, {"type": "laser_h", "y": 0.15}),
    (27.97, {"type": "flying_spinner", "side": "right", "cy_frac": 0.7,  "speed": -2.2}),
    (28.67, {"type": "laser_v", "x": 0.88}),
    (29.36, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.6,  "speed": 2.8}),
    (30.06, {"type": "laser_h", "y": 0.85}),
    (30.76, {"type": "blocks",  "cols": [2, 8]}),    # 2 ящика по бокам
    (31.45, {"type": "laser_v", "x": 0.12}),
    (32.15, {"type": "flying_spinner", "side": "right", "cy_frac": 0.4,  "speed": -2.5}),
    (32.84, {"type": "laser_h", "y": 0.1}),
    (33.54, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.25, "speed": 3.0}),
    (34.24, {"type": "laser_v", "x": 0.9}),
    (34.93, {"type": "blocks",  "cols": [5]}),       # 1 ящик центр
    (35.63, {"type": "flying_spinner", "side": "right", "cy_frac": 0.75, "speed": -3.0}),
    (36.33, {"type": "laser_h", "y": 0.9}),
    (37.02, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5,  "speed": 2.5}),
    (37.72, {"type": "laser_v", "x": 0.15}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 4: 39-52с — двойные лазеры + 1 палка + ящики раз в 2 такта
    # ══════════════════════════════════════════════════
    (38.07, {"type": "double_laser",   "y": 0.15, "x": 0.15}),
    (38.76, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.4,  "speed": 2.5}),
    (39.46, {"type": "double_laser",   "y": 0.85, "x": 0.88}),
    (40.16, {"type": "laser_v",        "x": 0.12}),
    (40.50, {"type": "blocks",         "cols": [3, 6]}),  # 2 ящика
    (40.85, {"type": "double_laser",   "y": 0.15, "x": 0.85}),
    (41.55, {"type": "flying_spinner", "side": "right", "cy_frac": 0.7,  "speed": -3.0}),
    (41.90, {"type": "double_laser",   "y": 0.8,  "x": 0.18}),
    (42.59, {"type": "laser_v",        "x": 0.88}),
    (42.94, {"type": "double_laser",   "y": 0.2,  "x": 0.82}),
    (43.64, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.65, "speed": 3.2}),
    (43.99, {"type": "double_laser",   "y": 0.88, "x": 0.12}),
    (44.34, {"type": "blocks",         "cols": [2, 8]}),  # 2 ящика по бокам
    (44.68, {"type": "laser_v",        "x": 0.85}),
    (45.38, {"type": "double_laser",   "y": 0.15, "x": 0.88}),
    (45.73, {"type": "flying_spinner", "side": "right", "cy_frac": 0.25, "speed": -2.8}),
    (46.07, {"type": "double_laser",   "y": 0.85, "x": 0.15}),
    (46.77, {"type": "laser_v",        "x": 0.1}),
    (47.12, {"type": "double_laser",   "y": 0.2,  "x": 0.85}),
    (47.47, {"type": "blocks",         "cols": [4]}),     # 1 ящик центр
    (47.82, {"type": "flying_spinner", "side": "left",   "cy_frac": 0.5,  "speed": 2.5}),
    (48.17, {"type": "double_laser",   "y": 0.88, "x": 0.15}),
    (48.86, {"type": "laser_v",        "x": 0.9}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 5: 52-66с — пик: двойные + 1 палка поочерёдно + ящик раз в 3 такта
    # ══════════════════════════════════════════════════
    (49.21, {"type": "double_laser",   "y": 0.1,  "x": 0.1}),
    (49.91, {"type": "double_laser",   "y": 0.9,  "x": 0.9}),
    (50.26, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.3,  "speed": 3.5}),
    (50.60, {"type": "double_laser",   "y": 0.15, "x": 0.85}),
    (51.30, {"type": "double_laser",   "y": 0.85, "x": 0.1}),
    (51.65, {"type": "flying_spinner", "side": "right", "cy_frac": 0.7,  "speed": -3.5}),
    (52.00, {"type": "double_laser",   "y": 0.1,  "x": 0.9}),
    (52.69, {"type": "double_laser",   "y": 0.9,  "x": 0.1}),
    (53.04, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5,  "speed": 4.0}),
    (53.39, {"type": "double_laser",   "y": 0.2,  "x": 0.8}),
    (53.74, {"type": "blocks",         "cols": [2, 5, 8]}),  # 3 ящика
    (54.08, {"type": "double_laser",   "y": 0.8,  "x": 0.2}),
    (54.78, {"type": "double_laser",   "y": 0.1,  "x": 0.1}),
    (54.78, {"type": "flying_spinner", "side": "right", "cy_frac": 0.4,  "speed": -4.0}),
    (55.48, {"type": "double_laser",   "y": 0.9,  "x": 0.9}),
    (56.17, {"type": "double_laser",   "y": 0.15, "x": 0.85}),
    (56.52, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.6,  "speed": 4.2}),
    (56.87, {"type": "double_laser",   "y": 0.85, "x": 0.15}),
    (57.57, {"type": "double_laser",   "y": 0.1,  "x": 0.9}),
    (57.92, {"type": "flying_spinner", "side": "right", "cy_frac": 0.3,  "speed": -4.2}),
    (58.26, {"type": "double_laser",   "y": 0.9,  "x": 0.1}),
    (58.96, {"type": "double_laser",   "y": 0.2,  "x": 0.2}),
    (58.96, {"type": "blocks",         "cols": [3, 7]}),     # 2 ящика
    (59.66, {"type": "double_laser",   "y": 0.8,  "x": 0.8}),
    (59.66, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5,  "speed": 4.8}),
    (60.35, {"type": "double_laser",   "y": 0.15, "x": 0.15}),
    (61.05, {"type": "double_laser",   "y": 0.85, "x": 0.85}),
    (61.40, {"type": "flying_spinner", "side": "right", "cy_frac": 0.6,  "speed": -4.8}),
    (61.74, {"type": "double_laser",   "y": 0.1,  "x": 0.9}),
    (62.44, {"type": "double_laser",   "y": 0.9,  "x": 0.1}),
    (62.79, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.35, "speed": 5.0}),
    (63.14, {"type": "double_laser",   "y": 0.2,  "x": 0.8}),
    (63.83, {"type": "double_laser",   "y": 0.8,  "x": 0.2}),
    (64.18, {"type": "flying_spinner", "side": "right", "cy_frac": 0.65, "speed": -5.0}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 6: 66-78с — КРАСНЫЙ ФОН, 1 палка + редкие лазеры
    # ══════════════════════════════════════════════════
    (64.53, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.3,  "speed": 5.5}),
    (65.92, {"type": "flying_spinner", "side": "right", "cy_frac": 0.7,  "speed": -5.5}),
    (66.97, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.6,  "speed": 5.0}),
    (67.66, {"type": "blocks",         "cols": [2, 5, 8]}),  # 3 ящика
    (68.36, {"type": "flying_spinner", "side": "right", "cy_frac": 0.4,  "speed": -5.0}),
    (69.75, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.2,  "speed": 5.8}),
    (70.10, {"type": "laser_h",        "y": 0.1}),
    (70.80, {"type": "laser_v",        "x": 0.9}),
    (71.15, {"type": "flying_spinner", "side": "right", "cy_frac": 0.8,  "speed": -5.8}),
    (71.84, {"type": "laser_h",        "y": 0.9}),
    (72.19, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5,  "speed": 5.5}),
    (72.54, {"type": "laser_v",        "x": 0.1}),
    (72.89, {"type": "blocks",         "cols": [4, 6]}),     # 2 ящика
    (73.24, {"type": "laser_h",        "y": 0.15}),
    (73.93, {"type": "flying_spinner", "side": "right", "cy_frac": 0.35, "speed": -5.0}),
    (74.63, {"type": "laser_v",        "x": 0.88}),
    (75.33, {"type": "laser_h",        "y": 0.85}),
    (75.67, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5,  "speed": 4.5}),
    (76.02, {"type": "laser_v",        "x": 0.12}),
    (76.37, {"type": "flying_spinner", "side": "right", "cy_frac": 0.5,  "speed": -4.5}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 7: 78-90с — спад, редкие лазеры + 1 палка + ящики
    # ══════════════════════════════════════════════════
    (76.72, {"type": "laser_h", "y": 0.1}),
    (78.11, {"type": "laser_v", "x": 0.9}),
    (79.50, {"type": "laser_h", "y": 0.9}),
    (80.20, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.5, "speed": 3.5}),
    (80.90, {"type": "laser_v", "x": 0.1}),
    (81.59, {"type": "blocks",  "cols": [3, 5, 7]}),  # 3 ящика
    (82.29, {"type": "laser_h", "y": 0.15}),
    (83.00, {"type": "flying_spinner", "side": "right", "cy_frac": 0.5, "speed": -3.5}),
    (83.68, {"type": "laser_v", "x": 0.88}),
    (85.08, {"type": "laser_h", "y": 0.85}),
    (85.77, {"type": "flying_spinner", "side": "left",  "cy_frac": 0.4, "speed": 3.0}),
    (86.47, {"type": "laser_v", "x": 0.12}),

    # ══════════════════════════════════════════════════
    # СЕКЦИЯ 8: 90-98с — затихание, только одиночные лазеры
    # ══════════════════════════════════════════════════
    (87.86, {"type": "laser_h", "y": 0.2}),
    (89.95, {"type": "laser_v", "x": 0.8}),
    (91.34, {"type": "laser_h", "y": 0.8}),
    (92.74, {"type": "laser_v", "x": 0.2}),
]

def get_timeline():  return TIMELINE
def get_effects():   return EFFECTS
def get_level_end(): return LEVEL_END
