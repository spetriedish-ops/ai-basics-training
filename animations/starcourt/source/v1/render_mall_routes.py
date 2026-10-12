#!/usr/bin/env python3
"""A cel-painted, 1985 mall cutaway: three illustrative routes to one API.

All architecture, props, typography and motion are generated from editable
paths. No downloaded footage or images. Uses the project's Pillow/FFmpeg
pipeline, with a new neon palette and a fixed axonometric camera.
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
OUT=HERE/'out'
AUDIT=HERE/'source'
PLAYER=HERE/'interactive'
W,H,FPS,DURATION=1920,1080,30,34
CREAM=(255,235,205)
PINK=(255,99,167)
CYAN=(78,231,223)
GOLD=(255,199,102)
NAVY=(25,29,56)
INK=(27,30,51)
TEAL=(46,167,154)
GREEN=(167,239,187)
LAVENDER=(177,170,228)
STAGES=[('MCP · choose a tool',0,11),('CLI · run a command',11,20),
        ('API · send a request',20,29),('Same service. Same check.',29,34)]
# Short symbolic labels describe the example, not real product command syntax.
ROUTES=[[(248,142),(365,142),(365,711),(1200,711),(1254,760),(1254,824)],
        [(675,142),(735,142),(735,747),(1200,747),(1254,760),(1254,824)],
        [(1108,118),(1126,118),(1126,785),(1212,785),(1254,760),(1254,824)]]
STARTS=[2.7,11.1,20.1]
COLORS=[PINK,CYAN,GOLD]


def clamp(x):return max(0.,min(1.,x))
def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)
def prog(t,a,b):return ease((t-a)/(b-a))
def mix(a,b,p):return tuple(round(x+(y-x)*p) for x,y in zip(a,b))
def lerp(a,b,p):return a+(b-a)*p


@lru_cache(maxsize=80)
def font(size,kind='sans'):
    filename={'sans':'Fredoka[wdth,wght].ttf','hand':'Delius-Regular.ttf',
              'label':'Baloo2[wght].ttf'}[kind]
    face=ImageFont.truetype(str(ROOT/'assets/fonts'/filename),size)
    if kind=='sans':face.set_variation_by_axes([450,95])
    elif kind=='label':face.set_variation_by_axes([550])
    return face


def P(x,y,z=0):return (80+.94*x+.48*y,630+.22*x-.38*y-z*.78)


def screen_point(point):return (173+point[0]*.82,150+point[1]*.82)


class Art:
    def __init__(self,im):self.im=im;self.d=ImageDraw.Draw(im)
    def poly(self,pts,fill,outline=None,width=2):
        self.d.polygon(pts,fill=fill)
        if outline:self.d.line(pts+[pts[0]],fill=outline,width=width,joint='curve')
    def line(self,pts,fill,width=2):self.d.line(pts,fill=fill,width=width,joint='curve')
    def rect(self,box,fill,outline=None,width=2,radius=0):
        self.d.rounded_rectangle(box,radius,fill=fill,outline=outline,width=width)
    def oval(self,box,fill,outline=None,width=2):self.d.ellipse(box,fill=fill,outline=outline,width=width)
    def text(self,xy,value,size=32,fill=CREAM,anchor='la',kind='sans'):
        self.d.text(xy,value,font=font(size,kind),fill=fill,anchor=anchor)
    def floor(self,x,y,w,d,fill,z=0,outline=None):
        self.poly([P(x,y,z),P(x+w,y,z),P(x+w,y+d,z),P(x,y+d,z)],fill,outline)
    def box(self,x,y,w,d,h,top,left,right,z=0,edge=None):
        self.poly([P(x,y,z),P(x+w,y,z),P(x+w,y,z+h),P(x,y,z+h)],left,edge)
        self.poly([P(x+w,y,z),P(x+w,y+d,z),P(x+w,y+d,z+h),P(x+w,y,z+h)],right,edge)
        self.floor(x,y,w,d,top,z+h,edge)


def neon(art,pts,color,width=4):
    art.line(pts,mix(color,NAVY,.62),width*5)
    art.line(pts,mix(color,NAVY,.25),width*2)
    art.line(pts,color,width)
    art.line(pts,mix(color,CREAM,.55),max(1,width//3))


def sign(art,x,y,z,value,color,w,size=31):
    """A sign on the storefront plane, tilted with the architecture."""
    label=Image.new('RGBA',(w,64))
    d=ImageDraw.Draw(label)
    while d.textlength(value,font=font(size))>w-18 and size>14:size-=1
    d.rounded_rectangle((0,0,w-1,59),6,fill=(*NAVY,255),outline=(*color,255),width=2)
    d.text((w/2,2),value,font=font(size),fill=(*color,255),anchor='ma')
    # Camera's x axis slopes down 13 degrees; shear preserves vertical letters.
    shear=.22/.94
    shaped=label.transform((w,64+round(w*shear)),Image.Transform.AFFINE,
                           (1,0,0,-shear,1,0),Image.Resampling.BICUBIC)
    px,py=P(x,y,z)
    art.im.alpha_composite(shaped,(round(px),round(py)))


def plant(a,x,y,size=1):
    a.box(x-27*size,y-26*size,54*size,52*size,33*size,
          (153,144,149),(96,78,102),(73,62,92),edge=(56,47,76))
    px,py=P(x,y,31*size)
    for i in range(9):
        angle=-math.pi*.92+i*math.pi*.105
        end=(px+math.cos(angle)*(44+13*(i%2))*size,py+math.sin(angle)*70*size)
        mid=(lerp(px,end[0],.55),lerp(py,end[1],.7)-14*size)
        a.poly([(px,py),(mid[0]-6*size,mid[1]),end,(mid[0]+7*size,mid[1])],
               [(52,119,108),(80,158,124),(78,175,143)][i%3])
        a.line([(px,py),mid,end],(133,194,142),max(1,round(size)))


def cartons(a,x,y,count=3):
    for i in range(count):
        xx=x+(i%2)*31;yy=y+(i//2)*31
        a.box(xx,yy,28,27,26,(218,171,122),(176,127,96),(148,102,82),edge=(107,75,74))
        a.floor(xx+12,yy,4,27,(243,204,152),26)


def shop(a,x,w,name,color,kind):
    # Stockroom (open roof) and shelves; storefront still faces the public.
    a.floor(x,354,w,267,(119,100,113),outline=(70,64,85))
    a.floor(x+9,363,w-18,167,(230,192,167))
    a.floor(x+9,543,w-18,70,(156,151,151))
    # Back partition has a real opening at the left end; route lanes run beside shops.
    a.box(x+9,620,w-18,8,70,(201,188,174),(131,139,148),(104,113,133))
    a.box(x,360,9,270,110,(220,190,177),(143,109,131),(109,91,119))
    a.box(x+w-9,360,9,270,110,(220,190,177),(143,109,131),(109,91,119))
    for yy in [560,598]:
        a.box(x+55,yy,w-82,19,44,(188,166,139),(111,112,127),(91,96,115))
        cartons(a,x+66,yy+1,3)
    # Display islands visibly differ, making the mall recognizable as retail.
    if kind=='records':
        for xx in [x+54,x+154]:
            a.box(xx,413,57,60,47,(229,171,166),(155,104,131),(119,87,112))
            for k in range(5):
                a.box(xx+5,417+k*10,45,4,9,[PINK,GOLD,CYAN,LAVENDER,CREAM][k],
                      (79,65,88),(57,51,76),z=47)
    elif kind=='books':
        for xx in [x+43,x+147]:
            a.box(xx,416,64,62,38,(224,187,142),(160,122,120),(111,98,119))
            for k in range(5):a.box(xx+4+k*11,420,8,46,25,[GOLD,CYAN,PINK,CREAM,LAVENDER][k],
                                   [GOLD,CYAN,PINK,CREAM,LAVENDER][k],(94,86,105),z=38)
    else:
        for xx in [x+54,x+158]:
            a.box(xx,421,61,47,67,(74,86,110),(38,45,72),(32,38,64))
            p=P(xx+10,420,66)
            a.rect((p[0],p[1]+12,p[0]+36,p[1]+37),(34,68,85),CYAN,1)
    # Two glass panels flank the open front door.
    a.box(x,350,w,11,12,(221,190,167),(165,126,138),(125,94,118))
    for xx,ww in [(x+10,76),(x+w-83,72)]:
        a.poly([P(xx,350,12),P(xx+ww,350,12),P(xx+ww,350,135),P(xx,350,135)],
               (61,97,112,160),(209,179,157),2)
        a.line([P(xx+6,349,29),P(xx+ww-6,349,104)],(134,184,181),2)
        a.line([P(xx+18,349,26),P(xx+ww-3,349,94)],(99,145,159),1)
    a.box(x-6,344,w+12,23,24,(221,177,163),(101,60,100),(69,48,85),z=136)
    sign(a,x+4,339,218,name,color,round(w*.94)-8,34)
    # Glow tube on the leading cornice.
    neon(a,[P(x-6,337,136),P(x+w+6,337,136)],color,3)
    sign(a,x+83,345,28,'OPEN',GREEN,91,19)


def kiosk(a):
    x,y=181,114
    a.box(x,y,108,63,108,(188,121,157),(99,51,98),(63,41,77))
    a.box(x-11,y-10,132,79,18,(224,173,162),(130,74,121),(91,51,99),z=108)
    px,py=P(x,y,260)
    a.rect((px-10,py,px+145,py+147),NAVY,PINK,3,9)
    a.text((px+68,py+6),'MCP',37,PINK,'ma')
    a.text((px+68,py+48),'TOOL DIRECTORY',14,CREAM,'ma')
    for i,label in enumerate(['READ ISSUE','CREATE ISSUE','SEARCH DOCS']):
        a.rect((px+5,py+73+i*23,px+130,py+93+i*23),(64,39,76),None,1,3)
        a.text((px+14,py+74+i*23),label,14,CREAM)
    neon(a,[(px-12,py+151),(px+148,py+151)],PINK,3)


def terminal(a):
    x,y=622,106
    a.box(x-8,y-8,143,79,77,(183,169,158),(125,123,140),(82,87,112))
    a.box(x,y+15,110,64,61,(180,177,165),(132,142,147),(91,105,120),z=77)
    px,py=P(x+7,y+10,138)
    a.rect((px,py,px+109,py+73),(20,50,62),CYAN,2,8)
    a.text((px+12,py+14),'> get issue',16,GREEN)
    a.text((px+12,py+37),'TEAM-24_',17,GREEN)
    for j in range(3):
        for i in range(8):a.floor(x+10+i*12,y-2-j*9,8,5,(53,67,92),80)
    # The CLI label is a freestanding brass sign, like an employee help desk.
    sx,sy=P(x+48,y-26,183)
    a.rect((sx-27,sy-30,sx+59,sy+10),NAVY,CYAN,2,5)
    a.text((sx+16,sy-28),'CLI',28,CYAN,'ma')


def dispatch(a):
    x,y=1060,70
    a.box(x,y,101,78,73,(224,176,120),(166,112,99),(107,79,95))
    a.floor(x+12,y+13,75,42,CREAM,74)
    p=P(x+16,y+10,74)
    a.line([(p[0],p[1]),(p[0]+50,p[1]+11)],RUST,2)
    sx,sy=P(x+40,y+22,144)
    a.rect((sx-37,sy-16,sx+82,sy+31),NAVY,GOLD,2,6)
    a.text((sx+22,sy-13),'DIRECT',24,GOLD,'ma')
    a.line([P(x+44,y+30,74),P(x+44,y+30,132)],GOLD,5)


RUST=(166,94,104)


@lru_cache(maxsize=1)
def backdrop():
    # Dark blue/plum stage with a soft colored pool behind the miniature.
    yy,xx=np.mgrid[:H,:W]
    halo=np.exp(-(((xx-995)/1080)**2+((yy-548)/620)**2)*2)
    img=np.empty((H,W,4),np.uint8)
    for i,(lo,hi) in enumerate([(14,48),(20,42),(40,78)]):img[:,:,i]=lo+(hi-lo)*halo
    img[:,:,3]=255
    return Image.fromarray(img,'RGBA')


@lru_cache(maxsize=1)
def base_plate():
    im=Image.new('RGBA',(W,H));a=Art(im)
    a.oval((130,813,1810,1028),(12,16,34))
    # Thick model base, tiled public concourse, and cool service corridor.
    a.box(0,0,1420,850,24,(229,190,169),(126,89,117),(76,74,104),z=-24)
    a.floor(0,0,1420,850,(224,192,173))
    for x in range(0,1420,95):
        for y in range(0,850,85):
            fill=(226,198,178) if (x//95+y//85)%2 else (213,180,168)
            a.floor(x+2,y+2,min(91,1420-x-2),min(81,850-y-2),fill)
    a.floor(0,655,1420,195,(93,120,130))
    for y in [667,825]:a.line([P(0,y),P(1420,y)],(146,173,165),3)
    # Service back wall and side wall have fluorescent lights and pipes.
    a.box(0,846,1420,9,154,(167,174,168),(84,109,127),(62,80,106))
    for x in range(0,1420,110):a.line([P(x,845,0),P(x,845,145)],(101,126,139),1)
    for z in [114,137]:a.line([P(8,834,z),P(1415,834,z)],(139,161,166),6)
    for x in [110,470,830]:
        neon(a,[P(x,831,112),P(x+168,831,112)],(190,248,226),3)
    # A high mezzanine strip and angular skylight framing at the far left.
    a.box(0,666,980,165,15,(103,111,133),(122,93,120),(81,78,110),z=193)
    a.box(0,820,980,18,96,(197,151,160),(99,67,105),(77,59,92),z=209)
    for x,name,col in [(35,'STARLIGHT CINEMA',GOLD),(369,'ROLLER DISCO',PINK),(708,'FOOD COURT',CYAN)]:
        sign(a,x,819,288,name,col,232,24)
    # Gold balustrade posts, two rails and soft neon running below.
    for x in range(0,1000,44):a.line([P(x,661,211),P(x,661,246)],(213,176,124),3)
    for z in [214,248]:a.line([P(0,661,z),P(980,661,z)],GOLD,3)
    neon(a,[P(0,654,195),P(980,654,195)],PINK,3)
    # Skylight facets rise from the back edge of the second floor.
    for x in range(0,980,196):
        pts=[P(x,836,310),P(x+196,836,310),P(x+196,932,354),P(x,932,354)]
        a.poly(pts,(77,109,147),(171,169,179),3)
        a.line([pts[0],pts[2]],(214,188,173),2)
    for x in [3,968]:a.box(x,657,18,24,205,(219,192,166),(185,145,146),(140,110,134))
    # Public shops, deliberately open-roofed for the explainer cutaway.
    shop(a,31,294,'ISSUES & CO.',PINK,'records')
    shop(a,409,286,'DOCS / BOOKS',CYAN,'books')
    shop(a,782,275,'PROJECT ARCADE',GOLD,'arcade')
    # Small stocked dolly in service aisle; corridor becomes tangible at a glance.
    a.box(940,708,86,55,6,(142,147,140),(93,99,114),(77,84,103),z=10)
    cartons(a,950,717,4)
    for xx in [946,1013]:
        p=P(xx,709,6);a.oval((p[0]-5,p[1]-5,p[0]+5,p[1]+5),INK)
    # Loading door at the shared destination. All routes end at this one hatch.
    a.box(1146,836,242,19,239,(161,169,168),(73,96,119),(49,65,95))
    a.poly([P(1187,829),P(1323,829),P(1323,829,185),P(1187,829,185)],(35,52,77),CYAN,2)
    for z in range(10,184,16):a.line([P(1189,828,z),P(1321,828,z)],(64,88,108),2)
    sign(a,1169,826,226,'READ ISSUE',CYAN,179,29)
    a.line([P(1187,827,10),P(1323,827,10)],GOLD,5)
    # Badge reader alongside the door, including a physical card slot.
    bx,by=P(1351,824,124)
    a.rect((bx-7,by-10,bx+31,by+47),(26,37,61),GOLD,2,5)
    a.rect((bx+1,by+18,bx+24,by+24),(181,195,168))
    a.oval((bx+7,by,bx+16,by+9),GOLD)
    # Service gate rails run beside, not across, the common approach.
    for xx in [1190,1325]:
        a.line([P(xx,787),P(xx,787,42)],(178,187,169),4)
        a.line([P(xx,787,42),P(xx,818,42)],(178,187,169),4)
    # Ground-floor planters, simple bench and a brass directory surround.
    for x,y,size in [(32,52,1.05),(443,49,.87),(833,42,.95),(1375,30,1.1),
                     (45,291,.65),(465,312,.62),(823,315,.62)]:plant(a,x,y,size)
    a.box(430,222,163,44,27,(186,132,121),(104,81,111),(81,67,102))
    for xx in [448,565]:a.box(xx,230,9,21,22,(135,132,122),(87,90,102),(66,70,95))
    # Small escalator at the public left edge creates a clear mall silhouette.
    for i in range(10):
        a.box(17,391+i*18,54,18,12,(147,165,163),(75,98,117),(58,79,105),z=i*18)
    for xx in [12,75]:
        a.line([P(xx,390,35),P(xx,570,215)],(194,174,139),5)
        a.line([P(xx,390,39),P(xx,570,219)],NAVY,3)
    kiosk(a);terminal(a);dispatch(a)
    # A gentle bloom on bright fixtures only; it never smears the labels.
    light=Image.new('RGBA',(W,H));la=Art(light)
    for x,w,col in [(31,294,PINK),(409,286,CYAN),(782,275,GOLD)]:
        la.line([P(x,337,136),P(x+w,337,136)],(*col,115),10)
    im=Image.alpha_composite(im,light.filter(ImageFilter.GaussianBlur(15)))
    return im


def courier_sprite(phase=0,pose='walk'):
    im=Image.new('RGBA',(240,340));a=Art(im)
    # Squashy courier proportions, big sneakers, teal windbreaker, pink stripe.
    swing=math.sin(phase)*13 if pose=='walk' else 0
    a.oval((49,307,203,329),(13,27,47,65))
    for x,k in [(105,swing),(145,-swing)]:
        a.line([(x,230),(x+k*.3,270),(x+k,308)],(36,58,82),19)
        a.poly([(x+k-13,303),(x+k+7,302),(x+k+22,313),(x+k+21,321),(x+k-18,321)],CREAM,INK,2)
        a.line([(x+k-14,315),(x+k+16,315)],PINK,3)
    # Behind-arm, soft padded jacket, and canvas shoulder bag.
    a.line([(89,160),(69-swing*.3,199),(81-swing,231)],TEAL,22)
    a.oval((72-swing,225,89-swing,244),(226,170,136),INK,1)
    a.poly([(93,136),(151,137),(174,178),(165,239),(88,239),(76,178)],TEAL,INK,3)
    a.poly([(83,176),(168,188),(168,205),(83,191)],(39,100,126))
    a.line([(81,177),(169,190)],PINK,8)
    a.line([(124,150),(130,233)],(193,240,214),2)
    a.line([(150,148),(104,220)],(238,197,141),9)
    a.rect((79,207,128,244),(228,185,133),INK,2,6)
    a.rect((92,216,115,229),CREAM)
    a.text((104,213),'AI',12,NAVY,'ma')
    arm=[(155,163),(178+swing*.3,199),(164+swing,228)]
    if pose in ['point','hold']:arm=[(155,163),(179,184),(204,160)]
    a.line(arm,TEAL,22)
    hx,hy=arm[-1];a.oval((hx-9,hy-9,hx+9,hy+10),(226,170,136),INK,1)
    a.rect((113,120,139,149),(226,170,136),INK,2,5)
    a.oval((86,52,163,137),(235,179,145),INK,3)
    a.poly([(86,79),(82,63),(96,45),(140,43),(160,62),(155,83),(143,72),
            (118,77),(112,64),(104,82)],(49,43,65))
    a.poly([(84,69),(152,55),(160,64),(86,79)],TEAL,INK,2)
    a.poly([(143,57),(181,64),(181,70),(149,72)],TEAL,INK,2)
    for x in [111,140]:a.oval((x-2,88,x+3,94),INK)
    a.line([(117,112),(128,117),(140,108)],INK,3)
    a.line([(127,93),(133,104),(127,105)],(183,112,101),2)
    if pose=='hold':
        a.rect((179,137,237,176),CREAM,TEAL,2,4)
        a.text((208,143),'24',24,NAVY,'ma')
    return im


def actor(im,x,y,t,pose='walk',scale=.59):
    px,py=P(x,y,4)
    spr=courier_sprite(t*8,pose)
    spr=spr.resize((round(240*scale),round(340*scale)),Image.Resampling.LANCZOS)
    im.alpha_composite(spr,(round(px-125*scale),round(py-318*scale)))


def on_path(points,p):
    lengths=[math.dist(P(*a),P(*b)) for a,b in zip(points,points[1:])]
    dist=clamp(p)*sum(lengths)
    for i,l in enumerate(lengths):
        if dist<=l or i==len(lengths)-1:
            u=clamp(dist/l)
            a,b=points[i],points[i+1]
            return (lerp(a[0],b[0],u),lerp(a[1],b[1],u))
        dist-=l
    return points[-1]


def route_line(a,points,color,amount=1,solid=True):
    pts=[P(x,y,6) for x,y in points]
    # Colored paths are deliberately lifted just above the floor, like mall wayfinding.
    col=mix(color,NAVY,1-amount)
    a.line(pts,(23,31,52),13)
    a.line(pts,mix(col,NAVY,.6),10)
    a.line(pts,col,4 if solid else 2)
    for p in [.18,.42,.69,.89]:
        x,y=on_path(points,p);nx,ny=on_path(points,min(1,p+.018))
        sx,sy=P(x,y,6);ex,ey=P(nx,ny,6)
        ang=math.atan2(ey-sy,ex-sx)
        a.poly([(sx+8*math.cos(ang),sy+8*math.sin(ang)),
                (sx+7*math.cos(ang+2.5),sy+7*math.sin(ang+2.5)),
                (sx+7*math.cos(ang-2.5),sy+7*math.sin(ang-2.5))],col)


def packet(a,xy,color,response=False):
    sx,sy=P(*xy,17)
    a.oval((sx-25,sy+16,sx+32,sy+30),(20,30,45,85))
    a.rect((sx-34,sy-25,sx+35,sy+22),CREAM, color,3,6)
    a.rect((sx-28,sy-19,sx+29,sy-10),color,None,1,2)
    a.text((sx,sy-5),'24',22,NAVY,'ma')
    if response:
        a.line([(sx+18,sy+5),(sx+23,sy+10),(sx+32,sy-3)],TEAL,4)


def pill(a,box,value,color=CYAN,size=21):
    a.rect(box,(24,32,57),mix(color,NAVY,.3),1,10)
    a.text(((box[0]+box[2])/2,box[1]+5),value,size,color,'ma')


def endpoint_overlay(a,status,t,open_amount=0):
    # Architectural plane remains fixed when the shutter lifts.
    if open_amount:
        top=12+151*open_amount
        a.poly([P(1189,828,12),P(1321,828,12),P(1321,828,top),P(1189,828,top)],
               (24,42,67))
        a.line([P(1190,827,top),P(1320,827,top)],(106,155,164),5)
        if open_amount>.6:
            for x in [1205,1238,1271]:
                a.box(x,842,21,17,37,(183,164,130),(122,123,119),(96,108,113),z=19)
        neon(a,[P(1187,826,14),P(1323,826,14)],GREEN,3)
    bx,by=P(1351,824,124)
    a.oval((bx+5,by-2,bx+18,by+11),GREEN if open_amount else GOLD)


def endpoint_annotation(a,status):
    # Large annotation sits above the shared door, connected with a fine rule.
    x0,y0,x1,y1=1445,161,1848,329
    a.rect((x0+7,y0+8,x1+7,y1+8),(10,17,35,80),None,1,14)
    a.rect((x0,y0,x1,y1),(32,49,73),mix(CYAN,NAVY,.65),2,14)
    a.text((x0+22,y0+13),'THE SAME SERVICE',20,CYAN)
    a.text((x0+22,y0+47),'Read issue TEAM-24',29,CREAM)
    a.text((x0+22,y0+89),'PROJECT A  /  READ ACCESS',19,(194,209,202))
    phrase={'idle':'Permission required','checking':'Checking caller + request',
            'approved':'Allowed for this request','response':'Issue returned'}[status]
    c=GREEN if status in ['approved','response'] else GOLD
    a.oval((x0+23,y0+131,x0+34,y0+142),c)
    a.text((x0+45,y0+121),phrase,23,c)
    a.line([(1646,329),(1646,353),screen_point(P(1270,841,239))],mix(CYAN,NAVY,.4),2)


def station_action(a,idx,t,state):
    if idx==0:
        px,py=P(181,114,260)
        a.rect((px+5,py+73,px+130,py+93),(114,57,109),PINK,2,3)
        a.text((px+14,py+74),'READ ISSUE',14,CREAM)
        if state=='select':
            a.poly([(px+119,py+83),(px+110,py+88),(px+114,py+73)],CREAM)
    elif idx==1:
        px,py=P(629,116,138)
        a.rect((px+6,py+7,px+102,py+66),(20,50,62),None,1,5)
        q=clamp((t-STARTS[1])/1.3)
        first='> get issue'[:round(q*11)]
        second='TEAM-24'[:round(clamp((q-.45)/.55)*7)]
        a.text((px+12,py+14),first,16,GREEN)
        a.text((px+12,py+37),second+('_' if state=='select' else ''),17,GREEN)


def scene_state(t):
    if t>=29:return 3,'summary',1
    route=0 if t<11 else 1 if t<20 else 2
    dt=t-STARTS[route]
    if dt<1.3:return route,'select',clamp(dt/1.3)
    if dt<3.8:return route,'outbound',prog(dt,1.3,3.8)
    if dt<4.65:return route,'checking',0
    if dt<5.45:return route,'approved',0
    if dt<7.2:return route,'response',prog(dt,5.45,7.2)
    return route,'complete',1


def compose(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=base_plate().copy();a=Art(im)
    idx,state,p=scene_state(t)
    # These are wayfinding stripes for this one illustrative request.
    for i,r in enumerate(ROUTES):
        if i<=idx:
            route_line(a,r,COLORS[i],.95 if idx==3 or i==idx else .33)
    # Three station number badges use shape and text in addition to color.
    for i,(wx,wy) in enumerate([(250,103),(684,102),(1120,59)]):
        x,y=P(wx,wy,85)
        if i==1:y+=57
        col=COLORS[i]
        a.oval((x-20,y-20,x+20,y+20),NAVY,col,2)
        a.text((x,y-17),str(i+1),26,col,'ma')
    positions=[(142,86),(578,77),(1013,24)]
    if idx<3:
        actor(im,*positions[idx],amb,pose='point' if state=='select' else 'hold' if state=='complete' else 'stand',scale=.58)
        station_action(a,idx,t,state)
    else:
        # All couriers hold the same issue result in the closing tableau.
        for pos in positions:actor(im,*pos,amb,pose='hold',scale=.58)
    endpoint='idle'
    if state in ['outbound','response']:
        xy=on_path(ROUTES[idx],p if state=='outbound' else 1-p)
        packet(a,xy,COLORS[idx],state=='response')
    if state=='checking':endpoint='checking'
    if state=='approved':
        endpoint='approved';packet(a,ROUTES[idx][-1],COLORS[idx])
    if state in ['response','complete','summary']:endpoint='response'
    opened=prog(t,STARTS[idx]+4.65,STARTS[idx]+5.05) if idx<3 and state=='approved' else (1 if endpoint=='response' else 0)
    endpoint_overlay(a,endpoint,amb,opened)
    # In-world fluorescent pulse, low amplitude and no flashes.
    x,y=P(1134,824,145)
    glow=round(160+25*math.sin(amb*math.tau/3))
    a.oval((x-4,y-4,x+4,y+4),(*CYAN,glow))
    a.line([P(0,654,195),P(980,654,195)],mix(PINK,CREAM,.18+.06*math.sin(amb*math.tau/3)),2)
    # Fit the miniature into its own composition band; headers never cover art.
    # A modest establishing push settles before the first request is dispatched.
    camera=.78+.04*prog(t,0,2.4)
    scene=im.resize((round(W*camera),round(H*camera)),Image.Resampling.LANCZOS)
    im=backdrop().copy()
    im.alpha_composite(scene,(round((W-W*camera)/2),round(150+(1-camera/.82)*360)))
    a=Art(im)
    # All labels remain still and legible while tiny fixture glints keep holds alive.
    a.text((79,35),'THE MALL BEHIND THE MALL',49,CREAM)
    a.text((82,96),'THREE ROUTES TO THE SAME SERVICE',20,(178,181,203))
    pill(a,(1552,43,1847,85),'AI BASICS  /  NUGGET 08',CYAN,20)
    a.line([(80,131),(1848,131)],(72,68,103),1)
    endpoint_annotation(a,endpoint)
    # Teaching captions sit on a separate quiet band below the mall miniature.
    a.rect((0,947,W,H),(15,23,43))
    a.line([(80,947),(1848,947)],(83,69,103),1)
    titles=['MCP: choose a tool.','CLI: run a command.','API: send a request.',
            'Same destination. Different way of getting there.']
    subt=['The tool makes the service request.',
          'The command makes the service request.',
          'The agent sends the service request directly.',
          'This example uses the same request and permissions.']
    a.text((80,968),titles[idx],37,CREAM)
    a.text((82,1023),subt[idx],22,(179,191,197))
    # Small progressing route legend; final frame is a useful standalone visual.
    for i,label in enumerate(['MCP','CLI','API']):
        x=1490+i*124
        col=COLORS[i] if i<=idx else (99,106,127)
        a.oval((x,989,x+10,999),col)
        a.text((x+18,974),label,28,col)
        if idx==3:a.line([(x+40,1023),(x+47,1030),(x+60,1015)],GREEN,3)
    # Soft vignette and film grain are static in holds, avoiding distracting boil.
    return im.convert('RGB')


def audits():
    AUDIT.mkdir(parents=True,exist_ok=True)
    samples=[1.6,5.4,7.6,9.1,14.5,16.1,18.1,23.5,25.1,27.2,31]
    sheet=Image.new('RGB',(1920,math.ceil(len(samples)/3)*392),(15,23,43))
    for i,t in enumerate(samples):
        img=compose(t);img.save(AUDIT/f'mall_routes_{t:04.1f}.jpg',quality=94)
        thumb=img.resize((640,360),Image.Resampling.LANCZOS)
        sheet.paste(thumb,((i%3)*640,(i//3)*392))
        ImageDraw.Draw(sheet).text(((i%3)*640+15,(i//3)*392+362),
                                  f'{t:g}s',font=font(20),fill=CREAM)
    sheet.save(AUDIT/'storyboard.jpg',quality=94)
    compose(31).save(OUT/'mall_routes_still.png')


def encode(path,frames):
    path.parent.mkdir(parents=True,exist_ok=True)
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast',
         '-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i,img in enumerate(frames):
            proc.stdin.write(img.tobytes())
            if i%150==0:print(f'{path.name}: {i} frames',flush=True)
    finally:proc.stdin.close()
    if proc.wait():raise RuntimeError(f'FFmpeg failed: {path}')


def write_player():
    PLAYER.mkdir(parents=True,exist_ok=True)
    manifest=[{'label':title,'src':f'stages/{i+1:02}.mp4','hold':f'holds/{i+1:02}.mp4'}
              for i,(title,_,_) in enumerate(STAGES)]
    (PLAYER/'index.html').write_text((HERE/'player.html').read_text().replace('/* STAGES */',json.dumps(manifest)))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    audits();write_player()
    if args.prepare_only:return
    master=OUT/'mall_routes.mp4'
    encode(master,(compose(i/FPS) for i in range(round(DURATION*FPS))))
    for i,(_,start,end) in enumerate(STAGES):
        stage=PLAYER/'stages'/f'{i+1:02}.mp4';stage.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
                        '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p',
                        '-movflags','+faststart',str(stage)],check=True)
        encode(PLAYER/'holds'/f'{i+1:02}.mp4',(compose(end-1/FPS,j/FPS) for j in range(90)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];'
                    '[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle',
                    '-loop','0',str(OUT/'mall_routes.gif')],check=True)
    print(f'Preview: {PLAYER / "index.html"}',flush=True)


if __name__=='__main__':main()
