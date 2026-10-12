"""Provider-neutral agent chat on a cartoon vintage CRT, with native boil holds."""
from pathlib import Path
import argparse
import math
import subprocess

from PIL import Image, ImageDraw
from render_computer_control_bonus import Sketch, encode, font, ease, progress, cursor
from render_context_room import paper_and_texture

HERE=Path(__file__).resolve().parent
OUT=HERE/'out'
SOURCE=HERE/'source/agent_chat'
PLAYER=HERE/'interactive/agent_chat'
W,H,FPS=1920,1080,30
INK=(64,62,63)
CREAM=(235,218,184)
TEAL=(49,128,118)
MUTED=(116,126,116)
SCREEN=(246,248,232)
DURATION=18.5
BEATS=[('Open a conversation',0,4),('Say hello',4,9),('Meet the agent',9,DURATION)]


def layer():return Image.new('RGBA',(W,H))


def robot(s,x,y):
    s.line([(x,y-16),(x,y-23)],TEAL,2)
    s.oval((x-3,y-28,x+3,y-22),TEAL,color=TEAL,width=1)
    s.rect((x-20,y-16,x+20,y+18),(207,228,213),TEAL,3,radius=9)
    for dx in [-8,8]:s.oval((x+dx-2,y-3,x+dx+2,y+3),TEAL,TEAL,1)
    s.line([(x-7,y+10),(x,y+12),(x+7,y+10)],TEAL,2)


def typed(s,text,xy,size,start,end,t,color=INK):
    n=round(len(text)*max(0,min(1,(t-start)/(end-start))))
    s.text(xy,text[:n],size,color)
    if start<=t<end:
        x=xy[0]+s.d.textlength(text[:n],font=font(size))+4
        s.line([(x,xy[1]+7),(x,xy[1]+size)],color,2)


class AgentChat:
    def __init__(self):
        self.paper=paper_and_texture()[0]
        self.shells=[self.shell(v) for v in range(3)]

    def shell(self,variant):
        art=layer();s=Sketch(art,variant)
        # Soft contact shadow anchors the CRT and keyboard to the same paper.
        s.oval((284,926,1760,1012),(232,224,208),color=(232,224,208),width=1)
        # Short pedestal, broad foot, and a little of the tube casing's depth.
        s.poly([(744,792),(1127,792),(1178,885),(691,885)],(185,174,146),INK,4)
        s.oval((641,863,1239,916),CREAM,INK,4)
        s.poly([(234,158),(393,106),(1700,106),(1545,159)],(249,236,206),INK,4)
        s.poly([(1542,157),(1700,106),(1700,754),(1542,811)],(191,170,135),INK,5)
        # The shape is intentionally chunky, with rounded cartoon corners.
        s.rect((213,142,1557,822),CREAM,INK,5,radius=46)
        s.line([(245,176),(1527,176)],(254,244,216),4)
        s.rect((265,197,1504,743),(139,133,112),INK,4,radius=42)
        s.rect((287,218,1481,719),(219,222,200),INK,3,radius=32)
        for i in range(8):
            x=1590+i*10
            s.line([(x,333-i*3),(x,570-i*3)],(110,105,87),3)
        # Tiny physical controls, no manufacturer name or logo.
        s.rect((1349,760,1458,799),(214,197,163),INK,2,radius=13)
        s.oval((1364,769,1382,787),(114,118,93),INK,2)
        s.line([(1408,770),(1408,789)],INK,3)
        s.line([(1427,770),(1427,789)],INK,3)
        s.line([(1445,770),(1445,789)],INK,3)
        for x in [294,310,326,342]:s.line([(x,777),(x+6,777)],(141,127,104),2)
        # Simple chunky keyboard; individual keys stay quiet behind the dialogue.
        s.poly([(461,878),(1309,878),(1385,982),(382,982)],(222,204,170),INK,4)
        s.poly([(382,982),(1385,982),(1370,1002),(396,1002)],(183,163,131),INK,3)
        for row in range(3):
            y=893+row*24
            for column in range(14):
                x=473+column*57-row*9
                s.rect((x,y,x+45,y+17),(247,235,207),(125,117,99),1,radius=3)
        s.rect((676,963,1073,977),(247,235,207),(125,117,99),2,radius=4)
        # A cord and oval mouse strengthen the vintage-computer silhouette.
        s.line([(1615,775),(1677,819),(1686,865),(1630,896),(1592,902)],INK,3)
        s.oval((1519,900,1638,987),CREAM,INK,3)
        s.line([(1529,936),(1628,936)],(143,128,103),2)
        s.line([(1578,906),(1578,935)],INK,2)
        return art

    def interface(self,t,variant):
        art=layer();s=Sketch(art,variant)
        s.rect((294,224,1475,712),SCREEN,color=(99,108,93),width=2,radius=28)
        # A small generic sidebar, conversation heading, messages, and composer.
        s.rect((307,237,477,698),(230,237,217),color=(230,237,217),width=1,radius=17)
        s.line([(491,232),(491,704)],(190,201,181),2)
        s.rect((324,254,458,297),(244,247,230),color=(154,178,155),width=2,radius=9)
        s.line([(338,275),(350,275)],TEAL,2);s.line([(344,269),(344,281)],TEAL,2)
        s.text((362,258),'new chat',25,TEAL)
        s.text((329,333),'conversations',22,MUTED)
        for i,length in enumerate([92,113,76]):
            s.line([(331,386+i*31),(331+length,386+i*31)],(178,191,170),2)
        s.line([(331,664),(436,664)],(178,191,170),2)
        s.oval((333,675,346,688),color=MUTED,width=2)
        s.line([(363,681),(420,681)],(178,191,170),2)
        s.text((535,247),'New conversation',34,INK)
        s.line([(528,301),(1440,301)],(204,214,195),2)
        # The first hold gives the narrator a clear, empty chat view.
        if t<7.65:
            robot(s,983,427)
            s.text((985,476),'How can I help?',38,INK,anchor='ma')
        else:
            s.rect((1056,329,1418,396),(217,232,217),color=(148,177,155),width=2,radius=17)
            s.text((1080,343),'Hi! Who are you?',34,INK)
        s.rect((531,650,1431,703),(252,252,241),color=(158,178,154),width=2,radius=15)
        s.oval((1378,660,1414,694),TEAL,color=TEAL,width=2)
        s.line([(1396,684),(1396,669)],(250,248,233),3)
        s.line([(1389,676),(1396,669),(1403,676)],(250,248,233),2)
        if 4.8<=t<7.65:
            typed(s,'Hi! Who are you?',(554,658),31,4.8,6.8,t)
        else:s.text((555,660),'Message your assistant',27,(139,149,132))
        # Agent identity/role arrives before it has learned anything about the user.
        if t>=9.35:
            robot(s,548,452)
            s.text((588,417),'Assistant',24,TEAL)
            if t<10.0:
                for i in range(3):s.oval((590+i*18,470,597+i*18,477),TEAL,TEAL,1)
            for text,y,start,end in [
                ("Hi! I'm your work assistant.",451,10.0,12.0),
                ('I can help you find information',493,12.05,14.2),
                ('and get things done.',535,14.25,15.8),
                ('What should I call you?',589,16.0,17.7)]:
                if t>=start:typed(s,text,(588,y),34,start,end,t)
        if 6.8<=t<8.35:
            p=progress(t,6.8,7.5)
            x=1230+(1396-1230)*p;y=613+(679-613)*p
            cursor(s,(x,y),t,[7.6])
        return art

    def frame(self,t,variant=None):
        variant=int(t*FPS)//5%3 if variant is None else variant
        canvas=self.paper.copy();canvas.alpha_composite(self.shells[variant])
        if t>=.5:
            ui=self.interface(t,variant)
            if t<1.5:
                # A restrained CRT opening: a horizontal glow expands into a chat.
                p=progress(t,.5,1.5);height=max(2,round(488*p))
                crop=ui.crop((294,224,1475,712)).resize((1181,height),Image.Resampling.BICUBIC)
                ui=layer();ui.alpha_composite(crop,(294,468-height//2))
            canvas.alpha_composite(ui)
            led=layer();Sketch(led,variant).oval((1367,772,1379,784),(88,166,113),color=(88,166,113),width=1)
            canvas.alpha_composite(led)
        return canvas.convert('RGB')


def prepare(scene):
    SOURCE.mkdir(parents=True,exist_ok=True);PLAYER.mkdir(parents=True,exist_ok=True)
    scene.frame(0).save(PLAYER/'poster.jpg',quality=96)
    for i,(_,_,end) in enumerate(BEATS):scene.frame(end-1/FPS).save(PLAYER/f'hold-{i+1:02}.jpg',quality=96)
    scene.frame(DURATION).save(SOURCE/'agent-introduction.png')
    sheet=Image.new('RGB',(1920,780),(250,247,239))
    for i,t in enumerate([0,3.8,6.1,8.8,13,18.4]):
        x,y=i%3*640,i//3*390
        sheet.paste(scene.frame(t).resize((640,360),Image.Resampling.LANCZOS),(x,y))
        ImageDraw.Draw(sheet).text((x+16,y+360),f'{t:g} seconds',font=font(22),fill=INK)
    sheet.save(SOURCE/'storyboard.jpg',quality=94)


def render(scene):
    master=OUT/'agent_chat.mp4'
    encode(master,(scene.frame(i/FPS) for i in range(round(DURATION*FPS))))
    for i,(_,start,end) in enumerate(BEATS):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
                        '-an','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',
                        str(PLAYER/f'beat-{i+1:02}.mp4')],check=True)
        phase=int((end-1/FPS)*FPS)//5%3
        encode(PLAYER/f'hold-{i+1:02}.mp4',(scene.frame(end-1/FPS,(phase+j//5)%3) for j in range(15)))
    encode(PLAYER/'ready.mp4',(scene.frame(0,j//5) for j in range(15)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop','0',str(OUT/'agent_chat.gif')],check=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    scene=AgentChat();prepare(scene)
    if not args.prepare_only:render(scene)
    print(f'Preview: {PLAYER / "index.html"}',flush=True)
