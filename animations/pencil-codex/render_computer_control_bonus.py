#!/usr/bin/env python3
"""Two silent, editable pencil cutaways for the computer-control bonus nugget.

Reuses the established notebook paper and palette. All new drawings are native
paths; there are no external images, browser recordings, or private work data.
Run with --prepare-only for visual checkpoints before encoding the masters.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import render_agentic_loop as established

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
AUDIT = HERE / "source" / "computer_control_bonus"
PLAYER = HERE / "interactive" / "computer_control_bonus"
W, H, FPS = 1920, 1080, 30
INK = (51, 50, 62)
TEAL = (46, 167, 154)
PAPER = (250, 247, 239)
WASH = (218, 237, 229)
WOOD = (225, 203, 168)
PALE_WOOD = (240, 228, 205)
RUST = (183, 104, 68)
MUTED = (108, 112, 112)
FONT = HERE.parent / "assets" / "fonts" / "PatrickHand-Regular.ttf"
SCENES = {
    "computer_control": {
        "title": "Computer control", "duration": 25,
        "stages": [("Open the browser", 0, 5), ("Complete the task", 5, 14),
                   ("Already signed in", 14, 25)],
        "samples": [1, 4.5, 7, 9.8, 12.5, 17.5, 22.5],
    },
    "saloon_doors": {
        "title": "The saloon doors", "duration": 31,
        "stages": [("An easy entrance", 0, 12), ("Board it up", 12, 17),
                   ("Try that again", 17, 31)],
        "samples": [2, 5.7, 7.4, 10.5, 15.7, 21.7, 22.8, 24.5, 28],
    },
}


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def progress(t, a, b):
    return ease((t - a) / (b - a))


def lerp(a, b, p):
    return a + (b - a) * p


@lru_cache(maxsize=40)
def font(size):
    return ImageFont.truetype(str(FONT), size)


class Sketch:
    """Soft wash, imperfect pencil outline, and a faint second pencil pass."""
    def __init__(self, layer, variant=0):
        self.layer = layer
        self.d = ImageDraw.Draw(layer)
        self.v = variant

    def line(self, points, color=INK, width=3, wobble=0.65):
        pts = []
        for a, b in zip(points, points[1:]):
            n = max(2, math.ceil(math.dist(a, b) / 12))
            for i in range(n):
                u = i / n
                x, y = lerp(a[0], b[0], u), lerp(a[1], b[1], u)
                dx = math.sin(y * .059 + x * .017 + self.v * 2.1) * wobble
                dy = math.sin(x * .043 - y * .013 + self.v * 1.7) * wobble
                pts.append((x + dx, y + dy))
        pts.append(points[-1])
        self.d.line(pts, fill=(*color, 225), width=width, joint="curve")
        self.d.line([(x + 1.4, y - 1.0) for x, y in pts],
                    fill=(*color, 50), width=1, joint="curve")

    def poly(self, pts, fill=None, color=INK, width=3):
        if fill:
            self.d.polygon(pts, fill=(*fill, 255))
        self.line(pts + [pts[0]], color, width)

    def rect(self, box, fill=None, color=INK, width=3, radius=0):
        x0, y0, x1, y1 = box
        if not radius:
            self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, color, width)
            return
        pts = []
        for cx, cy, start in [(x1-radius,y0+radius,-90), (x1-radius,y1-radius,0),
                              (x0+radius,y1-radius,90), (x0+radius,y0+radius,180)]:
            pts += [(cx+radius*math.cos(math.radians(a)),cy+radius*math.sin(math.radians(a)))
                    for a in range(start,start+91,10)]
        self.poly(pts, fill, color, width)

    def oval(self, box, fill=None, color=INK, width=3):
        x0,y0,x1,y1=box
        pts=[((x0+x1)/2+(x1-x0)/2*math.cos(a*math.tau/64),
              (y0+y1)/2+(y1-y0)/2*math.sin(a*math.tau/64)) for a in range(65)]
        self.poly(pts,fill,color,width)

    def text(self, xy, value, size=38, color=INK, anchor="la"):
        self.d.text(xy,value,font=font(size),fill=(*color,255),anchor=anchor)


def new_layer():
    return Image.new("RGBA", (W, H))


def caption(s, value):
    s.text((W/2, 37), value, 52, anchor="ma")


def check(s, x, y, scale=1, color=TEAL):
    s.line([(x-12*scale,y),(x-3*scale,y+10*scale),(x+17*scale,y-13*scale)],color,5)


def cursor(s, xy, t, clicks):
    x, y = xy
    for at in clicks:
        q = (t-at)/.5
        if 0 <= q <= 1:
            r=12+36*q
            s.oval((x-r,y-r,x+r,y+r),color=TEAL,width=3)
    s.poly([(x,y),(x+3,y+43),(x+14,y+32),(x+24,y+51),
            (x+33,y+46),(x+22,y+27),(x+40,y+24)],PAPER,TEAL,4)


def travel(t, keys):
    if t<=keys[0][0]: return keys[0][1]
    for (a,p),(b,q) in zip(keys,keys[1:]):
        if a<=t<=b:
            u=progress(t,a,b)
            return lerp(p[0],q[0],u),lerp(p[1],q[1],u)
    return keys[-1][1]


def app_icon(s, x, y, name, selected=False):
    s.rect((x-32,y-30,x+32,y+28),WASH if selected else PAPER,radius=10)
    if name=="Browser":
        s.oval((x-20,y-20,x+20,y+20),color=TEAL)
        s.oval((x-9,y-20,x+9,y+20),color=TEAL,width=2)
        s.line([(x-20,y),(x+20,y)],TEAL,2)
    elif name=="Mail":
        s.rect((x-21,y-14,x+21,y+15),color=MUTED,width=2)
        s.line([(x-21,y-14),(x,y+3),(x+21,y-14)],MUTED,2)
    elif name=="Files":
        s.poly([(x-23,y-13),(x-5,y-13),(x,y-20),(x+21,y-20),
                (x+21,y+17),(x-23,y+17)],PALE_WOOD,width=2)
    else:
        s.rect((x-20,y-20,x+20,y+20),color=MUTED,width=2)
        s.line([(x-20,y-7),(x+20,y-7)],MUTED,2)
        s.text((x,y-6),"12",23,anchor="ma")


def board(s,t):
    s.text((294,390),"Team board",43)
    s.text((294,442),"Website refresh",28,MUTED)
    for x,title in [(294,"To do"),(744,"In progress"),(1194,"Done")]:
        s.rect((x,495,x+393,747),(247,247,240),color=(188,192,184),radius=13,width=2)
        s.text((x+23,508),title,33)
        s.line([(x+22,553),(x+372,553)],(188,192,184),2)
    s.rect((317,576,664,687),PAPER,color=(149,152,146),radius=8,width=2)
    s.text((337,588),"Plan team demo",32)
    s.text((337,641),"TEAM-23",23,MUTED)
    x=lerp(767,1217,progress(t,11.5,12.2))
    s.rect((x,576,x+347,710),WASH if t>=10 else PAPER,color=TEAL,radius=8)
    s.text((x+19,589),"Update onboarding",30)
    s.text((x+19,626),"guide",30)
    s.text((x+19,673),"TEAM-24",23,MUTED)
    if t>=12.2: check(s,x+305,679,.7)


def computer_scene(t,variant):
    layer=new_layer(); s=Sketch(layer,variant)
    caption(s,"An agent can use the screen, too.")
    # Monitor, stand, and a few sketched physical desk details anchor the UI.
    s.poly([(889,887),(1031,887),(1050,947),(870,947)],(232,231,223))
    s.oval((827,935,1095,958),PAPER,width=3)
    s.rect((153,133,1767,902),PAPER,radius=25,width=4)
    s.rect((179,158,1741,863),(233,238,230),radius=10,width=2)
    s.line([(180,205),(1740,205)],MUTED,2)
    s.text((209,161),"Work desktop",30)
    s.oval((1564,171,1586,193),PAPER,color=TEAL,width=2)
    s.text((1601,161),"You",30)
    s.text((1698,168),"9:41",23,anchor="ra")
    s.oval((948,873,970,885),color=MUTED,width=2)
    # A permanent, plain-language control indicator makes the actor explicit.
    s.rect((216,222,506,269),WASH,color=TEAL,radius=14,width=2)
    s.oval((232,234,253,255),TEAL,color=TEAL,width=1)
    s.text((268,224),"Agent controlling",29)
    if t<3:
        s.text((960,397),"Your work, already open to you",40,anchor="ma")
        for x,name in [(725,"Browser"),(960,"Files"),(1195,"Calendar")]:
            app_icon(s,x,539,name)
            s.text((x,582),name,30,anchor="ma")
    # Dock is visible both before and after the browser opens.
    s.rect((711,786,1208,849),PAPER,color=(172,177,169),radius=18,width=2)
    for x,name in [(770,"Browser"),(897,"Mail"),(1023,"Files"),(1150,"Calendar")]:
        app_icon(s,x,817,name,t>=3 and name=="Browser")
    if t>=3:
        s.rect((247,282,1673,764),PAPER,radius=12,width=3)
        s.rect((247,282,1673,347),(236,235,225),radius=12,width=2)
        for i in range(3): s.oval((265+i*19,301,276+i*19,312),color=MUTED,width=2)
        active="Tasks" if t<16.3 else "Docs" if t<20.3 else "Calendar"
        for x,title in [(375,"Tasks"),(565,"Docs"),(755,"Calendar")]:
            if title==active:
                s.rect((x-18,290,x+152,339),PAPER,color=TEAL,radius=8,width=2)
            s.text((x,294),title,29)
        s.text((990,298),"work.example / team",27,MUTED)
        s.oval((1487,296,1519,328),WASH,color=TEAL,width=2)
        s.text((1503,295),"Y",24,TEAL,anchor="ma")
        s.text((1532,297),"You",27)
        if active=="Tasks": board(s,t)
        elif active=="Docs":
            s.text((294,385),"Team documents",43)
            for i,title in enumerate(["Onboarding guide","Team handbook","Project notes"]):
                y=477+i*79
                s.rect((310,y,344,y+43),PAPER,color=TEAL,width=2)
                for k in range(3): s.line([(318,y+12+k*9),(335,y+12+k*9)],MUTED,1)
                s.text((372,y-2),title,34)
                s.line([(310,y+59),(1565,y+59)],(204,203,190),1)
        else:
            s.text((294,385),"Team calendar",43)
            for i,name in enumerate(["MON","TUE","WED","THU","FRI"]):
                x=305+i*256
                s.text((x+111,466),name,28,MUTED,anchor="ma")
                s.rect((x,506,x+223,707),PAPER,color=(195,195,182),width=2)
            s.rect((575,546,769,636),WASH,color=TEAL,radius=8,width=2)
            s.text((595,556),"Team sync",29)
            s.text((595,597),"10:00",23,MUTED)
            s.rect((1088,596,1282,687),PALE_WOOD,color=RUST,radius=8,width=2)
            s.text((1106,610),"Project demo",27)
    if 5.7<=t<11.5:
        # A real sequence of observable controls: open ticket, dropdown, Done.
        s.rect((523,372,1412,745),PAPER,color=INK,radius=13,width=3)
        s.line([(1360,394),(1380,414)],MUTED,3)
        s.line([(1360,414),(1380,394)],MUTED,3)
        s.text((563,397),"TEAM-24",25,MUTED)
        s.text((563,438),"Update onboarding guide",44)
        s.text((563,514),"Status",30,MUTED)
        done=t>=10
        s.rect((563,561,983,622),WASH if done else PALE_WOOD,color=TEAL if done else INK,radius=9)
        s.text((586,568),"Done" if done else "In progress",34)
        s.line([(939,585),(950,595),(961,585)],INK,3)
        s.text((563,662),"Saved" if done else "Assignee: You",30,TEAL if done else MUTED)
        if done: check(s,690,685,.6)
        if 8.2<=t<10:
            s.rect((563,624,983,738),PAPER,color=INK,radius=6,width=2)
            s.text((590,631),"In progress",30,MUTED)
            s.rect((570,683,977,731),WASH,color=TEAL,width=1)
            s.text((590,684),"Done",32)
    # Explicit illustrated task caption below the monitor, not extra prose in UI.
    if t<14:
        s.text((960,985),'“Move the onboarding task to Done.”',42,anchor="ma")
    else:
        s.text((960,985),"Already signed in. Same available access.",42,anchor="ma")
        if t<16:
            s.oval((1467,279,1618,341),color=TEAL,width=4)
    xy=travel(t,[(0,(1390,684)),(1,(1270,659)),(2.6,(725,539)),
                 (3.2,(725,539)),(5.5,(909,619)),(6.3,(1000,508)),
                 (8.1,(930,585)),(8.5,(930,585)),(9.8,(747,709)),
                 (10.4,(747,709)),(11.3,(1370,404)),(13,(1497,687)),
                 (14.8,(1570,315)),(15.3,(1570,315)),(16.1,(625,315)),
                 (17.4,(719,501)),(19.2,(813,566)),(20.1,(805,315)),
                 (21.6,(692,591)),(23,(1415,715))])
    cursor(s,xy,t,[2.85,5.55,8.1,9.85,11.35,16.15,20.15])
    return layer


def hat(s, center, tilt=0):
    # Local coordinates are transformed with the head: brim + pinched crown.
    x,y=center
    def pts(values):
        a=math.radians(tilt)
        return [(x+px*math.cos(a)-py*math.sin(a),y+px*math.sin(a)+py*math.cos(a)) for px,py in values]
    s.poly(pts([(-57,1),(-51,-55),(-26,-69),(0,-53),(31,-67),(54,-52),(61,6)]),WOOD,width=4)
    s.poly(pts([(-55,-11),(57,-9),(60,6),(-57,6)]),(162,129,98),width=2)
    s.poly(pts([(-101,-8),(-78,3),(-39,8),(22,10),(74,1),(102,-14),
                 (96,7),(68,22),(0,28),(-65,18),(-93,5)]),WOOD,width=4)
    s.line(pts([(-36,-52),(-23,-36),(2,-29),(27,-36),(39,-51)]),RUST,2)


def cowboy(variant, phase=0, lean=0, seated=False, surprise=False, hat_lift=0):
    """An articulated, tipsy cowboy; drawn locally so he can recede in depth."""
    layer=Image.new("RGBA",(430,520)); s=Sketch(layer,variant)
    # Character feet are at (215, 488); proportions intentionally cartoonish.
    cx=213
    stride=math.sin(phase)*23 if not seated else 0
    hip=(cx+lean*.32,350 if not seated else 414)
    shoulder=(cx+lean,265 if not seated else 322)
    head=(cx+lean*1.4,203 if not seated else 260)
    # Boots and bent denim legs; no weapons.
    legs=[((hip[0]-23,hip[1]),(185+stride,410),(170-stride*.6,480)),
          ((hip[0]+23,hip[1]),(244-stride,415),(254+stride*.65,480))]
    if seated:
        legs=[((hip[0]-23,hip[1]),(158,448),(116,483)),
              ((hip[0]+23,hip[1]),(278,441),(329,480))]
    for a,b,c in legs:
        s.line([a,b,c],(111,126,127),28,0)
        s.line([(a[0]-14,a[1]),(b[0]-13,b[1]),(c[0]-10,c[1])],INK,3)
        s.line([(a[0]+14,a[1]),(b[0]+13,b[1]),(c[0]+10,c[1])],INK,3)
        x,y=c
        s.poly([(x-15,y-27),(x+13,y-27),(x+16,y-7),(x+38,y-1),
                (x+38,y+9),(x-19,y+9)],(163,128,98),width=3)
        s.line([(x-17,y+3),(x+36,y+3)],INK,2)
    # Shirt, vest, belt and oversized buckle.
    sx,sy=shoulder; hx,hy=hip
    s.poly([(sx-38,sy-16),(sx+35,sy-16),(hx+43,hy+8),(hx-45,hy+8)],
           (210,230,219),width=4)
    s.poly([(sx-39,sy-17),(sx-9,sy-12),(hx-6,hy-8),(hx-40,hy+2)],WOOD,width=3)
    s.poly([(sx+10,sy-12),(sx+37,sy-17),(hx+40,hy+2),(hx+7,hy-8)],WOOD,width=3)
    s.poly([(hx-43,hy-6),(hx+43,hy-6),(hx+41,hy+9),(hx-42,hy+9)],(142,111,90),width=2)
    s.rect((hx-13,hy-11,hx+13,hy+14),PALE_WOOD,width=3,radius=3)
    # Arms, one balancing ahead and one with a loosely held bottle.
    arm_swing=math.sin(phase)*15
    left=[(sx-35,sy),(sx-72,sy+39+arm_swing),(sx-85,sy+84+arm_swing)]
    right=[(sx+33,sy),(sx+68,sy+24-arm_swing),(sx+83,sy+59-arm_swing)]
    if surprise:
        left=[(sx-35,sy),(sx-76,sy-34),(sx-93,sy-72)]
        right=[(sx+33,sy),(sx+72,sy-29),(sx+86,sy-67)]
    for arm in [left,right]:
        s.line(arm,(196,219,210),19,0)
        s.line(arm,INK,3)
        x,y=arm[-1];s.oval((x-10,y-10,x+10,y+12),(238,216,188),width=2)
    bx,by=left[-1]
    if not surprise and not seated:
        s.poly([(bx-7,by+4),(bx+5,by+4),(bx+5,by+20),(bx+12,by+27),
                (bx+9,by+70),(bx-13,by+69),(bx-15,by+26),(bx-7,by+18)],(174,163,114),width=2)
        s.rect((bx-12,by+36,bx+10,by+55),PALE_WOOD,width=1)
    # Neck, bandana, head, ears, hair and sleepy expression.
    xx,yy=head
    s.poly([(xx-15,yy+34),(xx+16,yy+34),(sx+13,sy-9),(sx-11,sy-9)],(238,216,188),width=2)
    s.poly([(sx-24,sy-19),(sx+24,sy-19),(sx+3,sy+15)],TEAL,width=2)
    s.poly([(sx+2,sy+4),(sx+27,sy+32),(sx+30,sy+6)],TEAL,width=2)
    s.oval((xx-49,yy-20,xx-29,yy+7),(238,216,188),width=2)
    s.oval((xx+31,yy-20,xx+51,yy+7),(238,216,188),width=2)
    s.oval((xx-39,yy-48,xx+40,yy+47),(241,220,192),width=3)
    for dx in [-28,29]:
        s.oval((xx+dx-9,yy+7,xx+dx+9,yy+17),(230,165,146),color=(230,165,146),width=1)
    if surprise:
        for dx in [-15,16]: s.oval((xx+dx-5,yy-13,xx+dx+5,yy+1),PAPER,width=2)
        s.oval((xx-6,yy+21,xx+9,yy+37),PAPER,width=2)
    else:
        s.line([(xx-26,yy-5),(xx-13,yy-1),(xx-6,yy-5)],INK,3)
        s.line([(xx+7,yy-9),(xx+16,yy-6),(xx+26,yy-10)],INK,3)
        s.line([(xx-6,yy+30),(xx+7,yy+32),(xx+14,yy+26)],INK,2)
    s.line([(xx+2,yy-4),(xx+8,yy+12),(xx-1,yy+15)],RUST,2)
    s.poly([(xx,yy+15),(xx-13,yy+13),(xx-24,yy+25),(xx-7,yy+24),(xx+1,yy+19),
            (xx+10,yy+25),(xx+28,yy+21),(xx+14,yy+12)],(113,88,70),width=2)
    hat(s,(xx,yy-40-hat_lift),-9 if not surprise else 9)
    return layer


def place_cowboy(canvas,variant,x,y,scale,phase,lean=0,seated=False,surprise=False,hat_lift=0,opacity=1):
    actor=cowboy(variant,phase,lean,seated,surprise,hat_lift)
    actor=actor.resize((round(actor.width*scale),round(actor.height*scale)),Image.Resampling.LANCZOS)
    if opacity<1:
        actor.putalpha(actor.getchannel("A").point(lambda a:round(a*opacity)))
    canvas.alpha_composite(actor,(round(x-215*scale),round(y-488*scale)))


def door(s,side,opening):
    hinge=1109 if side==0 else 1561
    direction=1 if side==0 else -1
    w=216*(1-.92*opening)
    top=467+opening*31
    pts=[(hinge,436),(hinge+direction*w*.35,445+opening*15),
         (hinge+direction*w*.72,top+24),(hinge+direction*w,top+9),
         (hinge+direction*w,737-opening*21),(hinge,755)]
    s.poly(pts,PALE_WOOD,width=4)
    for u in [.2,.4,.6,.8]:
        x=hinge+direction*w*u
        s.line([(x,473+opening*21),(x,721-opening*8)],(168,141,108),2)
    for yy in [491,689]:
        s.line([(hinge+direction*8,yy),(hinge+direction*(w-7),yy+opening*16)],RUST,3)
    for yy in [488,696]: s.rect((hinge-9,yy-10,hinge+9,yy+12),(141,133,119),width=2)


def plank(s,index,p):
    # Planks fly into place and remain fixed. Nails visibly join them to frame.
    y=[491,614,727][index]-190*(1-p)
    x=1043+(1-p)*(-170 if index%2==0 else 230)
    slope=[-22,21,-18][index]
    pts=[(x,y),(x+589,y+slope),(x+588,y+slope+68),(x+2,y+68)]
    s.poly(pts,WOOD,width=4)
    for row in [19,45]:
        s.line([(x+18,y+row),(x+167,y+row+slope*.3+3),
                (x+385,y+row+slope*.65-2),(x+565,y+row+slope)],(164,129,94),2)
    s.oval((x+222,y+26+slope*.4,x+255,y+40+slope*.4),color=(164,129,94),width=2)
    for nx in [x+44,x+546]:
        ny=y+34+(nx-x)/589*slope
        s.line([(nx-5,ny-5),(nx+5,ny+5)],INK,3)
        s.line([(nx-5,ny+5),(nx+5,ny-5)],INK,3)


def saloon_scene(t,variant):
    layer=new_layer();s=Sketch(layer,variant)
    caption(s,"A wide-open front door" if t<12 else "For now, board it up.")
    # A generous stage leaves a long approach, making both attempts readable.
    s.line([(227,914),(656,911),(1017,921),(1700,912)],INK,3)
    s.line([(307,934),(669,938),(960,934)],(182,175,156),2)
    s.poly([(1027,872),(1639,872),(1683,910),(986,910)],(231,220,197),width=3)
    s.rect((1027,296,1640,871),(240,231,211),width=4)
    for x in [1053,1080,1604,1626]:s.line([(x,311),(x,855)],(181,158,125),2)
    s.rect((1097,321,1572,849),(222,216,197),width=4)
    # Sparse cross-hatching gives the interior depth without looking ominous.
    for x in range(1125,1570,38):s.line([(x,343),(min(1552,x+90),445)],(193,182,158),1)
    s.line([(1140,379),(1520,379)],(185,173,151),2)
    s.rect((1009,207,1660,317),PALE_WOOD,width=4)
    s.text((1335,215),"SALOON",74,anchor="ma")
    s.line([(1032,234),(1072,234)],RUST,2)
    s.line([(1594,234),(1634,234)],RUST,2)
    s.line([(1024,303),(1644,303)],(175,145,107),2)
    # One scruffy cactus, dust marks, and a horizon: enough to say Western.
    s.line([(308,876),(310,751),(329,737),(344,752),(343,868)],(129,152,127),21,0)
    s.line([(312,813),(278,806),(276,776)],(129,152,127),17,0)
    s.line([(339,831),(371,816),(372,787)],(129,152,127),17,0)
    s.line([(310,875),(312,754),(325,747),(336,754),(336,874)],INK,3)
    s.line([(312,815),(276,812),(268,801),(268,777)],INK,2)
    s.line([(341,831),(374,822),(381,810),(381,787)],INK,2)
    for x,y in [(440,901),(570,935),(885,894),(1735,903)]:
        s.line([(x,y),(x+17,y-3),(x+32,y+1)],(168,150,123),2)
    opened=0
    if 5.4<=t<7.7:opened=progress(t,5.4,6.2)
    elif 7.7<=t<11:opened=abs(math.cos((t-7.7)*5))*math.exp(-(t-7.7)*1.25)
    # Character recedes *behind* open doors only after crossing the threshold.
    if 6.25<=t<8.7:
        p=progress(t,6.25,8.7)
        place_cowboy(layer,variant,lerp(1295,1340,p),lerp(858,791,p),
                     lerp(.94,.55,p),t*8,math.sin(t*4)*10,opacity=1-progress(t,7.8,8.7))
    door(s,0,opened);door(s,1,opened)
    # Reinforced posts drawn last pin the doors and the boards to the same place.
    for x in [1083,1565]:s.rect((x,316,x+28,878),WOOD,width=3)
    if t>=12:
        for i in range(3):
            p=progress(t,12.4+i*.95,13.05+i*.95)
            if p>0:
                plank(s,i,p)
                # Small nail-impact rays; no explosion or breaking boards.
                dt=t-(13.05+i*.95)
                if 0<=dt<.25:
                    xx=1093; yy=[510,665,748][i]
                    for a in [0,.9,2.2,3.4,4.8]:
                        s.line([(xx+math.cos(a)*13,yy+math.sin(a)*13),
                                (xx+math.cos(a)*28,yy+math.sin(a)*28)],RUST,3)
    if t<6.25:
        p=progress(t,.7,6.25)
        x=lerp(435,1295,p);y=lerp(919,858,p)
        moving=.7<t<6.25
        sway=math.sin(t*4.7)*13 if moving else 0
        place_cowboy(layer,variant,x,y-abs(math.sin(t*8))*5 if moving else y,1,
                     t*8 if moving else 0,sway)
        if 1.7<t<3.6:
            s.text((x-99,y-421),"hic!",34,RUST)
            s.oval((x-49,y-390,x-38,y-379),color=RUST,width=2)
            s.oval((x-36,y-368,x-29,y-361),color=RUST,width=2)
    elif 17<=t<22.2:
        p=progress(t,17.2,22.2)
        x=lerp(435,1285,p);y=lerp(919,858,p)
        place_cowboy(layer,variant,x,y-abs(math.sin(t*8))*5,1,t*8,
                     math.sin(t*4.7)*13+progress(t,21.65,22.2)*16)
        if 18.1<t<19.4:s.text((x-90,y-420),"hic!",34,RUST)
    elif 22.2<=t<23.2:
        p=progress(t,22.2,23.2)
        # No frame lets him cross the boarded threshold: he recoils outward.
        x=lerp(1285,1129,p);y=lerp(858,916,p)
        place_cowboy(layer,variant,x,y,1,0,-28*math.sin(math.pi*p),
                     surprise=True,hat_lift=77*math.sin(math.pi*p))
        if t<22.75:
            s.text((1450,399),"bonk",42,RUST)
            for a in [-1.1,-.6,.1]:
                s.line([(1375+math.cos(a)*28,507+math.sin(a)*28),
                        (1375+math.cos(a)*54,507+math.sin(a)*54)],RUST,4)
    elif t>=23.2:
        p=progress(t,23.2,23.7)
        place_cowboy(layer,variant,1129,916,1,0,-9,seated=True,
                     surprise=t<25.1,hat_lift=28*(1-p))
        # Settling dust and a last, puzzled look hold for the voiceover.
        if t<24.15:
            q=progress(t,23.2,24.15)
            for xx in [948,1000,1260,1320]:
                s.oval((xx-12-q*14,925-q*18,xx+12+q*14,937-q*18),
                       color=(193,174,142),width=2)
        if t>=25.4:
            s.text((958,531),"?",60,INK)
    if t>=22.2:
        # His bottle slips from his hand, then stays on the ground after impact.
        p=progress(t,22.2,23.2)
        bx=lerp(1187,989,p);by=lerp(734,919,p)-61*math.sin(math.pi*p)
        s.poly([(bx-8,by-7),(bx+9,by-9),(bx+15,by-19),(bx+50,by-22),
                (bx+55,by+2),(bx+17,by+9),(bx+11,by+1),(bx-7,by+2)],
               (174,163,114),width=2)
        s.poly([(bx+25,by-19),(bx+40,by-21),(bx+45,by+5),(bx+29,by+7)],PALE_WOOD,width=1)
    if t<12:
        s.text((605,1000),"Walk right in.",40,anchor="ma")
    elif t<17:
        s.text((605,1000),"Close off the entrance.",40,anchor="ma")
    else:
        s.text((605,1000),"Same cowboy. Different outcome.",40,anchor="ma")
    return layer


def compose(scene,t,backgrounds,variant=None):
    v=int(t*FPS)//5%3 if variant is None else variant
    canvas=backgrounds[v].copy()
    art=(computer_scene if scene=="computer_control" else saloon_scene)(t,v)
    canvas.alpha_composite(art)
    return canvas.convert("RGB")


def audits(scene, backgrounds):
    AUDIT.mkdir(parents=True,exist_ok=True)
    thumbs=[]
    for t in SCENES[scene]["samples"]:
        frame=compose(scene,t,backgrounds)
        frame.save(AUDIT/f"{scene}_{t:05.1f}.jpg",quality=94)
        thumb=frame.resize((640,360),Image.Resampling.LANCZOS)
        card=Image.new("RGB",(640,397),PAPER)
        card.paste(thumb)
        ImageDraw.Draw(card).text((17,363),f"{t:g} seconds",font=font(24),fill=INK)
        thumbs.append(card)
    rows=math.ceil(len(thumbs)/3)
    sheet=Image.new("RGB",(1920,rows*397),(228,224,215))
    for i,img in enumerate(thumbs):sheet.paste(img,((i%3)*640,(i//3)*397))
    sheet.save(AUDIT/f"{scene}_storyboard.jpg",quality=94)


def encode(path, frames, fps=FPS):
    path.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f"{W}x{H}","-r",str(fps),"-i","-","-an","-c:v","libx264",
         "-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(path)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i,frame in enumerate(frames):
            process.stdin.write(frame.tobytes())
            if i%150==0:print(f"{path.name}: {i} frames",flush=True)
    finally:process.stdin.close()
    if process.wait():raise RuntimeError(f"Encoding failed: {path}")


def render(scene,backgrounds):
    data=SCENES[scene];master=OUT/f"{scene}.mp4"
    encode(master,(compose(scene,i/FPS,backgrounds) for i in range(round(data["duration"]*FPS))))
    for i,(label,start,end) in enumerate(data["stages"]):
        stage=PLAYER/scene/"stages"/f"{i+1:02}.mp4"
        stage.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(["ffmpeg","-y","-v","error","-ss",str(start),"-i",str(master),
                        "-t",str(end-start),"-an","-c:v","libx264","-crf","18","-preset","fast",
                        "-pix_fmt","yuv420p","-movflags","+faststart",str(stage)],check=True)
        # A native 15-frame boil cycle freezes the action while the pencil lives.
        encode(PLAYER/scene/"holds"/f"{i+1:02}.mp4",
               (compose(scene,end-1/FPS,backgrounds,j//5) for j in range(15)))
    subprocess.run(["ffmpeg","-y","-v","error","-i",str(master),"-vf",
        "fps=10,scale=720:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle","-loop","0",str(OUT/f"{scene}.gif")],check=True)


def write_player():
    PLAYER.mkdir(parents=True,exist_ok=True)
    manifest={name:{"title":data["title"],"master":f"../../out/{name}.mp4",
                       "poster":f"../../source/computer_control_bonus/{name}_{data['samples'][0]:05.1f}.jpg",
                       "stages":[{"label":label,"src":f"{name}/stages/{i+1:02}.mp4",
                                  "hold":f"{name}/holds/{i+1:02}.mp4"}
                                 for i,(label,_,_) in enumerate(data["stages"])]}
              for name,data in SCENES.items()}
    template=(HERE/"computer_control_bonus_player.html").read_text()
    (PLAYER/"index.html").write_text(template.replace("/* SCENE_MANIFEST */",json.dumps(manifest)))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--scene",choices=list(SCENES)+["all"],default="all")
    parser.add_argument("--prepare-only",action="store_true")
    args=parser.parse_args()
    backgrounds=established.make_notebook_backgrounds()
    for scene in SCENES if args.scene=="all" else [args.scene]:
        audits(scene,backgrounds)
        if not args.prepare_only:render(scene,backgrounds)
    write_player()
    print(f"Review: {PLAYER/'index.html'}",flush=True)


if __name__=="__main__":main()
