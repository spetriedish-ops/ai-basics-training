"""Pair B enters the context classroom, using generated hand-drawn walk cels.

Artwork is preserved as RGBA cels. Animation/compositing and three restrained
line-boil variants are deterministic. No pose crossfades or action in hold loops.
"""
from pathlib import Path
import argparse
import math
import shutil
import subprocess

import numpy as np
from scipy.ndimage import label, find_objects, binary_dilation
from PIL import Image, ImageDraw, ImageFilter

from render_context_room import Room, DOOR, DOOR_WINDOW, Sketch, encode, font

HERE = Path(__file__).resolve().parent
ASSETS = HERE/'assets/context_entry'
SOURCE = HERE/'source/context_entry'
PLAYER = HERE/'interactive/context_entry'
OUT = HERE/'out'
W, H, FPS = 1920, 1080, 30
DURATION = 8.5
INK = (71, 67, 69)


def clamp(v):
    return min(1, max(0, v))


def smooth(v):
    v = clamp(v)
    return v*v*(3-2*v)


def boil(im, variant):
    """Subpixel local line displacement, not a whole-character position jitter."""
    if variant == 0:
        return im.copy()
    w, h = im.size
    def offset(x, y):
        return (x + .58*math.sin(y/29+x/47+variant*2.1),
                y + .48*math.sin(x/33-y/61+variant*2.1))
    mesh = []
    for y in range(0,h,40):
        for x in range(0,w,40):
            r,b = min(w,x+40), min(h,y+40)
            quad = sum((offset(a,c) for a,c in [(x,y),(x,b),(r,b),(r,y)]),())
            mesh.append(((x,y,r,b),quad))
    return im.transform(im.size,Image.Transform.MESH,mesh,Image.Resampling.BICUBIC)


class Cast:
    def __init__(self,name,scale,hips):
        sheet = Image.open(ASSETS/f'{name}-walk-sheet.png').convert('RGBA')
        alpha = np.asarray(sheet)[:,:,3]
        labels, _ = label(alpha>100)
        objects = [(i+1,s) for i,s in enumerate(find_objects(labels))
                   if s and (s[0].stop-s[0].start)*(s[1].stop-s[1].start)>15000]
        # The generated sheet has small gutter overlaps. Isolate connected cels
        # before cropping, instead of cutting feet or hair at nominal grid lines.
        objects.sort(key=lambda p:(round(p[1][0].start/418),p[1][1].start))
        assert len(objects)==9, (name,len(objects))
        self.frames=[]
        target=ASSETS/name
        target.mkdir(exist_ok=True)
        for index,((ident,s),hip) in enumerate(zip(objects,hips)):
            box=(max(0,s[1].start-4),max(0,s[0].start-4),
                 min(sheet.width,s[1].stop+4),min(sheet.height,s[0].stop+4))
            x,y,r,b=box
            mask=binary_dilation(labels[y:b,x:r]==ident,iterations=4)
            cel=np.array(sheet.crop(box))
            cel[:,:,3]*=mask
            cel=Image.fromarray(cel)
            cel.save(target/f'cel-{index+1:02}.png')
            size=(round(cel.width*scale),round(cel.height*scale))
            cel=cel.resize(size,Image.Resampling.LANCZOS)
            anchor=((hip-x)*scale,(s[0].stop-y)*scale)
            self.frames.append(([boil(cel,v) for v in range(3)],anchor))


class Entry:
    def __init__(self):
        room=Room()
        self.background=[room.frame(19.5,v).convert('RGBA') for v in range(3)]
        self.human=Cast('human',1.13,[260,679,1095,269,678,1100,281,683,1080])
        self.agent=Cast('agent',.71,[227,641,1054,235,644,1052,248,641,1054])
        self.turn_frames=self.load_turn()

    def load_turn(self):
        sheet=Image.open(ASSETS/'human-turn-sheet.png').convert('RGBA')
        labels,_=label(np.asarray(sheet)[:,:,3]>100)
        objects=[(i+1,s) for i,s in enumerate(find_objects(labels))
                 if s and (s[0].stop-s[0].start)*(s[1].stop-s[1].start)>15000]
        objects.sort(key=lambda item:(item[1][0].start//(sheet.height//2),item[1][1].start))
        assert len(objects)==4, len(objects)
        frames=[]
        for i,((ident,s),hip) in enumerate(zip(objects,[352,720,321,730])):
            x,y=max(0,s[1].start-4),max(0,s[0].start-4)
            r,b=min(sheet.width,s[1].stop+4),min(sheet.height,s[0].stop+4)
            mask=binary_dilation(labels[y:b,x:r]==ident,iterations=4)
            cel=np.array(sheet.crop((x,y,r,b)))
            cel[:,:,3]*=mask
            cel=Image.fromarray(cel)
            cel.save(ASSETS/'human'/f'turn-{i+1:02}.png')
            # Match the approved standing cel's height and floor anchor.
            scale=461/(s[0].stop-s[0].start)
            cel=cel.resize((round(cel.width*scale),round(cel.height*scale)),Image.Resampling.LANCZOS)
            frames.append(([boil(cel,v) for v in range(3)],((hip-x)*scale,(s[0].stop-y)*scale)))
        return frames

    def door(self,im,p,variant):
        if p<=0:return
        layer=Image.new('RGBA',(W,H))
        pencil=Sketch(layer,variant)
        # Looking into a quiet, unlabelled corridor. Warm dark colors preserve
        # the classroom's painted palette instead of making a black portal.
        pencil.poly(DOOR,fill=(174,162,140),width=3)
        pencil.line([(1573,713),(1727,853)],(142,130,111),2)
        pencil.line([(1667,330),(1667,799)],(157,145,124),2)
        # Right hinge: the same door narrows as it swings into the corridor.
        opening=smooth(p)
        top=(1570+150*opening,356-45*opening)
        bottom=(1570+150*opening,777+137*opening)
        leaf=[top,(1730,307),(1730,924),bottom]
        pencil.poly(leaf,fill=(194,184,150),width=3)
        def project(u,v):
            lx=top[0]*(1-v)+bottom[0]*v
            ly=top[1]*(1-v)+bottom[1]*v
            return (lx*(1-u)+1730*u,ly*(1-u)+(307+617*v)*u)
        pencil.poly([project(.25,.16),project(.76,.16),project(.76,.43),project(.25,.43)],
                    fill=(185,203,194),width=2)
        pencil.line([project(.12,.58),project(.23,.58)],INK,3)
        im.alpha_composite(layer)

    def actor(self,im,cast,t,start,duration,end_x,variant):
        if t<start:return
        moving=t<start+duration
        elapsed=min(duration,t-start)
        progress=elapsed/duration
        # A steady travel speed makes the long strides readable. Only the last
        # half-step slows down as the feet plant, with no slide after stopping.
        slow=.08
        norm=1-slow/2
        travel=(progress if progress<1-slow else
                1-slow+(progress-(1-slow))-(progress-(1-slow))**2/(2*slow))/norm
        x=1900+(end_x-1900)*travel
        cel=min(25,int(progress*26))%8 if moving else 8
        frames,anchor=cast.frames[cel]
        if cast is self.human and t>=6.2:
            # Head/shoulders and feet turn through distinct cels, then remain
            # planted facing down-right toward the shorter agent. No flip/fade.
            frames,anchor=self.turn_frames[min(3,int((t-6.2)/.15))]
        art=frames[variant]
        y=879+10*(1-clamp((1900-x)/260))
        if not moving:
            # A small whole-body settle ends before the hold. Pose never cycles.
            settle=t-start-duration
            y+=3*math.sin(settle*13)*math.exp(-settle*9) if settle<.7 else 0
        # A faint contact shadow grounds the characters on the same floor.
        layer=Image.new('RGBA',(W,H))
        shadow=Image.new('RGBA',(W,H))
        d=ImageDraw.Draw(shadow)
        rx=81 if cast is self.human else 74
        d.ellipse((x-rx,y-10,x+rx,y+9),fill=(97,75,55,34))
        layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
        layer.alpha_composite(art,(round(x-anchor[0]),round(y-anchor[1])))
        # The right jamb physically masks arrival from the corridor. Nothing
        # fades in, scales up, or appears through the back wall.
        layer.paste((0,0,0,0),(1730,0,W,H))
        im.alpha_composite(layer)

    def frame(self,t,variant=None):
        variant=int(t*FPS)//5%3 if variant is None else variant
        im=self.background[variant].copy()
        p=smooth((t-.3)/.75)*(1-smooth((t-6.45)/.8))
        self.door(im,p,variant)
        self.actor(im,self.human,t,1.05,4.68,785,variant)
        self.actor(im,self.agent,t,2.3,3.78,1160,variant)
        return im.convert('RGB')


def prepare(scene):
    for folder in [SOURCE,PLAYER,OUT]:folder.mkdir(parents=True,exist_ok=True)
    scene.frame(0,0).save(PLAYER/'poster.jpg',quality=96)
    scene.frame(DURATION,0).save(PLAYER/'hold-01.jpg',quality=96)
    scene.frame(DURATION,0).save(SOURCE/'pair-b-in-classroom.png')
    times=[0,1.8,2.8,3.8,5,8.5]
    contact=Image.new('RGB',(1920,788),(250,247,239))
    d=ImageDraw.Draw(contact)
    for i,t in enumerate(times):
        x,y=i%3*640,i//3*394
        contact.paste(scene.frame(t).resize((640,360),Image.Resampling.LANCZOS),(x,y))
        d.text((x+20,y+364),f'{t:g}s',font=font(23),fill=INK)
    contact.save(SOURCE/'storyboard.jpg',quality=95)
    turn=Image.new('RGB',(1920,394),(250,247,239))
    for i,t in enumerate([6.1,6.4,7]):
        turn.paste(scene.frame(t).resize((640,360),Image.Resampling.LANCZOS),(i*640,0))
        ImageDraw.Draw(turn).text((i*640+20,364),f'{t:g}s',font=font(23),fill=INK)
    turn.save(SOURCE/'turn-storyboard.jpg',quality=95)


def render(scene):
    master=OUT/'context_entry.mp4'
    encode(master,(scene.frame(i/FPS) for i in range(round(DURATION*FPS))))
    shutil.copy2(master,PLAYER/'beat-01.mp4')
    encode(PLAYER/'ready.mp4',(scene.frame(0,j//5) for j in range(15)))
    encode(PLAYER/'hold-01.mp4',(scene.frame(DURATION,j//5) for j in range(15)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=15,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop','0',str(OUT/'context_entry.gif')],check=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    scene=Entry()
    prepare(scene)
    if not args.prepare_only:render(scene)
