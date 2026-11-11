"""Classroom improvements, external saved memory, and an Atlassian/Rovo teaser.

Reuses the approved room and cast. Supplied brand images are copied unchanged,
then proportionally displayed on white cards. Four manual teaching beats.
"""
import argparse,json,math,os,subprocess
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageOps
from render_context_entry import Entry,smooth,clamp
from render_computer_control_bonus import Sketch,encode,font

HERE=Path(__file__).resolve().parent
PLAYER=HERE/'interactive/context_ending'
FULL=HERE/'interactive/context_continued'
SOURCE=HERE/'source/context_ending'
ASSETS=HERE/'assets/context_ending'
PAPER=(250,247,239);INK=(71,67,69);TEAL=(75,126,113);RED=(180,68,55)
VERSION='context-ending-1'
BEATS=[('More room for context',0,7),('Keep the important instruction',7,15),('Saved memory, a fresh session',15,27),('Next: Atlassian and Rovo',27,33)]
CUES=[
 'Return to the familiar classroom. The walls move outward while the people and context keep their size. Larger supported context windows offer more room; model capacity complements harness improvements.',
 'A better compaction pass condenses the context while carrying the red approval instruction into the summary. This illustrates improvement, not a guarantee that every detail always survives.',
 'Pull back to reveal a memory archive outside the active context room. Save a preference, start a fresh session, and bring a copy of that saved preference into its context. The archive stays outside; this is selective memory, not automatic recall of everything.',
 'So if these capabilities are getting better, why did I just spend two nuggets teaching you all about it? In our next nugget, we’ll unpack how and why the context conversation is so important to Atlassian, including how we use AI in our work, how agentic Rovo experiences were designed and how the Teamwork Graph fits into the conversation.'
]

def lerp(a,b,u):return a+(b-a)*u

def place(im,art,center):
 im.alpha_composite(art,(round(center[0]-art.width/2),round(center[1]-art.height/2)))

class Ending:
 def __init__(self):
  self.entry=Entry()
  self.previous=Image.open(HERE/'interactive/inbox_laundry/hold-06.jpg').convert('RGBA')
  self.logos={n:Image.open(ASSETS/(n+'-logo-supplied.png')).convert('RGBA') for n in ['atlassian','rovo']}

 @lru_cache(maxsize=6)
 def cast(self,name,v):
  frames,anchor=self.entry.turn_frames[3] if name=='human' else self.entry.agent.frames[8]
  # Fixed standing cels keep the established characters planted during holds.
  a=frames[0];scale=.8
  a=a.resize((round(a.width*scale),round(a.height*scale)),Image.Resampling.LANCZOS)
  return a,(anchor[0]*scale,anchor[1]*scale)

 def people(self,im,v):
  for name,x in [('human',1140),('agent',1440)]:
   art,(ax,ay)=self.cast(name,v)
   ImageDraw.Draw(im).ellipse((x-48,883,x+48,898),fill=(130,104,76,70))
   im.alpha_composite(art,(round(x-ax),round(892-ay)))

 def room_background(self,amount,v):
  # Change room geometry while keeping the occupants and context at fixed scale.
  art=self.entry.background[v]
  width=round(1920*lerp(.78,1,amount))
  art=art.resize((width,1080),Image.Resampling.BICUBIC)
  im=Image.new('RGBA',(1920,1080),PAPER);im.alpha_composite(art,((1920-width)//2,0))
  return im

 def board(self,im,title,v):
  s=Sketch(im,v)
  s.text((930,404),title,42,(247,242,216),anchor='mt')

 def carton(self,im,x,y,w,h,color,v,seed):
  s=Sketch(im,v);d=17
  skew=math.sin(seed*3.7)*min(7,max(0,65-h)/6)
  s.poly([(x,y),(x+d,y-d),(x+w+d,y-d),(x+w,y)],tuple(min(255,c+20) for c in color),INK,2)
  s.poly([(x+w,y),(x+w+d,y-d),(x+w+d,y+h-d),(x+w,y+h)],tuple(max(0,c-22) for c in color),INK,2)
  s.poly([(x,y),(x+w,y),(x+w+skew,y+h*.5),(x+w,y+h),(x,y+h),(x-skew,y+h*.45)],color,INK,2)
  s.line([(x+10,y+h*.27),(x+w*.5,y+h*.55),(x+w-8,y+h*.73)],tuple(max(0,c-45) for c in color),1)

 def rule_card(self,v):
  a=Image.new('RGBA',(414,52));s=Sketch(a,v)
  s.rect((2,2,410,48),(248,216,186),RED,2,radius=4)
  s.text((16,8),'ASK BEFORE DISCARDING',28,RED)
  return a

 def compactor(self,im,t,v):
  deployed=smooth((t-7.25)/.8)
  squash=smooth((t-9.0)/2.3)
  retract=smooth((t-11.65)/1.1)
  output=smooth((t-12.5)/1.0)
  s=Sketch(im,v)
  if deployed:
   # A new press frame draws on around the existing context, without replacing it.
   top=lerp(902,565,deployed)
   for x in [365,840]:s.line([(x,909),(x,top)],(93,117,107),10)
   s.line([(365,top),(840,top)],(93,117,107),12)
   s.poly([(350,890),(853,890),(873,909),(370,909)],(174,191,159),INK,3)
   s.rect((370,909,872,934),(143,165,145),INK,3,radius=5)
   for x in [395,820]:s.oval((x-10,932,x+10,950),(100,112,99),INK,2)
  colors=[(203,193,151),(171,199,182),(224,187,157),(194,184,211),(176,197,207),(229,206,154)]
  for i in range(6):
   col=i%3;row=i//3
   w=lerp(91,75,squash);h=lerp(74,30,squash)
   x=lerp(440+col*99,485+col*78,squash)
   bottom=876-row*(h+3)
   self.carton(im,x,bottom-h,w,h,colors[i],v,i)
  # The red instruction remains full-sized and readable as it travels onto the output.
  y=lerp(690,795,squash)
  if deployed:
   plate=lerp(615,790,squash)*(1-retract)+615*retract
   s.rect((574,top,628,plate-16),(156,170,155),INK,3)
   s.poly([(390,plate-13),(807,plate-13),(828,plate),(410,plate)],(192,207,180),INK,3)
   s.rect((410,plate,828,plate+11),(119,149,133),INK,2)
  place(im,self.rule_card(v),(605,y))
  if output:
   s.rect((486,843,735,884),(249,238,199),INK,2,radius=4)
   s.text((611,847),'SUMMARY',29,TEAL,anchor='mt')
   # A small check beside the preserved constraint is an example, not a universal badge.
   if output>=1:s.line([(807,793),(815,802),(834,779)],TEAL,4)

 def classroom(self,t,v,fresh=False):
  expand=smooth((t-1.8)/3.8)
  im=self.room_background(expand,v)
  self.board(im,'NEW SESSION' if fresh else 'MORE ROOM' if t<7 else 'BETTER SUMMARIES',v)
  if not fresh:self.compactor(im,t,v)
  self.people(im,v)
  if 1.8<t<5.9:
   s=Sketch(im,v);u=smooth((t-1.8)/3.8)
   for sign in [-1,1]:
    x=960+sign*lerp(640,760,u)
    s.line([(x-sign*65,1008),(x,1008)],TEAL,4)
    s.line([(x-sign*17,996),(x,1008),(x-sign*17,1020)],TEAL,4)
  return im

 def camera(self,t):
  u=smooth((t-15.1)/1.7)
  return (lerp(0,25,u),lerp(0,175,u),lerp(1,.65,u))

 def mapped(self,t,x,y):
  xx,yy,k=self.camera(t);return(xx+x*k,yy+y*k)

 @lru_cache(maxsize=3)
 def memory_file(self,v):
  im=Image.new('RGBA',(260,164));s=Sketch(im,v)
  s.poly([(3,4),(203,4),(253,48),(253,159),(3,159)],(249,241,213),INK,3)
  s.poly([(203,4),(203,48),(253,48)],(219,228,196),INK,2)
  s.text((17,57),'preferences.md',29,TEAL)
  s.text((17,106),'Concise answers',28,INK)
  return im

 def cabinet(self,im,t,v,front=False):
  u=smooth((t-16.8)/.7)
  if u<=0:return
  x=1505+510*(1-u);y=545;s=Sketch(im,v)
  opened=smooth((t-18.25)/.5)*(1-smooth((t-20.45)/.5))
  opened=max(opened,smooth((t-23.1)/.45)*(1-smooth((t-25.8)/.6)))
  pull=opened*54
  if not front:
   s.poly([(x,y),(x+55,y-30),(x+325,y-30),(x+270,y)],(179,198,180),INK,3)
   s.poly([(x+270,y),(x+325,y-30),(x+325,y+337),(x+270,y+370)],(129,157,146),INK,3)
   s.rect((x,y,x+270,y+370),(162,185,166),INK,3,radius=6)
   s.text((x+135,y+28),'SAVED MEMORY',32,INK,anchor='mt')
   s.rect((x+17,y+92,x+254,y+204),(62,84,76),INK,2)
   s.rect((x+17,y+229,x+254,y+344),(172,192,172),INK,2)
   s.rect((x+91,y+270,x+178,y+285),(223,218,177),INK,2,radius=3)
   s.line([(x+13,y+377),(x+294,y+377)],(146,130,104),2)
  else:
   # The saved source folder remains in the drawer while a copy travels back.
   if t>=20.15:
    s.poly([(x+37,y+147+pull),(x+37,y+101+pull),(x+111,y+101+pull),(x+130,y+112+pull),(x+230,y+112+pull),(x+230,y+176+pull)],(229,199,132),INK,2)
   s.poly([(x+17,y+192),(x+17,y+192+pull),(x+254,y+192+pull),(x+254,y+192)],(128,158,140),INK,2)
   front_top=lerp(y+92,y+210,opened);front_bottom=y+205+pull
   s.rect((x+17,front_top,x+254,front_bottom),(172,192,172),INK,2,radius=3)
   s.text((x+135,(front_top+front_bottom)/2-16),'Preferences',27,INK,anchor='mt')

 def memory(self,t,v):
  im=Image.new('RGBA',(1920,1080),PAPER)
  old=self.classroom(14.9,v);fresh=self.classroom(14.9,v,True)
  opening=max(smooth((t-16.9)/.4)*(1-smooth((t-19.2)/.4)),smooth((t-23.7)/.4)*(1-smooth((t-25.7)/.4)))
  self.entry.door(old,opening,v);self.entry.door(fresh,opening,v)
  wipe=smooth((t-21.4)/1.2)
  if wipe>0:
   right=round(1920*wipe);old.alpha_composite(fresh.crop((0,0,right,1080)),(0,0))
   if wipe<1:Sketch(old,v).line([(right,130),(right+8,970)],(220,207,175),5)
  x,y,k=self.camera(t);old=old.resize((round(1920*k),round(1080*k)),Image.Resampling.LANCZOS)
  im.alpha_composite(old,(round(x),round(y)))
  self.cabinet(im,t,v)
  # Save one explicit preference through the doorway to the external archive.
  if 17.15<=t<20.95:
   a=self.mapped(t,1260,690);door=self.mapped(t,1655,590)
   if t<18.8:
    u=smooth((t-17.15)/1.65);p=(lerp(a[0],door[0],u),lerp(a[1],door[1],u))
   else:
    u=smooth((t-18.8)/1.4);p=(lerp(door[0],1640,u),lerp(door[1],685,u)-55*math.sin(math.pi*u))
   file=self.memory_file(v)
   if t>=19.8:
    stow=smooth((t-19.8)/.65)
    file=file.resize((round(lerp(260,208,stow)),round(lerp(164,131,stow))),Image.Resampling.LANCZOS)
    p=(p[0],lerp(p[1],735,stow))
   layer=Image.new('RGBA',im.size);place(layer,file,p)
   if t>=20.2:
    opened=1-smooth((t-20.45)/.5)
    front_top=round(lerp(637,755,opened))
    layer.paste((0,0,0,0),(0,front_top,1920,1080))
   im.alpha_composite(layer)
  self.cabinet(im,t,v,True)
  if t>=23.25:
   door=self.mapped(t,1655,590);dest=self.mapped(t,700,790)
   if t<23.6:
    u=smooth((t-23.25)/.35);p=(1640,lerp(735,630,u))
   elif t<24.85:
    u=smooth((t-23.6)/1.25);p=(lerp(1640,door[0],u),lerp(630,door[1],u)-55*math.sin(math.pi*u))
   else:
    u=smooth((t-24.85)/1.15);p=(lerp(door[0],dest[0],u),lerp(door[1],dest[1],u))
   layer=Image.new('RGBA',im.size);place(layer,self.memory_file(v),p)
   if t<23.6:
    front_top=round(lerp(637,755,smooth((t-23.1)/.45)))
    layer.paste((0,0,0,0),(0,front_top,1920,1080))
   im.alpha_composite(layer)
  return im

 def teaser(self,t,v):
  im=Image.new('RGBA',(1920,1080),PAPER);u=smooth((t-27.1)/1.4)
  scene=self.memory(26.9,v)
  k=lerp(1,.43,u);art=scene.resize((round(1920*k),round(1080*k)),Image.Resampling.LANCZOS)
  im.alpha_composite(art,(round(lerp(0,80,u)),round(lerp(0,340,u))))
  if t>=28.65:
   a=smooth((t-28.65)/.6);layer=Image.new('RGBA',im.size);s=Sketch(layer,v)
   s.text((960,133),'What does this mean for how we work?',65,INK,anchor='mt')
   s.text((960,220),'NEXT NUGGET',29,TEAL,anchor='mt')
   # Original supplied images, unaltered; only proportional display scaling.
   for name,cx in [('atlassian',1170),('rovo',1575)]:
    s.rect((cx-175,355,cx+175,720),(255,255,255),(218,210,194),2,radius=18)
    logo=ImageOps.contain(self.logos[name],(270,270),Image.Resampling.LANCZOS)
    place(layer,logo,(cx,510))
    s.text((cx,661),'Atlassian' if name=='atlassian' else 'Rovo',39,INK,anchor='mt')
   s.text((1380,796),'AI at work  ·  Rovo  ·  Teamwork Graph',32,TEAL,anchor='mt')
   layer.putalpha(layer.getchannel('A').point(lambda value:round(value*a)))
   im.alpha_composite(layer)
  return im

 def frame(self,t,v=None):
  v=int(t*30)//5%3 if v is None else v
  if t<15:im=self.classroom(t,v)
  elif t<27:im=self.memory(t,v)
  else:im=self.teaser(t,v)
  if t<1.35:
   reveal=round(1920*smooth(t/1.35))
   im.alpha_composite(self.previous.crop((reveal,0,1920,1080)),(reveal,0))
   if 0<reveal<1920:Sketch(im,v).line([(reveal,0),(reveal+9,1080)],INK,2)
  return im.convert('RGB')

 def prepare(self):
  PLAYER.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
  self.frame(0,0).save(PLAYER/'ready.jpg',quality=97)
  times=[0,2,6.9,9.5,11.4,14.9,19.4,22.9,26.9,28,30,32.9]
  board=Image.new('RGB',(1920,1440),PAPER)
  for i,t in enumerate(times):board.paste(self.frame(t,0).resize((640,360)),((i%3)*640,(i//3)*360))
  board.save(SOURCE/'storyboard.jpg',quality=97)
  for i,(_,a,b) in enumerate(BEATS):self.frame(b-1/30,0).save(PLAYER/f'hold-{i+1:02}.jpg',quality=97)

 def ui(self,dest,data,full=False):
  dest.mkdir(parents=True,exist_ok=True)
  (dest/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
  (dest/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2)+';\n')
  template=(HERE/'interactive/inbox_laundry/index.html').read_text()
  a=template.index('<header>');b=template.index('<main>')
  other='../context_ending/index.html' if full else '../context_continued/index.html'
  download='context_continued.mp4' if full else 'context_ending.mp4'
  template=template[:a]+f'<header><div><div class="eyebrow">AI Basics · context continued</div><h1>{"The complete nugget" if full else "Getting better. What comes next?"}</h1><p>{"Portfolio → mono-thread → compaction → laundry → improvements → Atlassian and Rovo." if full else "More room, better summaries, saved memory, and the next nugget."}</p></div><div class="actions"><a href="{other}?v={VERSION}">{"Preview just the ending" if full else "Full nugget click-through"}</a><a href="../../out/{download}" download>Download video</a><button id="fullscreen">Fullscreen</button></div></header>\n'+template[b:]
  a=template.index('<details class="review">');b=template.index('</details>',a)+10
  template=template[:a]+'<details class="review"><summary>Run of show and presenter cues</summary><p><a href="../../source/context_ending/talk-track-updated.txt">Updated talk track</a> · Improvements are illustrated, not guarantees of perfect recall. Supplied logos are preserved as provided.</p><ol id="run-of-show"></ol></details>'+template[b:]
  template=template.replace('inbox-metaphors-6',VERSION).replace('src="ready.jpg"',f'src="{data["ready"]}"')
  # Versions from future laundry revisions need not change this renderer.
  import re
  template=re.sub(r'(sequence|player)\.js\?v=[^"<]+',lambda m:m.group(1)+'.js?v='+VERSION,template)
  (dest/'index.html').write_text(template)
  player=(HERE/'interactive/inbox_laundry/player.js').read_text()
  player=player.replace("inbox:'loss-5'","inbox:'laundry-1',ending:'ending-1'")
  player=player.replace('Begin with the task and the explicit approval boundary. Each click plays one beat and then holds.','Each click plays one teaching beat and then holds for your narration.')
  (dest/'player.js').write_text(player)

 def render(self):
  self.prepare();frames=[self.frame(0,v) for v in range(3)]
  encode(PLAYER/'ready.mp4',(frames[n//5] for n in range(15)))
  beats=[]
  for i,((label,a,b),cue) in enumerate(zip(BEATS,CUES)):
   encode(PLAYER/f'beat-{i+1:02}.mp4',(self.frame(a+n/30) for n in range(round((b-a)*30))))
   frames=[self.frame(b-1/30,v) for v in range(3)]
   encode(PLAYER/f'hold-{i+1:02}.mp4',(frames[n//5] for n in range(15)))
   beats.append(dict(id=f'ending-{i+1}',section='Getting better — and what comes next',label=label,src=f'beat-{i+1:02}.mp4',hold=f'hold-{i+1:02}.mp4',poster=f'hold-{i+1:02}.jpg',cue=cue,note=None))
  data=dict(title='Context continued: getting better',version=VERSION,ready='ready.jpg',readyVideo='ready.mp4',beats=beats)
  self.ui(PLAYER,data);self.concat(PLAYER,beats,HERE/'out/context_ending.mp4')
  # Keep the approved classroom loss example; replace the rejected four inbox
  # clips with the chosen laundry treatment, then append the new conclusion.
  allbeats=[]
  for folder,selected in [(HERE/'interactive/context_loss',slice(0,33)),(HERE/'interactive/inbox_laundry',slice(None)),(PLAYER,slice(None))]:
   manifest=json.loads((folder/'manifest.json').read_text())
   for original in manifest['beats'][selected]:
    beat=dict(original)
    for key in ['src','hold','poster']:beat[key]=os.path.relpath((folder/beat[key]).resolve(),FULL)
    allbeats.append(beat)
  assert len(allbeats)==43
  data=dict(title='Context continued — complete nugget',version=VERSION,ready='../context_portfolio/ready.jpg',readyVideo='../context_portfolio/ready.mp4',beats=allbeats)
  self.ui(FULL,data,True);self.concat(FULL,allbeats,HERE/'out/context_continued.mp4')

 def concat(self,folder,beats,output):
  path=SOURCE/'concat.txt';path.write_text(''.join(f"file '{(folder/b['src']).resolve()}'\n" for b in beats))
  try:
   subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(path),'-c','copy','-movflags','+faststart',str(output)],check=True)
   # Keep the convenient combined download small enough for ordinary GitHub
   # storage. Individual action/hold files remain the original quality.
   if output.stat().st_size>90*1024*1024:
    smaller=output.with_name(output.stem+'-compact.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(output),'-an','-c:v','libx264','-preset','medium','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(smaller)],check=True)
    if smaller.stat().st_size>=100*1024*1024:raise RuntimeError('Combined download still exceeds GitHub file limit')
    smaller.replace(output)
  finally:path.unlink()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
 scene=Ending();scene.prepare() if a.prepare_only else scene.render()
