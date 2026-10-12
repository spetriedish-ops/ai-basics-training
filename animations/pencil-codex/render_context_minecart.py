"""Reference-led mine cart with physically layered, perspective-matched cargo.

Rear art -> floor-supported cube stacks -> near wall/rim. Flying cubes use the
same occlusion, and unload in reverse order. Context originals remain in room.
"""
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw,ImageChops
from render_context_volume import VolumeFill,project,SIZE
from render_context_fill import fitted,INK,PAPER
from render_context_entry import boil,smooth,clamp
from render_computer_control_bonus import Sketch,font,encode
from render_context_transport import extract_assets,prepare,render

HERE=Path(__file__).resolve().parent
W,H=1920,1080
DOCK,BOTTOM=515,945
COLS,ROWS=6,2
FIRST_START,FIRST_SPACING=1.8,.145
SECOND_START,SECOND_SPACING=21.15,.06
LOAD_TIME=.75
WIDE_SCALE=810/1640
WORK_START,WORK_DURATION=15.2,3.5

def wide_point(x,y):return (60+(x-140)*WIDE_SCALE,443+(y-125)*WIDE_SCALE)

def wide_track_y(x):return wide_point(140+(x-60)/WIDE_SCALE,track_y(140+(x-60)/WIDE_SCALE))[1]

def track_y(x):return BOTTOM-.027*(x-DOCK)

WIDE_START=wide_point(1990,track_y(1990))[0]

class Minecart:
    beats=[('Load the context',0,8),('Take it to the model',8,14),
           ('Bring the response back',14,24.5),('Send context again next turn',24.5,34.5)]
    storyboard_times=[5.2,7.9,12.8,16.9,24.4,34.4]
    def __init__(self):
        self.fill=VolumeFill()
        raw=Image.open(HERE/'assets/context_transport/minecart/minecart-v1.png').convert('RGBA')
        # Crop only transparent production padding; preserve the generated alpha.
        bounds=raw.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
        raw=raw.crop(bounds)
        art=fitted(raw,(470,310))
        self.cart=[boil(art,v) for v in range(3)]
        self.front=[]
        for art in self.cart:
            mask=Image.new('L',art.size)
            # Near lip from the generated prop; right end is also in front.
            edge=[(0,.168),(.795,.145),(1,.02),(1,1),(0,1)]
            ImageDraw.Draw(mask).polygon([(x*art.width,y*art.height) for x,y in edge],fill=255)
            fg=art.copy();fg.putalpha(ImageChops.multiply(art.getchannel('A'),mask));self.front.append(fg)
        raw=extract_assets()['model']
        self.model=[boil(fitted(raw,(410,500)),v) for v in range(3)]
        def item(name,title,x,color):
            return dict(name=name,title=title,kind='prompt',xyz=(x,3.85,0),color=color)
        self.prompt=item('new-prompt',['NEW','PROMPT'],.08,(238,220,170))
        self.responses=[item(f'response-{i}',['MODEL','REPLY'],.43+i*.35,(169,208,179)) for i in range(3)]
        self.followup=item('followup',['NEXT','PROMPT'],1.48,(232,183,156))
        self.first=self.fill.items+[self.prompt]
        self.second=self.first+self.responses+[self.followup]
        self.lookup={x['name']:x for x in self.second}
        self.reply=[(i*COLS*ROWS,x['name']) for i,x in enumerate(self.responses)]

    @lru_cache(maxsize=150)
    def content(self,name,variant):
        item=self.lookup[name];im=Image.new('RGBA',(256,256));p=Sketch(im,variant)
        if item['kind']=='prompt':
            p.rect((65,12,190,132),fill=PAPER,color=INK,width=4,radius=4)
            for y in (40,65,90,115):p.line([(83,y),(171,y)],INK,4)
        else:
            art=fitted(self.fill.art[item['kind']],(186,135))
            im.alpha_composite(art,((256-art.width)//2,8))
        d=ImageDraw.Draw(im)
        for j,line in enumerate(item['title']):
            fs=39
            while d.textbbox((0,0),line,font=font(fs))[2]>230:fs-=1
            d.text((128,152+j*43),line,font=font(fs),fill=INK,anchor='mt')
        return im

    def source_vertices(self,item):
        x,z,h=item['xyz']
        return {(a,b,c):np.array(project(x+a*SIZE,z+b*SIZE,h+c*SIZE)) for a in (0,1) for b in (0,1) for c in (0,1)}

    def slot(self,index,cx,bottom,scale=1):
        art=self.cart[0];w,h=art.width*scale,art.height*scale
        left,top=cx-w/2,bottom-h
        # Axes fit the open rim: nearly horizontal broad face, receding right
        # edge, and vertical sides. Floor lies well BELOW the near lip.
        origin=np.array([left+.08*w,top+.64*h])
        u=np.array([.65*w/COLS,-.015*h/COLS]);v=np.array([.16*w/ROWS,-.125*h/ROWS])
        level=index//(COLS*ROWS);col=index%COLS;row=ROWS-1-(index//COLS)%ROWS
        height=float(np.linalg.norm(u))
        start=origin+col*u+row*v-np.array([0,level*height])
        verts={(a,b,c):start+a*u*.96+b*v*.96-np.array([0,c*height]) for a in (0,1) for b in (0,1) for c in (0,1)}
        return verts,(row,level,col)

    def cube(self,im,name,verts,variant):
        item=self.lookup[name];values=np.array(list(verts.values()))
        left,top=np.floor(values.min(axis=0)-4).astype(int);right,bottom=np.ceil(values.max(axis=0)+5).astype(int)
        tile=Image.new('RGBA',(right-left,bottom-top));p=Sketch(tile,variant)
        pts={k:tuple(q-np.array([left,top])) for k,q in verts.items()}
        def face(keys,shade):
            p.poly([pts[k] for k in keys],fill=tuple(max(0,min(255,c+shade)) for c in item['color']),color=INK,width=2)
        face([(1,0,0),(1,1,0),(1,1,1),(1,0,1)],-25)
        face([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],23)
        face([(0,0,0),(1,0,0),(1,0,1),(0,0,1)],0)
        a=np.array(pts[(0,0,1)]);u=np.array(pts[(1,0,1)])-a;v=np.array(pts[(0,0,0)])-a
        inv=np.linalg.inv(np.column_stack((u,v)))*256;off=-inv@a
        coeff=(inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1])
        tile.alpha_composite(self.content(name,variant).transform(tile.size,Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC))
        im.alpha_composite(tile,(int(left),int(top)))

    def rails(self,im,variant,wide=False):
        p=Sketch(im,variant)
        # One world-space railway and sleeper cadence. The wide camera applies
        # exactly the classroom thumbnail's transform to the ENTIRE railway.
        transform=wide_point if wide else lambda x,y:(x,y)
        scale=WIDE_SCALE if wide else 1
        end=140+(1440-60)/WIDE_SCALE if wide else 1730
        for i in range(int((end-240)/59.6)+1):
            x=240+i*59.6;y=track_y(x)
            p.poly([transform(x-15,y-25),transform(x+12,y-25),transform(x+38,y+10),transform(x+11,y+10)],fill=(131,111,92),color=INK,width=max(1,round(2*scale)))
        for offset in [-19,0]:
            p.line([transform(240,track_y(240)+offset),transform(end,track_y(end)+offset)],(60,65,72),max(1,round(5*scale)))

    @lru_cache(maxsize=36)
    def room(self,variant,response_count=0,second=False,tracks=True):
        im=self.fill.base_scene(39,variant)
        if tracks:self.rails(im,variant)
        delivered=list(reversed(self.responses))[:response_count]
        for item in [self.prompt]+delivered+([self.followup] if second else []):
            self.cube(im,item['name'],self.source_vertices(item),variant)
        return im

    @lru_cache(maxsize=6)
    def outside(self,variant,second=False):
        im=self.fill.entry.background[variant].crop((0,0,1920,125)).resize((W,H)).convert('RGBA')
        p=Sketch(im,variant)
        p.rect((40,355,890,910),fill=(240,225,202),color=INK,width=3,radius=12)
        thumb=self.room(variant,3 if second else 0,second,False).crop((140,125,1780,975)).resize((810,420),Image.Resampling.LANCZOS)
        im.alpha_composite(thumb,(60,443))
        p.text((465,374),'CONTEXT WINDOW',38,INK,anchor='mt')
        p.rect((1400,345,1840,905),fill=(238,231,211),color=INK,width=3,radius=20)
        p.text((1620,220),'MODEL',49,INK,anchor='mt')
        self.rails(im,variant,True)
        return im

    def working_model(self,im,t,variant):
        progress=(t-WORK_START)/WORK_DURATION
        if not 0<progress<1:
            im.alpha_composite(self.model[variant],(1420,375))
            return
        strength=smooth(progress/.16)*(1-smooth((progress-.77)/.23))
        phase=progress*math.tau
        canvas=Image.new('RGBA',(610,692));p=Sketch(canvas,variant)
        # Accordion side vents telescope out, then tuck back into the cabinet.
        for side in [-1,1]:
            root=120 if side<0 else 494
            reach=60*strength
            points=[(root,345),(root+side*reach,330),(root+side*reach,410),(root,415)]
            p.poly(points,fill=(159,181,171),color=INK,width=3)
            for j in range(1,5):
                x=root+side*reach*j/5
                p.line([(x,345-15*j/5),(x,415-5*j/5)],INK,2)
        # Roof feelers rise on little spring stems; no new narration text.
        for x,y,reach in [(162,185,100),(452,127,75)]:
            tip=y-reach*strength
            p.line([(x,y),(x,tip)],INK,4)
            if strength>.04:
                p.oval((x-9,tip-9,x+9,tip+9),fill=(225,169,95),color=INK,width=3)
        canvas.alpha_composite(self.model[variant],(100,100))
        # A bright, softly changing display and spinning side reel.
        overlay=Image.new('RGBA',canvas.size);d=ImageDraw.Draw(overlay)
        d.rounded_rectangle((257,224,449,341),radius=24,fill=(91,206,177,round(180*strength)))
        for j in range(3):
            a=phase*2+j*math.tau/3
            x=351+56*math.cos(a);y=280+33*math.sin(a)
            d.ellipse((x-9,y-9,x+9,y+9),fill=(252,229,146,round(245*strength)))
        canvas.alpha_composite(overlay)
        reel=Sketch(canvas,variant)
        reel.oval((112,192,196,366),fill=(176,176,157),color=INK,width=3)
        for j in range(3):
            a=phase*3+j*math.tau/3
            pts=[(154,279)]+[(154+34*math.cos(a+k*.12),279+72*math.sin(a+k*.12)) for k in range(7)]
            reel.poly(pts,fill=(64,68,67),color=INK,width=2)
        reel.oval((145,265,163,293),fill=(124,129,120),color=INK,width=2)
        for j,(x,y) in enumerate([(345,393),(379,392),(447,373),(480,373)]):
            r=6+3*strength*(.5+.5*math.sin(phase*2+j))
            reel.oval((x-r,y-r,x+r,y+r),fill=(250,211,96),color=(128,96,63),width=1)
        # Rubber-body anticipation, squash/stretch, a shiver, then recovery.
        wave=math.sin(phase*3)
        sx=1+.12*strength*wave;sy=1-.11*strength*wave
        canvas=canvas.resize((round(610*sx),round(692*sy)),Image.Resampling.BICUBIC)
        canvas=canvas.rotate(4.5*strength*math.sin(phase*4),Image.Resampling.BICUBIC,expand=True)
        center_x=1625+7*strength*math.sin(phase*6)
        center_y=867-246*sy-14*strength*abs(math.sin(phase*2))
        im.alpha_composite(canvas,(round(center_x-canvas.width/2),round(center_y-canvas.height/2)))

    @lru_cache(maxsize=100)
    def packed(self,payload,variant):
        im=Image.new('RGBA',(650,500));draw=[]
        for index,name in payload:
            verts,(row,level,col)=self.slot(index,325,480)
            draw.append(((-row,level,col),name,verts))
        for _,name,verts in sorted(draw,key=lambda a:a[0]):self.cube(im,name,verts,variant)
        box=im.getbbox()
        return (im.crop(box),box[:2]) if box else (Image.new('RGBA',(1,1)),(0,0))

    def carrier(self,im,cx,bottom,variant,payload=(),active=(),scale=1,wide=False):
        layer=Image.new('RGBA',(W,H));art=self.cart[variant];front=self.front[variant]
        if scale!=1:
            size=(round(art.width*scale),round(art.height*scale))
            art=art.resize(size,Image.Resampling.LANCZOS);front=front.resize(size,Image.Resampling.LANCZOS)
        xy=(round(cx-art.width/2),round(bottom-art.height))
        layer.alpha_composite(art,xy)
        cargo,offset=self.packed(tuple(payload),variant)
        if scale!=1:cargo=cargo.resize((max(1,round(cargo.width*scale)),max(1,round(cargo.height*scale))),Image.Resampling.LANCZOS)
        layer.alpha_composite(cargo,(round(cx+(offset[0]-325)*scale),round(bottom+(offset[1]-480)*scale)))
        for name,verts in active:self.cube(layer,name,verts,variant)
        layer.alpha_composite(front,xy)
        p=Sketch(layer,variant)
        for u in [.207,.626]:
            x,y=xy[0]+u*art.width,xy[1]+.864*art.height
            r=art.height*.105
            for j in range(2):
                a=cx/35+j*math.pi
                p.line([(x,y),(x+r*math.cos(a),y+r*math.sin(a))],(99,111,143),2,.3)
        if not wide:layer.paste((0,0,0,0),(1730,0,W,H))
        im.alpha_composite(layer)

    def flight(self,source,target,q,arc=120):
        return {k:source[k]*(1-q)+target[k]*q-np.array([0,arc*math.sin(math.pi*q)]) for k in source}

    def loading(self,im,t,variant,second=False):
        payload=self.second if second else self.first
        start,spacing=(SECOND_START,SECOND_SPACING) if second else (FIRST_START,FIRST_SPACING)
        landed=[];active=[]
        for i,item in enumerate(payload):
            age=t-start-i*spacing
            if age>=LOAD_TIME:landed.append((i,item['name']))
            elif age>=0:
                target,_=self.slot(i,DOCK,BOTTOM)
                active.append((item['name'],self.flight(self.source_vertices(item),target,smooth(age/LOAD_TIME))))
        self.carrier(im,DOCK,BOTTOM,variant,landed,active)

    def model_slot(self):
        return {(a,b,c):np.array([1580+a*40+b*12,610-b*9-c*40]) for a in (0,1) for b in (0,1) for c in (0,1)}

    def frame(self,kind,t,variant=None):
        assert kind=='train'
        variant=int(t*30)//5%3 if variant is None else variant
        real_t=t
        if t>=WORK_START+WORK_DURATION:t-=WORK_DURATION
        elif t>=WORK_START:t=WORK_START
        second=t>=21;external=10.3<=t<18.3 or t>=26.3
        first=[(i,x['name']) for i,x in enumerate(self.first)]
        again=[(i,x['name']) for i,x in enumerate(self.second)]
        if external:
            im=self.outside(variant,second).copy()
            self.working_model(im,real_t,variant)
            if t<14:
                cx=WIDE_START+(1290-WIDE_START)*smooth((t-10.3)/3.15)
                self.carrier(im,cx,wide_track_y(cx),variant,first,scale=WIDE_SCALE,wide=True)
            elif t<16:
                landed=[];active=[]
                for order,(i,name) in enumerate(reversed(first)):
                    age=t-14-order*.027
                    if age<0:landed.append((i,name))
                    elif age<.28:
                        source,_=self.slot(i,1290,wide_track_y(1290),WIDE_SCALE)
                        active.append((name,self.flight(source,self.model_slot(),smooth(age/.28),55)))
                for j,(i,name) in enumerate(self.reply):
                    age=t-(15.22+j*.22)
                    if age>=.2:landed.append((i,name))
                    elif age>=0:
                        target,_=self.slot(i,1290,wide_track_y(1290),WIDE_SCALE)
                        active.append((name,self.flight(self.model_slot(),target,smooth(age/.2),65)))
                self.carrier(im,1290,wide_track_y(1290),variant,landed,active,scale=WIDE_SCALE,wide=True)
            elif t<18.3:
                cx=1290-(1290-WIDE_START)*smooth((t-16)/2.15)
                self.carrier(im,cx,wide_track_y(cx),variant,self.reply,scale=WIDE_SCALE,wide=True)
            else:
                cx=WIDE_START+(1290-WIDE_START)*smooth((t-26.3)/3.5)
                self.carrier(im,cx,wide_track_y(cx),variant,again,scale=WIDE_SCALE,wide=True)
        else:
            received=3 if second else max(0,min(3,int((t-20.45+1e-6)/.1)+1)) if t>=20.45 else 0
            im=self.room(variant,received,second).copy()
            if t<1.6:
                cx=1990-(1990-DOCK)*smooth((t-.15)/1.4)
                self.carrier(im,cx,track_y(cx),variant)
            elif t<8:self.loading(im,t,variant)
            elif t<10.3:
                cx=DOCK+(1990-DOCK)*smooth((t-8)/2.15)
                self.carrier(im,cx,track_y(cx),variant,first)
            elif t<19.8:
                cx=1990-(1990-DOCK)*smooth((t-18.3)/1.5)
                self.carrier(im,cx,track_y(cx),variant,self.reply)
            elif t<21:
                active=[];landed=[]
                for j,(index,name) in enumerate(reversed(self.reply)):
                    age=t-(19.8+j*.1)
                    if age<0:landed.append((index,name))
                    elif age<.65:
                        source,_=self.slot(index,DOCK,BOTTOM)
                        active.append((name,self.flight(source,self.source_vertices(self.lookup[name]),smooth(age/.65),110)))
                self.carrier(im,DOCK,BOTTOM,variant,landed,active)
            elif t<24.5:self.loading(im,t,variant,True)
            else:
                cx=DOCK+(1990-DOCK)*smooth((t-24.5)/1.7)
                self.carrier(im,cx,track_y(cx),variant,again)
            if .3<t<3.3:self.fill.bubble(im,'Help me track\nUNC workstreams.',t,variant,'human')
            if 20.65<=t<21:self.fill.bubble(im,'Here are the workstreams.',t,variant,'agent')
            if 21<=t<23.8:self.fill.bubble(im,'Now focus on next steps.',t,variant,'human')
        return im.convert('RGB')

    def coin_frame(self,t,variant=None):
        """Optional finale: the final wide tableau stays still under the coins."""
        variant=int(t*30)//5%3 if variant is None else variant
        im=self.frame('train',self.beats[-1][2],variant).convert('RGBA')
        coins=Image.new('RGBA',im.size);p=Sketch(coins,variant)
        for i in range(6):
            age=t-(.18+i*.32)
            if not 0<=age<1.02:continue
            q=min(1,age/.82)
            x=1760+(i%3-1)*22*(.35+.65*q)
            y=397-215*math.sin(q*math.pi*.70)
            if age<.82:
                rx=3+15*abs(math.cos(age*19+i*.7));ry=24
                p.oval((x-rx+4,y-ry,x+rx+4,y+ry),fill=(193,116,26),color=(123,77,27),width=2)
                p.oval((x-rx,y-ry,x+rx,y+ry),fill=(249,198,55),color=(137,88,28),width=2)
                if rx>8:
                    p.oval((x-rx*.69,y-18,x+rx*.69,y+18),color=(218,145,28),width=2)
                    p.line([(x-1,y-12),(x-1,y+12)],(255,239,151),3)
                    p.line([(x-rx*.52,y-15),(x-rx*.77,y-5)],(255,244,171),2)
            if age>.70:
                sparkle=math.sin(math.pi*clamp((age-.70)/.32))
                for j in range(3):
                    a=j*math.tau/3+i*.4
                    sx=x+math.cos(a)*30;sy=y+math.sin(a)*29
                    r=9*sparkle
                    p.poly([(sx,sy-r),(sx+2,sy-2),(sx+r,sy),(sx+2,sy+2),
                            (sx,sy+r),(sx-2,sy+2),(sx-r,sy),(sx-2,sy-2)],
                           fill=(255,218,85),color=(194,143,43),width=1)
        # Coins emerge through the roof instead of painting over the cabinet.
        coins.paste((0,0,0,0),(0,399,W,H))
        im.alpha_composite(coins)
        return im.convert('RGB')

    def render_coins(self):
        import shutil
        dest=HERE/'out/context_train_coins.mp4'
        encode(dest,(self.coin_frame(i/30) for i in range(108)))
        shutil.copy2(dest,HERE/'interactive/context_transport/train/coins.mp4')
        self.coin_frame(1.25,0).save(HERE/'source/context_transport/train/coins.png')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--coins-only',action='store_true');args=parser.parse_args()
    scene=Minecart()
    if not args.coins_only:prepare(scene,'train')
    if not args.prepare_only:
        if not args.coins_only:render(scene,'train')
        scene.render_coins()
