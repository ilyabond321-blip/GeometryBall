"""
Система локалізації — UA / EN.
Використання: from lang import T; T("play_btn")
"""

UA = {
    # Меню
    "play_btn":       "▶  ГРАТИ",
    "settings_btn":   "⚙  НАЛАШТУВАННЯ",
    "exit_hint":      "ESC — вихід   F11 — вікно",
    "select_level":   "ВИБІР РІВНЯ",
    "level_n":        "Рівень {}",
    "soon":           "🔒 Незабаром",
    "level_dur":      "{} сек",
    "editor_btn":     "✏️  Редактор рівнів",
    "back_hint":      "ESC — назад",
    # Гра
    "died":           "💀  ЗАГИНУВ!",
    "hud_hint":       "Стрілки — напрямок   ESC — меню   F11 — вікно",
    "time_deaths":    "⏱ {:.1f} с   💀 {}",
    # Перемога
    "win":            "ПЕРЕМОГА!",
    "deaths_count":   "Смертей: {}",
    "restart_hint":   "R — знову   ESC — меню",
    # Редактор
    "editor_title":   "РЕДАКТОР",
    "blocks_lbl":     "── БЛОКИ ──",
    "block":          "Блок",
    "half":           "Пів",
    "dark":           "Темний",
    "start_tool":     "4 Старт ▶",
    "finish_tool":    "5 Фініш 🏁",
    "erase_tool":     "6 Стерти",
    "attack_tool":    "7 Атака ⚡",
    "atk_lbl":        "── ТИП АТАКИ ──",
    "laser_h":        "Лазер →",
    "laser_v":        "Лазер ↓",
    "double_laser":   "2 Лазери",
    "flying_spinner": "Палиця",
    "blocks":         "Ящики",
    "circles":        "Кола",
    "atk_time_lbl":   "Час атаки (сек):",
    "atk_add":        "+Додати",
    "atk_list":       "Список атак:",
    "duration_lbl":   "Тривал.: {} сек",
    "clear_btn":      "🗑 Очистити",
    "save_btn":       "💾 Зберегти",
    "play_btn_ed":    "▶ ГРАТИ!",
    "tl_hint":        "ЛКМ на шкалу — поставити атаку  |  ПКМ — видалити",
    "esc_back":       "ESC — назад",
    # Налаштування
    "settings_title": "НАЛАШТУВАННЯ",
    "language":       "Мова / Language",
    "music_vol":      "Гучність музики",
    "sfx_vol":        "Гучність ефектів",
    "apply_btn":      "✔ Застосувати",
    "back_btn":       "← Назад",
    "lang_ua":        "🇺🇦 Українська",
    "lang_en":        "🇬🇧 English",
}

EN = {
    "play_btn":       "▶  PLAY",
    "settings_btn":   "⚙  SETTINGS",
    "exit_hint":      "ESC — exit   F11 — window",
    "select_level":   "SELECT LEVEL",
    "level_n":        "Level {}",
    "soon":           "🔒 Soon",
    "level_dur":      "{} sec",
    "editor_btn":     "✏️  Level Editor",
    "back_hint":      "ESC — back",
    "died":           "💀  YOU DIED!",
    "hud_hint":       "Arrows — direction   ESC — menu   F11 — window",
    "time_deaths":    "⏱ {:.1f} s   💀 {}",
    "win":            "YOU WIN!",
    "deaths_count":   "Deaths: {}",
    "restart_hint":   "R — retry   ESC — menu",
    "editor_title":   "EDITOR",
    "blocks_lbl":     "── BLOCKS ──",
    "block":          "Block",
    "half":           "Half",
    "dark":           "Dark",
    "start_tool":     "4 Start ▶",
    "finish_tool":    "5 Finish 🏁",
    "erase_tool":     "6 Erase",
    "attack_tool":    "7 Attack ⚡",
    "atk_lbl":        "── ATTACK TYPE ──",
    "laser_h":        "Laser →",
    "laser_v":        "Laser ↓",
    "double_laser":   "2 Lasers",
    "flying_spinner": "Stick",
    "blocks":         "Boxes",
    "circles":        "Circles",
    "atk_time_lbl":   "Attack time (sec):",
    "atk_add":        "+Add",
    "atk_list":       "Attack list:",
    "duration_lbl":   "Duration: {} sec",
    "clear_btn":      "🗑 Clear",
    "save_btn":       "💾 Save",
    "play_btn_ed":    "▶ PLAY!",
    "tl_hint":        "LMB on timeline — add attack  |  RMB — delete",
    "esc_back":       "ESC — back",
    "settings_title": "SETTINGS",
    "language":       "Language / Мова",
    "music_vol":      "Music volume",
    "sfx_vol":        "SFX volume",
    "apply_btn":      "✔ Apply",
    "back_btn":       "← Back",
    "lang_ua":        "🇺🇦 Українська",
    "lang_en":        "🇬🇧 English",
}

_lang = "ua"

def set_lang(code):
    global _lang
    _lang = code

def get_lang():
    return _lang

def T(key, *args):
    table = UA if _lang == "ua" else EN
    s = table.get(key, key)
    return s.format(*args) if args else s
