"""One literal portfolio, four independent room loads, then the classroom detail."""
from pathlib import Path
import json,math,subprocess,argparse
from PIL import Image
from render_context_portfolio import Portfolio,PLAYER,SOURCE,HERE,PAPER
from render_context_entry import boil,smooth,clamp
from render_context_volume import project
from render_computer_control_bonus import encode

ASSETS=HERE/'assets/context_portfolio'
VERSION='portfolio-5'
STARTS=[12.8+i*1.32 if i<5 else 21.8+(i-5)*1.32 for i in range(10)]
BEATS=[('A folder of text files',0,3.5),('Open identity.md',3.5,7.5),('One portfolio, four rooms',7.5,11.5),
       ('Share the first five files',11.5,20.5),('The same complete portfolio in every room',20.5,29.5),
       ('Return to our classroom',29.5,32.5),('Look closely at the context',32.5,35.5),('See the space it occupies',35.5,38.5)]
CUES=['The portfolio is a literal folder of Markdown text files.',
      'Open identity.md to show ordinary text. The sample details are fictional.',
      'The same human, four different agents and settings. One source portfolio remains on the monitor.',
      'Each room receives its own copies of communication style, projects, decisions, domain knowledge, and goals.',
      'Identity, responsibilities, relationships, systems, and preferences complete all four matching portfolios. These are separate conversations, not shared live context.',
      'Whichever agent you choose, reading the files still takes up room in that conversation’s context window.',
      'Move closer to the classroom’s existing stacks. All ten topics remain where they landed.',
      'The portfolio takes space, but plenty remains. Hold here for the next part of the narration.']
FULL=(0,0,1920,1080);CLOSE=(360,405,860,686.25)

def lerpbox(a,b,q):return tuple(x+(y-x)*q for x,y in zip(a,b))

class Portability:
    def __init__(self):
        self.base=Portfolio();self.rooms=[self.base.rooms];self.offsets=[(0,0),(0,85),(0,65),(0,50)]
        # The generated sheet has three deliberately separated gaze cels.
        sheet=Image.open(ASSETS/'human-gaze-sheet.png').convert('RGBA')
        gaze=[]
        for i in range(3):
            segment=sheet.crop((round(i*sheet.width/3),0,round((i+1)*sheet.width/3),sheet.height))
            bounds=segment.getchannel('A').getbbox()
            if bounds is None:raise ValueError('Missing gaze cel')
            cel=segment.crop(bounds);scale=461/cel.height
            cel=cel.resize((round(cel.width*scale),461),Image.Resampling.LANCZOS)
            gaze.append(([boil(cel,v) for v in range(3)],(cel.width*.47,461)))
        original=self.base.entry.turn_frames[3]
        for i,name in enumerate(['office','spaceship','wellness']):
            self.base.entry.turn_frames[3]=gaze[i]
            art=Image.open(ASSETS/f'{name}-room.png').convert('RGBA').resize((1920,1080),Image.Resampling.LANCZOS)
            variants=[]
            for v in range(3):
                room=boil(art,v)
                self.base.entry.actor(room,self.base.entry.human,8.5,1.05,4.68,1000,v)
                variants.append(room)
            self.rooms.append(variants)
        self.base.entry.turn_frames[3]=original
        self.monitors=[self.base.desktop(True,v,7,transparent=True) for v in range(3)]

    def room(self,k,t,v,crop=FULL,revisions=None):
        return self.base.room(t-k*.28,v,crop,self.rooms[k][v],self.offsets[k],7.0,STARTS,revisions=revisions)

    def hub(self,im,v,q=1,opacity=1):
        # Full screen CRT shrinks to a recognizable source at the cross-roads.
        width=round(1920+(220-1920)*q);height=round(width*1080/1920)
        art=self.monitors[v].resize((width,height),Image.Resampling.LANCZOS)
        if opacity<1:
            art=art.copy();art.putalpha(art.getchannel('A').point(lambda a:round(a*opacity)))
        im.alpha_composite(art,((1920-width)//2,(1080-height)//2))

    def delivery_motion(self,k,age,i,x,z,support):
        # One cube, one coordinate space, no clipped panel-to-panel handoff.
        # Ease to a visible crest just above the ceiling with zero velocity,
        # then accelerate from that same position into the original landing.
        flight=1.2
        if age < -flight:return None
        ox=(k%2)*960;oy=(k//2)*540
        px,ground=project(x+.17,z,0)
        unit=ground-project(x+.17,z,1)[1]
        height=(ground+self.offsets[k][1]-94)/unit
        if age>=0:
            rise,sx,sy=self.base.motion(age,height-support)
            return rise,sx,sy,0,0
        q=clamp((age+flight)/flight);ease=smooth(q)
        target=(ox+px/2,oy+47)
        source=(946,532)
        # A rounded upward sweep clears the people; the lower rooms travel
        # through the gutter before descending through their ceilings.
        arc=85 if k<2 else 24
        cx=source[0]+(target[0]-source[0])*ease
        cy=source[1]+(target[1]-source[1])*ease-arc*math.sin(math.pi*q)**2
        return height-support,1,1,(cx-target[0])*2,(cy-target[1])*2

    def grid(self,t,v,zoom=1,revisions=None):
        im=Image.new('RGBA',(1920,1080),(*PAPER,255))
        for k in range(4):
            x=round((k%2)*960*zoom);y=round((k//2)*540*zoom)
            if x>=1920 or y>=1080:continue
            art=self.rooms[k][v]
            art=art.convert('RGB').convert('RGBA')
            size=(round(960*zoom),round(540*zoom))
            im.alpha_composite(art.resize(size,Image.Resampling.LANCZOS),(x,y))
        # Draw every travelling and landed cube above the assembled rooms,
        # so crossing a quadrant boundary never hides or replaces it.
        for k in range(4):
            ox=(k%2)*1920;oy=(k//2)*1080
            if ox*zoom/2>=1920 or oy*zoom/2>=1080:continue
            crop=(-ox,-oy,3840/zoom-ox,2160/zoom-oy)
            self.base.room(min(t,29.5)-k*.28,v,crop,self.rooms[k][v],self.offsets[k],7.0,STARTS,
                           canvas=im,motion_override=lambda age,i,x,z,support,k=k:self.delivery_motion(k,age,i,x,z,support),
                           revisions=None if revisions is None else revisions[k])
        return im

    def frame(self,t,v=None):
        v=int(t*30)//5%3 if v is None else v
        if t<=7.5:return self.base.desktop(t>=4.5,v,t).convert('RGB')
        if t<11.5:
            im=self.grid(11.5,v)
            # Reveal the rooms as the cutout monitor retreats; its own paper
            # rectangle is never composited over their corners.
            reveal=smooth((t-7.5)/1.4)
            im=Image.blend(self.base.monitor.paper.convert('RGB'),im.convert('RGB'),reveal).convert('RGBA')
            self.hub(im,v,smooth((t-7.5)/3.5));return im.convert('RGB')
        if t<29.5:
            im=self.grid(t,v);self.hub(im,v);return im.convert('RGB')
        if t<32.5:
            q=smooth((t-29.5)/2.7);im=self.grid(29.5,v,1/(1-.5*q))
            if t<30.3:self.hub(im,v,1,1-smooth((t-29.5)/.8))
            return im.convert('RGB')
        amount=smooth((t-32.5)/2.7)*(1-smooth((t-35.5)/2.7))
        return self.room(0,29.5,v,lerpbox(FULL,CLOSE,amount)).convert('RGB')

    def prepare(self):
        PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
        self.frame(0,0).save(PLAYER/'ready.jpg',quality=97)
        for i,(_,start,end) in enumerate(BEATS,1):self.frame(end-1/30,0).save(PLAYER/f'hold-{i:02}.jpg',quality=97)
        sheet=Image.new('RGB',(1920,1080),PAPER)
        for j,t in enumerate([3,7,11.4,16.8,20.4,29.4,32.4,35.4,38.4]):
            sheet.paste(self.frame(t,0).resize((640,360),Image.Resampling.LANCZOS),((j%3)*640,(j//3)*360))
        sheet.save(SOURCE/'portability-storyboard.jpg',quality=95)

    def render(self):
        self.prepare()
        # Prefix new clips so the previous preview stays playable while rendering.
        for i,(_,start,end) in enumerate(BEATS,1):
            encode(PLAYER/f'shared-beat-{i:02}.mp4',(self.frame(start+j/30) for j in range(round((end-start)*30))))
            frames=[self.frame(end-1/30,v) for v in range(3)]
            encode(PLAYER/f'shared-hold-{i:02}.mp4',(frames[j//5] for j in range(15)))
        frames=[self.frame(0,v) for v in range(3)]
        encode(PLAYER/'ready.mp4',(frames[j//5] for j in range(15)))
        inputs=SOURCE/'concat.txt';inputs.write_text(''.join(f"file '{(PLAYER/f'shared-beat-{i:02}.mp4').as_posix()}'\n" for i in range(1,len(BEATS)+1)))
        try:subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(inputs),'-c','copy','-movflags','+faststart',str(HERE/'out/context_portfolio.mp4')],check=True)
        finally:inputs.unlink()
        data={'title':'One portfolio, four agents','version':VERSION,'ready':'ready.jpg','beats':[
            {'id':f'portfolio-{i}','section':'One portfolio, four agents','label':label,'src':f'shared-beat-{i:02}.mp4','hold':f'shared-hold-{i:02}.mp4','poster':f'hold-{i:02}.jpg','cue':cue,'note':None}
            for i,((label,_,_),cue) in enumerate(zip(BEATS,CUES),1)]}
        (PLAYER/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
        (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
    scene=Portability()
    scene.prepare() if args.prepare_only else scene.render()
