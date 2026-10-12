#!/usr/bin/env python3
"""Visible storefronts / invisible service routes, in a spooky mall cutaway.

All three backend routes stay behind a continuous wall. A viewer-only reveal
exposes the tunnels; computer control is confined to the public storefronts.
"""
from __future__ import annotations
import argparse
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT,AUDIT,PLAYER=HERE/'out',HERE/'source',HERE/'interactive'
W,H,FPS,DURATION=1920,1080,30,46
CREAM=(235,222,207);RED=(235,45,58);PINK=(245,118,156)
CYAN=(94,208,211);GOLD=(233,184,109);TEAL=(46,167,154)
GREEN=(146,218,169);MUTED=(144,157,170);BLACK=(7,9,16)
COLORS=[PINK,CYAN,GOLD]
STAGES=[('Computer control',0,10),('Reveal the corridor',10,16),
        ('MCP · choose a tool',16,24),('CLI · run a command',24,32),
        ('API · send a request',32,40),('Invisible to the user',40,46)]
STARTS=[16,24,32]
BACKSTAGE=(90,674,1828,919)
PUBLIC=(90,240,1828,629)
# Every backend vertex is below the unbroken wall at y=626..650.
ROUTES=[[(649,732),(1184,732),(1300,806),(1455,806)],
        [(649,807),(1455,807)],
        [(649,882),(1184,882),(1300,808),(1455,808)]]
PUBLIC_ROUTE=[(300,580),(454,494),(840,494),(1028,484)]

def clamp(x):return max(0.,min(1.,x))
def ease(x):
    x=clamp(x);return x*x*(3-2*x)
def prog(t,a,b):return ease((t-a)/(b-a))
def mix(a,b,p):return tuple(round(x+(y-x)*p) for x,y in zip(a,b))
def lerp(a,b,p):return a+(b-a)*p

@lru_cache(maxsize=100)
def font(size,kind='sans'):
    if kind=='title':
        path=Path('/System/Library/Fonts/Supplemental/Baskerville.ttc')
        if path.exists():return ImageFont.truetype(str(path),size,index=1)
    if kind=='mono':
        path=Path('/System/Library/Fonts/Menlo.ttc')
        if path.exists():return ImageFont.truetype(str(path),size)
    face=ImageFont.truetype(str(ROOT/'assets/fonts'/'Fredoka[wdth,wght].ttf'),size)
    face.set_variation_by_axes([450,95]);return face

def day_color(col):
    """Warm architectural palette for the unbranded opening set."""
    if col is None:return None
    rgb=tuple(col[:3])
    named={CREAM:(38,58,67),RED:(160,79,68),PINK:(155,77,110),CYAN:(33,113,123),
           GOLD:(150,104,53),TEAL:(36,128,115),GREEN:(48,120,87),MUTED:(74,93,103),BLACK:(249,246,235)}
    if rgb in named:out=named[rgb]
    elif rgb[0]==32 and 74<=rgb[1]<=94 and rgb[2]==71:out=(61,112+rgb[1]-74,87)
    else:
        lum=sum(rgb)/3
        out=tuple(round(max(0,min(255,248-.89*lum+(c-lum)*.36))) for c in rgb)
    return out+tuple(col[3:])

class Art:
    def __init__(self,im,palette=None):self.im,self.d,self.palette=im,ImageDraw.Draw(im),palette
    def color(self,col):return self.palette(col) if self.palette else col
    def rect(self,b,fill,outline=None,width=1,radius=0):
        self.d.rounded_rectangle(b,radius=radius,fill=self.color(fill),outline=self.color(outline),width=width)
    def poly(self,pts,fill,outline=None,width=1):
        self.d.polygon(pts,fill=self.color(fill))
        if outline:self.line(pts+[pts[0]],outline,width)
    def line(self,pts,col,width=2):self.d.line(pts,fill=self.color(col),width=width,joint='curve')
    def oval(self,b,fill,outline=None,width=1):self.d.ellipse(b,self.color(fill),self.color(outline),width)
    def text(self,xy,s,size=26,col=CREAM,anchor='la',kind='sans'):
        self.d.text(xy,s,font=font(size,kind),fill=self.color(col),anchor=anchor)

def tube(a,pts,color,width=3):
    a.line(pts,mix(color,BLACK,.86),width*7)
    a.line(pts,mix(color,BLACK,.5),width*3)
    a.line(pts,color,width)
    a.line(pts,mix(color,CREAM,.56),1)

def neon_text(im,xy,s,size,color,kind='sans',anchor='ma'):
    layer=Image.new('RGBA',im.size)
    ImageDraw.Draw(layer).text(xy,s,font=font(size,kind),fill=(*color,255),anchor=anchor)
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8)))
    im.alpha_composite(layer)

@lru_cache(maxsize=8)
def background(top='THE MALL',bottom='BEHIND THE MALL'):
    yy,xx=np.mgrid[:H,:W]
    red=np.exp(-(((xx-940)/960)**2+((yy-125)/160)**2)*2)
    blue=np.exp(-(((xx-960)/1200)**2+((yy-730)/430)**2)*2)
    arr=np.zeros((H,W,4),dtype=np.uint8)
    for i,(base,r,b) in enumerate([(5,22,5),(7,2,9),(13,4,17)]):arr[:,:,i]=base+r*red+b*blue
    arr[:,:,3]=255
    im=Image.fromarray(arr);a=Art(im)
    a.text((82,49),'AI BASICS',20,MUTED)
    a.text((82,77),'NUGGET 08',17,(102,108,122))
    a.text((1836,49),'STARCOURT',18,MUTED,'ra')
    a.text((1836,77),'AFTER HOURS',17,(102,108,122),'ra')
    # Hollow serif lettering and red rules echo the title sequence.
    title=Image.new('RGBA',(W,225));d=ImageDraw.Draw(title)
    for text,y,size in [(top,15,70),(bottom,77,103)]:
        d.text((960,y),text,font=font(size,'title'),anchor='ma',fill=(3,4,9,255),
               stroke_width=2,stroke_fill=(*RED,255))
    d.line([(470,199),(1450,199)],fill=(*RED,255),width=2)
    d.line([(791,25),(1129,25)],fill=(*RED,210),width=2)
    mask=title.getchannel('R').point(lambda p:max(0,p-30))
    glow=Image.new('RGBA',title.size,(*RED,0))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(8)))
    im.alpha_composite(glow);im.alpha_composite(title)
    return im

def shop(a,x,w,name,color,kind):
    a.rect((x,347,x+w,553),(11,15,27),(58,56,70),2)
    a.poly([(x,347),(x+16,361),(x+16,541),(x,553)],(41,41,51))
    a.poly([(x+w,347),(x+w-16,361),(x+w-16,541),(x+w,553)],(28,31,44))
    a.rect((x+16,361,x+w-16,541),(12,23,34))
    a.rect((x+25,371,x+w-25,402),(28,33,46))
    a.text((x+w/2,373),'NEW ARRIVALS' if kind=='records' else 'PROJECT A' if kind=='issues' else 'ONE SCOOP OR TWO?',19,MUTED,'ma')
    if kind=='records':
        for i in range(6):
            xx=x+38+i*48
            a.rect((xx,422,xx+35,474),mix(color,BLACK,.45),(74,77,94))
            a.oval((xx+4,429,xx+31,456),(16,20,30),color)
            a.oval((xx+15,440,xx+20,445),color)
        a.poly([(x+25,498),(x+w-27,498),(x+w-10,535),(x+10,535)],(67,45,61))
        a.line([(x+10,535),(x+w-10,535)],color,2)
        a.rect((x+w/2-44,482,x+w/2+44,511),(19,33,38),TEAL,2,3)
        a.text((x+w/2,483),'BROWSE',18,CREAM,'ma')
    elif kind=='issues':
        for j,s in enumerate(['PROJECTS','ISSUES','SEARCH']):a.text((x+29,415+j*34),s,18,(151,161,175))
        a.line([(x+139,412),(x+139,527)],(54,60,72),2)
        a.rect((x+162,421,x+w-32,457),(28,43,52),(71,93,104),1,3)
        a.text((x+179,425),'ISSUE LIST',19,CYAN)
        a.rect((x+162,468,x+w-32,510),(24,47,52),TEAL,2,3)
        a.text((x+183,474),'TEAM-24',24,CREAM)
    else:
        for i in range(5):
            xx=x+34+i*59
            a.poly([(xx+3,486),(xx+36,486),(xx+20,522)],(159,113,83))
            for dx,dy in [(0,0),(16,0),(8,-13)]:a.oval((xx+dx,459+dy,xx+dx+24,485+dy),[PINK,CYAN,CREAM][i%3])
        a.rect((x+19,521,x+w-19,545),(70,52,68))
        for i in range(10):
            a.poly([(x+19+i*32,522),(x+32+i*32,522),(x+43+i*32,545),(x+30+i*32,545)],(120,63,79))
    a.line([(x+13,412),(x+90,357)],(48,65,78),2)
    a.line([(x+w-13,497),(x+w-45,526)],(49,70,86),2)
    a.rect((x-6,311,x+w+6,351),(20,17,31),(94,45,60))
    if a.palette:a.text((x+w/2,312),name,31,color,'ma')
    else:neon_text(a.im,(x+w/2,312),name,31,color)
    tube(a,[(x-7,353),(x+w+7,353)],color,2)
    for xx in (x-7,x+w+3):a.rect((xx,354,xx+5,553),(77,65,76))

def palm(a,x,y,scale=1):
    a.poly([(x-21*scale,y),(x+21*scale,y),(x+15*scale,y+34*scale),(x-15*scale,y+34*scale)],(77,53,66))
    a.line([(x,y),(x-3*scale,y-100*scale)],(95,82,79),max(1,int(7*scale)))
    for i in range(9):
        ang=math.pi*1.08+i*math.pi*.105
        px=x+math.cos(ang)*70*scale;py=y-70*scale+math.sin(ang)*42*scale
        a.poly([(x-3*scale,y-95*scale),(px,py),(px+12*scale,py+13*scale)],(32,74+(i%3)*10,71))

@lru_cache(maxsize=2)
def public_plate(day=False):
    im=Image.new('RGBA',(W,H));a=Art(im,day_color if day else None)
    a.rect((80,235,1840,635),(10,15,26),(57,56,72),2)
    a.poly([(80,235),(1840,235),(1756,295),(164,295)],(22,25,41))
    for x in range(194,1690,250):
        a.poly([(x,239),(x+212,239),(x+180,279),(x+25,279)],(35,26,43),(84,54,65),2)
    tube(a,[(142,290),(1778,290)],(143,55,100),3)
    a.rect((80,552,1840,626),(32,32,44))
    for yy in [566,587,615]:a.line([(80,yy),(1840,yy)],(64,49,62))
    for x in range(-100,2100,116):a.line([(960+(x-960)*.91,552),(x,626)],(67,48,60))
    shop(a,272,365,'RECORD SHOP' if day else 'HAWKINS RECORDS',PINK,'records')
    shop(a,755,422,'ISSUE DEPARTMENT',CYAN,'issues')
    shop(a,1297,365,'ICE CREAM' if day else 'SCOOPS & BYTES',GOLD,'scoops')
    for x,w,col in [(272,365,PINK),(755,422,CYAN),(1297,365,GOLD)]:
        a.poly([(x,556),(x+w,556),(x+w+37,611),(x-37,611)],mix(col,BLACK,.88))
        a.line([(x+30,562),(x+w-30,562)],mix(col,BLACK,.45),2)
    for x in [214,698,1240,1725]:palm(a,x,541,.69)
    for x,sgn in [(95,1),(1825,-1)]:
        a.poly([(x,535),(x+sgn*75,444),(x+sgn*75,421),(x,505)],(33,44,59))
        for i in range(9):
            yy=524-i*9;xx=x+sgn*i*7;a.line([(xx,yy),(xx+sgn*18,yy)],(106,112,126))
        tube(a,[(x,501),(x+sgn*75,413)],(96,151,170),2)
    a.rect((80,626,1840,650),(55,46,58))
    a.line([(80,628),(1840,628)],(132,68,80),2)
    a.line([(80,648),(1840,648)],(9,13,22),5)
    for x in range(130,1800,170):a.line([(x,634),(x+20,644)],(75,58,68))
    return im

def pipe(a,y,color):
    a.line([(103,y),(1796,y)],(8,11,18),13)
    a.line([(103,y-1),(1796,y-1)],color,8)
    a.line([(103,y-3),(1796,y-3)],mix(color,CREAM,.22))
    for x in range(143,1810,151):a.rect((x,y-7,x+9,y+6),(57,59,68),(20,28,36))

@lru_cache(maxsize=1)
def corridor_plate():
    im=Image.new('RGBA',(W,H));a=Art(im)
    a.rect((80,650,1840,928),(14,21,30),(57,56,72),2)
    a.poly([(80,650),(1840,650),(1799,683),(121,683)],(22,30,41))
    a.poly([(80,650),(121,683),(121,901),(80,928)],(21,29,39))
    a.poly([(1840,650),(1799,683),(1799,901),(1840,928)],(19,26,34))
    a.poly([(80,928),(121,901),(1799,901),(1840,928)],(34,41,50))
    for y in [711,759,854]:a.line([(122,y),(1798,y)],(29,39,49))
    for row,y in enumerate([683,759,835]):
        for x in range(160+row%2*69,1800,138):a.line([(x,y),(x,y+73)],(26,35,45))
    pipe(a,666,(67,43,51));pipe(a,680,(44,59,69))
    for x in [305,930,1680]:
        a.rect((x-48,688,x+48,698),(37,48,62),(69,80,93),1,2)
        tube(a,[(x-35,692),(x+35,692)],(143,163,180),2)
        a.poly([(x-38,702),(x+38,702),(x+89,899),(x-89,899)],(24,34,45))
    for x in [103,1810]:
        a.rect((x-6,750,x+8,783),(64,24,31),(113,44,51),1,3)
        tube(a,[(x+1,755),(x+1,778)],RED,3)
    a.rect((1531,711,1762,895),(12,18,27),(56,62,74),2)
    for y in [757,808,859]:
        a.line([(1542,y),(1751,y)],(71,72,78),5)
        for x in [1556,1630,1703]:
            a.rect((x,y-32,x+36,y-3),(84,64,58),(123,92,71))
            a.line([(x+18,y-31),(x+18,y-4)],(151,118,85),3)
    a.rect((1435,709,1524,899),(55,59,69),(103,101,110),3)
    a.rect((1446,719,1512,897),(5,10,17))
    a.rect((140,737,318,873),(13,26,33),TEAL,2,8)
    a.text((229,743),'AI AGENT',25,TEAL,'ma')
    a.rect((196,788,262,832),(22,57,60),TEAL,2,13)
    for x in [213,242]:a.oval((x,805,x+7,812),CREAM)
    a.line([(215,821),(244,821)],TEAL,2)
    a.line([(229,789),(229,779)],TEAL,2);a.oval((225,774,233,782),TEAL)
    a.text((229,840),'authorized request',17,MUTED,'ma')
    for y in [732,807,882]:a.line([(318,806),(345,806),(345,y),(367,y)],(59,79,85),2)
    for base in [84,1806]:
        for k in range(3):
            a.line([(base+k*6+math.sin(i*.8+k)*6,657+i*13) for i in range(20)],(51+k*4,30,40),3)
    return im

@lru_cache(maxsize=1)
def cover_plate():
    im=Image.new('RGBA',(W,H));a=Art(im)
    a.rect((81,651,1839,927),(10,13,23))
    for y in range(653,927,45):
        a.line([(82,y),(1838,y)],(28,29,40))
        for x in range(82+(y//45%2)*95,1838,190):a.line([(x,y),(x,y+43)],(24,27,37))
    a.line([(120,712),(650,712)],(90,36,46));a.line([(1270,712),(1800,712)],(90,36,46))
    a.text((960,698),'BEHIND THE WALL',26,(149,89,101),'ma')
    a.text((960,765),'The service corridors are out of sight.',33,(146,151,168),'ma')
    a.text((960,815),'The customer sees the storefronts.',23,(95,112,132),'ma')
    return im

def on_path(path,p):
    lengths=[math.dist(a,b) for a,b in zip(path,path[1:])];dist=clamp(p)*sum(lengths)
    for i,length in enumerate(lengths):
        if dist<=length or i==len(lengths)-1:
            return tuple(lerp(a,b,dist/length) for a,b in zip(path[i],path[i+1]))
        dist-=length

def cursor(a,xy,t):
    x,y=xy;pts=[(x,y),(x+2,y+43),(x+14,y+32),(x+24,y+48),(x+34,y+42),(x+25,y+27),(x+42,y+25)]
    a.poly([(px+4,py+4) for px,py in pts],(2,4,8));a.poly(pts,CREAM,TEAL,3)
    for click in [3.9,7.1]:
        q=clamp((t-click)/.65)
        if 0<q<1:
            r=8+q*29;a.oval((x-r,y-r,x+r,y+r),None,mix(TEAL,BLACK,q),3)

def public_activity(im,t):
    a=Art(im)
    # Reading finishes before the reveal. Backend calls never animate this UI.
    if t>=3.9:
        a.rect((410,482,498,511),(28,76,71),TEAL,2,3)
        a.text((454,483),'BROWSE',18,CREAM,'ma')
    if t>=7.1:
        a.rect((917,413,1145,524),(18,43,46),TEAL,2,5)
        a.text((1031,415),'TEAM-24',26,CREAM,'ma')
        a.text((1031,452),'ISSUE DETAILS',18,CYAN,'ma')
        a.line([(963,489),(978,502),(1002,476)],GREEN,4)
        a.text((1058,480),'READ',22,GREEN,'ma')
    if t<9.6:
        split=math.dist(*PUBLIC_ROUTE[:2])/sum(math.dist(a,b) for a,b in zip(PUBLIC_ROUTE,PUBLIC_ROUTE[1:]))
        p=prog(t,1.6,3.9)*split if t<4.2 else split+(1-split)*prog(t,4.5,7.1)
        for i in range(35):
            q=i/34
            if q>p:break
            xx,yy=on_path(PUBLIC_ROUTE,q);a.oval((xx-2,yy-2,xx+2,yy+2),TEAL)
        cursor(a,on_path(PUBLIC_ROUTE,p),t)
    a.rect((104,248,505,281),(12,21,31),(50,75,91),1,3)
    a.text((120,250),'PUBLIC STOREFRONTS · USER INTERFACE',18,CYAN)
    a.rect((1456,248,1816,281),(13,24,33),(51,69,81),1,3)
    a.text((1636,250),'COMPUTER CONTROL · VISIBLE CLICKS' if t<10 else 'NO STOREFRONT NAVIGATION',18,CREAM if t<10 else MUTED,'ma')

def route_state(t):
    if t<16:return -1,'idle',0
    if t>=40:return 3,'summary',1
    idx=min(2,int((t-16)//8));dt=t-STARTS[idx]
    if dt<1:return idx,'select',dt
    if dt<3.2:return idx,'outbound',prog(dt,1,3.2)
    if dt<4.2:return idx,'checking',0
    if dt<4.8:return idx,'approved',prog(dt,4.2,4.8)
    if dt<6.7:return idx,'response',prog(dt,4.8,6.7)
    return idx,'complete',1

def service_door(a,state,opening):
    bottom=897-round(178*opening)
    if bottom>719:
        a.rect((1446,719,1512,bottom),(65,75,86))
        for y in range(724,bottom,12):a.line([(1447,y),(1511,y)],(27,37,48),2)
    status='SCOPED ACCESS' if state in ['idle','select','outbound'] else 'CHECKING KEY' if state=='checking' else 'ACCESS ALLOWED'
    col=GOLD if state=='checking' else GREEN if state in ['approved','response','complete','summary'] else MUTED
    a.rect((1328,695,1577,726),(11,19,28),(62,69,82),1,4)
    a.text((1452,696),'LOCKED API ENDPOINT',20,CREAM,'ma')
    a.rect((1297,867,1557,907),(11,19,28),col,1,4)
    a.text((1427,872),status,23,col,'ma')
    a.rect((1395,749,1424,789),(20,29,39),(86,95,109),2,4)
    a.oval((1403,758,1416,771),col);a.line([(1405,780),(1415,780)],col,2)
    if opening>.8:
        a.rect((1543,759,1751,841),(19,40,44),GREEN,2,4)
        a.text((1647,767),'TEAM-24',28,CREAM,'ma')
        a.text((1647,806),'READ RESULT',20,GREEN,'ma')
    else:a.text((1650,717),'READ ISSUE',23,CREAM,'ma')
    a.text((1677,868),'Project A · read',18,MUTED,'ma')

def hidden_activity(im,t):
    a=Art(im);idx,state,p=route_state(t)
    a.rect((102,653,768,683),(9,17,26),(61,66,81),1,2)
    a.text((119,651),'HIDDEN SERVICE CORRIDOR · CUTAWAY VIEW',22,CREAM)
    for i,path in enumerate(ROUTES):
        active=i==idx or idx==3;col=COLORS[i] if active else mix(COLORS[i],BLACK,.65)
        tube(a,path,col,3 if active else 1)
        y=path[0][1]
        a.rect((367,y-30,649,y+30),(16,26,39),col,2,5)
        a.text((384,y-23),['MCP','CLI','API'][i],31,col)
        a.line([(460,y-19),(460,y+19)],mix(col,BLACK,.4))
        a.text((478,y-13),['Choose a tool','Run a command','Send a request'][i],21,CREAM if active else MUTED)
        if idx==3 or i==idx and state=='complete':a.line([(650,y-25),(656,y-19),(667,y-34)],GREEN,2)
    opening=p if state=='approved' else 1 if state in ['response','complete','summary'] else 0
    service_door(a,state,opening)
    if state in ['outbound','response','checking']:
        x,y=on_path(ROUTES[idx],p if state=='outbound' else 1-p if state=='response' else 1)
        a.rect((x-26,y-21,x+26,y+21),(12,21,32),COLORS[idx],3,6)
        a.text((x,y-18),'24',28,CREAM,'ma')
        if state=='response':
            a.oval((x+15,y-28,x+35,y-8),GREEN)
            a.line([(x+19,y-19),(x+24,y-14),(x+31,y-23)],(12,34,29),2)
    if idx>=0:
        label=['TOOL CALL → SERVICE REQUEST','COMMAND → SERVICE REQUEST','DIRECT SERVICE REQUEST','THREE ROUTES · BACKEND ONLY'][idx]
        a.text((944,911),label,17,COLORS[idx] if idx<3 else CREAM,'ma')

def reveal_amount(t):return prog(t,10.5,13.5)*(1-prog(t,43.1,45.1))

def compose(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=background().copy();im.alpha_composite(public_plate());public_activity(im,t)
    im.alpha_composite(corridor_plate());hidden_activity(im,t)
    reveal=reveal_amount(t)
    # The wall slides away for the audience, then hides the entire corridor again.
    if reveal<1:
        shift=round(277*reveal)
        if shift<277:im.alpha_composite(cover_plate().crop((80,651,1840,928-shift)),(80,651+shift))
        if reveal>0:Art(im).line([(81,651+shift),(1839,651+shift)],(153,49,63),2)
    a=Art(im)
    for i in range(14):
        x=88+(i*137)%1730;y=209+((i*17+amb*1.5)%23)
        a.oval((x,y,x+1,y+1),(87,65,77))
    if reveal>.95:a.line([(895,692),(965,692)],mix((143,163,180),CREAM,.12+.03*math.sin(amb*math.tau/3)),2)
    a.line([(80,949),(1840,949)],(81,37,51))
    if t<10:title,subtitle='Computer control uses the storefronts.','You can watch the cursor navigate the interface.'
    elif t<16:title,subtitle='The service entrances are behind the scenes.','We reveal the corridor to see the metaphor.'
    elif t<24:title,subtitle='MCP tools use the hidden service corridor.','The tool sends the request through the corridor.'
    elif t<32:title,subtitle='CLI commands use the hidden service corridor.','The command sends the request through the corridor.'
    elif t<40:title,subtitle='API: send the request directly.','The endpoint checks the request and access.'
    else:title,subtitle='Backend work. No storefront navigation.','The result can appear. The clicks don’t.'
    stage=next((i for i,(_,s,e) in enumerate(STAGES) if s<=t<e),5)
    a.text((80,968),title,38,CREAM);a.text((82,1020),subtitle,25,MUTED)
    for i in range(6):
        x=1582+i*42;a.line([(x,985),(x+24,985)],RED if i==stage else (62,42,53),4)
    a.text((1837,1016),f'{stage+1:02} / 06',19,MUTED,'ra',kind='mono')
    return im.convert('RGB')

def audits():
    AUDIT.mkdir(parents=True,exist_ok=True)
    samples=[2.8,7.6,11.7,14.5,17.6,19.7,21.2,25.6,29.4,33.6,37.4,41.3,44.2,45.8]
    sheet=Image.new('RGB',(1920,math.ceil(len(samples)/3)*392),BLACK)
    for i,t in enumerate(samples):
        img=compose(t);img.save(AUDIT/f'mall_routes_{t:04.1f}.jpg',quality=94)
        sheet.paste(img.resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*392))
        ImageDraw.Draw(sheet).text(((i%3)*640+15,(i//3)*392+362),f'{t:g}s',font=font(20),fill=CREAM)
    sheet.save(AUDIT/'storyboard.jpg',quality=94);compose(41.3).save(OUT/'mall_routes_still.png')

def encode(path,frames):
    path.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast',
        '-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
    try:
        for i,img in enumerate(frames):
            proc.stdin.write(img.tobytes())
            if i%150==0:print(f'{path.name}: {i} frames',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError(f'FFmpeg failed: {path}')

def write_player():
    from render_service_scenes import write_player as write_collection
    write_collection()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);audits();write_player()
    if args.prepare_only:return
    master=OUT/'mall_routes.mp4';encode(master,(compose(i/FPS) for i in range(round(DURATION*FPS))))
    for i,(_,start,end) in enumerate(STAGES):
        stage=PLAYER/'stages'/f'{i+1:02}.mp4';stage.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
            '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(stage)],check=True)
        encode(PLAYER/'holds'/f'{i+1:02}.mp4',(compose(end-1/FPS,j/FPS) for j in range(90)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
        'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];'
        '[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle','-loop','0',str(OUT/'mall_routes.gif')],check=True)
    print(f'Preview: {PLAYER/"index.html"}',flush=True)

if __name__=='__main__':main()
