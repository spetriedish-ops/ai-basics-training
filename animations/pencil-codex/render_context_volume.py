"""Context occupies physical cube volumes in the classroom's floor perspective.

The projection fits all four existing floor corners. Cubes have world-space
footprints, supported upper layers, shaded faces, and depth-sorted occlusion.
Basketball-sized cubes leave ample room at this early stage of the conversation.
Existing cartoon illustrations identify each cube; speech bubbles stay in the
room, with no narration above or below it.
"""
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from render_context_entry import Entry,smooth,clamp
from render_context_fill import props,fitted,COLORS,INK,PAPER
from render_computer_control_bonus import Sketch,font

HERE=Path(__file__).resolve().parent
SIZE=.34
# Scale the established arrangement as a group around the back-left corner.
LAYOUT_SCALE=SIZE/1.12
VPY=229.42857142857144
FOCAL=202.5
DEPTH=.12681159420289856


def project(x,z,h=0):
    depth=1+DEPTH*z
    return (960+(x-4)*FOCAL/depth,VPY+(970-VPY-h*FOCAL)/depth)


def floor_position(px,py):
    depth=(970-VPY)/(py-VPY)
    return (4+(px-960)*depth/FOCAL,(depth-1)/DEPTH)


class VolumeFill:
    def __init__(self):
        self.entry=Entry()
        self.art=props()
        self.items=[]
        self.positions={'human':(3.016,1.1),'agent':(5.125,1.1)}
        # This modest amount of context does not yet displace the characters.
        self.moves={'human':[],'agent':[]}
        def add(name,kind,title,xyz,start,color=None,group=None):
            self.items.append(dict(name=name,kind=kind,title=title,xyz=xyz,start=start,
                                   end=start+.82,color=color or COLORS.get(kind,(229,208,163)),group=group or name))
        add('trophy','trophy',['SALES'],(.08,4.82,0),1.2,(230,198,125))
        add('team','team',['MY TEAM'],(1.22,4.82,0),3.4,(210,207,169))
        add('briefcase','briefcase',['UNC'],(.08,3.68,0),5.6,(224,184,150))
        add('keyboard','keyboard',['WRITING'],(1.22,3.68,0),7.8,(226,184,165))
        add('prompt','prompt',['YOUR','PROMPT'],(2.36,4.82,0),11.8,COLORS['prompt'])
        for name,title,x,start,color in [('rovo','ROVO',.08,15.0,'rovo'),('mail','GMAIL',1.22,17.1,'mail'),('calendar','CALENDAR',2.36,19.2,'calendar')]:
            add('tools-'+name,'manuals',[title,'TOOLS'],(x,4.82,SIZE),start,COLORS[color])
        groups=[
            ('pages','documents',['YOUR','PAGES'],23.0,[(2.36,3.68,0),(3.5,4.82,0),(3.5,4.82,SIZE)]),
            ('email','mail',['EMAIL'],25.1,[(3.5,3.68,0),(.08,2.54,0),(1.22,2.54,0)]),
            ('meetings','calendar',['MEETINGS'],27.2,[(2.36,2.54,0),(3.5,2.54,0),(4.64,4.82,0)]),
            ('replies','mail',['REPLIES'],29.3,[(4.64,3.68,0),(5.78,4.82,0),(6.92,4.82,0)]),
            ('notes','documents',['PROJECT','NOTES'],32.65,[(.08,1.4,0),(1.22,1.4,0),(2.36,1.4,0)]),
            ('more-mail','mail',['MORE','MAIL'],33.9,[(3.5,1.4,0),(4.64,2.54,0)]),
            ('past-work','documents',['PAST','WORK'],35.15,[(.08,.26,0),(1.22,.26,0),(2.36,.26,0)]),
            ('invites','calendar',['INVITES'],36.05,[(3.5,.26,0),(5.78,3.68,0)]),
            ('background','documents',['MORE','CONTEXT'],37.0,[(1.22,3.68,SIZE),(2.36,3.68,SIZE),(3.5,3.68,SIZE)])]
        for group,kind,title,start,locations in groups:
            for i,xyz in enumerate(locations):add(f'{group}-{i+1}',kind,title,xyz,start+i*.24,group=group)
        for item in self.items:
            x,z,h=item['xyz']
            if h:
                support=next(other for other in self.items if other['xyz']==(x,z,h-SIZE))
                item['start']=max(item['start'],support['end']+.08)
                item['end']=item['start']+.82
        for item in self.items:
            x,z,h=item['xyz']
            item['xyz']=(.08+(x-.08)*LAYOUT_SCALE,
                         6-SIZE-.06-(4.82-z)*LAYOUT_SCALE,h)
        # Projected final sprites are useful for later transport studies. The
        # fill animation itself draws the same cube geometry at its live height.
        for i,item in enumerate(self.items):
            images=[];offset=None
            for v in range(3):
                art,offset=self.cube(i,1,v)
                images.append(art)
            item['frames']=images;item['xy']=offset

    def inventory(self,t):return [item['name'] for item in self.items if t>=item['end']]

    def cube(self,index,p,variant):
        item=self.items[index]
        x,z,h=item['xyz']
        size=SIZE*(.12+.88*smooth(min(1,p*1.7)))
        x+=(SIZE-size)/2;z+=(SIZE-size)/2
        h+=SIZE*.54*math.sin(math.pi*clamp(p))
        pts={(a,b,c):project(x+a*size,z+b*size,h+c*size) for a in (0,1) for b in (0,1) for c in (0,1)}
        bounds=(math.floor(min(q[0] for q in pts.values()))-9,math.floor(min(q[1] for q in pts.values()))-9,
                math.ceil(max(q[0] for q in pts.values()))+10,math.ceil(max(q[1] for q in pts.values()))+10)
        left,top,right,bottom=bounds
        im=Image.new('RGBA',(right-left,bottom-top))
        sk=Sketch(im,variant)
        def face(keys,shade):
            points=[(pts[k][0]-left,pts[k][1]-top) for k in keys]
            mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(points,fill=255)
            yy,xx=np.mgrid[:im.height,:im.width]
            texture=1.3*np.sin(xx/17+yy/13)+.7*np.sin(xx/5-yy/8)
            rgba=np.zeros((im.height,im.width,4),dtype=np.uint8)
            for c in range(3):rgba[:,:,c]=np.clip(item['color'][c]+shade+texture,0,255)
            rgba[:,:,3]=np.asarray(mask)
            im.alpha_composite(Image.fromarray(rgba))
            sk.line(points+[points[0]],INK,2,.35)
        # Vertical front face, receding side, and horizontal top share vertices.
        side=1 if x+size/2<4 else 0
        face([(side,0,0),(side,1,0),(side,1,1),(side,0,1)],-27)
        face([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],24)
        face([(0,0,0),(1,0,0),(1,0,1),(0,0,1)],0)
        a=pts[(0,0,1)];b=pts[(1,0,0)]
        fw,fh=b[0]-a[0],b[1]-a[1]
        if fw>14:
            content=Image.new('RGBA',(256,256))
            if item['kind']=='prompt':
                cp=Sketch(content,variant)
                cp.rect((68,18,191,130),fill=PAPER,color=INK,width=4,radius=5)
                for yy in (45,68,91):cp.line([(86,yy),(172,yy)],INK,4)
            else:
                art=fitted(self.art[item['kind']],(186,148 if len(item['title'])==1 else 125))
                content.alpha_composite(art,((256-art.width)//2,10))
            d=ImageDraw.Draw(content)
            start=180 if len(item['title'])==1 else 150
            for row,line in enumerate(item['title']):
                fs=43
                while d.textbbox((0,0),line,font=font(fs))[2]>226:fs-=1
                d.text((128,start+row*46),line,font=font(fs),fill=INK,anchor='mt')
            content=content.resize((max(1,round(fw-4)),max(1,round(fh-4))),Image.Resampling.LANCZOS)
            im.alpha_composite(content,(round(a[0]-left+2),round(a[1]-top+2)))
        return im,(left,top)

    @lru_cache(maxsize=150)
    def resting(self,index,variant):return self.cube(index,1,variant)

    def character_state(self,name,t):
        pos=self.positions[name]
        moving=False;phase=0
        for start,end,a,b in self.moves[name]:
            if t>=end:pos=b
            elif t>=start:
                q=smooth((t-start)/(end-start))
                pos=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q)
                moving=True;phase=(t-start)/(end-start)
                break
        return pos,moving,phase

    def character(self,name,t,variant):
        pos,moving,phase=self.character_state(name,t)
        cast=self.entry.human if name=='human' else self.entry.agent
        if moving:
            # A short walk uses the existing approved cels. The human steps
            # right; the agent backs away while continuing to face its user.
            cel=[0,1,2,3,4,5,6,7,1,2][min(9,int(phase*10))]
            if name=='agent':cel=7-cel
            frames,anchor=cast.frames[cel]
            art=frames[variant]
            if name=='human':
                art=art.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                anchor=(art.width-anchor[0],anchor[1])
        elif name=='human':
            frames,anchor=self.entry.turn_frames[3];art=frames[variant]
        else:
            frames,anchor=cast.frames[8];art=frames[variant]
        scale=(1+DEPTH*1.1)/(1+DEPTH*pos[1])
        if abs(scale-1)>.001:
            art=art.resize((round(art.width*scale),round(art.height*scale)),Image.Resampling.LANCZOS)
            anchor=(anchor[0]*scale,anchor[1]*scale)
        px,py=project(*pos)
        return art,(round(px-anchor[0]),round(py-anchor[1])),pos

    def base_scene(self,t,variant):
        im=self.entry.background[variant].copy()
        # The door and its approach remain visible. Draw the open leaf behind
        # every cube and actor so it can never erase accumulated context.
        opening=smooth((t-14.5)/.5)
        self.entry.door(im,opening,variant)
        shadows=Image.new('RGBA',im.size);sd=ImageDraw.Draw(shadows)
        render=[]
        for i,item in enumerate(self.items):
            if t<item['start']:continue
            p=clamp((t-item['start'])/(item['end']-item['start']))
            x,z,h=item['xyz']
            if h==0:
                shadow=[project(x+a*SIZE+SIZE*.1,z+b*SIZE-SIZE*.035) for a,b in [(0,0),(1,0),(1,1),(0,1)]]
                sd.polygon(shadow,fill=(79,60,39,35))
            art,xy=self.resting(i,variant) if p>=1 else self.cube(i,p,variant)
            # Far to near, with upper layers last for the same footprint.
            render.append((-z-SIZE/2,h,art,xy))
        for name in ['human','agent']:
            art,xy,pos=self.character(name,t,variant)
            px,py=project(*pos)
            sd.ellipse((px-68,py-7,px+68,py+10),fill=(79,60,39,35))
            render.append((-pos[1],.1,art,xy))
        im.alpha_composite(shadows.filter(ImageFilter.GaussianBlur(4)))
        for _,_,art,xy in sorted(render,key=lambda r:(r[0],r[1])):im.alpha_composite(art,xy)
        return im

    def frame(self,t,variant=None):
        variant=int(t*30)//5%3 if variant is None else variant
        im=self.base_scene(t,variant)
        for start,end,text in [(0.6,2.9,'I work in sales.'),(3.0,5.1,"Here's my account team."),
                              (5.2,7.3,'I look after UNC.'),(7.4,9.7,'Help me write follow-ups.'),
                              (10.8,13.6,'Learn about me.\nStart with my Confluence space.')]:
            if start<=t<end:self.bubble(im,text,t,variant,'human')
        if 14.65<=t<16.7:self.bubble(im,'Which tools can I use?',t,variant,'agent')
        elif 22.6<=t<24.5:self.bubble(im,'Find pages, mail,\nand meetings.',t,variant,'agent')
        return im.convert('RGB')

    def bubble(self,im,text,t,variant,speaker):
        pos,_,_=self.character_state(speaker,t)
        initial=self.positions[speaker]
        dx=project(*pos)[0]-project(*initial)[0]
        x,y=(885+dx,427) if speaker=='human' else (1100+dx,430)
        lines=text.split('\n')
        width=max(ImageDraw.Draw(im).textbbox((0,0),line,font=font(31))[2] for line in lines)+50
        height=45*len(lines)+28
        sk=Sketch(im,variant)
        sk.rect((x,y,x+width,y+height),fill=PAPER,color=INK,width=3,radius=16)
        tail=([(x+30,y+height-3),(x-28,y+height+25),(x+7,y+height-12)] if speaker=='human' else
              [(x+52,y+height-3),(1143+dx,610),(x+89,y+height-3)])
        sk.poly(tail,fill=PAPER,color=INK,width=2)
        for i,line in enumerate(lines):sk.text((x+24,y+18+i*42),line,31,INK)
