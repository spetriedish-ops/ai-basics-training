"""Two presenter-controlled metaphors for a constraint omitted in compaction.

Generated, transparent character cels + individually animated inventory. The
paper is an explicit context inset; the garden/laundry stage is the task world.
No deleted items reappear, and no destructive action precedes compaction.
"""
import argparse
import json
import math
import subprocess
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
from render_computer_control_bonus import Sketch, encode, font
from render_context_entry import smooth, clamp, boil

HERE=Path(__file__).resolve().parent
ASSETS=HERE/'assets/inbox_metaphors'
SOURCE=HERE/'source/inbox_metaphors'
PAPER=(250,247,235)
INK=(42,40,42)
TEAL=(77,139,132)
CORAL=(208,91,68)
GOLD=(222,176,72)
VERSION='inbox-metaphors-6'
BEATS=[('The task — and the boundary',0,4),('Leave the agent to it',4,8),
       ('More context, a longer list',8,16),('Compaction drops the boundary',16,22),
       ('An overenthusiastic cleanup',22,32),('The big reveal',32,37)]
CUES=[
 'Give the task and explicitly require approval before anything is discarded. This is a fictional metaphor, with a fictional researcher and agent.',
 'The researcher steps out for coffee. The approval instruction remains in the context list.',
 'The agent accumulates observations, conversation details and tool results. The context list grows; the original approval instruction is still present.',
 'The long context feeds into a summarizer. The shorter summary retains the task but omits the approval constraint. This illustrates the reported compaction explanation; it is not an independently verified reconstruction.',
 'With that constraint missing, the agent takes the cleanup far beyond the intended scope.',
 'The researcher returns to an empty work area. The delighted agent thinks the job is finished. Hold here as long as needed.'
]


def lerp(a,b,u):return a+(b-a)*u

def at(im,art,x,y,angle=0):
    if angle:art=art.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    im.alpha_composite(art,(round(x-art.width/2),round(y-art.height/2)))


def sheet(name,cols,rows):
    im=Image.open(ASSETS/(name+'.png')).convert('RGBA');out=[]
    if name in ('robot-poses-v1','laundry-gag-poses-v1'):
        # The ta-da glove crosses the nominal grid cell. Find complete connected
        # characters on the original sheet instead of clipping at grid boundaries.
        alpha=np.array(im.getchannel('A'))
        labels,_=ndimage.label(alpha>100)
        for r in range(rows):
            for c in range(cols):
                region=labels[round(r*im.height/rows):round((r+1)*im.height/rows),round(c*im.width/cols):round((c+1)*im.width/cols)]
                counts=np.bincount(region.ravel());counts[0]=0
                mask=ndimage.binary_dilation(labels==counts.argmax(),iterations=2)
                cel=im.copy();cel.putalpha(Image.fromarray(np.where(mask,alpha,0).astype('uint8')))
                bb=cel.getchannel('A').getbbox()
                out.append(cel.crop((max(0,bb[0]-3),max(0,bb[1]-3),min(im.width,bb[2]+3),min(im.height,bb[3]+3))))
        return out
    for r in range(rows):
        for c in range(cols):
            cel=im.crop((round(c*im.width/cols),round(r*im.height/rows),round((c+1)*im.width/cols),round((r+1)*im.height/rows)))
            if name.startswith('topiary'):
                # Ignore slivers from adjacent cells; retain the single prop's
                # connected silhouette with a two-pixel antialiased edge.
                alpha=np.array(cel.getchannel('A'))
                labels,n=ndimage.label(alpha>100)
                counts=np.bincount(labels.ravel());counts[0]=0
                main=ndimage.binary_dilation(labels==counts.argmax(),iterations=2)
                cel.putalpha(Image.fromarray(np.where(main,alpha,0).astype('uint8')))
            bb=cel.getchannel('A').point(lambda a:255 if a>100 else 0).getbbox()
            if not bb:raise ValueError(f'Empty sprite {name} {r} {c}')
            out.append(cel.crop((max(0,bb[0]-3),max(0,bb[1]-3),min(cel.width,bb[2]+3),min(cel.height,bb[3]+3))))
    return out


class Metaphor:
    def __init__(self,kind):
        self.kind=kind
        self.human=sheet('researcher-poses-v1',4,2)
        self.robot=sheet('robot-poses-v1',4,2)
        self.clothes=sheet('laundry-props-v1',4,2)
        if kind=='laundry':
            self.quiet=sheet('laundry-quiet-props-v1',2,2)
            for cel in sheet('laundry-gag-poses-v1',3,1):
                ratio=self.robot[0].height/cel.height
                self.robot.append(cel.resize((round(cel.width*ratio),self.robot[0].height),Image.Resampling.LANCZOS))
        treefile='topiary-props-v2'
        self.tree=sheet(treefile,3,2)
        self.task='SORT AND FOLD' if kind=='laundry' else 'TIDY THE TREE'
        self.rule='ASK BEFORE DISCARDING'
        self.notes=(['Laundry inventory checked','Care labels checked','Separate lights / darks','Socks: several odd pairs','Shirts grouped by color','Delicates identified','New request: tidy the rack','Tool result: inventory','Progress: sorting complete'] if kind=='laundry' else
                    ['Branches mapped','Growth measured','Envelope leaves counted','Sunny side identified','Uneven crown noted','Pruning tools inspected','New request: tidy the base','Tool result: branch map','Progress: survey complete'])
        # Each item owns one source, release time and permanent destination.
        self.inventory=[]
        if kind=='laundry':
            for i,(pos,start,width) in enumerate([((1315,665),22.5,200),((1510,659),24.6,170),((1380,854),26.8,185)]):
                self.inventory.append(dict(index=i,source=pos,start=start,width=width,angle=0,duration=1.6 if i<2 else 4.4))
        else:
            positions=[(1320,405),(1460,385),(1530,485),(1410,500),(1260,515),(1355,600),(1490,615),(1330,680)]
            for i,p in enumerate(positions):self.inventory.append(dict(index=1+i%2,source=p,start=22.5+i*.85,width=240,angle=(i%3-1)*12))

    @lru_cache(maxsize=512)
    def art(self,group,index,width,v=0):
        a=getattr(self,group)[index]
        a=a.resize((width,round(a.height*width/a.width)),Image.Resampling.LANCZOS)
        return a if group=='quiet' else boil(a,v)

    @lru_cache(maxsize=96)
    def actor_art(self,who,pose,v):
        group=self.human if who=='human' else self.robot
        scale=(495 if who=='human' else 340)/group[0].height
        a=group[pose].resize((round(group[pose].width*scale),round(group[pose].height*scale)),Image.Resampling.LANCZOS)
        # Register the unwarped cel once; ink displacement must never move its anchor.
        # Keep the robot still between intentional pose changes.
        # The human retains only local, subpixel ink movement.
        alpha=np.array(a.getchannel('A'));ys,xs=np.where(alpha>150)
        bottom=ys.max();foot=xs[ys>bottom-18]
        anchor=(float(np.median(foot)),bottom)
        return (a if who=='robot' else boil(a,v)),anchor

    def actor(self,im,who,pose,x,y,v,flip=False):
        a,(ax,ay)=self.actor_art(who,pose,v)
        if flip:a=a.transpose(Image.Transpose.FLIP_LEFT_RIGHT);ax=a.width-ax
        im.alpha_composite(a,(round(x-ax),round(y-ay)))

    def laundry_agent(self,im,t,v):
        if t>=7.65:
            self.actor(im,'robot',self.robot_pose(t),1045,949,v)
            return
        # Listen toward the taller researcher at screen left. Once she exits,
        # make a short planted pivot toward the work rather than sliding sideways.
        art,(ax,ay)=self.actor_art('robot',0,0)
        turn=smooth((t-7.2)/.45)
        if turn<.5:
            art=art.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            ax=art.width-ax
        width_scale=1-.62*math.sin(math.pi*turn)
        width=max(1,round(art.width*width_scale))
        if width!=art.width:
            scale=width/art.width
            art=art.resize((width,art.height),Image.Resampling.LANCZOS)
            ax*=scale
        im.alpha_composite(art,(round(1045-ax),round(949-ay)))

    def woman(self,im,t,v):
        x=225;pose=0;flip=False;y=947
        if 4.35<t<7.15:
            u=(t-4.35)/2.8;x=lerp(225,-265,u);pose=[1,2,3,4][int(u*20)%4];y+=3*math.sin(u*20*math.pi)
        elif 7.15<=t<32.4:return
        elif 32.4<=t<34.65:
            u=(t-32.4)/2.25;x=lerp(-265,225,u);pose=[1,2,3,4][int(u*16)%4];flip=True;y+=3*math.sin(u*16*math.pi)
        elif t>=34.65:
            pose=6 if t<35.25 or t>=35.85 else 7
        self.actor(im,'human',pose,x,y,v,flip)
        if 35.32<t<35.95:
            u=(t-35.32)/.63;s=Sketch(im,v)
            for j in range(9):
                q=clamp(u*1.45-j*.055);xx=340+q*(120+18*j);yy=535-q*(40-j*11)+q*q*140
                if 0<q<1:s.oval((xx,yy,xx+7,yy+4),(128,87,52),INK,1)

    def bubble(self,im,t,v):
        if t>=4.3:return
        s=Sketch(im,v)
        # One perimeter includes the tail, with no seam across its base.
        points=[]
        for cx,cy,start in [(410,125,-90),(410,295,0)]:
            points.extend((cx+30*math.cos(math.radians(a)),cy+30*math.sin(math.radians(a))) for a in range(start,start+91,10))
        points.extend([(306,325),(275,424),(222,325)])
        for cx,cy,start in [(90,295,90),(90,125,180)]:
            points.extend((cx+30*math.cos(math.radians(a)),cy+30*math.sin(math.radians(a))) for a in range(start,start+91,10))
        s.poly(points,PAPER,INK,3)
        lines=['Sort and fold these.','Don’t throw anything','out without asking me!'] if self.kind=='laundry' else ['Tidy up this tree.','Don’t throw anything','out without asking me!']
        for j,line in enumerate(lines):s.text((82,128+j*51),line,32,INK)

    def context(self,im,t,v):
        # Append rows with a physically extending sheet, retaining the first rule.
        growth=clamp((t-8.35)/6.5)*9
        h=157+38*growth
        feed=smooth((t-16.5)/3.8)
        paper=Image.new('RGBA',im.size);s=Sketch(paper,v)
        yy=100+575*feed;x=470;w=470
        if feed<1:
            s.poly([(x,yy),(x+w,yy+2),(x+w-3,yy+h),(x+8,yy+h-3)],(255,252,227),INK,3)
            s.text((x+24,yy+15),'CONTEXT WINDOW',34,TEAL)
            s.line([(x+22,yy+58),(x+w-23,yy+58)],TEAL,2)
            s.text((x+24,yy+67),self.task,31,INK)
            s.rect((x+15,yy+111,x+w-15,yy+148),(245,207,171),CORAL,2,radius=4)
            s.text((x+27,yy+113),self.rule,29,CORAL)
            for j,note in enumerate(self.notes):
                if growth>=j+1:s.text((x+27,yy+163+j*38),note,27,INK)
            if t>=16:
                # The entire sheet enters the slot continuously, top to bottom.
                paper=paper.crop((0,0,1920,670));im.alpha_composite(paper)
            else:im.alpha_composite(paper)
        if t<16.5:
            s=Sketch(im,v);s.rect((963,131,980,634),(230,224,203),INK,2,radius=6)
            bottom=632;top=bottom-(h/500)*495
            s.rect((966,max(134,top),977,bottom),CORAL if growth>7 else TEAL,TEAL,1,radius=3)
        # Red instruction is visibly omitted by the summarizer, not deliberately
        # discarded by the agent. It exits beside the machine and remains.
        if t>=19.25:
            u=smooth((t-19.25)/2.1);xx=lerp(495,285,u);yy=lerp(778,995,u)-120*math.sin(math.pi*u)
            strip=Image.new('RGBA',(430,48));ss=Sketch(strip,v)
            ss.rect((3,3,427,45),(245,207,171),CORAL,2,radius=3)
            ss.text((18,6),self.rule,28,CORAL)
            at(im,strip,xx,yy,lerp(0,-7,u))
        if t>=20.25:
            u=smooth((t-20.25)/1.2)
            x=lerp(775,965,u);y=lerp(760,430,u)
            card=Image.new('RGBA',(330,143));ss=Sketch(card,v)
            ss.poly([(4,4),(324,8),(325,136),(9,139)],(255,249,209),INK,3)
            ss.text((23,16),'SUMMARY',30,TEAL)
            ss.text((23,64),'TIDY THE CLOTHES' if self.kind=='laundry' else self.task,30,INK)
            at(im,card,x,y,lerp(-10,2,u))

    def machine(self,im,t,v):
        if t<16:return
        rise=smooth((t-16)/.45);shift=280*(1-rise)
        # Composite only the machine silhouette; never a paper-colored matte.
        layer=Image.new('RGBA',im.size)
        s=Sketch(layer,v);x=640;y=795+shift
        angle=(t-16.5)*7 if 16.5<t<20.4 else 0
        pivot=(913-133*smooth((t-20.4)/.6),y-14)
        s.line([(825,y-14),pivot],INK,7)
        s.oval((pivot[0]-40,pivot[1]-40,pivot[0]+40,pivot[1]+40),GOLD,INK,4)
        for j in range(3):
            angle_j=angle+j*math.pi*2/3
            endpoint=(pivot[0]+36*math.cos(angle_j),pivot[1]+36*math.sin(angle_j))
            s.line([pivot,endpoint],TEAL,5)
        s.oval((pivot[0]-7,pivot[1]-7,pivot[0]+7,pivot[1]+7),TEAL,INK,2)
        # Hand-cranked, ridiculous desktop summarizer.
        s.poly([(485,y-125),(788,y-125),(835,y-80),(535,y-80)],(222,190,116),INK,4)
        s.rect((535,y-80,835,y+110),(215,168,72),INK,4,radius=12)
        s.poly([(485,y-125),(535,y-80),(535,y+110),(485,y+70)],(181,130,66),INK,4)
        s.oval((520,y-132,775,y-104),(68,67,61),INK,3)
        s.rect((565,y-36,804,y+26),(247,229,180),INK,2,radius=5)
        s.text((588,y-31),'COMPACT',39,INK)
        for xx in [565,790]:
            s.line([(xx,y+106),(xx,y+144)],INK,6)
            s.oval((xx-12,y+139,xx+12,y+163),(91,81,60),INK,3)
        s.line([(579,y+58),(760,y+58)],INK,5)
        s.line([(490,y-11),(458,y-11)],INK,6)
        s.oval((447,y-21,470,y+2),CORAL,INK,3)
        if 16.5<t<20.4:
            for j in range(3):
                xx=587+j*68;s.line([(xx,y-155),(xx-9,y-170-8*math.sin(t*9+j))],CORAL,3)

        layer.putalpha(layer.getchannel('A').point(lambda a:255 if a else 0))
        im.alpha_composite(layer)

    def bin(self,im,v,front=False):
        s=Sketch(im,v)
        if not front:
            s.oval((1640,689,1892,758),(60,77,74),INK,4)
        else:
            s.poly([(1648,732),(1674,953),(1861,953),(1884,732)],(156,178,164),INK,4)
            for x in range(1683,1860,29):s.line([(x,762),(1768+(x-1768)*.8,931)],(92,122,112),3)
            s.line([(1647,731),(1886,731)],INK,5)
            s.rect((1705,813,1827,870),(242,224,175),INK,3,radius=5);s.text((1722,822),'TRASH',30,INK)
            # Lid sits beside the can, never mistaken for a chute.
            s.oval((1814,954,1906,982),(156,178,164),INK,3)

    def furniture(self,im,t,v):
        s=Sketch(im,v)
        if self.kind=='laundry':
            # A quiet folding table, two plain garments, and one basket.
            s.poly([(1210,754),(1590,754),(1610,775),(1190,775)],(210,183,143),INK,4)
            s.line([(1230,776),(1220,949)],INK,6);s.line([(1570,776),(1582,949)],INK,6)
            at(im,self.art('quiet',3,265,0),1380,878)
            self.bin(im,v)
        else:
            if t>=29.75:at(im,self.art('tree',3,220,v),1410,898)
            at(im,self.art('tree',4,280,v),1762,883)

    def destination(self,i):
        if self.kind=='laundry':return [(1766,767),(1790,754),(1758,717)][i]
        return (1660+(i%3)*65,835-(i//3)*66)

    def prop_status(self,item,t):
        age=t-item['start']
        if age<0:return 'source'
        if age<item.get('duration',1.0):return 'moving'
        return 'stored'

    def cleanup(self,im,t,v):
        if self.kind=='laundry':
            self.laundry_cleanup(im,t,v)
            return
        self.furniture(im,t,v)
        # Tree trunk moves independently of the canopy and ends in the basket.
        if self.kind=='topiary':
            if t<29.75:at(im,self.art('tree',0,430,v),1400,720)
            else:
                u=smooth((t-29.75)/1.3)
                trunk=self.art('tree',0,430,v)
                at(im,trunk,lerp(1400,1660,u),lerp(720,834,u)-140*math.sin(math.pi*u),-80*u)
        # Landed objects are drawn first; the container's front occludes them.
        for i,item in enumerate(self.inventory):
            if self.prop_status(item,t)=='stored':
                art=self.art('clothes' if self.kind=='laundry' else 'tree',item['index'],item['width'],v)
                at(im,art,*self.destination(i),angle=(i%3-1)*30)
        for i,item in enumerate(self.inventory):
            state=self.prop_status(item,t)
            if state=='stored':continue
            art=self.art('clothes' if self.kind=='laundry' else 'tree',item['index'],item['width'],v)
            if state=='source':at(im,art,*item['source'],angle=item['angle']);continue
            age=t-item['start'];a=item['source'];b=self.destination(i)
            if self.kind=='laundry':
                # Pick up into the windup hand, release, then fall INSIDE the can.
                grip=(951,702)
                if age<.25:
                    u=smooth(age/.25);x=lerp(a[0],grip[0],u);y=lerp(a[1],grip[1],u);angle=-25*u
                elif age<.37:
                    u=smooth((age-.25)/.12);x=lerp(grip[0],1210,u);y=lerp(grip[1],655,u)-60*math.sin(math.pi*u);angle=lerp(-25,20,u)
                else:
                    u=(age-.37)/.63;x=lerp(1210,b[0],u);y=lerp(655,b[1],u)-255*math.sin(math.pi*u);angle=lerp(20,360+(i%3-1)*30,u)
            else:
                u=age;x=lerp(a[0],b[0],u);y=lerp(a[1],b[1],u)-170*math.sin(math.pi*u);angle=lerp(item['angle'],-360+(i%3-1)*30,u)
            at(im,art,x,y,angle)
        if self.kind=='laundry':self.bin(im,v,True)
        else:
            # Crop the front of the actual basket sprite: no foliage floats over its rim.
            basket=self.art('tree',4,280,v);cut=round(basket.height*.45)
            im.alpha_composite(basket.crop((0,cut,basket.width,basket.height)),(round(1762-basket.width/2),round(883-basket.height/2+cut)))
            if t>=31:
                u=smooth((t-31)/.4);at(im,self.art('tree',5,max(1,round(105*u)),v),1410,889)

    def basket_front(self,im):
        basket=self.art('quiet',3,265,0);cut=round(basket.height*.31)
        im.alpha_composite(basket.crop((0,cut,basket.width,basket.height)),(round(1380-basket.width/2),round(878-basket.height/2+cut)))

    @staticmethod
    def trash_angle(i):
        return [-12,0,15][i]

    def trash_item(self,im,art,x,y,angle):
        # Contents enter through the opening. Everything below the front rim
        # is inside the opaque can, including pixels outside its tapered sides.
        layer=Image.new('RGBA',im.size)
        at(layer,art,x,y,angle)
        im.alpha_composite(layer.crop((0,0,1920,731)))

    def boxer_position(self,t):
        source=self.inventory[2]['source'];held=(1260,810)
        if t<27.6:
            u=smooth((t-26.8)/.8)
            return (lerp(source[0],held[0],u),lerp(source[1],held[1],u)-75*math.sin(math.pi*u),0)
        if t<29.65:return (*held,0)
        if t<30:
            u=smooth((t-29.65)/.35)
            return (lerp(held[0],1305,u),lerp(held[1],745,u),-15*u)
        u=clamp((t-30)/1.2);dest=self.destination(2)
        return (lerp(1305,dest[0],smooth(u/.72)),lerp(745,dest[1],u)-220*math.sin(math.pi*u),lerp(-15,self.trash_angle(2),u))

    def laundry_cleanup(self,im,t,v):
        self.furniture(im,t,v)
        # Show the boxers inside the basket before their separate inspection.
        if t<26.8:
            at(im,self.art('quiet',2,185,0),*self.inventory[2]['source'])
        self.basket_front(im)
        for i,item in enumerate(self.inventory):
            art=self.art('quiet',item['index'],item['width'],0)
            if i==2:
                if t>=31.2:self.trash_item(im,art,*self.destination(i),self.trash_angle(i))
                continue
            state=self.prop_status(item,t)
            if state=='stored':self.trash_item(im,art,*self.destination(i),self.trash_angle(i))
            elif state=='source':at(im,art,*item['source'])
            else:
                age=t-item['start'];a=item['source'];b=self.destination(i);grip=(951,702)
                if age<.55:
                    u=smooth(age/.55);x=lerp(a[0],grip[0],u);y=lerp(a[1],grip[1],u)-45*math.sin(math.pi*u);angle=-15*u
                elif age<.85:
                    u=smooth((age-.55)/.3);x=lerp(grip[0],1210,u);y=lerp(grip[1],655,u);angle=lerp(-15,10,u)
                else:
                    u=(age-.85)/.75;x=lerp(1210,b[0],smooth(u/.72));y=lerp(655,b[1],u)-190*math.sin(math.pi*u);angle=lerp(10,self.trash_angle(i),u)
                if age>=.85+.75*.72:self.trash_item(im,art,x,y,angle)
                else:at(im,art,x,y,angle)
        self.bin(im,v,True)

    def boxer_foreground(self,im,t,v):
        if not 26.8<=t<31.2:return
        # Held below the pinched fingers; passes in front of the source basket,
        # then behind the trash can's front rim on the descent.
        x,y,angle=self.boxer_position(t)
        art=self.art('quiet',2,185,0)
        if t>=30+1.2*.72:self.trash_item(im,art,x,y,angle)
        else:at(im,art,x,y,angle)
        if t<27.05:self.basket_front(im)
        self.bin(im,v,True)

    def shears(self,im,t,v):
        # Absurdly long blades sweep to each actual branch before closing.
        s=Sketch(im,v);targets=[(22.5+i*.85,item['source']) for i,item in enumerate(self.inventory)]+[(29.75,(1400,875))]
        target=targets[0][1];cut=targets[0][0]
        for j,(when,point) in enumerate(targets):
            if t<=when+.12:
                previous=targets[max(0,j-1)][1]
                u=smooth((t-(when-.63))/.50)
                target=tuple(lerp(a,b,u) for a,b in zip(previous,point));cut=when;break
        else:target=targets[-1][1];cut=targets[-1][0]
        opening=.05+.24*min(1,abs(t-cut)/.24)
        pivot=(1210,784);theta=math.atan2(target[1]-pivot[1],target[0]-pivot[0])
        length=math.hypot(target[0]-pivot[0],target[1]-pivot[1])+30
        for sign in [-1,1]:
            angle=theta+sign*opening;dx=math.cos(angle);dy=math.sin(angle)
            # A true isosceles triangle: broad symmetrical heel and long apex.
            half_width=46
            heel=(pivot[0]+dx*18,pivot[1]+dy*18)
            blade=[(heel[0]-dy*half_width,heel[1]+dx*half_width),
                   (pivot[0]+dx*length,pivot[1]+dy*length),
                   (heel[0]+dy*half_width,heel[1]-dx*half_width)]
            s.poly(blade,(181,199,191) if sign==-1 else (216,225,207),INK,5)
            s.line([heel,(pivot[0]+dx*length*.82,pivot[1]+dy*length*.82)],(139,164,155),2)
            hx=pivot[0]-dx*85;hy=pivot[1]-dy*85
            s.line([(hx,hy),pivot],INK,10)
            s.oval((hx-29,hy-21,hx+29,hy+21),CORAL,INK,4)
            s.oval((hx-15,hy-10,hx+15,hy+10),PAPER,INK,2)
        s.oval((pivot[0]-13,pivot[1]-13,pivot[0]+13,pivot[1]+13),GOLD,INK,3)
        if abs(t-cut)<.10:
            for j in range(3):s.line([(target[0]+j*13,target[1]-j*10),(target[0]+10+j*15,target[1]-18-j*10)],CORAL,3)

    def robot_pose(self,t):
        if 16.5<t<20.4:return 1 if int((t-16.5)*6)%2 else 7
        if self.kind=='laundry':
            if 26.8<=t<27.85:return 8
            if 27.85<=t<29.3:return 9
            if 29.3<=t<29.65:return 8
            if 29.65<=t<31.3:return 10
            for item in self.inventory[:2]:
                age=t-item['start']
                if 0<=age<item['duration']:return 2 if age<.55 else 3
        elif 22.4<t<31:
            return 4 if ((t-22.5)/.85)%1<.5 else 5
        return 6 if t>=31.3 else 0

    def frame(self,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        im=Image.new('RGBA',(1920,1080),PAPER);s=Sketch(im,v)
        Sketch(im,0).line([(55,957),(1885,957)],(171,157,124),2)
        if self.kind=='topiary':
            for x in [1180,1520,1590]:s.line([(x-12,956),(x-7,942),(x,956),(x+7,945)],TEAL,2)
            # Open paper stage; no room boundaries or decorative captions.
        self.context(im,t,v)
        self.machine(im,t,v)
        self.cleanup(im,t,v)
        # Agent is never hidden behind the task's foreground inventory.
        if self.kind=='laundry':self.laundry_agent(im,t,v)
        else:self.actor(im,'robot',self.robot_pose(t),1045,949,v)
        if self.kind=='topiary' and 22.4<t<31:self.shears(im,t,v)
        if self.kind=='laundry':self.boxer_foreground(im,t,v)
        self.woman(im,t,v);self.bubble(im,t,v)
        return im.convert('RGB')

    def prepare(self):
        dest=HERE/'interactive'/('inbox_'+self.kind);dest.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        self.frame(0,0).save(dest/'ready.jpg',quality=96)
        for i,(_,a,b) in enumerate(BEATS):self.frame(b-1/30,0).save(dest/f'hold-{i+1:02}.jpg',quality=96)
        times=[3.9,7.9,12,15.9,18.8,21.9,24.3,28.5,36.9]
        contact=Image.new('RGB',(1920,1080),PAPER)
        for i,t in enumerate(times):contact.paste(self.frame(t,0).resize((640,360)),((i%3)*640,(i//3)*360))
        contact.save(SOURCE/(self.kind+'-storyboard.jpg'),quality=96)
        self.player(dest)

    def player(self,dest):
        data=dict(title='The '+self.kind+' metaphor',version=VERSION,ready='ready.jpg',readyVideo='ready.mp4',beats=[])
        for i,((label,a,b),cue) in enumerate(zip(BEATS,CUES)):
            if self.kind=='laundry' and i==4:cue+=' Three garments go one at a time. The heart-print boxers get a lifted inspection, an ick face, a cheerful recovery and a casual toss into Trash.'
            data['beats'].append(dict(id=f'{self.kind}-{i+1}',section='The '+self.kind+' metaphor',label=label,src=f'beat-{i+1:02}.mp4',hold=f'hold-{i+1:02}.mp4',poster=f'hold-{i+1:02}.jpg',cue=cue,note=None))
        (dest/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
        (dest/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')
        base=(HERE/'interactive/context_loss/index.html').read_text()
        begin=base.index('<header>');end=base.index('<main>')
        other='topiary' if self.kind=='laundry' else 'laundry'
        title='The overhelpful laundry assistant' if self.kind=='laundry' else 'A very thorough pruning'
        header=f'<header><div><div class="eyebrow">AI Basics · context continued · {self.kind} option</div><h1>{title}</h1><p>A growing context list, a missing constraint, and one wildly overenthusiastic agent.</p></div><div class="actions"><a href="../inbox_{other}/index.html?v={VERSION}">Try the {other} version</a><a href="../../out/inbox_{self.kind}.mp4" download>Download video</a><button id="fullscreen">Fullscreen</button></div></header>\n'
        base=base[:begin]+header+base[end:]
        begin=base.index('<details class="review">');end=base.index('</details>',begin)+10
        base=base[:begin]+'<details class="review"><summary>Run of show and presenter cues</summary><p>A fictional metaphor for an approval constraint omitted during compaction. The growing paper list represents context; the task takes place on a separate open stage. Each click ends in a gently jittering hold.</p><ol id="run-of-show"></ol></details>'+base[end:]
        base=base.replace('context-loss-1',VERSION).replace('../context_portfolio/ready.jpg','ready.jpg').replace('The portfolio folder is ready to open','The task is ready to begin').replace('Ready to open the folder','Ready to begin').replace('Open the portfolio →','Begin →')
        (dest/'index.html').write_text(base)
        player=(HERE/'interactive/context_loss/player.js').read_text().replace('Ready to open the folder','Ready to begin').replace('Open the portfolio →','Begin →').replace('The portfolio folder is ready to open','The task is ready to begin').replace('Start with the folder, show all four rooms loading copies, then move into the classroom to see the context it uses.','Begin with the task and the explicit approval boundary. Each click plays one beat and then holds.')
        (dest/'player.js').write_text(player)

    def render(self):
        self.prepare();dest=HERE/'interactive'/('inbox_'+self.kind)
        frames=[self.frame(0,v) for v in range(3)];encode(dest/'ready.mp4',(frames[i//5] for i in range(15)))
        for i,(_,a,b) in enumerate(BEATS):
            encode(dest/f'beat-{i+1:02}.mp4',(self.frame(a+n/30) for n in range(round((b-a)*30))))
            frames=[self.frame(b-1/30,v) for v in range(3)]
            encode(dest/f'hold-{i+1:02}.mp4',(frames[n//5] for n in range(15)))
        concat=SOURCE/(self.kind+'-concat.txt');concat.write_text(''.join(f"file '{dest/f'beat-{i+1:02}.mp4'}'\n" for i in range(6)))
        try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(HERE/'out'/('inbox_'+self.kind+'.mp4'))],check=True)
        finally:concat.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['laundry','topiary','both'],default='both');p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
    for kind in ['laundry','topiary'] if a.kind=='both' else [a.kind]:
        scene=Metaphor(kind)
        scene.prepare() if a.prepare_only else scene.render()
