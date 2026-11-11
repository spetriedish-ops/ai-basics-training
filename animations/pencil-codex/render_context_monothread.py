"""One conversation, a VHS work montage, then an unhurried search through it.

The floor plan leaves a measured serpentine aisle. Every cube has a supported
world-space location; actors and cubes share perspective and depth occlusion.
Only the accumulation montage receives VHS processing or accelerated action.
"""
import argparse
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.ndimage import label as connected_components, binary_dilation
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from render_context_portfolio_update import PortfolioUpdate, CHANGED, blend
from render_context_portfolio import TOPICS, PAPER, INK, icon, fittext
from render_context_entry import smooth, clamp, boil
from render_context_volume import project, floor_position, DEPTH
from render_computer_control_bonus import Sketch, encode, font

HERE=Path(__file__).resolve().parent
PLAYER=HERE/'interactive/context_monothread'
SOURCE=HERE/'source/context_monothread'
VERSION='monothread-3'
SIZE=.34
BEATS=[
    ('Stay in one conversation',0,3),
    ('Everything goes into this chat',3,5.5),
    ('Fast-forward through weeks of work',5.5,25.5),
    ('Ask about an earlier decision',25.5,28),
    ('Search the first aisle',28,37),
    ('Work around another stack',37,45.5),
    ('Find the earlier pilot decision',45.5,54.5),
]
CUES=[
    'Return to the classroom with the updated portfolio already present.',
    'One continuing conversation carries many different work topics. No new chat or context window is created.',
    'Only this montage is fast-forwarded: account work, MCP tools, calls and results, writing, research, debugging, and personal tangents accumulate. The VHS effect stops before the hold.',
    'The user asks for the pilot success measures discussed with Ted at the beginning of the montage.',
    'Normal speed. The agent follows the right-hand gap, then the first narrow aisle. The first stack is a meal plan.',
    'Normal speed. The agent goes around the left end of the next row and searches another aisle. This stack is espresso experiments.',
    'Normal speed. The agent reaches the back aisle and finds the original pilot goals: less manual follow-up and faster handoffs. The crowding makes the search harder; the information still exists here.',
]
TOPICS_WORK=[
    ('PILOT\nGOALS', (228,184,145), 4, "Let's plan the Nugget Factory pilot.", 'With Ted: less manual follow-up\nand faster handoffs.'),
    ('CRM\nTOOLS', (165,202,180), 8, 'Connect the CRM tools.', 'Loaded the tools and their instructions.'),
    ('ACCOUNT\nPLAN', (203,195,153), 1, 'Build our account plan.', 'Notes, research, and a first draft.'),
    ('EMAIL\nDRAFTS', (225,178,161), 0, 'Draft a follow-up for Jack.', 'Three drafts. One final version.'),
    ('MEETING\nNOTES', (231,207,143), 7, 'Find a slot for Ted and David.', 'Calendars checked. Notes pulled in.'),
    ('QBR\nSLIDES', (187,181,215), 3, 'Help me build the QBR deck.', 'Charts, slides, and a few more revisions.'),
    ('SALES\nFORECAST', (172,201,210), 4, 'Sanity-check this forecast.', 'Spreadsheet read. Assumptions flagged.'),
    ('COMPETITOR\nRESEARCH', (202,186,208), 3, 'Research our competitors.', 'Search results, pages, and comparisons.'),
    ('LAUNCH\nPLAN', (228,192,137), 1, 'Plan our product launch.', 'Milestones, risks, and action items.'),
    ('DEBUG\nLOGS', (164,197,183), 8, 'Why is this script failing?', 'Logs, a fix, and the test results.'),
    ('MEAL\nPLAN', (202,207,151), 9, 'Also, make a meal plan.', 'High protein. Minimal washing-up.'),
    ('ESPRESSO', (212,175,146), 9, 'One last thing: optimize my espresso.', 'A grind-size experiment. Obviously.'),
]


class MonoThread:
    def __init__(self):
        self.update=PortfolioUpdate();self.p=self.update.p;self.entry=self.p.base.entry
        self.expressions={name:self.load_expressions(name) for name in ['agent','human']}
        self.initial={'human':floor_position(1120,879),'agent':floor_position(1495,879)}
        self.human_end=(6.0,.15)
        self.items=[];self.columns=[];self.targets={}
        # The ten portfolio boxes are carried forward without another load.
        for i in range(10):
            self.items.append(dict(x=.15+(i//5)*1.1,z=5.55,h=(i%5)*SIZE,start=-10,
                                   topic=-1,original=i,label=TOPICS[i][1],color=TOPICS[i][2],kind='topic'))
        columns=[]
        for row,z in enumerate([4.85,5.19]):
            for c in range(16):
                height=(2+int(c%3==0)) if row==0 else (3+int(c%3==0))
                if row==0 and c==9:height=1
                columns.append(dict(x=.10+c*.36,z=z,height=height,band='back',c=c,row=row))
        for row,z in enumerate([3.50,3.84]):
            for c in range(15):columns.append(dict(x=1.95+c*.36,z=z,height=1+c%3 if row==0 else 2+c%2,band='middle',c=c,row=row))
        for row,z in enumerate([1.80,2.14]):
            for c in range(15):columns.append(dict(x=.10+c*.36,z=z,height=1+c%3 if row==0 else 2+c%2,band='front',c=c,row=row))
        for row,z in enumerate([.18,.54]):
            for c in range(13):columns.append(dict(x=.15+c*.36,z=z,height=3 if c in (0,12) else 1+c%2,band='foreground',c=c,row=row))
        # Three recognizable stops sit beside the actual aisles. The correct
        # pilot decision is laid down in the very first exchange.
        pilot=next(c for c in columns if c['band']=='back' and c['row']==1 and c['c']==9)
        meal=next(c for c in columns if c['band']=='front' and c['row']==1 and c['c']==2)
        coffee=next(c for c in columns if c['band']=='middle' and c['row']==0 and c['c']==11)
        pilot['height']=meal['height']=coffee['height']=3
        for c in columns:
            if c['band']=='front' and c['row']==0 and c['c']==2:c['height']=1
            if c['band']=='middle' and c['row']==0 and c['c']==13:c['height']=1
        columns.remove(pilot);columns.insert(0,pilot)
        self.columns=columns
        total=sum(c['height'] for c in columns)
        count=0;per_topic={i:0 for i in range(12)}
        for column in columns:
            support_start=-10
            for layer in range(column['height']):
                topic=min(11,int(count*12/total))
                target=None
                if layer==column['height']-1:
                    if column is pilot:topic=0;target='pilot'
                    elif column is meal:topic=10;target='meal'
                    elif column is coffee:topic=11;target='coffee'
                label,color,_,_,_=TOPICS_WORK[topic]
                kind='topic'
                if target is None:
                    kind=['topic','tools','call','result','topic','topic','topic'][count%7]
                    if kind=='tools':label='MCP\nTOOLS';color=(167,199,180)
                    elif kind=='call':label='TOOL\nCALL';color=(166,194,210)
                    elif kind=='result':label='TOOL\nRESULT';color=(193,181,208)
                start=.6+topic*1.53+per_topic[topic]*.021
                start=max(start,support_start+.10)
                support_start=start;per_topic[topic]+=1
                item=dict(x=column['x'],z=column['z'],h=layer*SIZE,start=start,topic=topic,
                          original=None,label=label,color=color,kind=kind)
                if target:self.targets[target]=len(self.items)
                self.items.append(item);count+=1
        self.montage_end=max(i['start']+.36 for i in self.items)
        assert self.montage_end<19.55,self.montage_end
        self.routes=[
            (28.35,28.95,self.initial['agent'],(6.45,1.1)),
            (28.95,30.70,(6.45,1.1),(6.45,3.0)),
            (30.70,35.05,(6.45,3.0),(1.15,3.0)),
            (37.35,38.85,(1.15,3.0),(1.15,4.5)),
            (38.85,43.30,(1.15,4.5),(5.70,4.5)),
            (45.85,46.55,(5.70,4.5),(6.45,4.5)),
            (46.55,48.10,(6.45,4.5),(6.45,6.1)),
            (48.10,50.10,(6.45,6.1),(3.9,6.1)),
        ]
        try:self.vhs_font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',34)
        except OSError:self.vhs_font=font(34)
        self.shadows=[self.floor_shadows(v) for v in range(3)]

    def load_expressions(self,name):
        """Register new cels to the approved feet, rather than their hair/arms.

        The six generated cells retain their alpha; crop/scale/line boil are
        ordinary animation assembly, with no painted-over eyes or background.
        """
        sheet=Image.open(HERE/f'assets/context_monothread/{name}-expressions-v1.png').convert('RGBA')
        variants,ref_anchor=(self.entry.agent.frames[8] if name=='agent' else self.entry.turn_frames[0])
        ref=variants[0];bounds=ref.getchannel('A').getbbox()
        def feet_center(im):
            a=np.asarray(im.getchannel('A'));ys,xs=np.where(a>100)
            bottom=ys.max()+1
            _,feet=np.where(a[max(0,bottom-round((ys.max()-ys.min())*.08)):bottom]>100)
            return (float(feet.min()+feet.max())/2,bottom)
        ref_x,ref_y=feet_center(ref)
        delta=(ref_anchor[0]-ref_x,ref_anchor[1]-ref_y)
        height=bounds[3]-bounds[1]
        cels=[]
        for i in range(6):
            cell=sheet.crop((round(i%3*sheet.width/3),round(i//3*sheet.height/2),round((i%3+1)*sheet.width/3),round((i//3+1)*sheet.height/2)))
            # Ignore near-invisible generator edge pixels when registering the
            # cel, but retain the original alpha inside its padded crop.
            ys,xs=np.where(np.asarray(cell.getchannel('A'))>100)
            if not len(xs):raise ValueError(f'Missing {name} expression {i}')
            box=(max(0,int(xs.min())-3),max(0,int(ys.min())-3),min(cell.width,int(xs.max())+4),min(cell.height,int(ys.max())+4))
            art=cell.crop(box);scale=height/art.height
            art=art.resize((round(art.width*scale),height),Image.Resampling.LANCZOS)
            fx,fy=feet_center(art)
            cels.append(([boil(art,v) for v in range(3)],(fx+delta[0],fy+delta[1])))
        return cels

    @staticmethod
    def agent_expression(t,moving):
        if moving:
            # The eyes shift between the nearby stack and the next aisle while
            # the chin hand changes contact cels. Original legs keep walking.
            return 2 if int((t-28.35)/.8)%3==0 else 3
        for start,end in [(35.05,37.35),(43.30,45.85),(50.10,1000)]:
            if start<=t<end:
                a=t-start
                if start==50.10 and a>=1.3:return 5
                if a<.16:return 0
                if a<.30:return 4
                if a<.57:return 2
                if a<.80:return 3
                if a<1.03:return 2
                return 3
        return 0

    @staticmethod
    def human_expression(t):
        if t>=51.4:return 5
        if 40.5<=t<40.65 or 46.7<=t<46.85:return 4
        if t>=38.85:return 3
        if t>=37.35:return 1
        if t>=35.05:return 2
        if 32<=t<33.1:return 1
        return 0

    @lru_cache(maxsize=120)
    def searching_walk(self,cel,expression,v):
        """Use generated thinking upper cels over the existing stepping legs.

        Both thinking poses keep the right hand above the waist, so a single
        belt seam can join them without cutting hands or duplicating limbs.
        """
        # The two very high kicks cross the belt seam, so this restrained search
        # gait uses the other approved stepping cels in a complete cycle.
        step=[0,1,2,4,5,6,2,1][cel]
        walk,wa=self.entry.agent.frames[step];body,ba=self.expressions['agent'][expression]
        old=walk[v];upper=body[v]
        leg_height=round(self.entry.agent.frames[8][0][0].height*.34)
        cut_old=max(0,round(wa[1]-leg_height))
        cut_new=min(upper.height,round(ba[1]-self.entry.agent.frames[8][0][0].height*.25+8))
        im=Image.new('RGBA',(440,400));anchor=(180,340)
        legs=old.crop((0,cut_old,old.width,old.height))
        pixels=np.asarray(legs).copy();labels,_=connected_components(pixels[:,:,3]>70)
        shoes=(pixels[:,:,:3].min(axis=2)>165)&(pixels[:,:,3]>70)
        ids=np.unique(labels[shoes]);ids=ids[ids!=0]
        mask=binary_dilation(np.isin(labels,ids),iterations=2)
        pixels[:,:,3]*=mask;legs=Image.fromarray(pixels)
        im.alpha_composite(legs,
                           (round(anchor[0]-wa[0]),round(anchor[1]-wa[1]+cut_old)))
        bob=-2*math.sin(cel*math.pi/4)**2
        im.alpha_composite(upper.crop((0,0,upper.width,cut_new)),
                           (round(anchor[0]-ba[0]),round(anchor[1]-ba[1]+bob)))
        return im,anchor

    @lru_cache(maxsize=60)
    def graphic(self, topic, kind, v):
        if kind=='topic' and topic not in (10,11):return icon(TOPICS_WORK[topic][2],v)
        im=Image.new('RGBA',(240,160));s=Sketch(im,v)
        if kind=='tools':
            s.rect((62,48,177,112),(214,229,208),INK,4,radius=14)
            for x in [89,150]:s.line([(x,48),(x,20)],INK,7)
            s.line([(120,111),(120,141),(191,141)],INK,7)
            s.text((120,66),'MCP',32,INK,anchor='mt')
        elif kind=='call':
            s.poly([(65,37),(32,80),(65,123)],None,INK,8)
            s.poly([(177,37),(210,80),(177,123)],None,INK,8)
            s.line([(91,80),(151,80)],(53,132,117),7)
            s.line([(133,63),(152,80),(133,97)],(53,132,117),7)
        elif kind=='result':
            s.rect((59,15,183,148),(250,239,213),INK,4,radius=6)
            for y in [43,67,91,115]:s.line([(77,y),(161,y)],INK,4)
            s.line([(140,122),(157,137),(195,96)],(63,136,103),8)
        elif topic==10:
            s.oval((37,70,207,143),(249,240,216),INK,4)
            for n in range(7):
                s.line([(68+n*14,98),(62+n*14,76),(76+n*14,65),(69+n*14,52)],(211,160,81),6)
            s.line([(192,22),(192,86)],INK,5)
            for x in [181,192,203]:s.line([(x,19),(x,45)],INK,3)
        else:
            s.rect((53,49,163,127),(245,234,206),INK,4,radius=14)
            s.oval((52,38,163,69),(119,81,60),INK,4)
            s.oval((164,63,206,110),None,INK,7)
            s.oval((30,127,190,146),(214,189,156),INK,3)
            for x in [83,117,147]:s.line([(x,32),(x-5,18),(x+1,5)],INK,3)
        return im

    def cube(self,index,age,v):
        item=self.items[index];x,z,h=item['x'],item['z'],item['h']
        rise=0;sx=sy=1
        if age<.24:
            ground=project(x,z,h)[1];unit=project(x,z,0)[1]-project(x,z,1)[1]
            rise=(ground+90)/unit*(1-clamp(age/.24)**2)
        elif age<.33:
            squeeze=math.sin(math.pi*(age-.24)/.09)
            sx=1+.10*squeeze;sy=1-.14*squeeze
        pts={(a,b,c):project(x+SIZE/2+(a-.5)*SIZE*sx,z+b*SIZE,h+rise+c*SIZE*sy)
             for a in (0,1) for b in (0,1) for c in (0,1)}
        l=math.floor(min(p[0] for p in pts.values()))-4;t=math.floor(min(p[1] for p in pts.values()))-4
        r=math.ceil(max(p[0] for p in pts.values()))+5;b=math.ceil(max(p[1] for p in pts.values()))+5
        im=Image.new('RGBA',(r-l,b-t));s=Sketch(im,v);col=item['color']
        def face(keys,shade):
            s.poly([(pts[k][0]-l,pts[k][1]-t) for k in keys],tuple(max(0,min(255,n+shade)) for n in col),INK,1)
        side=1 if x+SIZE/2<4 else 0
        face([(side,0,0),(side,1,0),(side,1,1),(side,0,1)],-27)
        face([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],24)
        face([(0,0,0),(1,0,0),(1,0,1),(0,0,1)],0)
        ax,ay=pts[(0,0,1)];bx,by=pts[(1,0,0)];fw=bx-ax;fh=by-ay
        art=icon(item['original'],v) if item['original'] is not None else self.graphic(item['topic'],item['kind'],v)
        im.alpha_composite(art.resize((max(1,round(fw*.91)),max(1,round(fh*.55))),Image.Resampling.LANCZOS),(round(ax-l+fw*.045),round(ay-t+fh*.04)))
        for row,line in enumerate(item['label'].split('\n')):
            fittext(s,(ax-l+fw*.5,ay-t+fh*(.64+row*.17)),line,max(5,round(fh*.17)),fw*.93)
        if item['original'] in CHANGED:
            seal=max(6,fw*.32);cx=bx-l-seal*.42;cy=ay-t+seal*.43
            s.oval((cx-seal*.55,cy-seal*.55,cx+seal*.55,cy+seal*.55),(65,137,110),INK,1)
            s.line([(cx-seal*.27,cy),(cx-seal*.06,cy+seal*.21),(cx+seal*.29,cy-seal*.24)],(255,252,232),1)
        return im,(l,t)

    @lru_cache(maxsize=1600)
    def resting(self,index,v):return self.cube(index,1,v)

    def floor_shadows(self,v):
        # Original portfolio shadows are always present. New shadows are drawn
        # only once their own floor-level cube arrives.
        im=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(im)
        for item in self.items[:10]:
            if item['h']==0:d.polygon([project(item['x']+a*SIZE,item['z']+b*SIZE) for a,b in [(0,0),(1,0),(1,1),(0,1)]],fill=(97,75,55,35))
        return im

    def agent_state(self,t):
        pos=self.initial['agent'];facing=-1
        for start,end,a,b in self.routes:
            dx=b[0]-a[0]
            direction=(1 if dx>0 else -1) if abs(dx)>.001 else facing
            if t>=end:pos=b;facing=direction
            elif t>=start:
                q=clamp((t-start)/(end-start))
                # Rounded start/stop, steady steps through the middle.
                edge=.1
                u=(q*q/(2*edge) if q<edge else q-edge/2 if q<=1-edge else 1-edge-(1-q)**2/(2*edge))/(1-edge)
                return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u),True,(t-start)*9,direction
            else:break
        return pos,False,0,facing

    def human_state(self,t):
        q=smooth((t-(5.5+11.0))/1.5)
        a=self.initial['human'];b=self.human_end
        return (a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q),0<q<1,(t-16.5)*17

    def character(self,name,t,v):
        if name=='agent':
            pos,moving,phase,facing=self.agent_state(t)
            if t>=28.35:
                expression=self.agent_expression(t,moving)
                if moving:art,anchor=self.searching_walk(int(phase)%8,expression,v)
                else:
                    frames,anchor=self.expressions['agent'][expression];art=frames[v]
            else:
                frames,anchor=self.entry.agent.frames[int(phase)%8 if moving else 8];art=frames[v]
            if facing>0:art=art.transpose(Image.Transpose.FLIP_LEFT_RIGHT);anchor=(art.width-anchor[0],anchor[1])
        else:
            pos,moving,phase=self.human_state(t)
            if moving:
                frames,anchor=self.entry.human.frames[int(phase)%8]
                art=frames[v].transpose(Image.Transpose.FLIP_LEFT_RIGHT);anchor=(art.width-anchor[0],anchor[1])
            else:
                if t>=30.65:
                    frames,anchor=self.expressions['human'][self.human_expression(t)];art=frames[v]
                else:
                    turn=3-min(3,max(0,int((t-30.1)/.15))) if t>=30.1 else 3
                    frames,anchor=self.entry.turn_frames[turn];art=frames[v]
        scale=(1+DEPTH*self.initial[name][1])/(1+DEPTH*pos[1])
        if abs(scale-1)>.001:
            art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
            anchor=(anchor[0]*scale,anchor[1]*scale)
        px,py=project(*pos)
        return art,(round(px-anchor[0]),round(py-anchor[1])),pos

    def scene(self,t,v,character_override=None):
        im=self.entry.background[v].copy();im.alpha_composite(self.shadows[v])
        mt=clamp((t-5.5)/20)*20
        shadows=Image.new('RGBA',im.size);d=ImageDraw.Draw(shadows);layers=[]
        for index,item in enumerate(self.items):
            age=mt-item['start']
            if age<0:continue
            if item['h']==0 and index>=10 and age>=.20:
                d.polygon([project(item['x']+a*SIZE,item['z']+b*SIZE) for a,b in [(0,0),(1,0),(1,1),(0,1)]],fill=(97,75,55,35))
            art,xy=self.resting(index,v) if age>=.33 else self.cube(index,age,v)
            layers.append((-item['z']-SIZE/2,item['h'],art,xy))
        for name in ['human','agent']:
            art,xy,pos=(character_override or self.character)(name,t,v);px,py=project(*pos)
            radius=68*(1+DEPTH*1.1)/(1+DEPTH*pos[1])
            d.ellipse((px-radius,py-7,px+radius,py+10),fill=(97,75,55,34))
            layers.append((-pos[1],.01,art,xy))
        if 43.30<=t<45.85:
            # The espresso inspection belongs at the box's depth, behind the
            # foreground user, rather than on top of the finished picture.
            item=self.items[self.targets['coffee']]
            inspection=Image.new('RGBA',im.size)
            self.inspect(inspection,'coffee',t,v,min(t-43.30,1.15))
            layers.append((-item['z'],item['h'],inspection,(0,0)))
        im.alpha_composite(shadows.filter(ImageFilter.GaussianBlur(3)))
        for _,_,art,xy in sorted(layers,key=lambda r:(r[0],r[1])):im.alpha_composite(art,xy)
        return im

    def speech(self,im,text,t,v,speaker='human',montage=False):
        sk=Sketch(im,v);lines=text.split('\n')
        if montage:
            x,y,width=(665,140,1050) if speaker=='human' else (1050,300,730)
            size=32;step=40;height=30+step*len(lines)
        else:
            pos=self.human_state(t)[0] if speaker=='human' else self.agent_state(t)[0]
            px,py=project(*pos)
            width=max(sk.d.textlength(line,font=font(34)) for line in lines)+58
            width=min(1000,max(400,width));x=max(175,min(1750-width,px-width*.5))
            y=135 if speaker=='human' else 260
            size=34;step=43;height=32+step*len(lines)
        pos=self.human_state(t)[0] if speaker=='human' else self.agent_state(t)[0]
        px,py=project(*pos)
        height_actor=(461 if speaker=='human' else 265)*(1+DEPTH*1.1)/(1+DEPTH*pos[1])
        tip=(px-10,py-height_actor+70)
        tx=max(x+40,min(x+width-40,tip[0]))
        sk.poly([(tx-22,y+height-3),tip,(tx+20,y+height-3)],PAPER,INK,2)
        sk.rect((x,y,x+width,y+height),PAPER,INK,3,radius=18)
        for j,line in enumerate(lines):fittext(sk,(x+26,y+17+j*step),line,size,width-52,anchor='lt')

    def inspect(self,im,key,t,v,progress,found=False):
        item=self.items[self.targets[key]];x,z,h=item['x'],item['z'],item['h']
        # A visible lens traces the correct box's front, not an arbitrary point.
        ax,ay=project(x,z,h+SIZE);bx,by=project(x+SIZE,z,h)
        sk=Sketch(im,v);col=(54,130,95) if found else (191,135,57)
        sk.rect((ax-3,ay-3,bx+3,by+3),None,col,3)
        scan=min(progress,1.15)
        cx=(ax+bx)/2+math.sin(scan*5)*8;cy=(ay+by)/2
        radius=24
        sk.oval((cx-radius,cy-radius,cx+radius,cy+radius),None,col,4)
        sk.line([(cx+17,cy+17),(cx+41,cy+43)],INK,7)
        if found:
            sk.line([(bx+8,ay+7),(bx+18,ay+18),(bx+39,ay-8)],col,5)

    def tracking(self,im,mt,strength):
        if strength<=0:return im
        original=im.convert('RGB');arr=np.asarray(original).copy()
        yy=np.arange(1080)
        # Tracking bands bend horizontal strips rather than flickering the
        # entire frame. Deterministic noise keeps exported frames reproducible.
        band=(mt*164+340)%1160-40
        second=550+85*math.sin(mt*2.7)
        mask=(abs(yy-band)<18)|(abs(yy-second)<9)
        offsets=np.where(mask,np.rint(12*np.sin(yy*.71+mt*31)+7*np.sin(mt*9)),0).astype(int)
        for y in np.where(mask)[0]:arr[y]=np.roll(arr[y],int(offsets[y]),axis=0)
        arr[::4]=(arr[::4].astype(np.float32)*.93).astype(np.uint8)
        rng=np.random.default_rng(int(mt*30)+408)
        for y in [int(band),int(second)]:
            if 2<=y<1074:
                noise=rng.integers(0,36,(5,1920,1))
                arr[y:y+5]=np.clip(arr[y:y+5].astype(np.int16)*.8+noise+25,0,255).astype(np.uint8)
        result=Image.blend(original,Image.fromarray(arr),strength).convert('RGBA')
        overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
        counter=int(mt*4135)
        labels=[((160,88),'FF >>'),((1440,88),'CHAT 01'),((1480,936),f'{counter//3600:02}:{counter//60%60:02}:{counter%60:02}')]
        for xy,text in labels:
            d.text((xy[0]+2,xy[1]+2),text,font=self.vhs_font,fill=(52,50,56,230))
            d.text(xy,text,font=self.vhs_font,fill=(255,252,229,245))
        overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*strength)))
        result.alpha_composite(overlay)
        return result

    def frame(self,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        if t<3:
            q=smooth(t/2.65)
            im=self.p.grid(29.5,v,1/(1-.5*q),revisions=[CHANGED]*4)
            self.update.monitor(im,v,220,opacity=1-smooth(t/.65))
            return im.convert('RGB')
        im=self.scene(t,v)
        if t<5.5:
            if t<3.35:im=blend(self.p.room(0,29.5,v,revisions=CHANGED),im,smooth((t-3)/.35))
            overlay=Image.new('RGBA',im.size)
            self.speech(overlay,"Let's keep all our work in this same chat.",t,v)
            self.speech(overlay,"Okay. I'll keep the context here.",t,v,'agent',True)
            overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*smooth((t-3.35)/.4))))
            im.alpha_composite(overlay)
        elif t<25.5:
            mt=t-5.5
            if mt<.35:
                im=blend(self.frame(5.49,v),im,smooth(mt/.35))
            j=min(11,max(0,int((mt-.6)/1.53)))
            if .6<=mt<19.3:
                self.speech(im,TOPICS_WORK[j][3],t,v,'human',True)
                if (mt-.6)%1.53>.45:self.speech(im,TOPICS_WORK[j][4],t,v,'agent',True)
            im=self.tracking(im,mt,smooth(mt/.45)*(1-smooth((mt-19.25)/.45)))
        elif t<28:
            overlay=Image.new('RGBA',im.size)
            self.speech(overlay,'What pilot success measures\ndid we agree on with Ted?',t,v)
            overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*smooth((t-25.5)/.4))))
            im.alpha_composite(overlay)
        else:
            # Search playback is entirely clean and at normal speed.
            if 28<=t<28.35:
                overlay=Image.new('RGBA',im.size)
                self.speech(overlay,'What pilot success measures\ndid we agree on with Ted?',t,v)
                overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*(1-smooth((t-28)/.35)))))
                im.alpha_composite(overlay)
            for start,end,key,line in [
                (35.05,37.35,'meal',"Nope. That's the meal plan."),
                (43.30,45.85,'coffee',"That's the espresso experiment…"),
                (50.10,1000,'pilot','Found it: less manual follow-up\nand faster handoffs!'),
            ]:
                if start<=t<end:
                    elapsed=t-start
                    if key!='coffee':
                        self.inspect(im,key,t,v,min(elapsed,1.15),found=key=='pilot' and elapsed>=1.3)
                    if elapsed>=1.3:self.speech(im,line,t,v,'agent')
        return im.convert('RGB')

    def prepare(self):
        PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        for j,(_,start,end) in enumerate(BEATS,1):self.frame(end-1/30,0).save(PLAYER/f'mono-hold-{j:02}.jpg',quality=97)
        times=[5.4,8,13,19,25.4,27.9,36.9,45.4,54.4]
        sheet=Image.new('RGB',(1920,1080),PAPER)
        for j,t in enumerate(times):sheet.paste(self.frame(t,0).resize((640,360),Image.Resampling.LANCZOS),((j%3)*640,(j//3)*360))
        sheet.save(SOURCE/'storyboard.jpg',quality=96)
        # Floor-plan audit: the lens stops and the entire walk remain in aisles.
        plan=Image.new('RGB',(1000,850),PAPER);d=ImageDraw.Draw(plan)
        def pt(x,z):return 70+x*105,760-z*105
        d.rectangle((*pt(0,6.5),*pt(8,0)),outline=INK,width=3)
        for c in self.columns:d.rectangle((*pt(c['x'],c['z']+SIZE),*pt(c['x']+SIZE,c['z'])),fill=(188,178,153),outline=INK)
        for _,_,a,b in self.routes:d.line([pt(*a),pt(*b)],fill=(42,133,121),width=5)
        for key,index in self.targets.items():
            item=self.items[index];px,py=pt(item['x']+.17,item['z']+.17)
            d.ellipse((px-10,py-10,px+10,py+10),fill=(184,100,66));d.text((px+14,py),key,font=font(23),fill=INK)
        plan.save(SOURCE/'floor-plan.png')
        (SOURCE/'layout.json').write_text(json.dumps({'cube_size':SIZE,'items':self.items,'routes':self.routes,'targets':self.targets},indent=2)+'\n')

    def render(self,search_only=False):
        self.prepare()
        portfolio=HERE/'interactive/context_portfolio'
        existing=json.loads((portfolio/'manifest.json').read_text())
        assert len(existing['beats'])==18,'Render the portfolio update before the mono-thread section.'
        prior=[]
        for b in existing['beats']:
            b=dict(b)
            for key in ['src','hold','poster']:b[key]='../context_portfolio/'+b[key]
            prior.append(b)
        added=[]
        for j,((label,start,end),cue) in enumerate(zip(BEATS,CUES),1):
            src=f'mono-beat-{j:02}.mp4';hold=f'mono-hold-{j:02}.mp4'
            if not search_only or j>=5:
                encode(PLAYER/src,(self.frame(start+n/30) for n in range(round((end-start)*30))))
                frames=[self.frame(end-1/30,v) for v in range(3)]
                encode(PLAYER/hold,(frames[n//5] for n in range(15)))
            else:assert (PLAYER/src).is_file() and (PLAYER/hold).is_file()
            added.append({'id':f'monothread-{j}','section':'One very long conversation','label':label,'src':src,'hold':hold,'poster':f'mono-hold-{j:02}.jpg','cue':cue,'note':None})
        data={'title':'Context continued','version':VERSION,'ready':'../context_portfolio/ready.jpg','readyVideo':'../context_portfolio/ready.mp4','beats':prior+added}
        inputs=SOURCE/'concat.txt'
        inputs.write_text(''.join(f"file '{(PLAYER/b['src']).resolve().as_posix()}'\n" for b in data['beats']))
        try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(inputs),'-c','copy','-movflags','+faststart',str(HERE/'out/context_continued.mp4')],check=True)
        finally:inputs.unlink()
        (PLAYER/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
        (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');p.add_argument('--search-only',action='store_true');a=p.parse_args()
    scene=MonoThread()
    scene.prepare() if a.prepare_only else scene.render(a.search_only)
