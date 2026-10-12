"""Three comparable harness transport studies: trolley, wheelbarrow, train.

Context is copied, never removed. A cut to a wider view separates the classroom
from the model. The response returns, and a second turn sends a fresh bundle.
"""
from pathlib import Path
from functools import lru_cache
import argparse
import math
import subprocess
import numpy as np
from scipy.ndimage import label,find_objects,binary_dilation
from PIL import Image,ImageDraw
from render_context_fill import Fill,tag,fitted,INK,PAPER
from render_context_entry import boil,smooth,clamp
from render_computer_control_bonus import Sketch,font,encode

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'assets/context_transport'
SOURCE=HERE/'source/context_transport'
PLAYER=HERE/'interactive/context_transport'
OUT=HERE/'out'
W,H,FPS=1920,1080,30
KINDS=['trolley','wheelbarrow','train']
BEATS=[('Load the context',0,8),('Take it to the model',8,14),
       ('Bring the response back',14,21),('Send context again next turn',21,31)]
DURATION=31


def card(title,lines,color=(245,229,191),width=330):
    im=Image.new('RGBA',(width,100))
    p=Sketch(im);p.rect((3,3,width-4,96),fill=color,color=INK,width=3,radius=6)
    p.text((width/2,10),title,28,INK,anchor='mt')
    for i,line in enumerate(lines):p.text((width/2,45+i*24),line,23,INK,anchor='mt')
    return im


def extract_assets():
    sheet=Image.open(ASSETS/'transport-sheet.png').convert('RGBA')
    labels,_=label(np.asarray(sheet)[:,:,3]>100)
    objects=[(i+1,s) for i,s in enumerate(find_objects(labels))
             if s and (s[0].stop-s[0].start)*(s[1].stop-s[1].start)>50000]
    objects.sort(key=lambda z:(((z[1][0].start+z[1][0].stop)/2)//600,z[1][1].start))
    assert len(objects)==4
    result={}
    for name,(ident,s) in zip(['wheelbarrow','trolley','train','model'],objects):
        x,y=max(0,s[1].start-3),max(0,s[0].start-3)
        r,b=min(sheet.width,s[1].stop+3),min(sheet.height,s[0].stop+3)
        a=np.array(sheet.crop((x,y,r,b)))
        a[:,:,3]*=binary_dilation(labels[y:b,x:r]==ident,iterations=3)
        im=Image.fromarray(a);im.save(ASSETS/f'{name}.png');result[name]=im
    return result


class Transport:
    def __init__(self):
        self.fill=Fill()
        raw=extract_assets()
        self.vehicles={}
        for kind in KINDS:
            art=fitted(raw[kind],(400 if kind=='wheelbarrow' else 350,270))
            # Readable harness label is drawn independently of generated art.
            tag(art,'HARNESS',art.width*(.58 if kind=='wheelbarrow' else .49),art.height*.43,27,180)
            self.vehicles[kind]=[boil(art,v) for v in range(3)]
        art=fitted(raw['model'],(430,515))
        self.model=[boil(art,v) for v in range(3)]
        self.prompt=card('NEW PROMPT',['Help me track','UNC workstreams.'])
        self.response=card('MODEL RESPONSE',['A response for this turn.'],(218,234,213))
        self.followup=card('NEXT PROMPT',['Now focus on next steps.'],(242,214,190))
        self.cards={name:[boil(im,v) for v in range(3)] for name,im in
                    [('prompt',self.prompt),('response',self.response),('followup',self.followup)]}
        self.payloads=list(self.fill.items)
        self.payloads.append(dict(name='new-prompt',frames=self.cards['prompt'],xy=(885,247)))
        self.second=self.payloads+[dict(name='previous-response',frames=self.cards['response'],xy=(885,147))]
        self.second.append(dict(name='next-prompt',frames=self.cards['followup'],xy=(1290,170)))

    def payload(self,second):return self.second if second else self.payloads

    def rails(self,im,kind,wide=False):
        p=Sketch(im)
        if kind=='trolley':
            if wide:
                points=[(660,415),(1400,415)]
            else:points=[(800,420),(1775,350)]
            p.line(points,(83,79,73),5)
            p.line([(x,y+13) for x,y in points],(151,139,120),2)
        elif kind=='train':
            if wide:
                a,b=(765,835),(1360,835)
            else:a,b=(810,923),(1770,869)
            for i in range(22):
                q=i/21;x=a[0]+(b[0]-a[0])*q;y=a[1]+(b[1]-a[1])*q
                p.line([(x-9,y-8),(x+11,y+35)],(159,129,94),5)
            p.line([a,b],(104,102,98),4)
            separation=23 if wide else 28
            p.line([(a[0],a[1]+separation),(b[0],b[1]+separation)],(104,102,98),4)

    @lru_cache(maxsize=60)
    def room(self,kind,variant,response=False,second=False,open_door=True):
        e=self.fill.entry
        im=e.background[variant].copy()
        if open_door:e.door(im,1,variant)
        self.rails(im,kind)
        im.alpha_composite(self.fill.settled(tuple(self.fill.inventory(39)),variant))
        e.actor(im,e.human,8.5,1.05,4.68,785,variant)
        e.actor(im,e.agent,8.5,2.3,3.78,1160,variant)
        self.fill.draw_item(im,self.fill.items[4],39,variant)
        for item in self.fill.personal:self.fill.draw_item(im,item,39,variant)
        im.alpha_composite(self.cards['prompt'][variant],(885,247))
        if response:im.alpha_composite(self.cards['response'][variant],(885,147))
        if second:im.alpha_composite(self.cards['followup'][variant],(1290,170))
        return im

    @lru_cache(maxsize=24)
    def outside(self,kind,variant,second=False):
        im=self.fill.entry.background[variant].copy()
        # Fresh paper establishes a distinct, wider location with ample distance
        # between the original classroom and the separate model station.
        paper=self.fill.entry.background[variant].crop((0,0,1920,125)).resize((W,H))
        im=paper.convert('RGBA')
        p=Sketch(im,variant)
        p.rect((40,355,890,910),fill=(240,225,202),color=INK,width=3,radius=12)
        thumb=self.room(kind,variant,second,second).crop((140,125,1780,975)).resize((810,420),Image.Resampling.LANCZOS)
        im.alpha_composite(thumb,(60,443))
        p.text((465,374),'YOUR CONTEXT WINDOW',38,INK,anchor='mt')
        p.text((465,878),'The conversation stays here.',26,INK,anchor='mm')
        p.line([(900,881),(1820,881)],(159,145,125),3)
        p.rect((1400,345,1840,905),fill=(238,231,211),color=INK,width=3,radius=20)
        art=self.model[variant]
        im.alpha_composite(art,(1410,365))
        p.text((1610,305),'MODEL',49,INK,anchor='mt')
        self.rails(im,kind,True)
        return im

    def geometry(self,kind,cx,bottom,scale=1):
        art=self.vehicles[kind][0]
        w,h=art.width*scale,art.height*scale
        left,top=cx-w/2,bottom-h
        pile_x=cx+(28*scale if kind=='wheelbarrow' else 0)
        mouth=top+(42 if kind=='wheelbarrow' else 45)*scale
        return left,top,pile_x,mouth

    def slot(self,kind,cx,bottom,index,count,scale=1):
        _,_,px,mouth=self.geometry(kind,cx,bottom,scale)
        if index==count-1:return px-70*scale,mouth-185*scale,140*scale,62*scale
        col=index%5;row=index//5
        return px+(col-2)*52*scale-34*scale,mouth-(row+1)*46*scale-20*scale,76*scale,76*scale

    def carrier(self,im,kind,cx,bottom,variant,t,load=None,count=None,response=False,wide=False,scale=1):
        layer=Image.new('RGBA',(W,H))
        p=Sketch(layer,variant)
        left,top,px,mouth=self.geometry(kind,cx,bottom,scale)
        if kind=='trolley':
            wire_y=415 if wide else 420+(cx-800)*(350-420)/975
            p.line([(cx-110*scale,wire_y+15),(left+50*scale,top+18*scale)],INK,3)
            p.line([(cx+110*scale,wire_y+15),(left+300*scale,top+34*scale)],INK,3)
            p.line([(cx-130*scale,wire_y+10),(cx+130*scale,wire_y+10)],INK,6)
            for x in [cx-110*scale,cx+110*scale]:
                p.oval((x-12,wire_y-12,x+12,wire_y+12),fill=(185,177,159),color=INK,width=3)
        if load:
            for i,item in enumerate(load[:count if count is not None else len(load)]):
                x,y,w,h=self.slot(kind,cx,bottom,i,len(load),scale)
                art=fitted(item['frames'][variant],(round(w),round(h)))
                layer.alpha_composite(art,(round(x),round(y)))
        if response:
            art=fitted(self.cards['response'][variant],(230,90))
            layer.alpha_composite(art,(round(px-115),round(mouth-65)))
        art=self.vehicles[kind][variant]
        if scale!=1:art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
        layer.alpha_composite(art,(round(left),round(top)))
        # Animated wheel spokes supply visible rolling, while hold frames freeze
        # the wheel phase. All three comparisons share the same travel timing.
        if kind in ('train','wheelbarrow'):
            centers=[(.247,.714),(.674,.81)] if kind=='train' else [(.79,.79)]
            for u,v in centers:
                x,y=left+art.width*u,top+art.height*v
                radius=(20 if kind=='train' else 27)*scale
                for j in range(3):
                    a=cx/35+j*math.tau/3
                    p.line([(x,y),(x+radius*math.cos(a),y+radius*math.sin(a))],(116,109,93),2,.3)
        if not wide:layer.paste((0,0,0,0),(1730,0,W,H))
        im.alpha_composite(layer)

    def loading(self,im,kind,t,variant,start,second=False):
        payload=self.payload(second)
        spacing=.21 if not second else .13
        duration=.9 if not second else .65
        cx,bottom=980,939
        landed=0
        for i in range(len(payload)):
            if t>=start+i*spacing+duration:landed=i+1
        self.carrier(im,kind,cx,bottom,variant,t,payload,landed)
        for i,item in enumerate(payload):
            age=t-(start+i*spacing)
            if not 0<=age<duration:continue
            q=smooth(age/duration)
            src=item['frames'][variant]
            tx,ty,w,h=self.slot(kind,cx,bottom,i,len(payload))
            target=fitted(src,(round(w),round(h)))
            sw,sh=src.size
            width=round(sw*(1-q)+target.width*q);height=round(sh*(1-q)+target.height*q)
            art=src.resize((max(1,width),max(1,height)),Image.Resampling.BICUBIC)
            x=item['xy'][0]*(1-q)+tx*q
            y=item['xy'][1]*(1-q)+ty*q-115*math.sin(math.pi*q)
            im.alpha_composite(art,(round(x),round(y)))

    def frame(self,kind,t,variant=None):
        variant=int(t*FPS)//5%3 if variant is None else variant
        second=t>=21
        external=10.3<=t<18.3 or t>=26.3
        if external:
            im=self.outside(kind,variant,second).copy()
            if t<14:
                q=smooth((t-10.3)/3.15)
                cx=780+510*q
                self.carrier(im,kind,cx,858,variant,t,self.payload(False),wide=True,scale=.88)
            elif t<16:
                # Context enters the model in a visibly discrete request.
                remaining=max(0,len(self.payloads)-int((t-14)/1.0*len(self.payloads)))
                self.carrier(im,kind,1290,858,variant,t,self.payloads,remaining,wide=True,scale=.88)
                for i,item in enumerate(self.payloads):
                    age=t-14-i*.055
                    if 0<=age<.3:
                        q=smooth(age/.3)
                        art=fitted(item['frames'][variant],(75,75))
                        im.alpha_composite(art,(round(1290+290*q),round(610-60*math.sin(math.pi*q))))
                if t<15.5:
                    Sketch(im,variant).text((1660,565),'Working…',30,PAPER,anchor='mm')
                if t>15.4:
                    q=smooth((t-15.4)/.6)
                    art=fitted(self.cards['response'][variant],(230,90))
                    _,_,px,mouth=self.geometry(kind,1290,858,.88)
                    im.alpha_composite(art,(round(1560*(1-q)+(px-115)*q),round(800*(1-q)+(mouth-65)*q-70*math.sin(math.pi*q))))
            elif t<18.3:
                cx=1290-510*smooth((t-16)/2.15)
                self.carrier(im,kind,cx,858,variant,t,response=True,wide=True,scale=.88)
            else:
                cx=780+510*smooth((t-26.3)/3.5)
                self.carrier(im,kind,cx,858,variant,t,self.payload(True),wide=True,scale=.88)
        else:
            im=self.room(kind,variant,t>=20.65,second).copy()
            if t<1.6:
                cx=1900-920*smooth((t-.15)/1.4)
                self.carrier(im,kind,cx,939-(cx-980)*.06,variant,t)
            elif t<8:
                self.loading(im,kind,t,variant,1.8)
            elif t<10.3:
                cx=980+950*smooth((t-8)/2.15)
                self.carrier(im,kind,cx,939-(cx-980)*.06,variant,t,self.payload(False))
            elif t<19.8:
                cx=1900-920*smooth((t-18.3)/1.5)
                self.carrier(im,kind,cx,939-(cx-980)*.06,variant,t,response=True)
            elif t<21:
                self.carrier(im,kind,980,939,variant,t)
                if t<20.65:
                    q=smooth((t-19.8)/.85)
                    src=self.cards['response'][variant]
                    art=src.resize((round(230+100*q),round(70+30*q)),Image.Resampling.BICUBIC)
                    _,_,px,mouth=self.geometry(kind,980,939)
                    im.alpha_composite(art,(round((px-115)*(1-q)+885*q),round((mouth-65)*(1-q)+147*q)))
            elif t<24.5:
                self.loading(im,kind,t,variant,21.15,True)
            else:
                cx=980+950*smooth((t-24.5)/1.7)
                self.carrier(im,kind,cx,939-(cx-980)*.06,variant,t,self.payload(True))
        p=Sketch(im,variant)
        title=('The harness gathers context + your prompt.' if t<8 else
               'The context travels out to the model.' if t<14 else
               'The model sends a response back.' if t<21 else
               'Next turn: send a fresh context bundle.')
        p.text((960,45),title,41,INK,anchor='mt')
        p.text((960,1008),'Copies travel. The conversation stays in the room.',28,INK,anchor='mt')
        return im.convert('RGB')


def prepare(scene,kind):
    target=PLAYER/kind;target.mkdir(parents=True,exist_ok=True)
    dest=SOURCE/kind;dest.mkdir(parents=True,exist_ok=True)
    scene.frame(kind,0,0).save(target/'poster.jpg',quality=96)
    sheet=Image.new('RGB',(1920,780),PAPER)
    for i,t in enumerate(getattr(scene,"storyboard_times",[5.2,7.9,12.8,15.8,20.9,30.9])):
        frame=scene.frame(kind,t)
        sheet.paste(frame.resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*390))
        ImageDraw.Draw(sheet).text(((i%3)*640+16,(i//3)*390+363),f'{t:g}s',font=font(22),fill=INK)
    sheet.save(dest/'storyboard.jpg',quality=95)
    for i,(_,_,end) in enumerate(getattr(scene,"beats",BEATS),1):
        frame=scene.frame(kind,end-1/FPS,0)
        frame.save(target/f'hold-{i:02}.jpg',quality=96)
        if i in (1,2):frame.save(dest/('loaded.png' if i==1 else 'outside-model.png'))


def render(scene,kind):
    target=PLAYER/kind;master=OUT/f'context_{kind}.mp4'
    beats=getattr(scene,"beats",BEATS)
    encode(master,(scene.frame(kind,i/FPS) for i in range(round(beats[-1][2]*FPS))))
    encode(target/'ready.mp4',(scene.frame(kind,0,j//5) for j in range(15)))
    for i,(_,start,end) in enumerate(beats,1):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),'-t',str(end-start),
                        '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target/f'beat-{i:02}.mp4')],check=True)
        encode(target/f'hold-{i:02}.mp4',(scene.frame(kind,end-1/FPS,j//5) for j in range(15)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop','0',str(OUT/f'context_{kind}.gif')],check=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--kind',choices=KINDS)
    args=parser.parse_args()
    SOURCE.mkdir(parents=True,exist_ok=True)
    for kind in ([args.kind] if args.kind else KINDS):
        if kind=='train':
            from render_context_minecart import Minecart
            scene=Minecart()
        else:scene=Transport()
        prepare(scene,kind)
        if not args.prepare_only:
            render(scene,kind)
            if kind=='train':scene.render_coins()
