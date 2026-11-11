"""Money before retrieval, then a cartoon sci-fi compactor and tiny summary.

Reuses the approved clips. The full manifest inserts the expense gag directly
after accumulation and appends the compaction study after the normal-speed search.
"""
import argparse
import json
import math
import subprocess
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from render_context_monothread import MonoThread, HERE
from render_context_portfolio import PAPER, INK
from render_context_entry import smooth, clamp, boil
from render_context_volume import project, DEPTH
from render_computer_control_bonus import Sketch, encode
from context_press_mechanics import MechanicalCompactor

PLAYER=HERE/'interactive/context_compaction'
SOURCE=HERE/'source/context_compaction'
ASSETS=HERE/'assets/context_compaction'
VERSION='compaction-5'
BEATS=[('A costly quick question',0,5.5),('Enter the context compactor',0,3),
       ('Crush the crowded context',3,10),('Stamp a summary cube',10,17)]
CUES=[
    'Expense comes first in the narration: money flies out of the user’s pocket as another turn uses the long conversation. This is a playful metaphor, not a price estimate.',
    'After the search, introduce compaction with a cartoon homage to the original Star Wars trash-compactor scene. Forty-nine individually rendered cartons and the armor represent the accumulated context in a shallow press bed.',
    'The pressure walls ratchet inward. Outer cartons move only when a wall reaches them, then push their neighbors; touching cartons buckle separately, while a bracing pipe springs away. An abandoned stormtrooper helmet and chest plate are caught in the pile and crushed along with it.',
    'An overhead hydraulic press contacts the tallest stacks first, then compresses the supported cartons into a cube. The same cartons and armor remain in place when the press and walls reopen; there is no replacement cube. The cube is marked SUMMARY. This represents summarization, not lossless storage compression; details and instructions can be lost.',
]


class Compaction:
    def __init__(self):
        self.mono=MonoThread()
        art=Image.open(ASSETS/'compactor-room-v1.png').convert('RGBA').resize((1920,1080),Image.Resampling.LANCZOS)
        self.background=[boil(art,v) for v in range(3)]
        self.plate_sources=[[(150,130),(500,275),(500,650),(150,970)],
                            [(1770,130),(1420,275),(1420,650),(1770,970)]]
        self.plates=[]
        for v in range(3):
            pair=[]
            for polygon in self.plate_sources:
                mask=Image.new('L',(1920,1080));ImageDraw.Draw(mask).polygon(polygon,fill=255)
                pair.append(Image.composite(self.background[v],Image.new('RGBA',(1920,1080)),mask))
            self.plates.append(pair)
        yy,xx=np.mgrid[:1080,:1920]
        grain=4*np.sin(xx/17+yy/90)+3*np.sin(xx/33-yy/19)+2*np.sin(xx/7+yy/11)
        texture=np.empty((1080,1920,4),dtype=np.uint8)
        for c,base in enumerate((133,130,108)):texture[:,:,c]=np.clip(base+grain,0,255)
        texture[:,:,3]=255;self.press_texture=Image.fromarray(texture)
        self.mechanics=MechanicalCompactor(self)

    @lru_cache(maxsize=6)
    def bill(self,v,flap):
        im=Image.new('RGBA',(156,96));s=Sketch(im,v)
        # Tiny paper wings give the notes an intentionally ridiculous escape.
        wing=8 if flap else 27
        s.poly([(29,46),(3,wing),(12,52),(1,64),(35,59)],(251,247,226),INK,2)
        s.poly([(126,46),(153,wing),(146,52),(155,64),(121,59)],(251,247,226),INK,2)
        s.rect((25,30,131,88),(177,209,153),INK,2,radius=5)
        s.rect((32,36,124,82),None,(83,124,78),1,radius=4)
        s.oval((62,40,94,79),(220,232,181),(83,124,78),2)
        s.text((78,39),'$',34,(57,99,63),anchor='mt')
        for x in [43,114]:s.oval((x-6,52,x+6,65),(216,230,181),(83,124,78),1)
        return im

    def cost(self,t,v):
        def cast(name,unused,variant):
            if name!='human' or t<.6 or t>=4.65:return self.mono.character(name,25.49,variant)
            expression=1 if t<1.5 else 4 if 3.8<=t<3.97 else 2
            frames,anchor=self.mono.expressions['human'][expression]
            art=frames[variant].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            anchor=(art.width-anchor[0],anchor[1])
            pos=self.mono.human_state(25.49)[0]
            scale=(1+DEPTH*self.mono.initial['human'][1])/(1+DEPTH*pos[1])
            art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
            px,py=project(*pos)
            return art,(round(px-anchor[0]*scale),round(py-anchor[1]*scale)),pos
        im=self.mono.scene(25.49,v,character_override=cast)
        pocket=(1365,730)
        for i in range(9):
            age=t-(.35+i*.25)
            if not 0<=age<=1.5:continue
            q=age/1.5;travel=q*q*(3-2*q)
            x=pocket[0]+(2110-pocket[0])*travel
            y=pocket[1]-300*travel-110*math.sin(math.pi*q)
            art=self.bill(v,int(age*13)%2).rotate(22*math.sin(age*12+i),Image.Resampling.BICUBIC,expand=True)
            im.alpha_composite(art,(round(x-art.width/2),round(y-art.height/2)))
        # One reluctant last coin follows after the notes have fled.
        age=t-3.18
        if 0<=age<1.10:
            q=age/1.10;x=pocket[0]+700*q;y=pocket[1]-230*math.sin(math.pi*q)+130*q
            s=Sketch(im,v);rx=4+11*abs(math.cos(q*16))
            s.oval((x-rx,y-18,x+rx,y+18),(239,194,73),(150,103,49),2)
            if rx>9:s.text((x,y-14),'$',25,(139,91,39),anchor='mt')
        return im.convert('RGB')

    @lru_cache(maxsize=3)
    def armor(self,v):
        """Native pencil prop: discarded empty helmet and loose chest plate."""
        im=Image.new('RGBA',(290,235));s=Sketch(im,v)
        ivory=(234,229,207);shade=(173,181,166);dark=(54,61,57)
        # Chest plate with an open neck hole: clearly costume parts, not a body.
        s.poly([(135,107),(166,94),(190,113),(230,117),(261,159),(248,207),(204,217),(163,199),(130,159)],ivory,INK,2)
        s.poly([(166,107),(187,121),(209,121),(202,138),(174,134)],dark,INK,2)
        s.line([(149,141),(174,155),(197,157),(211,142),(237,139)],shade,4)
        s.line([(162,174),(196,183),(230,175)],shade,4)
        s.poly([(235,169),(274,175),(275,201),(257,207),(238,194)],ivory,INK,2)
        for yy in [181,188,195]:s.line([(251,yy),(273,yy+3)],shade,2)
        # Classic bulbous helmet, black brow, cheek tubes, triangular mouth.
        s.poly([(35,112),(34,77),(48,38),(78,18),(115,14),(148,29),(167,59),(171,102),(182,136),(161,174),(126,190),(83,182),(48,157)],ivory,INK,3)
        s.poly([(38,79),(63,68),(101,68),(133,81),(165,81),(169,98),(130,98),(102,86),(68,87),(42,95)],dark,INK,2)
        s.poly([(58,94),(90,93),(97,104),(82,116),(57,109)],dark,INK,2)
        s.poly([(111,100),(143,105),(158,119),(137,124),(112,113)],dark,INK,2)
        s.poly([(99,118),(120,141),(139,151),(130,164),(95,160),(82,144)],shade,INK,2)
        s.poly([(101,124),(116,144),(94,141)],dark,INK,2)
        s.oval((49,125,79,169),ivory,INK,2);s.oval((139,141,169,179),ivory,INK,2)
        s.oval((60,146,76,162),dark,INK,1);s.oval((146,158,161,173),dark,INK,1)
        for i in range(5):
            s.line([(88+i*9,151+i*1.1),(89+i*9,158+i*1.1)],dark,2)
        for i in range(4):s.line([(41+i*5,111),(43+i*5,125)],shade,2)
        s.line([(68,42),(84,31),(117,30)],(250,244,225),4)
        s.line([(124,42),(134,45)],(151,120,85),2)
        return im

    def shutter(self,im,closed,v):
        if closed<=0:return
        s=Sketch(im,v);width=960*closed
        for left,right in [(0,width),(1920-width,1920)]:
            s.rect((left,0,right,1080),(111,119,110),INK,3)
            for y in range(60,1080,100):s.line([(left,y),(right,y)],(75,86,82),5)
        s.line([(width-9,0),(width-9,1080)],(178,127,71),11)
        s.line([(1920-width+9,0),(1920-width+9,1080)],(178,127,71),11)

    def compactor(self,t,v):
        return self.mechanics.frame(t,v)

    def frame(self,index,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        return self.cost(t,v) if index==0 else self.compactor(t,v)

    def prepare(self):
        PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        for j,(_,start,end) in enumerate(BEATS):self.frame(j,end-1/30,0).save(PLAYER/f'extra-hold-{j+1:02}.jpg',quality=97)
        sheet=Image.new('RGB',(1920,1080),PAPER)
        for j,(scene,t) in enumerate([(1,2.9),(1,5.1),(1,8.7),(1,10.8),(1,11.65),(1,12.02),(1,12.8),(1,14.5),(1,16.5)]):
            sheet.paste(self.frame(scene,t,0).resize((640,360),Image.Resampling.LANCZOS),((j%3)*640,(j//3)*360))
        sheet.save(SOURCE/'storyboard.jpg',quality=96)
        self.cost(2.2,0).save(SOURCE/'money-review.jpg',quality=97)

    def render(self):
        self.prepare()
        previous=HERE/'interactive/context_monothread'
        data=json.loads((previous/'manifest.json').read_text());assert len(data['beats'])==25
        prior=[]
        for b in data['beats']:
            b=dict(b)
            for key in ['src','hold','poster']:
                b[key]='../context_monothread/'+b[key]
            prior.append(b)
        added=[]
        for j,((label,start,end),cue) in enumerate(zip(BEATS,CUES)):
            src=f'extra-beat-{j+1:02}.mp4';hold=f'extra-hold-{j+1:02}.mp4'
            encode(PLAYER/src,(self.frame(j,start+n/30) for n in range(round((end-start)*30))))
            frames=[self.frame(j,end-1/30,v) for v in range(3)]
            encode(PLAYER/hold,(frames[n//5] for n in range(15)))
            added.append({'id':'monothread-cost' if j==0 else f'compaction-{j}','section':'One very long conversation' if j==0 else 'Compacting the context','label':label,'src':src,'hold':hold,'poster':f'extra-hold-{j+1:02}.jpg','cue':cue,'note':None})
        insert=next(i for i,b in enumerate(prior) if b['id']=='monothread-4')
        beats=prior[:insert]+[added[0]]+prior[insert:]+added[1:]
        result={'title':'Context continued: portfolios, one long conversation, and compaction','version':VERSION,'ready':'../context_portfolio/ready.jpg','readyVideo':'../context_portfolio/ready.mp4','beats':beats}
        inputs=SOURCE/'concat.txt';inputs.write_text(''.join(f"file '{(PLAYER/b['src']).resolve().as_posix()}'\n" for b in beats))
        try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(inputs),'-c','copy','-movflags','+faststart',str(HERE/'out/context_continued.mp4')],check=True)
        finally:inputs.unlink()
        (PLAYER/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
        (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(result,indent=2)+';\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
    scene=Compaction();scene.prepare() if a.prepare_only else scene.render()
