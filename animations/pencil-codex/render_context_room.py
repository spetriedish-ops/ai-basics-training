"""An empty context classroom: pencil construction, then textured watercolor.

Keep the camera and room geometry fixed so later context objects can be added
without changing the capacity of the room. All artwork is native drawing data.
"""
from pathlib import Path
import argparse
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from render_computer_control_bonus import Sketch, encode, font

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source" / "context_room"
OUT = HERE / "out"
PLAYER = HERE / "interactive" / "context_room"
W, H, FPS = 1920, 1080, 30
PAPER = (250, 247, 239)
INK = (71, 67, 69)
DURATION = 19.5
BEATS = [("Draw the room", 0, 10.8), ("Paint it in", 10.8, DURATION)]

# One shared perspective. The bottom half stays empty for future context blocks.
A, B, C, D = (150, 130), (1770, 130), (1770, 970), (150, 970)
E, F, G, J = (500, 275), (1420, 275), (1420, 650), (500, 650)
BOARD = [(665, 356), (1195, 356), (1195, 553), (665, 553)]
WINDOW = [(219, 340), (438, 393), (438, 599), (219, 694)]
# Side entrance leaves room for a readable, side-on character walk.
DOOR = [(1570,356),(1730,307),(1730,924),(1570,777)]
DOOR_WINDOW = [(1610,413),(1691,397),(1691,566),(1610,563)]


def clamp(x):
    return max(0, min(1, x))


def stroke(points, width=3, color=INK, start=None, duration=None):
    return dict(points=points, width=width, color=color, start=start, duration=duration)


def closed(points):
    return points + [points[0]]


def geometry():
    lines = []
    # The room first, in distinct pencil strokes rather than one overall wipe.
    for points in [[A, B], [B, C], [C, D], [D, A], [E, F], [E, J],
                   [F, G], [J, G], [A, E], [B, F], [D, J], [C, G]]:
        lines.append(stroke(points, 4))
    # Baseboards, a picture rail, and the empty teaching wall.
    for points in [[(150, 939), (500, 630), (1420, 630), (1560,755)],
                   [(1741,918),(1770,939)],
                   [(150, 230), (500, 322), (1420, 322), (1770, 230)]]:
        lines.append(stroke(points, 2, (126, 113, 104)))
    lines.append(stroke(closed(BOARD), 4))
    lines.append(stroke(closed([(652,343),(1208,343),(1208,566),(652,566)]), 3))
    lines.append(stroke([(647, 567), (1214, 567), (1209, 578), (652, 578), (647, 567)], 2))
    # A pair of tall window panes on the left wall, with perspective mullions.
    lines.append(stroke(closed(WINDOW), 4))
    lines.append(stroke(closed([(208,325),(449,382),(449,611),(208,710)]), 3))
    lines.append(stroke([(328,367),(328,646)], 3))
    lines.append(stroke([(219,513),(438,496)], 3))
    lines.append(stroke([(204,711),(451,612),(462,619),(212,725),(204,711)], 2))
    # Plain closed door, with an unmarked inset window; no agent or furniture yet.
    lines.append(stroke(closed(DOOR), 3))
    lines.append(stroke([(1560,779),(1560,347),(1741,291),(1741,937)], 3))
    lines.append(stroke(closed(DOOR_WINDOW), 2))
    lines.append(stroke([(1588,603),(1603,607),(1603,614),(1588,610)], 3))
    # A familiar rectangular classroom light in the ceiling.
    lines.append(stroke(closed([(790,196),(1120,196),(1160,222),(762,222)]), 2))
    lines.append(stroke([(762,222),(762,229),(1160,229),(1160,222)], 2))
    # Floor planks converge toward a single vanishing point above the back wall.
    for x in [610, 745, 880, 1015, 1150, 1285]:
        bottom = 960 + (x - 960) * (970 - 360) / (650 - 360)
        lines.append(stroke([(x,650),(bottom,970)], 2, (154,125,103)))
    # Staggered board ends read as wood, rather than a grid of floor tiles.
    seams = [610,745,880,1015,1150,1285]
    for i,x in enumerate(seams[:-1]):
        y = [750,850,715,815,905][i]
        scale = (y-360)/(650-360)
        left, right = 960+(x-960)*scale, 960+(seams[i+1]-960)*scale
        lines.append(stroke([(left,y),(right,y)],1,(175,146,117)))
    for x,y in [(545,883),(802,780),(1115,878),(1350,810)]:
        lines.append(stroke([(x-14,y+12),(x,y),(x+6,y-15)],1,(184,151,118)))
    cursor = .45
    for item in lines:
        length = sum(math.dist(a,b) for a,b in zip(item['points'], item['points'][1:]))
        item['start'] = cursor
        item['duration'] = min(.55, max(.11, length / 3000))
        cursor += item['duration'] + .035
    # Normalize the drawing so even the last short stroke finishes before the hold.
    scale = 10.1 / cursor
    for item in lines:
        item['start'] *= scale
        item['duration'] *= scale
    return lines


LINES = geometry()


def partial(points, fraction):
    lengths = [math.dist(a,b) for a,b in zip(points,points[1:])]
    distance = sum(lengths) * fraction
    result = [points[0]]
    for a,b,length in zip(points,points[1:],lengths):
        if distance >= length:
            result.append(b)
            distance -= length
        else:
            ratio = distance / max(length, 1)
            result.append((a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio))
            break
    return result


def paper_and_texture():
    rng = np.random.default_rng(8128)
    coarse = Image.fromarray(rng.integers(0,256,(36,64),dtype=np.uint8)).resize((W,H),Image.Resampling.BICUBIC)
    broad = np.asarray(coarse.filter(ImageFilter.GaussianBlur(22)),dtype=np.float32)/255
    grain = rng.normal(0, 1.1, (H,W)).astype(np.float32)
    base = np.full((H,W,3), PAPER,dtype=np.float32)
    base += grain[:,:,None] + ((broad-.5)*2)[:,:,None]
    return Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert('RGBA'), broad, grain


class Watercolor:
    def __init__(self, points, color, begin, duration, texture, grain, opacity=.85):
        mask = Image.new('L',(W,H)); ImageDraw.Draw(mask).polygon(points,fill=255)
        # Pigment collects at a soft wet edge; paper remains visible throughout.
        smooth = np.asarray(mask.filter(ImageFilter.GaussianBlur(2)),dtype=np.float32)/255
        inner = np.asarray(mask.filter(ImageFilter.MinFilter(7)),dtype=np.float32)/255
        alpha = np.clip(smooth * (opacity*(.77+.20*texture)) + (smooth-inner)*.10,0,1)
        self.alpha = alpha
        self.begin, self.duration = begin, duration
        yy,xx = np.mgrid[:H,:W].astype(np.float32)
        xs, ys = zip(*points)
        # Broad overlapping brush passes travel down the painted surface. The
        # irregular edge is deterministic and continuous, with no particle noise.
        wave = 13*np.sin(xx/83) + 8*np.sin(xx/29 + yy/133)
        self.arrival = np.clip((yy-min(ys)+wave)/max(max(ys)-min(ys),1),0,1)
        rgba = np.empty((H,W,4),dtype=np.uint8)
        for channel in range(3):
            rgba[:,:,channel] = np.clip(color[channel]+(texture-.5)*13+grain*.7,0,255)
        rgba[:,:,3] = np.uint8(alpha*255)
        self.final = Image.fromarray(rgba)
        self.rgba = rgba

    def layer(self,t):
        p = (t-self.begin)/self.duration
        if p <= 0: return None
        if p >= 1.12: return self.final
        coverage = np.clip((p-self.arrival)*13,0,1)
        rgba = self.rgba.copy()
        rgba[:,:,3] = np.uint8(self.alpha*coverage*255)
        return Image.fromarray(rgba)


class Room:
    def __init__(self):
        self.paper, texture, grain = paper_and_texture()
        self.paint = []
        def wash(points,color,start,duration,opacity=.85):
            self.paint.append(Watercolor(points,color,start,duration,texture,grain,opacity))
        wash([A,B,F,E],(239,225,202),10.9,2.1)
        wash([A,E,J,D],(222,215,191),11.25,3)
        wash([E,F,G,J],(244,220,180),11.55,2.7)
        wash([B,C,G,F],(218,203,184),11.8,3.1)
        wash([J,G,C,D],(221,179,132),12.4,3.9)
        wash([(652,343),(1208,343),(1208,566),(652,566)],(159,116,81),13.8,1.2)
        wash(BOARD,(68,119,112),14.1,1.65,.94)
        wash(WINDOW,(182,220,229),14.35,1.4)
        wash(DOOR,(177,165,126),14.75,1.6)
        wash(DOOR_WINDOW,(175,201,200),15.2,1.1)
        wash([(790,196),(1120,196),(1160,222),(762,222)],(255,251,222),15.5,.8)
        # A warm, very faint afternoon light patch gives the empty room life.
        wash([(314,842),(595,705),(1043,743),(684,944)],(255,238,188),16.1,1.2,.38)
        self.complete_inks = [self.ink(10.8,variant) for variant in range(3)]

    def ink(self,t,variant=0):
        layer = Image.new('RGBA',(W,H))
        pencil = Sketch(layer,variant)
        for line in LINES:
            p = clamp((t-line['start'])/line['duration'])
            if p > 0:
                pencil.line(partial(line['points'],p),line['color'],line['width'],.9)
        return layer

    def frame(self,t,variant=None):
        variant=int(t*FPS)//5%3 if variant is None else variant
        image = self.paper.copy()
        for paint in self.paint:
            layer = paint.layer(t)
            if layer is not None: image.alpha_composite(layer)
        image.alpha_composite(self.complete_inks[variant] if t>=10.8 else self.ink(t,variant))
        return image.convert('RGB')


def prepare(room):
    SOURCE.mkdir(parents=True,exist_ok=True)
    PLAYER.mkdir(parents=True,exist_ok=True)
    room.frame(0).save(PLAYER/'blank.jpg',quality=96)
    for i,(_,_,end) in enumerate(BEATS):
        room.frame(end-1/FPS).save(PLAYER/f'hold-{i+1:02}.jpg',quality=97)
    room.frame(DURATION).save(SOURCE/'classroom.png')
    sheet = Image.new('RGB',(1920,780),PAPER)
    for i,t in enumerate([2.1,5.2,10.7,12.6,15.1,19.5]):
        image = room.frame(t).resize((640,360),Image.Resampling.LANCZOS)
        x,y = (i%3)*640,(i//3)*390
        sheet.paste(image,(x,y))
        ImageDraw.Draw(sheet).text((x+18,y+360),f'{t:g} seconds',font=font(22),fill=INK)
    sheet.save(SOURCE/'storyboard.jpg',quality=94)


def render(room):
    OUT.mkdir(exist_ok=True)
    master = OUT/'context_room.mp4'
    encode(master,(room.frame(i/FPS) for i in range(round(DURATION*FPS))))
    for i,(_,start,end) in enumerate(BEATS):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(master),
                        '-t',str(end-start),'-an','-c:v','libx264','-crf','18',
                        '-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',
                        str(PLAYER/f'beat-{i+1:02}.mp4')],check=True)
        # Hold the action at the beat boundary while cycling three pencil states.
        # Fifteen frames make one native, seamless 6 Hz boil loop at 30 fps.
        phase=int((end-1/FPS)*FPS)//5%3
        encode(PLAYER/f'hold-{i+1:02}.mp4',
               (room.frame(end-1/FPS,(phase+j//5)%3) for j in range(15)))
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(master),'-vf',
                    'fps=10,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
                    '-loop','0',str(OUT/'context_room.gif')],check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only',action='store_true')
    args = parser.parse_args()
    room = Room()
    prepare(room)
    if not args.prepare_only: render(room)
    print(f'Preview: {PLAYER / "index.html"}',flush=True)
