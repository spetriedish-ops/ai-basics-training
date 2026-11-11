#!/usr/bin/env python3
"""Check visibility boundaries, encoded access checks, formats, and native holds."""
import json
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
import render_mall_routes as scene

HERE=Path(__file__).resolve().parent


def require(ok,message):
    if not ok:raise AssertionError(message)
    print(f'PASS: {message}',flush=True)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
                                               '-show_format','-of','json',str(path)]))


def frame(path,t):
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),
        '-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])
    return np.frombuffer(data,np.uint8).reshape(1080,1920,3).astype(np.int16)


def main():
    master=HERE/'out/mall_routes.mp4'
    info=probe(master);stream=info['streams'][0]
    require(stream['codec_name']=='h264' and (stream['width'],stream['height'])==(1920,1080)
            and Fraction(stream['r_frame_rate'])==30,'Master is 1080p H.264 at 30 fps')
    require(len(info['streams'])==1 and abs(float(info['format']['duration'])-46)<.04,
            'Master is silent and 46 seconds')
    require((HERE/'out/mall_routes.gif').stat().st_size<10_000_000,'GIF is under 10 MB')
    for i,duration in enumerate([10,6,8,8,8,6],1):
        clip=HERE/'interactive/stages'/f'{i:02}.mp4';hold=HERE/'interactive/holds'/f'{i:02}.mp4'
        require(abs(float(probe(clip)['format']['duration'])-duration)<.04,f'Beat {i}: duration is correct')
        require(abs(float(probe(hold)['format']['duration'])-3)<.04,f'Beat {i}: dedicated three-second hold')
        last,first,later=frame(clip,duration-.034),frame(hold,0),frame(hold,1)
        require(float(np.abs(last-first).mean())<.8,f'Beat {i}: hold preserves the completed action')
        require(float(np.abs(first-later).mean())<.3,f'Beat {i}: gentle ambient motion only')
    # Actual door pixels change only after the permission-check phase.
    door=np.s_[740:860,1486:1511,:]
    closed=[];opened=[]
    for name,check,allowed in [('MCP',19.7,21.2),('CLI',27.7,29.2),('API',35.7,37.2)]:
        a,b=frame(master,check),frame(master,allowed)
        delta=float(np.abs(a[door]-b[door]).mean())
        require(delta>8,f'{name}: shutter opens after the check ({delta:.1f} pixel delta)')
        closed.append(a[door]);opened.append(b[door])
    require(all(float(np.abs(closed[0]-x).mean())<2 for x in closed[1:]),
            'All three routes use the same locked endpoint')
    require(all(float(np.abs(opened[0]-x).mean())<2 for x in opened[1:]),
            'All three routes receive the same endpoint result')
    # This is the teaching boundary that v1 violated. Check geometry including
    # the moving packet's outline, then compare actual delivered video pixels.
    x0,y0,x1,y1=scene.BACKSTAGE
    require(all(x0+35<x<x1-35 and y0+28<y<y1-28 for route in scene.ROUTES for x,y in route),
            'Every backend path and packet stays inside the hidden corridor')
    require(all(y<scene.PUBLIC[3] for x,y in scene.PUBLIC_ROUTE),
            'Computer-control path stays on the public side')
    public=np.s_[295:627,90:1828,:]
    before=frame(master,14.5)[public]
    for name,t in [('MCP',17.6),('MCP return',21.2),('CLI',25.6),('CLI return',29.2),('API',33.6),('API return',37.2)]:
        delta=float(np.abs(frame(master,t)[public]-before).mean())
        require(delta<.4,f'{name}: no storefront activity ({delta:.3f} pixel delta)')
    # Source comparison is exact, so compression cannot mask an accidental cursor.
    base=np.asarray(scene.compose(14.5))[public]
    require(all(np.array_equal(base,np.asarray(scene.compose(t))[public]) for t in np.arange(16,40,.5)),
            'Storefront pixels are identical throughout all three backend calls')
    cursor_area=np.s_[400:610,270:1170,:]
    require(float(np.abs(frame(master,2.8)[cursor_area]-frame(master,7.6)[cursor_area]).mean())>1,
            'Computer control visibly moves the cursor and opens an issue')
    hidden=np.s_[704:908,367:1350,:]
    require(float(np.abs(frame(master,2.8)[hidden]-frame(master,17.6)[hidden]).mean())>7,
            'Audience cutaway visibly reveals the service corridor')
    require(float(np.abs(frame(master,2.8)[hidden]-frame(master,45.8)[hidden]).mean())<.5,
            'Closing wall hides the service corridor again')
    finish=frame(master,41.3)
    for color in [scene.PINK,scene.CYAN,scene.GOLD]:
        count=int((np.abs(finish-np.array(color)).sum(axis=2)<70).sum())
        require(count>2500,f'Comparison retains route color {color}: {count} pixels')


if __name__=='__main__':main()
