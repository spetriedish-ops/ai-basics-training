"""Personal context, tool definitions, and retrieved information fill one room.

The main sequence uses perspective cubes from render_context_volume. The legacy
Fill class remains for the unselected transport studies. Every item persists
after arrival; every narration beat has an action-frozen boil loop.
"""
from pathlib import Path
from functools import lru_cache
import argparse
import json
import math
import subprocess

import numpy as np
from scipy.ndimage import label, find_objects, binary_dilation
from PIL import Image, ImageDraw, ImageFilter

from render_context_entry import Entry, boil, smooth, clamp
from render_computer_control_bonus import Sketch, font, encode

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'assets/context_fill'
SOURCE=HERE/'source/context_fill'
PLAYER=HERE/'interactive/context_fill'
OUT=HERE/'out'
W,H,FPS=1920,1080,30
INK=(61,56,57)
PAPER=(250,247,239)
BEATS=[('Introduce yourself',0,10.5),('Ask for research',10.5,14.5),
       ('Bring in MCP tools',14.5,22.5),('Retrieve information',22.5,32.5),
       ('Watch the room fill',32.5,39)]
DURATION=BEATS[-1][2]
NAMES=['trophy','briefcase','team','keyboard','manuals','mail','calendar','documents']
COLORS={'rovo':(191,205,181),'mail':(235,182,158),'calendar':(229,203,145),
        'documents':(195,182,209),'prompt':(238,220,170)}


def props():
    sheet=Image.open(ASSETS/'props-sheet.png').convert('RGBA')
    labels,_=label(np.asarray(sheet)[:,:,3]>100)
    objects=[(i+1,s) for i,s in enumerate(find_objects(labels))
             if s and (s[0].stop-s[0].start)*(s[1].stop-s[1].start)>15000]
    objects.sort(key=lambda item:(item[1][0].start//512,item[1][1].start))
    assert len(objects)==8,len(objects)
    result={}
    for name,(ident,s) in zip(NAMES,objects):
        x,y=max(0,s[1].start-3),max(0,s[0].start-3)
        r,b=min(sheet.width,s[1].stop+3),min(sheet.height,s[0].stop+3)
        arr=np.array(sheet.crop((x,y,r,b)))
        arr[:,:,3]*=binary_dilation(labels[y:b,x:r]==ident,iterations=3)
        im=Image.fromarray(arr)
        im.save(ASSETS/f'{name}.png')
        result[name]=im
    return result


def fitted(im,box):
    im=im.copy()
    im.thumbnail(box,Image.Resampling.LANCZOS)
    return im


def tag(im,text,center,y,size=28,width=None):
    d=ImageDraw.Draw(im)
    while width and d.textbbox((0,0),text,font=font(size))[2]>width and size>22:
        size-=1
    tw=d.textbbox((0,0),text,font=font(size))[2]
    d.rounded_rectangle((center-tw/2-9,y-2,center+tw/2+9,y+size+6),5,
                        fill=(*PAPER,245),outline=(*INK,255),width=1)
    d.text((center,y),text,font=font(size),fill=INK,anchor='mt')


def prop_sprite(im,width,text):
    art=fitted(im,(width,200))
    layer=Image.new('RGBA',(max(art.width,width)+30,art.height+48))
    layer.alpha_composite(art,((layer.width-art.width)//2,0))
    tag(layer,text,layer.width/2,art.height+3,28,layer.width-25)
    if text=='QUICK QUESTION':
        d=ImageDraw.Draw(layer)
        d.text((layer.width*.52,art.height*.55),'?',font=font(35),fill=INK,anchor='mm')
    return layer


def carton(art,cells,title,color,unit=120,subtitle=None):
    """A contiguous polyomino crate with hand-drawn seams and one clear label."""
    cols=max(x for x,y in cells)+1
    rows=max(y for x,y in cells)+1
    layer=Image.new('RGBA',(cols*unit+20,rows*unit+20))
    d=ImageDraw.Draw(layer)
    mask=Image.new('L',layer.size)
    md=ImageDraw.Draw(mask)
    for x,y in cells:md.rectangle((x*unit+8,y*unit+8,(x+1)*unit+8,(y+1)*unit+8),fill=255)
    yy,xx=np.mgrid[:layer.height,:layer.width]
    grain=2*np.sin(xx/21+yy/16)+1.5*np.sin(xx/7-yy/25)
    rgba=np.zeros((layer.height,layer.width,4),dtype=np.uint8)
    for c in range(3):rgba[:,:,c]=np.clip(color[c]+grain,0,255)
    rgba[:,:,3]=np.asarray(mask)
    layer.alpha_composite(Image.fromarray(rgba))
    pencil=Sketch(layer)
    occupied=set(cells)
    for x,y in cells:
        a,b=x*unit+8,y*unit+8
        for neighbor,edge in [((x,y-1),[(a,b),(a+unit,b)]),
                              ((x+1,y),[(a+unit,b),(a+unit,b+unit)]),
                              ((x,y+1),[(a,b+unit),(a+unit,b+unit)]),
                              ((x-1,y),[(a,b),(a,b+unit)])]:
            pencil.line(edge,INK if neighbor not in occupied else tuple(int(v*.83) for v in color),
                        3 if neighbor not in occupied else 1,.7)
    # Find the widest connected row for a legible front label.
    rowspec=[(sum(y==row for x,y in cells),row) for row in range(rows)]
    count,labelrow=max(rowspec)
    xs=[x for x,y in cells if y==labelrow]
    cx=(min(xs)+max(xs)+1)*unit/2+8
    if subtitle:
        tag(layer,title,layer.width/2,13,30,cols*unit-20)
        d.text((layer.width/2,57),'definitions + instructions',font=font(23),fill=INK,anchor='mt')
        graphic=fitted(art,(cols*unit-45,rows*unit-100))
        layer.alpha_composite(graphic,((layer.width-graphic.width)//2,85))
        # Keep the explanatory label at the top, above the foreground props.
    else:
        # Artwork occupies a cell, never a missing corner of the Tetris shape.
        for cell in cells:
            graphic=fitted(art,(unit-18,unit-48 if cell[1]==labelrow else unit-18))
            layer.alpha_composite(graphic,(cell[0]*unit+8+(unit-graphic.width)//2,
                                           cell[1]*unit+15))
        tag(layer,title,cx,(labelrow+1)*unit-37,29,count*unit-20)
    return layer


class Fill:
    def __init__(self):
        self.entry=Entry()
        self.art=props()
        self.items=[]
        def add(name,art,xy,start,duration=1.25,origin='door',angle=0):
            self.items.append(dict(name=name,frames=[boil(art,v) for v in range(3)],
                                   xy=xy,start=start,end=start+duration,origin=origin,angle=angle))
        # The first few facts arrive from the human, one at a time.
        for name,width,text,xy,start in [
            ('trophy',175,'SALES',(310,718),1.2),
            ('team',158,'MY TEAM',(175,510),3.4),
            ('briefcase',203,'UNC · FOLLOW UP',(515,742),5.6),
            ('keyboard',210,'QUICK QUESTION',(875,746),7.8)]:
            add(name,prop_sprite(self.art[name],width,text),xy,start,1.2,'human',-9)
        prompt=Image.new('RGBA',(322,100))
        sk=Sketch(prompt);sk.rect((3,3,319,96),fill=COLORS['prompt'],color=INK,width=3,radius=7)
        sk.text((161,12),'YOUR RESEARCH PROMPT',size=29,color=INK,anchor='mt')
        sk.text((161,51),'+ Confluence space link',size=25,color=INK,anchor='mt')
        add('prompt',prompt,(1330,856),11.8,1.3,'human',5)
        # Separate MCP payloads enter BEFORE any retrieved information.
        square=[(0,0),(1,0),(0,1),(1,1)]
        for key,title,xy,start in [
            ('rovo','ROVO MCP',(425,620),15.0),
            ('mail','GMAIL MCP',(895,590),17.1),
            ('calendar','CALENDAR MCP',(1320,630),19.2)]:
            add('tools-'+key,carton(self.art['manuals'],square,title,COLORS[key],subtitle='tools + instructions'),xy,start,1.6,angle=8)
        # Interlocking shapes share exact cell positions; their missing corners
        # leave visible gaps which subsequent deliveries physically occupy.
        deliveries=[
            ('documents',[(0,0),(0,1),(1,1)],'YOUR PAGES',(305,380),23.0,1.7,-12),
            ('mail',[(0,0),(1,0),(1,1)],'EMAIL THREADS',(425,380),25.1,1.7,11),
            ('calendar',[(0,0),(1,0),(1,1)],'MEETINGS',(1320,390),27.2,1.7,-10),
            ('mail',[(0,0)],'REPLIES',(1320,510),29.3,1.3,9),
            ('documents',[(0,0),(0,1),(1,1)],'PROJECT NOTES',(895,350),32.8,1.25,-15),
            ('mail',[(0,0)],'MORE MAIL',(1015,350),33.9,1.1,12),
            ('documents',[(0,0),(1,0)],'PAST WORK',(1320,270),35.0,1.0,-8),
            ('calendar',[(0,0),(0,1)],'INVITES',(1560,630),35.9,.95,9),
            ('documents',[(0,0),(1,0),(2,0)],'A LITTLE MORE BACKGROUND…',(305,260),36.7,1.0,-6)]
        for i,(kind,cells,title,xy,start,duration,angle) in enumerate(deliveries):
            add(f'data-{i+1}',carton(self.art[kind],cells,title,COLORS[kind]),xy,start,duration,angle=angle)
        self.personal=self.items[:4]
        self.payloads=self.items[4:]

    def inventory(self,t):
        return [item['name'] for item in self.items if t>=item['end']]

    def draw_item(self,layer,item,t,variant):
        if t<item['start']:return
        art=item['frames'][variant]
        p=clamp((t-item['start'])/(item['end']-item['start']))
        tx,ty=item['xy']
        if p<1:
            q=smooth(p)
            ox,oy=(790,595) if item['origin']=='human' else (1730,530)
            # A single opaque object travels and rotates into a fixed slot.
            # Personal facts blossom from speech; research comes from outside.
            scale=.18+.82*q if item['origin']=='human' else .75+.25*q
            original=art.size
            art=art.resize((max(1,round(art.width*scale)),max(1,round(art.height*scale))),Image.Resampling.BICUBIC)
            angle=item['angle']*math.sin(math.pi*p)
            art=art.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
            cx=ox*(1-q)+(tx+original[0]/2)*q
            cy=oy*(1-q)+(ty+original[1]/2)*q-135*math.sin(math.pi*p)
            x,y=round(cx-art.width/2),round(cy-art.height/2)
        else:
            x,y=tx,ty
        layer.alpha_composite(art,(x,y))

    @lru_cache(maxsize=100)
    def settled(self,inventory,variant):
        layer=Image.new('RGBA',(W,H))
        for item in self.payloads:
            if item['name'] in inventory and item['name']!='prompt':self.draw_item(layer,item,item['end'],variant)
        return layer

    def bubble(self,im,text,variant,speaker='human'):
        layer=Image.new('RGBA',(W,H))
        pencil=Sketch(layer,variant)
        lines=text.split('\n')
        width=max(ImageDraw.Draw(layer).textbbox((0,0),line,font=font(31))[2] for line in lines)+50
        x,y=(885,427) if speaker=='human' else (1100,430)
        height=45*len(lines)+28
        pencil.rect((x,y,x+width,y+height),fill=PAPER,color=INK,width=3,radius=16)
        if speaker=='human':
            tail=[(x+30,y+height-3),(x-28,y+height+25),(x+7,y+height-12)]
        else:
            tail=[(x+52,y+height-3),(1143,610),(x+89,y+height-3)]
        pencil.poly(tail,fill=PAPER,color=INK,width=2)
        for i,line in enumerate(lines):pencil.text((x+24,y+18+i*42),line,31,INK)
        im.alpha_composite(layer)

    def frame(self,t,variant=None):
        variant=int(t*FPS)//5%3 if variant is None else variant
        im=self.entry.background[variant].copy()
        # Door remains open for the deliveries, then settles shut at the end.
        opening=smooth((t-14.5)/.5)*(1-smooth((t-38)/.6))
        self.entry.door(im,opening,variant)
        im.alpha_composite(self.settled(tuple(self.inventory(t)),variant))
        for item in self.payloads:
            if item['name']!='prompt' and item['start']<=t<item['end']:self.draw_item(im,item,t,variant)
        # Characters retain the approved height, location, faces, and leaflet.
        self.entry.actor(im,self.entry.human,8.5,1.05,4.68,785,variant)
        self.entry.actor(im,self.entry.agent,8.5,2.3,3.78,1160,variant)
        self.draw_item(im,self.items[4],t,variant)
        for item in self.personal:self.draw_item(im,item,t,variant)
        for start,end,text in [(0.6,2.9,'I work in sales.'),(3.0,5.1,"Here's my account team."),
                              (5.2,7.3,'I look after UNC.'),(7.4,9.7,'Help me write follow-ups.'),
                              (10.8,13.6,'Learn about me.\nStart with my Confluence space.')]:
            if start<=t<end:self.bubble(im,text,variant)
        if 14.65<=t<16.7:
            self.bubble(im,'Which tools can I use?',variant,'agent')
        elif 22.6<=t<24.5:
            self.bubble(im,'Find pages, mail,\nand meetings.',variant,'agent')
        if t>.3:
            title=('First, you introduce yourself.' if t<10.5 else
                   'The request takes up space, too.' if t<14.5 else
                   'Tool descriptions + instructions arrive.' if t<22.5 else
                   'Then comes the information.' if t<32.5 else
                   'All this before the work begins.')
            pencil=Sketch(im,variant)
            pencil.text((960,51),title,42,INK,anchor='mt')
            if t>=14.5:pencil.text((960,1006),'Same room. More context.  •  Tool context varies by harness.',25,INK,anchor='mt')
        return im.convert('RGB')


def prepare(scene):
    for folder in [SOURCE,PLAYER,OUT]:folder.mkdir(exist_ok=True,parents=True)
    scene.frame(0,0).save(PLAYER/'poster.jpg',quality=96)
    for i,(name,start,end) in enumerate(BEATS,1):
        scene.frame(end-1/FPS,0).save(PLAYER/f'hold-{i:02}.jpg',quality=96)
    scene.frame(10.45,0).save(SOURCE/'personal-context.png')
    scene.frame(22.45,0).save(SOURCE/'mcp-tools-take-space.png')
    scene.frame(38.95,0).save(SOURCE/'room-full.png')
    times=[0,10.45,14.45,22.45,32.45,38.95]
    contact=Image.new('RGB',(1920,800),PAPER)
    for i,t in enumerate(times):
        x,y=i%3*640,i//3*400
        contact.paste(scene.frame(t).resize((640,360),Image.Resampling.LANCZOS),(x,y))
        ImageDraw.Draw(contact).text((x+15,y+365),['Ready','1. Personal context','2. Research prompt','3. MCP tool definitions','4. Retrieved information','5. Room filling'][i],font=font(23),fill=INK)
    contact.save(SOURCE/'storyboard.jpg',quality=95)
    cues=[dict(label=name,start=start,end=end,contents=scene.inventory(end-1/FPS)) for name,start,end in BEATS]
    (SOURCE/'beat-inventory.json').write_text(json.dumps(cues,indent=2)+'\n')


def render(scene):
    master=OUT/'context_fill.mp4'
    encode(master,(scene.frame(i/FPS) for i in range(round(DURATION*FPS))))
    encode(PLAYER/'ready.mp4',(scene.frame(0,j//5) for j in range(15)))
    for i,(name,start,end) in enumerate(BEATS,1):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
                        '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(PLAYER/f'beat-{i:02}.mp4')],check=True)
        encode(PLAYER/f'hold-{i:02}.mp4',(scene.frame(end-1/FPS,j//5) for j in range(15)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=192[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop','0',str(OUT/'context_fill.gif')],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(OUT/'context_entry.mp4'),'-i',str(master),
                    '-filter_complex','[0:v][1:v]concat=n=2:v=1:a=0[v]','-map','[v]',
                    '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
                    '-movflags','+faststart',str(OUT/'context_entry_and_fill.mp4')],check=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    # Keep Fill available for the transport comparison studies. The current
    # room-fill sequence uses physical cubes projected onto the classroom floor.
    from render_context_volume import VolumeFill
    scene=VolumeFill()
    prepare(scene)
    if not args.prepare_only:render(scene)
