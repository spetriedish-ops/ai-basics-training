"""Personal context portfolio: literal .md files, then matching classroom cubes."""
from pathlib import Path
from functools import lru_cache
import math,json,argparse,subprocess
from PIL import Image,ImageDraw
from render_agent_chat import AgentChat
from render_context_entry import Entry,smooth,clamp
from render_context_volume import project
from render_computer_control_bonus import Sketch,font,encode,cursor
HERE=Path(__file__).resolve().parent
PLAYER=HERE/'interactive/context_portfolio';SOURCE=HERE/'source/context_portfolio'
INK=(65,62,65);PAPER=(250,247,239);TEAL=(49,128,118)
TOPICS=[('communication-style','COMMUNICATION\nSTYLE',(231,188,140)),('current-projects','CURRENT\nPROJECTS',(166,207,193)),('decision-log','DECISION\nLOG',(225,168,153)),('domain-knowledge','DOMAIN\nKNOWLEDGE',(188,184,218)),('goals-and-priorities','GOALS &\nPRIORITIES',(233,211,137)),('identity','IDENTITY',(170,201,218)),('role-and-responsibilities','ROLE &\nRESPONSIBILITIES',(203,195,155)),('team-and-relationships','TEAM &\nRELATIONSHIPS',(221,180,197)),('tools-and-systems','TOOLS &\nSYSTEMS',(164,202,179)),('preferences-and-constraints','PREFERENCES\n& CONSTRAINTS',(222,188,150))]
BEATS=[('A folder of text files',0,3.5),('Open identity.md',3.5,7.5),('The same room',7.5,10),('Zoom into the corner',10,12.5),('Build the first tower',12.5,20),('Build the second tower',20,27.5),('See the whole room',27.5,30.5)]
def fittext(s,xy,text,size,width,anchor='mt',color=INK):
    while s.d.textlength(text,font=font(size))>width:size-=1
    s.text(xy,text,size,color,anchor=anchor)
@lru_cache(maxsize=30)
def icon(i,v):
    im=Image.new('RGBA',(240,160));s=Sketch(im,v)
    gold=(237,193,86);blue=(104,157,177);cream=(250,236,201);red=(192,99,87)
    if i==0:
        s.poly([(39,80),(137,38),(137,114),(39,98)],gold,INK,4)
        s.rect((28,77,58,101),TEAL,INK,3,radius=6)
        s.poly([(67,99),(91,106),(80,147),(57,139)],blue,INK,3)
        s.oval((123,36,153,119),cream,INK,4)
        for a,b in [((163,45),(185,31)),((169,76),(199,76)),((163,109),(185,125))]:s.line([a,b],INK,4)
        s.text((198,5),'TL;DR',24,INK,anchor='mt')
    elif i==1:
        for x,y,c in [(55,54,blue),(120,35,gold),(185,65,red)]:
            s.line([(x,y+10),(x,133)],INK,4);s.oval((x-33,y-9,x+33,y+9),c,INK,3)
            s.rect((x-18,y-41,x+19,y-10),cream,INK,3,radius=4);s.line([(x-9,y-31),(x+10,y-31)],INK,2)
        s.line([(31,139),(208,139)],INK,4)
    elif i==2:
        s.poly([(28,74),(191,57),(214,137),(48,151)],cream,INK,3)
        s.rect((70,68,182,94),red,INK,4,radius=5);s.rect((100,42,153,72),gold,INK,3,radius=5)
        s.oval((102,16,151,53),blue,INK,4);s.text((132,113),'DECIDED',26,red,anchor='mt')
        s.line([(30,25),(43,41)],INK,3);s.line([(191,19),(181,37)],INK,3)
    elif i==3:
        s.poly([(23,66),(115,75),(115,145),(23,133)],cream,INK,4);s.poly([(115,75),(207,62),(207,132),(115,145)],PAPER,INK,4)
        for y in [89,108,124]:s.line([(38,y),(99,y+7)],blue,3);s.line([(132,y+4),(191,y-5)],blue,3)
        s.poly([(65,32),(125,10),(188,29),(123,52)],INK,INK,3);s.rect((97,47,152,65),blue,INK,3)
        s.line([(183,30),(199,58),(198,83)],gold,4)
    elif i==4:
        for r,c in [(61,red),(43,cream),(24,red),(7,gold)]:s.oval((114-r,80-r,114+r,80+r),c,INK,2)
        s.line([(114,80),(195,12)],INK,5);s.poly([(184,21),(207,17),(203,38),(188,38)],TEAL,INK,2)
        s.line([(68,138),(57,154)],INK,4);s.line([(159,138),(170,154)],INK,4)
    elif i==5:
        s.line([(98,12),(86,36),(151,36),(140,12)],blue,6);s.rect((46,32,198,151),cream,INK,4,radius=12)
        s.rect((104,43,141,50),INK,INK,2,radius=3);s.oval((69,67,122,120),gold,INK,3)
        for x in [81,107]:s.oval((x-10,81,x+10,99),PAPER,INK,3)
        s.line([(91,88),(97,88)],INK,3);s.line([(89,108),(99,112),(110,106)],INK,2)
        s.text((155,81),'ALEX',24,TEAL,anchor='mt');s.text((121,129),'HELLO!',22,INK,anchor='mt')
    elif i==6:
        s.line([(120,24),(120,148)],INK,5);s.line([(58,149),(181,149)],INK,5);s.line([(61,63),(177,63)],INK,4)
        s.oval((29,49,105,72),gold,INK,3);s.rect((45,28,89,57),gold,INK,3,radius=9)
        s.poly([(139,57),(149,25),(180,25),(192,58)],blue,INK,3);s.oval((127,56,207,71),blue,INK,3)
        s.oval((76,94,168,115),red,INK,3);s.rect((95,72,150,102),red,INK,3,radius=8)
    elif i==7:
        s.line([(55,54),(186,54),(119,115),(55,54)],red,4)
        for x,y,c in [(54,52,gold),(184,52,blue),(119,113,TEAL)]:
            s.oval((x-24,y-29,x+24,y+16),cream,INK,3);s.poly([(x-29,y+29),(x-21,y+5),(x+20,y+5),(x+29,y+29)],c,INK,3)
            s.oval((x-12,y-13,x-6,y-6),INK,INK,1);s.oval((x+7,y-13,x+13,y-6),INK,INK,1)
            s.line([(x-7,y+1),(x,y+4),(x+9,y)],INK,2)
    elif i==8:
        s.poly([(85,91),(52,16),(66,11),(112,85)],blue,INK,3);s.poly([(122,89),(175,12),(189,21),(148,105)],cream,INK,3)
        s.line([(106,87),(113,10)],INK,7);s.poly([(91,25),(93,5),(113,17),(132,5),(136,26),(114,39)],gold,INK,3)
        s.rect((47,86,202,136),red,INK,4,radius=21)
        for x in [70,179]:s.oval((x-6,105,x+6,117),cream,INK,2)
        s.line([(104,109),(144,109)],cream,4)
    else:
        s.rect((27,30,214,145),cream,INK,4,radius=12)
        for y,x in [(61,75),(91,171),(121,110)]:s.line([(45,y),(194,y)],blue,4);s.rect((x-8,y-11,x+8,y+11),gold,INK,3,radius=4)
        s.text((122,0),'NO 7 AM!',24,red,anchor='mt')
    return im
class Portfolio:
    def __init__(self):
        self.monitor=AgentChat();self.entry=Entry();self.rooms=[]
        # Stage both actors farther right, before the camera moves. The crop
        # contains only the portfolio, avoiding a mismatched enlarged outline.
        for v in range(3):
            room=self.entry.background[v].copy()
            self.entry.actor(room,self.entry.human,8.5,1.05,4.68,1120,v)
            self.entry.actor(room,self.entry.agent,8.5,2.3,3.78,1495,v)
            self.rooms.append(room)
        self.monitors=[self.monitor.paper.copy() for _ in range(3)]
        for v in range(3):self.monitors[v].alpha_composite(self.monitor.shells[v])
    def desktop(self,opened,v,t,transparent=False):
        im=self.monitor.shells[v].copy() if transparent else self.monitors[v].copy();s=Sketch(im,v)
        s.rect((294,224,1475,712),(247,246,231),INK,2,radius=24);s.rect((314,241,1454,290),(211,225,208),INK,2,radius=9)
        s.poly([(329,257),(344,257),(350,251),(372,251),(372,278),(329,278)],(234,192,99),INK,2)
        s.text((388,247),'personal-context-portfolio',34,INK);s.text((1426,255),'10 files',24,TEAL,anchor='rt')
        s.line([(921,306),(921,681)],(183,190,172),2)
        for i,(name,label,color) in enumerate(TOPICS):
            if t < .35+i*.18:continue
            y=315+i*35
            if opened and i==5:s.rect((319,y-4,905,y+30),(212,231,217),TEAL,2,radius=6)
            im.alpha_composite(icon(i,v).resize((40,27),Image.Resampling.LANCZOS),(328,y))
            s.text((379,y),name,27,INK,anchor='lt');xx=379+s.d.textlength(name,font=font(27));s.text((xx,y),'.md',27,(164,79,65),anchor='lt')
        s.rect((945,309,1436,677),(255,253,244),(185,185,164),2,radius=9)
        if opened:
            s.text((967,324),'identity.md',31,TEAL);s.line([(965,367),(1413,367)],(198,204,183),2)
            for y,line in zip([387,438,477,516,568,607],['# Identity','Name: Alex','Role: Account lead','Account: United Nugget Corp.','Outside work: coffee and','overly ambitious hobbies.']):fittext(s,(967,y),line,30,443,anchor='lt')
        else:
            s.text((1189,424),'A little about me.',38,INK,anchor='mt');s.text((1189,478),'Choose a text file to open.',29,TEAL,anchor='mt')
        s.text((323,680),'Documents  /  personal-context-portfolio',21,(110,115,100))
        if 3.5<=t<4.7:
            q=smooth((t-3.5)/.95);cursor(s,(750-80*q,620-118*q),t,[4.45])
        return im
    def camera(self,t):
        amount=smooth((t-10)/2.4)*(1-smooth((t-27.5)/2.6))
        return tuple(a+(b-a)*amount for a,b in zip((0,0,1920,1080),(360,405,860,686.25)))
    @staticmethod
    def motion(age,distance):
        """Gravity, a brief contact squash, one rebound, then a planted hold."""
        impact=.62
        if age<impact:
            q=max(0,age/impact)
            return distance*(1-q*q),1.0,1.0
        a=age-impact
        if a<.12:
            squeeze=math.sin(math.pi*a/.12)
            return 0,1+.14*squeeze,1-.19*squeeze
        if a<.38:
            q=(a-.12)/.26
            return .12*4*q*(1-q),1-.035*math.sin(math.pi*q),1+.06*math.sin(math.pi*q)
        if a<.50:
            squeeze=.045*math.sin(math.pi*(a-.38)/.12)
            return 0,1+squeeze,1-squeeze
        return 0,1,1

    def room(self,t,v,crop=None,background=None,offset=(0,0),spawn_height=2.6,starts=None,canvas=None,motion_override=None,revisions=None):
        crop=self.camera(t) if crop is None else crop;l,top,r,b=crop;scale=1920/(r-l)
        source=self.rooms[v] if background is None else background
        im=canvas if canvas is not None else (source.copy() if tuple(crop)==(0,0,1920,1080) else source.transform((1920,1080),Image.Transform.EXTENT,crop,Image.Resampling.BICUBIC))
        dx=dy=0
        def xy(x,z,h):
            px,py=project(x,z,h);return ((px+offset[0]+dx-l)*scale,(py+offset[1]+dy-top)*scale)
        dust=[]
        for i in range(10):
            start=(12.8+i*1.32 if i<5 else 20.3+(i-5)*1.32) if starts is None else starts[i]
            age=t-start
            size=.34;x=.15+(i//5)*1.10;z=5.55;support=(i%5)*size
            if motion_override is not None:
                state=motion_override(age,i,x,z,support)
                if state is None:continue
                rise,sx,sy,dx,dy=state
            else:
                if age<0:continue
                rise,sx,sy=self.motion(age,spawn_height-support)
                dx=dy=0
            h=support+rise
            # Squash pivots on the contact plane so a box never sinks through
            # the floor or the box supporting it. The front art deforms with it.
            pts={(a,c,d):xy(x+size/2+(a-.5)*size*sx,z+c*size,h+d*size*sy) for a in (0,1) for c in (0,1) for d in (0,1)}
            s=Sketch(im,v);col=TOPICS[i][2]
            if support==0 and age>=0:
                shadow=[xy(x+a*size,z+c*size,0) for a,c in [(0,0),(1,0),(1,1),(0,1)]]
                ink=Image.new('RGBA',im.size);ImageDraw.Draw(ink).polygon(shadow,fill=(97,75,55,round(35*(1-clamp(rise/spawn_height)))));im.alpha_composite(ink)
            def face(keys,delta):s.poly([pts[k] for k in keys],tuple(max(0,min(255,n+delta)) for n in col),INK,max(1,round(scale*.60)))
            face([(1,0,0),(1,1,0),(1,1,1),(1,0,1)],-27)
            face([(0,0,1),(1,0,1),(1,1,1),(0,1,1)],24)
            face([(0,0,0),(1,0,0),(1,0,1),(0,0,1)],0)
            ax,ay=pts[(0,0,1)];bx,by=pts[(1,0,0)];fw=bx-ax;fh=by-ay
            im.alpha_composite(icon(i,v).resize((max(1,round(fw*.91)),max(1,round(fh*.55))),Image.Resampling.LANCZOS),(round(ax+fw*.045),round(ay+fh*.04)))
            for row,line in enumerate(TOPICS[i][1].split('\n')):
                fittext(s,(ax+fw*.5,ay+fh*(.64+row*.17)),line,max(5,round(fh*.17)),fw*.93)
            if revisions and i in revisions:
                # A small green revision seal changes the existing box; a file
                # update does not create another box or another stack.
                seal=max(6,fw*.32);cx=bx-seal*.42;cy=ay+seal*.43
                s.oval((cx-seal*.55,cy-seal*.55,cx+seal*.55,cy+seal*.55),(65,137,110),INK,max(1,round(scale*.45)))
                s.line([(cx-seal*.27,cy),(cx-seal*.06,cy+seal*.21),(cx+seal*.29,cy-seal*.24)],(255,252,232),max(1,round(scale*.75)))
            # Small dusty lobes expand sideways from the actual contact point.
            # Finish before the next drop, and never animate inside a hold.
            elapsed=age-.62
            if 0<=elapsed<.48:dust.append((xy(x+size/2,z,support),fw,elapsed,i))
        for (cx,cy),width,elapsed,i in dust:
            q=elapsed/.48;art=Image.new('RGBA',im.size);sk=Sketch(art,v)
            for side in [-1,1]:
                for n in range(3):
                    spread=width*(.36+.48*q+n*.16)
                    px=cx+side*spread;py=cy-width*(.04+.20*q+n*.035)
                    radius=width*(.06+.065*math.sin(math.pi*q))*(1-.13*n)
                    sk.oval((px-radius,py-radius*.75,px+radius,py+radius*.75),(234,221,192),(156,139,113),max(1,round(scale*.45)))
            if q<.35:
                for side in [-1,1]:
                    sk.line([(cx+side*width*.56,cy-width*.03),(cx+side*width*.74,cy-width*.13)],(137,117,93),max(1,round(scale*.5)))
            art.putalpha(art.getchannel('A').point(lambda a:round(a*(1-q)**.65)))
            im.alpha_composite(art)
        return im
    def frame(self,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        if t<7.5:return self.desktop(t>=4.5,v,t).convert('RGB')
        if t<9.1:
            q=smooth((t-7.5)/1.6);im=Image.new('RGBA',(1920,1080),(*PAPER,255))
            im.alpha_composite(self.desktop(True,v,7),(round(-1920*q),0));im.alpha_composite(self.room(t,v),(round(1920*(1-q)),0));return im.convert('RGB')
        return self.room(t,v).convert('RGB')
    def render(self,prepare=False):
        PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        self.frame(0,0).save(PLAYER/'ready.jpg',quality=96)
        for i,(name,start,end) in enumerate(BEATS,1):self.frame(end-1/30,0).save(PLAYER/f'hold-{i:02}.jpg',quality=97)
        sheet=Image.new('RGB',(1920,720),PAPER)
        for j,t in enumerate([3,7,9.8,19.9,27.4,30.4]):sheet.paste(self.frame(t,0).resize((640,360),Image.Resampling.LANCZOS),((j%3)*640,(j//3)*360))
        sheet.save(SOURCE/'storyboard.jpg',quality=96)
        if prepare:return
        for i,(name,start,end) in enumerate(BEATS,1):
            encode(PLAYER/f'beat-{i:02}.mp4',(self.frame(start+j/30) for j in range(round((end-start)*30))))
            encode(PLAYER/f'hold-{i:02}.mp4',(self.frame(end-1/30,j//5) for j in range(15)))
        encode(PLAYER/'ready.mp4',(self.frame(0,j//5) for j in range(15)))
        cues=['A real folder with ten Markdown text files. Each topic has its own file.','Open identity.md: a .md file contains ordinary text.','Return to the established classroom with the user and their agent.','Move closer to the back-left corner to read the topic illustrations.','Communication style, current projects, decision log, domain knowledge, and goals and priorities.','Identity, role and responsibilities, team and relationships, tools and systems, and preferences and constraints.','These files contribute context when read into a conversation. Plenty of room remains.']
        data={'title':'Personal context portfolio','version':'portfolio-2','ready':'ready.jpg','beats':[{'id':f'portfolio-{i}','section':'Personal context portfolio','label':name,'src':f'beat-{i:02}.mp4','hold':f'hold-{i:02}.mp4','poster':f'hold-{i:02}.jpg','cue':cue,'note':None} for i,((name,_,_),cue) in enumerate(zip(BEATS,cues),1)]}
        (PLAYER/'manifest.json').write_text(json.dumps(data,indent=2)+'\n');(PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')
        assemble()
def assemble():
    inputs=SOURCE/'concat.txt'
    inputs.write_text(''.join(f"file '{(PLAYER/f'beat-{i:02}.mp4').as_posix()}'\n" for i in range(1,len(BEATS)+1)))
    try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(inputs),'-c','copy','-movflags','+faststart',str(HERE/'out/context_portfolio.mp4')],check=True)
    finally:inputs.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');args=p.parse_args();Portfolio().render(args.prepare_only)
