#!/usr/bin/env python3
"""Presenter-paced films for the mall/service-route training nugget.

The opener is unbranded daylight until the separately cued third beat. The
tool and terminal sequences are entirely in the hidden service corridor.
"""
from __future__ import annotations
import argparse
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import render_mall_routes as mall
from render_mall_routes import (Art,font,ease,prog,clamp,mix,lerp,tube,encode,
    CREAM,RED,PINK,CYAN,GOLD,TEAL,GREEN,MUTED,BLACK,W,H,FPS)

HERE=Path(__file__).resolve().parent
OUT=HERE/'out';PLAYER=HERE/'interactive';AUDIT=HERE/'source'
SCENES={
    'mall_opener':{'label':'Mall opener','duration':19,'poster':3,
        'beats':[('A familiar mall',0,6),('Behind the storefronts',6,12),('Make it spooky',12,19)],
        'samples':[3,8,11,13.8,16.5,18.8]},
    'secret_elevator':{'label':'Secret elevator','duration':13,'poster':11.5,
        'beats':[('A normal service elevator',0,5),('Going suspiciously far down',5,13)],
        'samples':[1.5,4.5,6.5,8.5,10.5,12.5]},
    'mcp_directory':{'label':'MCP directory','duration':34,'poster':12,
        'beats':[('A useful menu',0,7),('The menu grows',7,15),('The wrong tool',15,24),('Choose again',24,34)],
        'samples':[2,6,9,12,16,19.5,22,25.5,29,33]},
    'cli_terminal':{'label':'CLI terminal','duration':35,'poster':11,
        'beats':[('Type a command',0,9),('Read the result',9,17),('A command mistake',17,25),('Correct and retry',25,35)],
        'samples':[1.5,4.8,8.8,11,13.5,16,20,23,27,30,34]},
    'mcp_cli_overlap':{'label':'MCP + CLI overlap','duration':26,'poster':22,
        'beats':[('Two entrances',0,7),('Shared capabilities',7,16),('One, the other, or both',16,26)],
        'samples':[1.5,5.8,8.5,12,15.5,17.5,21.5,25.5]},
    'agency_guardrails':{'label':'Agency + guardrails','duration':31,'poster':23,
        'beats':[('One approved action',0,8),('A goal with choices',8,18),('Choices inside boundaries',18,25),('Keep the gates',25,31)],
        'samples':[1.5,5.5,8.5,12,17.5,19,23.5,26,28,30.5]},
    'context_handoff':{'label':'Next: context','duration':15,'poster':13,
        'beats':[('What the agent carries',0,8),('Next: context',8,15)],
        'samples':[1,3.5,7.5,9,12,14.5]},
}


def footer(im,title,subtitle,step,total,day=False):
    a=Art(im,mall.day_color if day else None)
    a.line([(80,949),(1840,949)],(81,37,51))
    a.text((80,968),title,38,CREAM)
    a.text((82,1020),subtitle,25,MUTED)
    for i in range(total):
        x=1838-total*42+i*42;a.line([(x,985),(x+24,985)],RED if i==step else (62,42,53),4)
    a.text((1837,1016),f'{step+1:02} / {total:02}',19,MUTED,'ra',kind='mono')


@lru_cache(maxsize=2)
def intro_plate(day):
    if day:
        im=Image.new('RGBA',(W,H),(247,244,234));a=Art(im)
        a.text((82,49),'AI BASICS',20,(85,108,114));a.text((82,77),'NUGGET 08',17,(111,131,133))
        a.text((960,60),'THE MALL BEHIND THE MALL',65,(34,74,83),'ma')
        a.text((960,145),'A familiar place. A hidden network.',27,(98,116,118),'ma')
        a.line([(470,199),(1450,199)],(143,171,166),2)
    else:im=mall.background().copy()
    im.alpha_composite(mall.public_plate(day))
    a=Art(im,mall.day_color if day else None)
    a.rect((104,248,526,281),(12,21,31),(50,75,91),1,3)
    a.text((120,250),'PUBLIC STOREFRONTS · USER INTERFACE',18,CYAN)
    # Three ordinary back doors replace the agent-route diagrams for this opener.
    a.rect((80,650,1840,928),(14,21,30),(57,56,72),2)
    a.poly([(80,650),(1840,650),(1799,689),(121,689)],(22,30,41))
    a.poly([(80,928),(121,895),(1799,895),(1840,928)],(34,41,50))
    for y in range(704,897,43):
        a.line([(121,y),(1799,y)],(29,39,49))
        for x in range(151+((y//43)%2)*60,1798,123):a.line([(x,y),(x,y+41)],(26,35,45))
    mall.pipe(a,666,(67,43,51));mall.pipe(a,680,(44,59,69))
    for x,label in [(280,'STOCKROOM'),(825,'KITCHEN'),(1370,'DELIVERIES')]:
        a.rect((x-7,704,x+205,898),(57,67,75),(104,111,116),2)
        a.rect((x,711,x+198,895),(35,47,56),(11,22,29),2)
        a.rect((x+12,722,x+186,757),(19,32,39),(81,95,104),1,3)
        a.text((x+99,726),label,23,CREAM,'ma')
        a.rect((x+152,796,x+176,834),(15,26,34),(83,99,108),1,3)
        a.oval((x+159,804,x+169,814),GOLD)
        a.line([(x+155,842),(x+181,842)],MUTED,4)
        a.rect((x+47,687,x+151,697),(74,91,101),None,1,3)
        a.line([(x+53,691),(x+145,691)],CREAM,2)
    # A cart and delivery boxes make the corridor a concrete place.
    a.rect((575,808,711,873),(71,78,85),(101,116,124),2)
    a.rect((587,765,647,807),(135,102,72),(181,151,109),2)
    a.rect((651,779,697,807),(133,94,68),(181,151,109),2)
    for x in [590,691]:a.oval((x-9,875,x+9,893),(28,35,42),MUTED,2)
    a.line([(571,808),(566,786),(549,782)],MUTED,4)
    a.rect((102,652,767,683),(9,17,26),(61,66,81),1,2)
    a.text((119,651),'HIDDEN SERVICE CORRIDOR · CUTAWAY VIEW',22,CREAM)
    return im


@lru_cache(maxsize=2)
def intro_cover(day):
    im=Image.new('RGBA',(1760,277));a=Art(im,mall.day_color if day else None)
    a.rect((0,0,1759,276),(10,13,23))
    for y in range(0,277,44):
        a.line([(0,y),(1759,y)],(28,29,40))
        for x in range((y//44%2)*95,1760,190):a.line([(x,y),(x,y+42)],(24,27,37))
    a.text((880,78),'BEHIND THE WALL',26,(149,89,101),'ma')
    a.text((880,132),'The service corridors are out of sight.',33,MUTED,'ma')
    return im


def opener_layer(t,day):
    im=intro_plate(day).copy();q=prog(t,6.4,9.5)
    shift=round(q*277)
    if shift<277:im.alpha_composite(intro_cover(day).crop((0,0,1760,277-shift)),(80,651+shift))
    a=Art(im,mall.day_color if day else None)
    if 0<q<1:a.line([(81,651+shift),(1839,651+shift)],CYAN,2)
    if t<6:title,sub,step='Picture a platform as a shopping mall.','The storefronts are what the customer sees.',0
    elif t<12:title,sub,step='Behind the shops: rooms and service corridors.','They stay out of the customer’s view.',1
    else:title,sub,step='Welcome to Starcourt.','The service entrances still stay out of sight.',2
    footer(im,title,sub,step,3,day)
    return im


def compose_opener(t,ambient_t=None):
    # No branded lettering or spooky palette occurs in the first two beats.
    q=prog(t,12.65,16.3)
    if q==0:
        im=opener_layer(t,True)
        # The cue starts on the exact previous hold before revealing the reference.
        if t>=12:
            a=Art(im);a.rect((0,950,W,H),(247,244,234))
            footer(im,'Behind the shops: rooms and service corridors.',
                   'They stay out of the customer’s view.',1,3,True)
    elif q==1:im=opener_layer(t,False)
    else:
        # A gentle lights-out transition avoids overlapping differently named
        # storefronts and title letterforms. No strobe or rapid flashes.
        dark=Image.new('RGBA',(W,H),(*BLACK,255))
        if q<.48:im=Image.blend(opener_layer(11.99,True),dark,ease(q/.48))
        elif q<.55:im=dark
        else:im=Image.blend(dark,opener_layer(t,False),ease((q-.55)/.45))
    return im.convert('RGB')


@lru_cache(maxsize=3)
def service_set(top,bottom):
    im=mall.background(top,bottom).copy();a=Art(im)
    a.rect((80,235,1840,927),(12,22,32),(55,61,73),2)
    a.poly([(80,235),(1840,235),(1784,300),(136,300)],(24,32,44))
    a.poly([(80,927),(136,860),(1784,860),(1840,927)],(33,41,50))
    for y in range(311,861,69):
        a.line([(136,y),(1784,y)],(29,41,53))
        for x in range(136+((y//69)%2)*90,1784,180):a.line([(x,y),(x,y+66)],(27,37,48))
    for y,col in [(261,(72,41,48)),(279,(46,60,72))]:mall.pipe(a,y,col)
    for x in [256,932,1650]:
        a.rect((x-59,292,x+59,307),(49,60,75),(78,88,100),1,3)
        tube(a,[(x-49,299),(x+49,299)],(135,165,188),2)
        a.poly([(x-49,310),(x+49,310),(x+148,860),(x-148,860)],(18,31,44))
    for x in [103,1810]:tube(a,[(x,526),(x,559)],RED,4)
    a.rect((102,237,695,269),(9,17,26),(61,66,81),1,2)
    a.text((118,238),'BACKSTAGE · HIDDEN FROM THE PUBLIC',22,CREAM)
    return im


def robot(a,x,y,pose='read',scale=1):
    def rect(b,fill,outline=None,width=2,radius=0):
        a.rect(tuple((x+v*scale) if i%2==0 else (y+v*scale) for i,v in enumerate(b)),fill,outline,width,round(radius*scale))
    def line(pts,col,width=3):a.line([(x+px*scale,y+py*scale) for px,py in pts],col,width)
    a.oval((x-80*scale,y+153*scale,x+84*scale,y+176*scale),(6,12,19))
    rect((-46,128,-13,163),(24,63,65),TEAL,2,7);rect((13,128,46,163),(24,63,65),TEAL,2,7)
    rect((-66,23,66,135),(24,88,84),TEAL,3,18)
    rect((-71,-71,71,29),(23,62,66),TEAL,3,20)
    line([(0,-72),(0,-90)],TEAL,3);a.oval((x-7*scale,y-103*scale,x+7*scale,y-89*scale),CYAN)
    for xx in [-29,24]:
        rect((xx,-34,xx+12,-19),CREAM,None,1,3)
    if pose=='confused':
        line([(-20,7),(-7,-1),(8,7),(22,-1)],GOLD,3)
        a.text((x+91*scale,y-98*scale),'?',round(57*scale),GOLD,'ma')
    else:line([(-24,5),(-13,11),(15,11),(28,3)],CYAN,3)
    if pose=='point':line([(66,55),(101,19),(141,5)],TEAL,12)
    else:line([(67,55),(83,97),(51,111)],TEAL,12)
    line([(-66,55),(-83,103),(-55,115)],TEAL,12)
    a.text((x,y+53*scale),'AI',round(36*scale),CREAM,'ma')


def token_coins(a,t,active):
    if not active:return
    # Symbolic coins, deliberately no numeric cost claim.
    a.text((246,900),'MORE TOKENS',22,GOLD,'ma')
    for i in range(3):
        phase=(t*.52+i*.27)%1
        x=193+i*51;y=868+phase*13
        a.oval((x-13,y-13,x+13,y+13),(115,77,40),GOLD,2)
        a.text((x,y-13),'T',19,GOLD,'ma')


def packet(a,path,p,label,color,returning=False):
    x,y=mall.on_path(path,p)
    a.rect((x-37,y-25,x+37,y+25),(13,26,37),color,3,7)
    a.text((x,y-20),label,27,CREAM,'ma')
    if returning:
        a.oval((x+23,y-35,x+47,y-11),GREEN)
        a.line([(x+29,y-24),(x+34,y-19),(x+42,y-29)],(11,43,38),2)


def hatch(a,x,y,w,h,status='idle'):
    a.rect((x-10,y-10,x+w+10,y+h+10),(56,68,78),(104,108,119),2,3)
    a.rect((x,y,x+w,y+h),(5,13,23))
    if status not in ['open','response']:
        a.rect((x,y,x+w,y+h),(60,75,88))
        for yy in range(y+9,y+h,15):a.line([(x+1,yy),(x+w-1,yy)],(22,37,49),2)
    else:
        for yy in [y+38,y+91]:a.line([(x+20,yy),(x+w-20,yy)],(99,81,68),4)
        a.rect((x+w/2-36,y+41,x+w/2+36,y+88),(111,83,61),(185,147,98),2)
        a.line([(x+w/2,y+43),(x+w/2,y+86)],GOLD,3)
    col=GOLD if status=='checking' else GREEN if status in ['open','response'] else MUTED
    a.rect((x-41,y+26,x-19,y+66),(14,28,39),MUTED,1,3)
    a.oval((x-36,y+34,x-25,y+45),col)
    a.text((x+w/2,y-49),'API ENDPOINT',24,CREAM,'ma')
    a.text((x+w/2,y+h+19),'CHECKING ACCESS' if status=='checking' else 'ACCESS ALLOWED' if status in ['open','response'] else 'SCOPED ACCESS',21,col,'ma')


@lru_cache(maxsize=2)
def extra_panel(side):
    w=350 if side=='left' else 557
    im=Image.new('RGBA',(w,342));a=Art(im)
    a.rect((0,0,w-1,341),(24,31,47),PINK,2,5)
    a.text((w/2,10),'MORE TOOLS',24,PINK,'ma')
    names=['Read project','Read issue links','Read issue history','Find issue comments','Search issue fields'] if side=='left' else [
           'Read issue attachments','Read issue watchers','Read issue transitions','Read issue worklogs','Read issue properties']
    descriptions=['Project details','Linked issues','Past changes','Search conversations','Issue field values'] if side=='left' else [
                  'Attached files','People following the issue','Available next steps','Time entries','Stored properties']
    for i,name in enumerate(names):
        y=54+i*56
        a.rect((12,y,w-13,y+48),(13,25,37),(65,73,93),1,3)
        a.text((24,y+2),name,22,CREAM)
        a.text((25,y+28),descriptions[i],16,MUTED)
    return im


def backpack(a,fill,t):
    x,y=1587,789
    a.line([(x-68,y-79),(x-68,y-104),(x+68,y-104),(x+68,y-79)],(82,120,123),12)
    a.rect((x-158,y-87,x+158,y+112),(24,58,65),TEAL,3,29)
    a.rect((x-167,y-52,x-147,y+74),(35,86,88),TEAL,2,7)
    a.rect((x+147,y-52,x+167,y+74),(35,86,88),TEAL,2,7)
    a.rect((x-156,y-89,x+156,y-21),(32,79,83),TEAL,2,22)
    a.text((x,y-75),'AGENT’S CONTEXT',27,CREAM,'ma')
    a.rect((x-122,y+4,x+122,y+88),(17,42,52),(80,135,138),2,12)
    a.text((x,y+13),'ROOM USED',19,MUTED,'ma')
    a.rect((x-99,y+48,x+99,y+68),(8,25,35),(65,113,121),1,4)
    a.rect((x-97,y+50,x-97+194*fill,y+66),GOLD if fill>.7 else CYAN,None,1,3)
    # Description cards sit above the flap, making the bag visibly overstuffed.
    for i in range(round(max(0,fill-.25)*13)):
        xx=x-100+i*28;yy=y-109-(i%3)*10
        a.rect((xx,yy,xx+25,yy+27),(183,160,151),PINK,1,2)
        a.line([(xx+4,yy+8),(xx+20,yy+8)],(91,64,82),1)


MCP_PATH=[(1248,630),(1353,630),(1353,466),(1450,466)]


def mcp_state(t):
    """Returns phase, chosen tool, motion progress. Choice 1 is the wrong tool."""
    if 7<=t<15:return 'expand',-1,prog(t,7,10)
    offset=0 if t<7 else 15 if t<24 else 24
    dt=t-offset;choice=1 if offset==15 else 0
    times=(3,4.2,5,5.4,6.4) if offset==0 else (1,3,3.8,4.2,5.5) if offset==15 else (1.5,3.5,4.3,4.8,6.3)
    a,b,c,d,e=times
    if dt<a:return 'select',choice,prog(dt,0,a)
    if dt<b:return 'outbound',choice,prog(dt,a,b)
    if dt<c:return 'checking',choice,0
    if dt<d:return 'open',choice,0
    if dt<e:return 'response',choice,prog(dt,d,e)
    return 'wrong' if choice else 'complete',choice,1


def compose_mcp(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=service_set('THE TOOL','DIRECTORY').copy();a=Art(im)
    phase,choice,p=mcp_state(t)
    expanded=prog(t,7.1,10.2)
    # The end-user never visits this directory: it is the tool menu metaphor.
    a.rect((741,237,1788,269),(9,17,26),(61,66,81),1,2)
    a.text((1265,238),'TASK: READ ISSUE TEAM-24',22,CREAM,'ma')
    hatch(a,1450,365,250,198,phase if phase in ['checking','open','response'] else 'open' if phase in ['complete','wrong'] else 'idle')
    tube(a,MCP_PATH,PINK if phase not in ['expand'] else (81,69,83),3)
    # Hinged wings unfold independently, then the right wing folds to reveal
    # the physical service hatch again for the request/response demonstration.
    right=expanded*(1-prog(t,15,16))
    for side,q in [('left',expanded),('right',right)]:
        if q>.001:
            panel=extra_panel(side);width=max(2,round(panel.width*q))
            panel=panel.resize((width,342),Image.Resampling.BICUBIC)
            im.alpha_composite(panel,(440-width if side=='left' else 1263,314))
    a=Art(im)
    a.rect((440,317,1257,814),(57,55,77),(152,103,130),3,10)
    a.rect((452,329,1245,802),(12,23,37),(95,63,89),2,7)
    a.rect((468,343,1230,400),(37,29,51),PINK,2,4)
    a.text((849,346),'MCP TOOL DIRECTORY',39,PINK,'ma')
    names=['Read issue','Read issue comments','Read issue history' if expanded>.5 else 'Search docs']
    descriptions=['Get the issue’s details.','Get the conversation on an issue.',
                  'Get the changes made to an issue.' if expanded>.5 else 'Find documents matching a search.']
    for i,(name,description) in enumerate(zip(names,descriptions)):
        y=422+i*99
        selected=choice==i and phase!='expand'
        col=GOLD if selected and choice==1 else PINK if selected else (72,85,107)
        a.rect((477,y,1221,y+84),(36,37,52) if selected else (18,31,45),col,3 if selected else 1,5)
        a.text((499,y+6),name,33,CREAM)
        a.text((501,y+49),description,23,MUTED)
        if selected:a.poly([(1186,y+27),(1202,y+42),(1186,y+57)],col)
    a.text((849,743),'Choose a tool by its description.',24,MUTED,'ma')
    a.text((849,775),'Each tool exposes a particular action.',18,(116,133,151),'ma')
    # Agent, context bag, and symbolic token meter remain outside the menu.
    robot(a,242,744,'confused' if phase=='wrong' else 'point' if phase=='select' else 'read',.68)
    fill=.22+.60*prog(t,7.5,13.7)+.07*prog(t,24,30)
    backpack(a,fill,amb)
    if 7.6<t<14.6:
        for i in range(5):
            q=clamp((t-(7.6+i*.85))/2.8)
            if 0<q<1:
                x=lerp(1140,1560,ease(q));y=lerp(477,676,ease(q))-math.sin(q*math.pi)*94
                a.rect((x-26,y-22,x+26,y+22),(205,175,171),PINK,2,3)
                for off in [-9,0,9]:a.line([(x-17,y+off),(x+17,y+off)],(92,61,80),2)
    if phase in ['outbound','response']:
        packet(a,MCP_PATH,p if phase=='outbound' else 1-p,'24',PINK,phase=='response')
    if phase in ['complete','wrong']:
        col=GOLD if phase=='wrong' else GREEN
        a.rect((124,770,355,829),(86,65,54),col,2,5)
        a.line([(239,772),(239,828)],(180,137,90),5)
        a.rect((138,784,341,818),(15,29,35),col,1,2)
        a.text((239,785),'COMMENTS' if phase=='wrong' else 'ISSUE TEAM-24',23,col,'ma')
        if phase=='wrong':a.text((239,836),'WRONG TOOL',23,GOLD,'ma')
    token_coins(a,amb,7.5<t<15 or t>=21)
    if t<7:title,sub,step='A menu of tools, with descriptions.','The agent chooses an action for the task.',0
    elif t<15:title,sub,step='More descriptions take more context.','Reading the menu also uses tokens.',1
    elif t<24:title,sub,step='Similar names. The wrong tool.','Comments arrive when the agent needs issue details.',2
    else:title,sub,step='Choose again. Get the right result.','Recovering from a wrong choice uses more tokens.',3
    footer(im,title,sub,step,4)
    return im.convert('RGB')


CLI_PATH=[(1140,490),(1280,490),(1280,419),(1450,419)]


def cli_state(t):
    if 9<=t<17:return 'inspect',1
    if 17<=t<25:return ('typo',prog(t,17.3,19.5)) if t<20 else ('error',0)
    dt=t if t<9 else t-25
    if dt<2.7:return 'type',prog(dt,.35,2.6)
    if dt<4.2:return 'outbound',prog(dt,2.7,4.2)
    if dt<5.2:return 'checking',0
    if dt<5.8:return 'open',0
    if dt<7:return 'response',prog(dt,5.8,7)
    return 'complete',prog(dt,7,8.7)


@lru_cache(maxsize=1)
def crt_plate():
    im=Image.new('RGBA',(W,H));a=Art(im)
    a.oval((301,823,1182,906),(7,14,23))
    a.poly([(327,348),(364,315),(1123,315),(1166,352)],(122,116,127),(63,64,84),2)
    a.poly([(1140,352),(1166,352),(1166,723),(1140,755)],(66,72,91),(47,56,72),2)
    a.rect((327,344,1140,755),(93,96,110),(153,149,154),3,27)
    a.rect((367,380,1089,696),(32,51,65),(45,65,77),6,28)
    a.rect((382,396,1075,679),(6,25,32),(19,58,61),3,17)
    for y in range(401,675,5):a.line([(397,y),(1060,y)],(10,30,36),1)
    a.text((736,352),'SERVICE TERMINAL',21,(213,205,198),'ma')
    a.text((737,713),'ILLUSTRATIVE COMMAND',20,(206,210,208),'ma')
    for x in [1041,1091]:a.oval((x,709,x+20,729),(27,40,51),(149,151,158),2)
    a.oval((1062,745,1071,754),GREEN)
    a.poly([(365,764),(1106,764),(1181,867),(289,867)],(74,87,104),(124,136,149),2)
    for row in range(4):
        yy=779+row*19
        for i in range(14):
            xx=375+i*48-row*11
            a.rect((xx,yy,xx+36,yy+12),(40,59,77),(105,117,131),1,2)
    a.line([(584,856),(888,856)],(32,48,65),10)
    return im


def receipt(a,amount,highlight=None):
    x,y,w,h=1288,566,485,319
    # A clipping layer ensures the receipt emerges from the printer slot.
    page=Image.new('RGBA',(w,h));p=Art(page)
    p.rect((0,0,w-1,h-1),(231,226,208),(147,151,145),1)
    for i in range(16):p.poly([(i*32,h-1),(i*32+8,h-9),(i*32+16,h-1)],(37,47,53))
    p.text((w/2,10),'SERVICE RESPONSE',26,(37,63,67),'ma')
    p.line([(22,48),(w-22,48)],(144,157,147),1)
    rows=[('KEY','TEAM-24'),('STATUS','IN PROGRESS'),('PROJECT','A'),('PRIORITY','NORMAL'),('CHECKLIST','DONE')]
    for i,(label,value) in enumerate(rows):
        yy=65+i*42
        if highlight==i:p.rect((14,yy-3,w-15,yy+34),(222,198,151) if i==4 else (168,207,187),(122,134,117),1,3)
        p.text((25,yy),label,21,(78,95,97),kind='mono')
        p.text((w-25,yy),value,23,(25,65,64),'ra',kind='mono')
    p.text((w/2,285),'END OF RESPONSE',17,(107,122,116),'ma')
    visible=round(h*clamp(amount))
    if visible>0:a.im.alpha_composite(page.crop((0,0,w,visible)),(x,y))


def compose_cli(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=service_set('THE SERVICE','TERMINAL').copy();a=Art(im)
    phase,p=cli_state(t)
    a.rect((741,237,1788,269),(9,17,26),(61,66,81),1,2)
    a.text((1265,238),'TASK: READ ISSUE TEAM-24',22,CREAM,'ma')
    hatch(a,1450,320,250,165,'open' if phase in ['complete','inspect'] else phase if phase in ['checking','open','response'] else 'idle')
    tube(a,CLI_PATH,CYAN if phase not in ['typo','error'] else (59,76,89),3)
    im.alpha_composite(crt_plate());a=Art(im)
    command='issue reed TEAM-24' if phase in ['typo','error'] else 'issue read TEAM-24'
    typed=command[:round(len(command)*p)] if phase in ['type','typo'] else command
    a.text((408,418),'> '+typed+('_' if phase in ['type','typo'] else ''),29,GREEN,kind='mono')
    if phase=='error':
        a.text((408,488),'Unknown command: reed',29,(240,140,123),kind='mono')
        a.text((408,543),'Try: issue read TEAM-24',27,CREAM,kind='mono')
        a.text((408,602),'Request not sent.',25,MUTED,kind='mono')
    elif phase in ['checking','outbound','open']:
        a.text((408,502),'Requesting issue…',28,CYAN,kind='mono')
    elif phase in ['response','complete','inspect']:
        a.text((408,493),'Result received: TEAM-24',28,CYAN,kind='mono')
        a.text((408,544),'Read the response →',27,CREAM,kind='mono')
        if 11<t<13.8:a.text((408,601),'Issue done?',29,GOLD,kind='mono')
        elif t>=13.8 and t<17:a.text((408,601),'Still in progress.',28,GREEN,kind='mono')
    # Printer; paper emerges only when the service has actually returned data.
    a.rect((1269,531,1792,575),(79,95,107),(124,144,157),2,8)
    a.rect((1288,552,1773,566),(4,17,26),(44,63,76),2,4)
    a.text((1531,532),'RETURNED DATA',19,CREAM,'ma')
    amount=p if phase=='complete' else 1 if phase=='inspect' else 0
    highlight=4 if 11<t<13.8 else 1 if 13.8<=t<17 or t>33 else None
    receipt(a,amount,highlight)
    if phase in ['outbound','response']:
        packet(a,CLI_PATH,p if phase=='outbound' else 1-p,'24',CYAN,phase=='response')
    robot(a,199,720,'confused' if phase=='error' or 11<t<13.8 else 'point',.64)
    a.text((190,623),'AI AGENT',21,TEAL,'ma')
    if phase=='error':
        a.rect((1288,648,1773,780),(19,31,43),(133,86,85),2,5)
        a.text((1531,671),'NO SERVICE CALL',31,(227,154,136),'ma')
        a.text((1531,728),'The command needs correcting.',24,MUTED,'ma')
    if t<9:title,sub,step='Type a command. Read what comes back.','Can be lighter on context.',0
    elif t<17:
        title='A result still needs careful reading.'
        sub='A completed checklist doesn’t mean a completed issue.';step=1
    elif t<25:title,sub,step='A small typo. A command error.','The request never leaves the terminal.',2
    else:title,sub,step='Correct the command. Try again.','The agent still has to interpret the result.',3
    footer(im,title,sub,step,4)
    return im.convert('RGB')


def capability_door(a,x,y,label,access,active=False):
    col=GREEN if active else (82,94,108)
    a.rect((x,y,x+350,y+110),(15,27,39),col,3 if active else 1,7)
    a.rect((x+16,y+15,x+82,y+94),(35,47,59),(94,104,112),2,4)
    for yy in range(y+24,y+90,13):a.line([(x+19,yy),(x+79,yy)],(20,30,42),2)
    a.text((x+104,y+16),label,27,CREAM)
    a.text((x+105,y+56),access,19,col)
    if active:
        a.oval((x+315,y+14,x+337,y+36),GREEN)
        a.line([(x+321,y+25),(x+326,y+30),(x+334,y+19)],(10,39,35),2)


def entry_terminal(a,x,y,label,color,subtitle,active=True):
    col=color if active else mix(color,BLACK,.68)
    a.rect((x,y,x+380,y+154),(17,28,42),col,3 if active else 1,10)
    a.rect((x+17,y+18,x+363,y+72),(36,31,52),col,2,5)
    a.text((x+190,y+24),label,31,col,'ma')
    a.text((x+190,y+89),subtitle,21,CREAM if active else MUTED,'ma')
    a.text((x+190,y+119),'AGENT ACCESS POINT',16,MUTED,'ma')


MCP_SHARED=[(470,423),(650,423),(750,535),(1390,535)]
CLI_SHARED=[(470,688),(650,688),(750,590),(1390,590)]


def compose_overlap(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=service_set('TWO WAYS','ONE PLATFORM').copy();a=Art(im)
    a.rect((746,237,1788,269),(9,17,26),(61,66,81),1,2)
    a.text((1267,238),'ROVO MCP + TEAMWORK GRAPH CLI',22,CREAM,'ma')
    mcp_on=prog(t,1,3);cli_on=prog(t,3.4,5.7)
    shared=prog(t,7.5,11.2)
    a.rect((750,325,1785,780),(12,23,36),(66,68,91),2,9)
    a.text((1267,352),'SHARED TEAMWORK GRAPH TOOLS',32,CREAM,'ma')
    a.text((1267,403),'Some tools are available through either entrance.',25,MUTED,'ma')
    entry_terminal(a,90,346,'ROVO MCP',PINK,'Choose a described tool',mcp_on>.2)
    entry_terminal(a,90,611,'TEAMWORK GRAPH CLI',CYAN,'Run a command',cli_on>.2)
    # Both lanes visibly reach the SAME door. No invented exclusive actions.
    for path,col,on in [(MCP_SHARED,PINK,mcp_on),(CLI_SHARED,CYAN,cli_on)]:
        tube(a,path,mix(col,BLACK,.72*(1-on)),3 if on>.5 else 1)
    a.text((1060,481),'MCP TOOL',24,PINK,'ma')
    a.text((1060,627),'CLI COMMAND',24,CYAN,'ma')
    capability_door(a,1390,515,'SHARED TOOL','MCP  +  CLI',shared>.5)
    a.text((1267,715),'Two interfaces. An overlapping set of capabilities.',24,CREAM,'ma')
    if 16.2<t<19.5:
        packet(a,MCP_SHARED,prog(t,16.2,19.5),'M',PINK)
    if 19.7<t<23:
        packet(a,CLI_SHARED,prog(t,19.7,23),'C',CYAN)
    if t>=21:
        a.rect((800,822,1735,909),(18,31,43),GREEN,2,7)
        a.text((1267,841),'ONE · THE OTHER · OR BOTH',34,CREAM,'ma')
    robot(a,625,797,'point' if t<16 else 'read',.46)
    if t<7:title,sub,step='Two entrances to platform capabilities.','An agent may be set up with either route.',0
    elif t<16:title,sub,step='Some capabilities overlap.','The entrances stay independent.',1
    else:title,sub,step='Use one, the other, or both.','The agent’s setup determines what is available.',2
    footer(im,title,sub,step,3)
    return im.convert('RGB')


def audit_camera(a,x,y,active=True):
    col=GREEN if active else MUTED
    a.rect((x,y,x+74,y+45),(38,48,59),col,2,6)
    a.oval((x+22,y+9,x+55,y+40),(10,21,29),col,2)
    a.oval((x+33,y+19,x+44,y+30),col)
    a.line([(x+37,y+45),(x+37,y+64)],col,3)
    a.text((x+37,y+69),'AUDIT',15,col,'ma')


def goal_door(a,x,y,label,allowed=True,active=False):
    col=GREEN if active else CYAN if allowed else (122,59,67)
    a.rect((x,y,x+238,y+143),(14,25,37),col,3 if active else 1,6)
    a.rect((x+18,y+18,x+220,y+56),(25,39,50),(74,89,100),1,3)
    a.text((x+119,y+22),label,22,CREAM,'ma')
    a.text((x+119,y+82),'APPROVED' if allowed else 'OUT OF BOUNDS',18,col,'ma')
    a.rect((x+185,y+102,x+211,y+130),(26,38,47),MUTED,1,3)


def compose_agency(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=service_set('ROOM TO ACT','WITHIN BOUNDS').copy();a=Art(im)
    a.line([(900,315),(900,898)],(72,51,65),2)
    a.text((465,323),'PREDICTABLE REQUEST',24,MUTED,'ma')
    a.text((1355,315),'AGENTIC GOAL',21,MUTED,'ma')
    # Fixed path: one request, one door, one response.
    a.rect((112,384,416,470),(18,31,43),GOLD,2,8)
    a.text((264,394),'ONE APPROVED ACTION',24,GOLD,'ma')
    a.text((264,431),'GET ISSUE TEAM-24',20,CREAM,'ma')
    fixed=[(255,492),(255,620),(668,620),(668,492)]
    tube(a,fixed,GOLD,4)
    goal_door(a,550,350,'READ ISSUE',True,t<8)
    fixed_p=prog(t,1.2,3.6) if t<4 else 1-prog(t,4,6.8)
    packet(a,fixed,fixed_p,'24',GOLD,t>=4)
    a.rect((137,735,793,830),(17,29,41),(73,81,96),2,7)
    a.text((465,747),'FIXED ROUTE',27,CREAM,'ma')
    a.text((465,790),'Highly predictable · automation-like',20,MUTED,'ma')
    # Goal side: choices appear, but the security boundary stays explicit.
    # The notched boundary leaves the denied door physically OUTSIDE the zone.
    a.poly([(953,344),(1759,344),(1759,700),(1388,700),
            (1388,848),(953,848)],(11,25,35),GREEN,3)
    a.text((1356,352),'APPROVED ZONE',21,GREEN,'ma')
    a.rect((1003,392,1327,492),(37,28,48),PINK,2,7)
    a.text((1165,401),'UPDATE READY' if t>=22 else 'GOAL',18,GREEN if t>=22 else PINK,'ma')
    a.text((1165,434),'PREPARE PROJECT UPDATE',22,CREAM,'ma')
    goal_door(a,1430,388,'READ ISSUES',True,10<t<14)
    goal_door(a,1430,548,'SEARCH DOCS',True,14<=t<19)
    goal_door(a,1010,663,'DRAFT UPDATE',True,19<=t<25)
    goal_door(a,1430,708,'DELETE PROJECT',False,False)
    choice1=[(1278,540),(1370,540),(1370,459),(1430,459)]
    choice2=[(1278,540),(1364,540),(1364,619),(1430,619)]
    choice3=[(1278,540),(1278,734),(1248,734)]
    for path,on in [(choice1,t>=9),(choice2,t>=12),(choice3,t>=17)]:tube(a,path,GREEN if on else (48,62,70),3 if on else 1)
    # The agent stays at its decision point; requests return before the next
    # choice. This avoids teleporting the character between service doors.
    for route,start,end in [(choice1,9,13),(choice2,14,18),(choice3,19,22)]:
        if start<=t<end:
            p=prog(t,start,end)
            packet(a,route,2*p if p<.5 else 2-2*p,'✓' if p>=.5 else '?',GREEN,p>=.5)
    robot(a,1190,568,pose='point',scale=.35)
    audit_camera(a,961,541,True);audit_camera(a,1692,541,True)
    # Unsafe counterfactual: every branch lights briefly, then the gates return.
    risk=prog(t,25.2,27)*(1-prog(t,28.2,30.2))
    if risk>.01:
        for end in [(1782,370),(1810,500),(1805,666),(1772,810)]:
            a.line([(1350,540),end],mix(RED,BLACK,1-risk),max(2,round(7*risk)))
        a.text((1355,864),'TOO MANY UNBOUNDED OPTIONS',24,RED,'ma')
    gate=1-risk
    for x in [942,1768]:
        for i in range(6):
            yy=374+i*74
            h=52*gate
            a.rect((x,yy,x+18,yy+h),(99,40,52),RED,1,2)
    if t<8:title,sub,step='One request. One approved action.','Predictable enough to resemble automation.',0
    elif t<18:title,sub,step='A goal creates choices.','The agent uses judgment to plan the work.',1
    elif t<25:title,sub,step='Agency stays inside boundaries.','Permissions limit actions. Audit records show what happened.',2
    else:title,sub,step='More freedom needs stronger guardrails.','Keep the gates, permissions, and audit trail.',3
    footer(im,title,sub,step,4)
    return im.convert('RGB')


def context_bag(a,x,y,fill,scale=1):
    a.line([(x-88*scale,y-104*scale),(x-88*scale,y-137*scale),(x+88*scale,y-137*scale),(x+88*scale,y-104*scale)],(82,120,123),round(13*scale))
    a.rect((x-205*scale,y-111*scale,x+205*scale,y+154*scale),(24,58,65),TEAL,3,round(35*scale))
    a.rect((x-190*scale,y-114*scale,x+190*scale,y-31*scale),(32,79,83),TEAL,2,round(25*scale))
    a.text((x,y-99*scale),'AGENT’S CONTEXT',round(31*scale),CREAM,'ma')
    a.rect((x-154*scale,y+17*scale,x+154*scale,y+119*scale),(17,42,52),(80,135,138),2,round(12*scale))
    a.text((x,y+28*scale),'ROOM USED',round(20*scale),MUTED,'ma')
    a.rect((x-126*scale,y+72*scale,x+126*scale,y+96*scale),(8,25,35),(65,113,121),1,4)
    a.rect((x-123*scale,y+75*scale,x-123*scale+246*scale*fill,y+93*scale),GOLD if fill>.78 else CYAN,None,1,3)


def context_card(a,x,y,label,color,scale=1,angle=0):
    w,h=215*scale,72*scale
    a.rect((x-w/2,y-h/2,x+w/2,y+h/2),(24,35,48),color,2,5)
    a.text((x,y-14*scale),label,round(22*scale),CREAM,'ma')
    a.line([(x-w*.38,y+h*.2),(x+w*.38,y+h*.2)],mix(color,BLACK,.38),2)


def compose_context(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=service_set('WHAT THE AGENT','CARRIES').copy();a=Art(im)
    fill=.18+.75*prog(t,.8,7.2)
    bag_y=635+prog(t,8.3,10.2)*20
    context_bag(a,960,bag_y,fill,1.1)
    cards=[('TASK',PINK,(400,395),.7),('TOOL DESCRIPTIONS',CYAN,(770,395),1.8),
           ('RECENT RESULTS',GREEN,(1140,395),3.0),('ROUTE NOTES',GOLD,(1510,395),4.2)]
    for i,(label,col,startpos,start) in enumerate(cards):
        q=prog(t,start,start+2.4)
        # Keep readable labels as a legend while a copy moves into the bag.
        a.rect((startpos[0]-156,350,startpos[0]+156,439),(24,35,48),col,2,7)
        a.text((startpos[0],367),label,25,CREAM,'ma')
        a.text((startpos[0],402),'LOADED' if q>=.98 else 'READY TO LOAD',18,col,'ma')
        if 0<q<.98:
            x=lerp(startpos[0],960,ease(q));y=lerp(466,bag_y-135,ease(q))
            a.rect((x-37,y-22,x+37,y+22),(24,35,48),col,2,4)
            for offset in [-8,0,8]:a.line([(x-22,y+offset),(x+22,y+offset)],col,2)
        elif q>=.98:
            xx=840+i*80;yy=bag_y-145-(i%2)*10
            a.rect((xx-35,yy-22,xx+35,yy+22),(24,35,48),col,2,4)
    # Luggage scale enters for the next-nugget handoff.
    show=prog(t,8.2,10.5)
    if show>.02:
        y=825
        a.rect((660,y,1260,y+69),(42,49,60),(107,112,124),2,9)
        a.text((960,y+20),'Everything loaded takes room.',24,CREAM,'ma')
        # A separate scale display leaves the context meter fully visible.
        a.line([(1260,858),(1565,858),(1565,781)],(80,91,103),8)
        a.rect((1380,644,1750,799),(21,31,43),CYAN,2,8)
        a.text((1565,661),'NEXT: CONTEXT',33,CYAN,'ma')
        a.line([(1420,760),(1710,760)],(80,91,103),7)
        for x in range(1420,1711,29):a.line([(x,749),(x,765)],MUTED,2)
        needle=lerp(1440,1690,show)
        a.line([(1565,776),(needle,727)],GOLD,5)
    robot(a,348,703,'confused' if fill>.75 else 'point',.64)
    if t<8:title,sub,step='Every loaded item takes room.','Task, tools, history, results, and route notes.',0
    else:title,sub,step='Next stop: context.','What fits can shape what the agent remembers.',1
    footer(im,title,sub,step,2)
    return im.convert('RGB')


def compose_elevator(t,ambient_t=None):
    amb=t if ambient_t is None else ambient_t
    im=mall.background('SERVICE','ELEVATOR').copy();a=Art(im)
    a.rect((80,235,1840,928),(10,18,28),(59,58,73),2)
    # Cutaway shaft with floor markers and a surprisingly deep basement.
    a.rect((645,286,1275,902),(5,11,20),(84,76,87),4)
    for x in [690,1230]:a.line([(x,286),(x,902)],(72,82,93),7)
    for y,label in [(338,'SERVICE'),(468,'LOADING'),(598,'B1'),(728,'B2'),(858,'???')]:
        a.line([(645,y),(1275,y)],(47,52,67),2)
        a.text((1305,y-16),label,20,RED if label=='???' else MUTED)
    a.rect((105,324,515,621),(14,25,37),(66,75,88),2,8)
    a.text((310,345),'SERVICE LEVEL',25,CREAM,'ma')
    a.text((310,397),'A perfectly ordinary',22,MUTED,'ma')
    a.text((310,430),'back hallway elevator.',22,MUTED,'ma')
    a.rect((245,488,375,585),(25,36,46),(88,99,110),2,6)
    a.text((310,500),'↓',53,CYAN,'ma')
    a.oval((294,553,326,585),RED)
    a.text((310,554),'B',20,CREAM,'ma')
    q=prog(t,5.2,10.4);cab_y=300+q*492
    a.rect((720,cab_y,1200,cab_y+106),(33,43,55),(133,119,126),3,5)
    a.rect((743,cab_y+15,1177,cab_y+91),(13,26,37),(74,89,100),2,3)
    a.line([(960,cab_y+16),(960,cab_y+90)],(79,87,99),4)
    robot(a,885,cab_y+60,'confused' if q>.7 else 'read',.28)
    a.rect((880,cab_y-35,1040,cab_y-4),(12,21,31),RED if q>.8 else CYAN,1,3)
    a.text((960,cab_y-32),f'B{round(q*27):02}',18,CREAM,'ma',kind='mono')
    # Original cartoon lab: consoles, glowing chamber, suspicious inventory.
    glow=prog(t,9.3,11.3)
    if glow>.01:
        col=mix((42,31,49),RED,.35*glow)
        a.rect((1350,588,1787,884),(17,22,35),col,2,8)
        a.text((1568,607),'SECRET LAB?',28,RED,'ma')
        a.rect((1400,674,1508,830),(10,30,38),CYAN,2,24)
        a.oval((1426,703,1482,791),mix(CYAN,BLACK,.3),CYAN,2)
        for x in [1538,1640]:
            a.rect((x,700,x+82,816),(29,39,51),(83,91,105),2,4)
            a.rect((x+10,713,x+72,758),(11,35,43),GREEN,1,3)
            for k in range(3):a.line([(x+16,773+k*11),(x+66,773+k*11)],RED if k==1 else MUTED,2)
        for x in [1365,1515,1670]:
            a.rect((x,838,x+88,878),(91,66,56),(151,108,76),2)
            a.line([(x+44,840),(x+44,876)],GOLD,3)
        a.text((1568,648),'Definitely extra credit.',20,MUTED,'ma')
    if t<5:title,sub,step='A normal mall service elevator.','Probably.',0
    else:title,sub,step='Starcourt goes much farther down.','The secret lab is extra credit.',1
    footer(im,title,sub,step,2)
    return im.convert('RGB')


COMPOSERS={'mall_opener':compose_opener,'secret_elevator':compose_elevator,
           'mcp_directory':compose_mcp,'cli_terminal':compose_cli,
           'mcp_cli_overlap':compose_overlap,'agency_guardrails':compose_agency,
           'context_handoff':compose_context}


def audits(key):
    s=SCENES[key];folder=AUDIT/key;folder.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1920,math.ceil(len(s['samples'])/3)*392),BLACK)
    for i,t in enumerate(s['samples']):
        img=COMPOSERS[key](t);img.save(folder/f'{t:04.1f}.jpg',quality=94)
        sheet.paste(img.resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*392))
        ImageDraw.Draw(sheet).text(((i%3)*640+15,(i//3)*392+362),f'{t:g}s',font=font(20),fill=CREAM)
    sheet.save(folder/'storyboard.jpg',quality=94)
    COMPOSERS[key](s['poster']).save(OUT/f'{key}_still.png')


def render(key):
    s=SCENES[key];compose=COMPOSERS[key];master=OUT/f'{key}.mp4'
    encode(master,(compose(i/FPS) for i in range(round(s['duration']*FPS))))
    for i,(_,start,end) in enumerate(s['beats']):
        stage=PLAYER/'stages'/key/f'{i+1:02}.mp4';stage.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
            '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(stage)],check=True)
        encode(PLAYER/'holds'/key/f'{i+1:02}.mp4',(compose(end-1/FPS,j/FPS) for j in range(90)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
        'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];'
        '[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle','-loop','0',str(OUT/f'{key}.gif')],check=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--scene',choices=['all',*SCENES],default='all');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    keys=SCENES.keys() if args.scene=='all' else [args.scene]
    for key in keys:
        audits(key)
        if not args.prepare_only:render(key)
    write_player()
    print('Collection ready: http://127.0.0.1:8765/starcourt/interactive/index.html',flush=True)


def write_player():
    PLAYER.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for key,s in SCENES.items():
        manifest.append({'id':key,'label':s['label'],'duration':s['duration'],
            'src':f'../out/{key}.mp4','poster':f'../out/{key}_still.png',
            'beats':[{'label':label,'start':start,'end':end,'src':f'stages/{key}/{i+1:02}.mp4',
                      'hold':f'holds/{key}/{i+1:02}.mp4'} for i,(label,start,end) in enumerate(s['beats'])]})
    manifest.insert(2,{'id':'mall_routes','label':'Route comparison','duration':46,
        'src':'../out/mall_routes.mp4','poster':'../out/mall_routes_still.png',
        'beats':[{'label':label,'start':start,'end':end,'src':f'stages/{i+1:02}.mp4','hold':f'holds/{i+1:02}.mp4'}
                 for i,(label,start,end) in enumerate(mall.STAGES)]})
    # Match the displayed frame while the next video loads. In particular, a
    # night hold must never flash the scene's neutral daylight poster.
    for s in manifest:
        compose=mall.compose if s['id']=='mall_routes' else COMPOSERS[s['id']]
        folder=PLAYER/'posters'/s['id'];folder.mkdir(parents=True,exist_ok=True)
        for i,b in enumerate(s['beats'],1):
            for field,suffix,t in [('poster','start',b['start']),('holdPoster','end',b['end']-1/FPS)]:
                b[field]=f'posters/{s["id"]}/{i:02}-{suffix}.png'
                compose(t).save(PLAYER/b[field])
    # Present in narration order, returning to the same map between close-ups.
    # Reuse the existing chapter/hold files rather than duplicating renders.
    films={s['id']:s for s in manifest}
    def route_section(key,label,first,last):
        source=films['mall_routes'];beats=source['beats'][first:last]
        return {**source,'id':key,'label':label,'section':True,'beats':beats,
                'duration':sum(b['end']-b['start'] for b in beats),
                'poster':beats[-1]['holdPoster']}
    playlist=[films['mall_opener'],films['secret_elevator'],
        route_section('routes_intro','Storefronts + service routes',0,2),
        route_section('route_mcp','Map: MCP route',2,3),films['mcp_directory'],
        route_section('route_cli','Map: CLI route',3,4),films['cli_terminal'],
        route_section('route_api','Map: API + comparison',4,6),
        films['mcp_cli_overlap'],films['agency_guardrails'],films['context_handoff']]
    (PLAYER/'index.html').write_text((HERE/'player.html').read_text().replace('/* SCENES */',json.dumps(playlist)))


if __name__=='__main__':main()
