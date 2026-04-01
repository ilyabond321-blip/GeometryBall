"""
Runner для кастомного уровня — использует таймлайн из editor.get_scripted_timeline().
"""
import pygame, math, random
from constants import *
import attacks as atk_module

# Границы игровой зоны в кастомном уровне (совпадают с editor.ED_LEFT / ED_RIGHT)
GL = 300  # PANEL_W_ED
GR = WIDTH

_timeline = []
_atk_idx  = 0
_pending  = []

def reset(timeline):
    global _timeline, _atk_idx, _pending
    _timeline = sorted(timeline, key=lambda x: x[0])
    _atk_idx  = 0
    _pending  = []
    atk_module.reset_attacks()

# Эффекты — кастомный уровень без них
def get_shake():     return (0, 0)
def get_bg_color():  return BG_LEVEL
def barriers_on():   return False
def get_barrier_w(): return 0

def _build(entry, phase):
    t  = entry["type"]
    GW = GR - GL
    if t == "laser_h":
        return {"type":"laser_h","phase":phase,"timer":0.0,"active_time":0.55,
                "data":{"y":int(entry["y"]*HEIGHT),"thick":sc(22)},"_eid":id(entry)}
    elif t == "laser_v":
        return {"type":"laser_v","phase":phase,"timer":0.0,"active_time":0.55,
                "data":{"x":int(GL+entry["x"]*GW),"thick":sc(22)},"_eid":id(entry)}
    elif t == "double_laser":
        return {"type":"double_laser","phase":phase,"timer":0.0,"active_time":0.55,
                "data":{"y":int(entry["y"]*HEIGHT),"x":int(GL+entry["x"]*GW),"thick":sc(20)},
                "_eid":id(entry)}
    elif t == "flying_spinner":
        side = entry.get("side","left"); cy = int(entry.get("cy_frac",0.5)*HEIGHT)
        L = sc(120); cx = GL-L if side=="left" else GR+L; vx = sc(5.5) if side=="left" else -5.5
        return {"type":"flying_spinner","phase":phase,"timer":0.0,"active_time":5.5,
                "data":{"cx":float(cx),"cy":float(cy),"vx":vx,"vy":0.0,
                        "angle":random.uniform(0,math.pi*2),
                        "speed":entry.get("speed",3.0),"length":L,"thick":sc(13)},
                "_eid":id(entry)}
    elif t == "blocks":
        seg = GW//10
        return {"type":"blocks","phase":phase,"timer":0.0,"active_time":3.2,
                "data":{"blocks":[{"x":GL+c*seg,"y":-sc(80),"vy":sc(9),"w":sc(72),"h":sc(72)}
                                   for c in entry.get("cols",[3,7])]},"_eid":id(entry)}
    elif t == "circles":
        side = entry.get("side","left"); circs=[]
        for i in range(5):
            if side=="left":    cx2,cy2,vx,vy=GL-50,110+i*(HEIGHT//6),7,0
            elif side=="right": cx2,cy2,vx,vy=GR+50,110+i*(HEIGHT//6),-7,0
            elif side=="top":   cx2,cy2,vx,vy=GL+160+i*((GW-320)//5),-50,0,7
            else:               cx2,cy2,vx,vy=GL+160+i*((GW-320)//5),HEIGHT+50,0,-7
            circs.append({"x":float(cx2),"y":float(cy2),"vx":vx,"vy":vy,"r":sc(28)})
        return {"type":"circles","phase":phase,"timer":0.0,"active_time":3.8,
                "data":{"side":side,"circs":circs},"_eid":id(entry)}
    return None

def update(dt, elapsed):
    global _atk_idx
    WARN = 2.0
    while _atk_idx < len(_timeline) and elapsed >= _timeline[_atk_idx][0]:
        wt, entry = _timeline[_atk_idx]
        atk = _build(entry, "warn")
        if atk:
            atk_module.attacks.append(atk)
            _pending.append({"atk":atk,"fire_at":wt+WARN})
        _atk_idx += 1
    for pw in _pending[:]:
        if elapsed >= pw["fire_at"]:
            a = pw["atk"]
            if a["phase"] == "warn": a["phase"]="active"; a["timer"]=0.0
            _pending.remove(pw)
    for atk in atk_module.attacks:
        atk["timer"] += dt
        if atk["phase"]=="active" and atk["timer"]>=atk["active_time"]:
            atk["phase"]="done"; continue
        if atk["phase"]=="active":
            tp = atk["type"]
            if tp=="blocks":
                for b in atk["data"]["blocks"]: b["y"]+=b["vy"]
            elif tp=="circles":
                for c in atk["data"]["circs"]: c["x"]+=c["vx"]; c["y"]+=c["vy"]
            elif tp=="flying_spinner":
                d=atk["data"]; d["cx"]+=d["vx"]; d["cy"]+=d["vy"]; d["angle"]+=d["speed"]*dt
                if d["cx"]<GL-400 or d["cx"]>GR+400: atk["phase"]="done"
            elif tp=="spinners":
                for sp in atk["data"]["spinners"]: sp["angle"]+=sp["speed"]*dt
    atk_module.attacks[:] = [a for a in atk_module.attacks if a["phase"]!="done"]
