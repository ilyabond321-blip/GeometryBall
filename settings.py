"""
Налаштування гри — зберігаються у settings.json.
"""
import json, os

SETTINGS_FILE = "settings.json"

_defaults = {
    "lang":      "ua",
    "music_vol": 0.75,
    "sfx_vol":   0.80,
}

_cfg = dict(_defaults)

def load():
    global _cfg
    if os.path.exists(SETTINGS_FILE):
        try:
            _cfg = {**_defaults, **json.load(open(SETTINGS_FILE))}
        except Exception:
            _cfg = dict(_defaults)

def save():
    json.dump(_cfg, open(SETTINGS_FILE, "w"), indent=2)

def get(key):
    return _cfg.get(key, _defaults.get(key))

def set(key, val):
    _cfg[key] = val
