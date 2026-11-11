"""Render a continuous 3D paper crumple, then package the presenter preview.

Blender deforms one opaque UV-textured sheet throughout the shot. The rendered
frames are composited onto the next scene's paper; there is no image crossfade.
"""
from pathlib import Path
import argparse
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFilter
from render_computer_control_bonus import encode, font

HERE=Path(__file__).resolve().parent
OUT=HERE/'out'
SOURCE=HERE/'source/paper_transition'
PLAYER=HERE/'interactive/paper_transition'
FRAMES=SOURCE/'frames'
W,H,FPS=1920,1080,30
DURATION=4.3


class PaperTransition:
    def __init__(self,drawing,fresh):
        self.drawing=Image.open(drawing).convert('RGB').resize((W,H))
        self.fresh=Image.open(fresh).convert('RGBA').resize((W,H))

    def frame(self,t):
        frame=round(t*FPS)
        if frame<20:return self.drawing.copy()
        if frame>=110:return self.fresh.convert('RGB')
        with Image.open(FRAMES/f'{frame:04}.png') as source:
            paper=source.convert('RGBA')
        if paper.size!=(W,H):raise ValueError(f'Frame {frame} is a draft, not a full-resolution frame')
        image=self.fresh.copy()
        toss=max(0,min(1,(t-2.82)/.83))
        alpha=paper.getchannel('A').point(lambda value:round(value*.16*(1-toss)))
        shadow=Image.new('RGBA',(W,H),(59,50,41,0));shadow.putalpha(alpha)
        shifted=Image.new('RGBA',(W,H));shifted.alpha_composite(shadow,(12,18))
        image.alpha_composite(shifted.filter(ImageFilter.GaussianBlur(12)))
        image.alpha_composite(paper)
        return image.convert('RGB')


def prepare(effect):
    SOURCE.mkdir(parents=True,exist_ok=True);PLAYER.mkdir(parents=True,exist_ok=True)
    effect.drawing.save(PLAYER/'poster.jpg',quality=96)
    effect.fresh.convert('RGB').save(PLAYER/'fresh.jpg',quality=96)
    sheet=Image.new('RGB',(1920,780),(250,247,239))
    for i,t in enumerate([.5,1.25,1.85,2.65,3.13,3.85]):
        frame=effect.frame(t);frame.save(SOURCE/f'frame-{i+1:02}.jpg',quality=94)
        x,y=i%3*640,i//3*390
        sheet.paste(frame.resize((640,360),Image.Resampling.LANCZOS),(x,y))
        ImageDraw.Draw(sheet).text((x+15,y+360),f'{t:g} seconds',fill=(71,67,69),font=font(22))
    sheet.save(SOURCE/'storyboard.jpg',quality=94)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true',help='Inspect existing full-resolution 3D frames')
    parser.add_argument('--assemble-only',action='store_true',help='Reuse already rendered 3D frames')
    args=parser.parse_args()
    if not args.assemble_only and not args.prepare_only:
        blender=shutil.which('blender')
        if not blender:raise RuntimeError('Blender is required to render the continuously folded paper.')
        subprocess.run([blender,'--background','--factory-startup','--python',str(HERE/'paper_crumple_3d.py')],check=True)
    effect=PaperTransition(HERE/'source/harness_mind_map/stage_06_context.jpg',HERE/'interactive/context_room/blank.jpg')
    prepare(effect)
    if not args.prepare_only:
        master=OUT/'paper_crumple.mp4'
        encode(master,(effect.frame(i/FPS) for i in range(round(DURATION*FPS))))
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                        'fps=15,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
                        '-loop','0',str(OUT/'paper_crumple.gif')],check=True)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),
                        '-i',str(OUT/'context_room.mp4'),'-filter_complex',
                        '[0:v][1:v]concat=n=2:v=1:a=0[v]','-map','[v]',
                        '-an','-c:v','libx264','-preset','fast','-crf','18',
                        '-pix_fmt','yuv420p','-movflags','+faststart',
                        str(OUT/'paper_crumple_to_room.mp4')],check=True)
    print(f'Preview: {PLAYER / "index.html"}',flush=True)
