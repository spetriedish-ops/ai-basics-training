"""A missing detail in the summary, then a separate illustrated inbox incident."""
import argparse
import json
import math
import subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from render_context_compaction import Compaction, HERE
from context_press_mechanics import project as press_project, FINAL_HEIGHT, BED_FRONT
from render_context_volume import project, DEPTH
from render_context_entry import smooth,clamp
from render_context_portfolio import PAPER,INK,fittext
from render_computer_control_bonus import Sketch,encode,font

PLAYER=HERE/'interactive/context_loss'
SOURCE=HERE/'source/context_loss'
VERSION='context-loss-1'
BEATS=[
    ('Return with only the summary',0,3.5),
    ('Ask for the earlier success measures',3.5,6.5),
    ('Inspect what survived',6.5,12),
    ('The specific detail is missing',12,15.5),
    ('A separate reported inbox incident',0,4),
    ('Messages start going to Trash',4,8),
    ('Stop requests do not stop the actions',8,12.5),
    ('Stop the agent at the computer',12.5,17),
]
CUES=[
    'Return to the original classroom. The same crumpled summary cube is now the only context object; the original user and agent remain.',
    'Ask about the pilot success measures agreed with Ted. Those measures were explicitly established and retrieved before compaction: less manual follow-up and faster handoffs.',
    'The agent walks to the summary and unfolds its contents. Broad topics survived, including the Nugget Factory pilot; the exact success measures are omitted.',
    'The agent explains that the measures are not in this summary and asks the user to remind it. This is a fictional illustration of information loss, not a guarantee that compaction loses this particular detail.',
    'Begin a separate, stylized reconstruction of Summer Yue’s reported February 2026 OpenClaw inbox incident. The dialogue and interface are paraphrased illustrations, not screenshots or a depiction of Yue. She described testing on a toy inbox before using her real inbox.',
    'Yue reported that the agent began deleting messages despite an instruction to wait for approval. She attributed the lost instruction to compaction. That explanation is her account, not an independently established root cause. We show mail moved to Trash, not permanent destruction.',
    'She reported that stop requests from her phone did not halt the agent. The animation intentionally keeps the approval request visible on the phone while more messages move to Trash.',
    'She said she had to go to her Mac mini to stop it. A local Stop agent button illustrates intervention, not the exact interface she used. We do not show an empty inbox, a deleted-message count, or claim this was her work inbox. Sources and narration notes are saved beside this renderer’s review assets.',
]


def opacity(im,amount):
    im=im.copy();im.putalpha(im.getchannel('A').point(lambda a:round(a*clamp(amount))));return im


class ContextLoss:
    def __init__(self):
        self.compaction=Compaction();self.mono=self.compaction.mono
        self.press=self.compaction.mechanics
        self.human_pos=(6.1,.45)
        self.agent_start=(4.9,1.4);self.agent_end=(3.95,3.15)

    @staticmethod
    def room_projection(x,z,h):
        return project(2.5+(x-4)*.80,3.4+(z-1.75)*.80,h*.80)

    @lru_cache(maxsize=3)
    def summary(self,v):
        return self.summary_at(v,self.room_projection,.80)

    def summary_at(self,v,projection,label_scale=1):
        im=Image.new('RGBA',(1920,1080))
        for b in sorted(self.press.layout(1,FINAL_HEIGHT),key=lambda b:(-b['z'],b['h'])):
            self.press.carton(im,b,v,projection=projection)
        left,right=self.press.wall_limits(1);s=Sketch(im,v)
        corners=[projection(x,BED_FRONT-.005,h) for x,h in [(left+.13,.91),(right-.13,.91),(right-.13,.64),(left+.13,.64)]]
        s.poly(corners,(242,229,191),INK,1)
        cx=sum(x for x,y in corners)/4;cy=sum(y for x,y in corners)/4
        s.text((cx,cy-14*label_scale),'SUMMARY',round(26*label_scale),INK,anchor='mt')
        # Sketch strokes are opaque in the original RGB press render. Keep
        # that same ink when carrying the cube on a transparent stage layer.
        im.putalpha(im.getchannel('A').point(lambda a:255 if a else 0))
        return im

    def agent_position(self,t):
        u=smooth((t-6.8)/2.1)
        return tuple(a+(b-a)*u for a,b in zip(self.agent_start,self.agent_end))

    def actor(self,name,t,v):
        if name=='agent':
            pos=self.agent_position(t);moving=6.8<t<8.9
            if moving:
                art,anchor=self.mono.searching_walk(int((t-6.8)*9)%8,2 if int(t*3)%3 else 3,v)
            else:
                expression=0 if t<8.9 else [0,2,3,4,3][min(4,int((t-8.9)*2.4))]
                if t>=12.6:expression=2
                frames,anchor=self.mono.expressions['agent'][expression];art=frames[v]
        else:
            pos=self.human_pos
            expression=0 if t<4 else 1 if t<10.5 else 2
            frames,anchor=self.mono.expressions['human'][expression];art=frames[v]
        scale=(1+DEPTH*self.mono.initial[name][1])/(1+DEPTH*pos[1])
        art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
        px,py=project(*pos)
        return art,(round(px-anchor[0]*scale),round(py-anchor[1]*scale)),pos

    def speech(self,im,lines,v,box,tip,amount=1):
        layer=Image.new('RGBA',im.size);s=Sketch(layer,v)
        x,y,w=box;height=34+43*len(lines)
        tx=max(x+35,min(x+w-35,tip[0]))
        s.poly([(tx-22,y+height-2),tip,(tx+20,y+height-2)],PAPER,INK,2)
        s.rect((x,y,x+w,y+height),PAPER,INK,2,radius=18)
        for j,line in enumerate(lines):fittext(s,(x+23,y+17+j*43),line,34,w-46,anchor='lt')
        im.alpha_composite(opacity(layer,amount))

    def summary_note(self,im,t,v):
        progress=smooth((t-9.0)/1.0)
        if progress<=0:return
        # One note unfolds out of the same summary cube; no new boxes appear.
        x,y=460,390;w,h=450,185
        floor_y=646
        top=floor_y+(y-floor_y)*progress
        height=h*progress
        s=Sketch(im,v)
        s.poly([(690,floor_y),(720,top+height),(758,top+height),(739,floor_y)],(227,212,174),INK,1)
        s.poly([(x,top),(x+w-8,top+4),(x+w,top+height),(x+9,top+height-5)],(249,237,202),INK,2)
        if progress>.92:
            s.text((x+25,top+17),'SUMMARY',28,INK)
            for j,line in enumerate(['Nugget Factory pilot','Account planning','Team coordination']):
                s.text((x+28,top+61+j*36),line,27,INK)
        if t>=10:
            a=min(t-10,1.55)
            cx=815+math.sin(a*4.2)*12;cy=470+min(1,a/1.3)*65
            s.oval((cx-30,cy-30,cx+30,cy+30),None,(169,123,55),5)
            s.line([(cx+21,cy+22),(cx+36,cy+39)],INK,8)

    def classroom(self,t,v):
        if t==0:return self.compaction.compactor(17,v)
        transition=smooth(t/2.35)
        im=Image.blend(self.compaction.background[v],self.mono.entry.background[v],transition)
        cast=Image.new('RGBA',im.size);shadows=Image.new('RGBA',im.size);d=ImageDraw.Draw(shadows)
        for name in ['agent','human']:
            art,xy,pos=self.actor(name,t,v);px,py=project(*pos)
            d.ellipse((px-60,py-7,px+60,py+10),fill=(97,75,55,36));cast.alpha_composite(art,xy)
        cast_background=shadows.filter(ImageFilter.GaussianBlur(4));cast_background.alpha_composite(cast)
        if transition<1:
            im.alpha_composite(opacity(cast_background,smooth((t-1.1)/1.15)))
            def camera(x,z,h):
                a=press_project(x,z,h);b=self.room_projection(x,z,h)
                return tuple(a[i]*(1-transition)+b[i]*transition for i in range(2))
            im.alpha_composite(self.summary_at(v,camera,1-.2*transition))
        else:
            im.alpha_composite(self.summary(v));im.alpha_composite(cast_background)
        if t>=3.5:
            amount=smooth((t-3.5)/.35)*(1-smooth((t-9.1)/.6))
            if amount>0:self.speech(im,['What success measures did','we agree on with Ted?'],v,(1090,200,620),(1330,450),amount)
        self.summary_note(im,t,v)
        if t>=12.2:
            self.speech(im,['The pilot is here, but those','measures aren’t in the summary.','Could you remind me?'],v,(1005,190,650),(959,580),smooth((t-12.2)/.4))
        return im.convert('RGB')

    @lru_cache(maxsize=3)
    def mail_envelope(self,v):
        im=Image.new('RGBA',(140,92));s=Sketch(im,v)
        s.rect((4,5,136,87),(246,230,192),INK,3,radius=5)
        s.line([(6,8),(70,52),(134,8)],INK,3)
        s.line([(6,84),(49,45)],INK,2);s.line([(134,84),(92,45)],INK,2)
        return im

    def phone(self,im,t,v):
        s=Sketch(im,v)
        s.rect((175,245,565,900),(82,94,90),INK,4,radius=35)
        s.rect((194,277,546,848),(242,236,217),INK,2,radius=14)
        s.line([(306,262),(426,262)],INK,5);s.oval((345,861,391,889),(163,174,151),INK,2)
        s.text((215,302),'Messages',28,INK)
        s.line([(213,343),(528,343)],(171,169,143),2)
        s.rect((214,367,525,515),(201,219,196),INK,2,radius=13)
        for j,line in enumerate(['Review my inbox.','Suggest what to remove.','Wait for my approval.']):
            s.text((231,383+j*36),line,25,INK)
        if t>=8.3:
            reveal=smooth((t-8.3)/.35)
            layer=Image.new('RGBA',im.size);ss=Sketch(layer,v)
            ss.rect((214,553,525,672),(235,191,166),INK,2,radius=13)
            ss.text((231,570),'Stop. Don’t delete',27,INK);ss.text((231,607),'anything.',27,INK)
            im.alpha_composite(opacity(layer,reveal))
        if t>=9.8:
            s.rect((214,707,525,782),(226,156,136),INK,2,radius=13)
            s.text((240,725),'STOP!',37,(112,52,45))

    def monitor(self,im,t,v):
        s=Sketch(im,v)
        s.poly([(661,167),(1603,167),(1643,760),(636,760)],(213,201,167),INK,4)
        s.rect((681,191,1592,714),(115,131,120),INK,3,radius=27)
        s.rect((704,216,1568,691),(245,240,221),INK,2,radius=20)
        s.text((731,235),'INBOX',34,INK)
        s.rect((1247,232,1543,279),(211,223,201),INK,2,radius=6)
        s.text((1264,239),'OpenClaw',27,INK)
        s.line([(727,291),(1541,291)],(161,166,143),2)
        phase=sum(max(0,min(t,end)-start) for start,end in [(4.4,7.55),(8.15,12.05),(12.65,13.85)])
        rows=['Meeting follow-up','Project update','Travel details','Newsletter','Shared document','Calendar invitation']
        # A scrolling inbox remains populated. These are fictional messages;
        # no all-deleted state or purported real message count is presented.
        offset=(phase*94)%55
        content=Image.new('RGBA',im.size);cs=Sketch(content,v)
        for j in range(8):
            y=309+j*55-offset
            cs.rect((737,y+8,770,y+34),(228,216,179),INK,1)
            cs.line([(738,y+8),(753,y+22),(769,y+8)],INK,1)
            cs.text((791,y+7),rows[(j+int(phase*94/55))%len(rows)],28,INK)
            cs.line([(734,y+48),(1528,y+48)],(195,195,171),1)
        mask=Image.new('L',im.size);ImageDraw.Draw(mask).rectangle((723,307,1543,609),fill=255)
        content.putalpha(Image.composite(content.getchannel('A'),Image.new('L',im.size),mask))
        im.alpha_composite(content)
        status='Review requested' if t<4.4 else 'Moving messages to Trash…' if t<13.85 else 'Agent stopped'
        s=Sketch(im,v);s.rect((723,626,1545,673),(223,222,197),INK,1,radius=7)
        s.text((739,637),status,25,(145,70,54) if 4.4<=t<13.85 else (64,111,87))
        s.poly([(1013,760),(1280,760),(1306,834),(986,834)],(166,159,128),INK,3)
        s.rect((862,831,1410,886),(215,202,167),INK,3,radius=12)
        s.rect((884,846,1190,871),(130,141,122),INK,2,radius=4)
        button=(150,168,138) if t>=13.85 else (198,101,79)
        s.rect((1217,840,1393,878),button,INK,2,radius=6)
        s.text((1305,845),'STOP AGENT' if t<13.85 else 'STOPPED',21,(251,242,215),anchor='mt')
        for xx in range(668,814,18):s.line([(xx,739),(xx+9,739)],(116,119,100),3)

    def bin(self,im,v,front=False):
        s=Sketch(im,v)
        if not front:
            s.oval((1628,724,1824,779),(90,103,91),INK,3)
            s.poly([(1636,754),(1655,938),(1798,938),(1816,754)],(174,186,157),INK,3)
        else:
            s.poly([(1636,759),(1655,938),(1798,938),(1816,759)],(174,186,157),INK,3)
            s.line([(1636,759),(1816,759)],INK,4)
            for x in [1663,1695,1727,1759,1791]:s.line([(x,782),(1727+(x-1727)*.75,919)],(121,143,118),2)
            s.rect((1662,814,1790,867),(235,226,190),INK,2,radius=5)
            s.text((1726,825),'TRASH',29,INK,anchor='mt')

    def stop_hand(self,im,t,v):
        # A stylized local intervention, not a claim about the exact UI used.
        enter=smooth((t-12.7)/1.15);leave=smooth((t-14.65)/.8)
        amount=enter*(1-leave)
        if amount<=0:return
        x=1306;y=1130+(858-1130)*amount
        s=Sketch(im,v)
        s.poly([(x-12,y+300),(x-47,y+89),(x-50,y+49),(x-37,y+39),(x-21,y+60),(x-19,y+7),(x-7,y-3),(x+5,y+6),(x+10,y+59),(x+41,y+74),(x+53,y+112),(x+36,y+300)],(225,180,139),INK,3)
        s.line([(x+10,y+59),(x+13,y+106)],(151,106,79),2)

    def inbox(self,t,v):
        if t==0:return self.classroom(15.5,v)
        im=Image.new('RGBA',(1920,1080),PAPER);s=Sketch(im,v)
        # A fresh desk/phone composition, separate from the classroom metaphor.
        s.line([(119,944),(1834,944)],(143,128,102),3)
        s.poly([(178,140),(564,146),(558,224),(181,218)],(237,225,190),INK,2)
        s.text((201,153),'Reported inbox incident',29,INK)
        s.text((201,189),'Summer Yue · Feb 2026',23,INK)
        self.monitor(im,t,v);self.phone(im,t,v);self.bin(im,v)
        if t>=4.4:
            launches=[4.4+i*.32 for i in range(8)]+[8.15+i*.30 for i in range(11)]+[12.65,12.90]
            for i,launch in enumerate(launches):
                age=t-launch
                if not 0<=age<=.90:continue
                u=age/.90
                x=1490+(1726-1490)*u;y=454+400*u-95*math.sin(math.pi*u)
                art=self.mail_envelope(v).rotate(-15+50*u+12*math.sin(i),Image.Resampling.BICUBIC,expand=True)
                scale=1-.22*u;art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
                im.alpha_composite(art,(round(x-art.width/2),round(y-art.height/2)))
        self.bin(im,v,True);self.stop_hand(im,t,v)
        if t<1.2:
            # A paper wipe signals a new example rather than another room.
            old=self.classroom(15.5,v)
            reveal=round(1920*smooth(t/1.2))
            im.alpha_composite(old.convert('RGBA').crop((reveal,0,1920,1080)),(reveal,0))
            if 0<reveal<1920:Sketch(im,v).line([(reveal,0),(reveal+9,1080)],INK,2)
        return im.convert('RGB')

    def frame(self,index,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        return self.classroom(t,v) if index<4 else self.inbox(t,v)

    def prepare(self):
        PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        for i,(_,start,end) in enumerate(BEATS):self.frame(i,end-1/30,0).save(PLAYER/f'loss-hold-{i+1:02}.jpg',quality=97)
        sheet=Image.new('RGB',(1920,1440),PAPER)
        for i,(scene,t) in enumerate([(0,3.4),(0,6.4),(0,9),(0,11.8),(0,15.4),(4,3.9),(4,6.3),(4,10.7),(4,13.8),(4,16.8)]):
            sheet.paste(self.frame(scene,t,0).resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*360))
        sheet.save(SOURCE/'storyboard.jpg',quality=97)

    def render(self):
        self.prepare();prior=json.loads((HERE/'interactive/context_compaction/manifest.json').read_text())
        assert len(prior['beats'])==29
        beats=[]
        for beat in prior['beats']:
            b=dict(beat)
            for key in ['src','hold','poster']:b[key]='../context_compaction/'+b[key]
            beats.append(b)
        for i,((label,start,end),cue) in enumerate(zip(BEATS,CUES)):
            src=f'loss-beat-{i+1:02}.mp4';hold=f'loss-hold-{i+1:02}.mp4'
            encode(PLAYER/src,(self.frame(i,start+n/30) for n in range(round((end-start)*30))))
            frames=[self.frame(i,end-1/30,v) for v in range(3)]
            encode(PLAYER/hold,(frames[n//5] for n in range(15)))
            beats.append(dict(id=f'loss-{i+1}',section='A detail missing from the summary' if i<4 else 'A reported inbox incident',label=label,src=src,hold=hold,poster=f'loss-hold-{i+1:02}.jpg',cue=cue,note=None))
        data=dict(title='Context continued: what a summary can lose',version=VERSION,ready='../context_portfolio/ready.jpg',readyVideo='../context_portfolio/ready.mp4',beats=beats)
        concat=SOURCE/'concat.txt';concat.write_text(''.join(f"file '{(PLAYER/b['src']).resolve().as_posix()}'\n" for b in beats))
        try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(HERE/'out/context_continued.mp4')],check=True)
        finally:concat.unlink()
        (PLAYER/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
        (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
    scene=ContextLoss();scene.prepare() if a.prepare_only else scene.render()
