#!/usr/bin/env python3
"""Validate the delivered films and their central teaching transitions."""
from fractions import Fraction
import numpy as np
from verify import require,probe,frame
import render_service_scenes as scenes


def count(im,color,tol=70):return int((np.abs(im-np.array(color)).sum(axis=2)<tol).sum())


def main():
    for key,s in scenes.SCENES.items():
        master=scenes.OUT/f'{key}.mp4';data=probe(master);stream=data['streams'][0]
        require(stream['codec_name']=='h264' and (stream['width'],stream['height'])==(1920,1080)
                and Fraction(stream['r_frame_rate'])==30,f'{key}: 1080p H.264 at 30 fps')
        require(len(data['streams'])==1 and abs(float(data['format']['duration'])-s['duration'])<.04,
                f'{key}: silent master has the intended duration')
        require((scenes.OUT/f'{key}.gif').stat().st_size<10_000_000,f'{key}: GIF under 10 MB')
        for i,(_,start,end) in enumerate(s['beats'],1):
            clip=scenes.PLAYER/'stages'/key/f'{i:02}.mp4';hold=scenes.PLAYER/'holds'/key/f'{i:02}.mp4'
            require(abs(float(probe(clip)['format']['duration'])-(end-start))<.04,f'{key} beat {i}: clip duration')
            require(abs(float(probe(hold)['format']['duration'])-3)<.04,f'{key} beat {i}: native 3-second hold')
            last,first,later=frame(clip,end-start-.034),frame(hold,0),frame(hold,1)
            require(float(np.abs(last-first).mean())<.8,f'{key} beat {i}: hold preserves the completed action')
            require(float(np.abs(first-later).mean())<.3,f'{key} beat {i}: hold has ambient motion only')

    opener=scenes.OUT/'mall_opener.mp4'
    for t in [0,3,6,9,11.9,12.1]:
        im=frame(opener,t)
        require(count(im,scenes.RED)<100,f'Opener {t}s: no red spooky title before the cue')
        require(float(im[35:110,1640:1850].mean())>235,f'Opener {t}s: no early Starcourt corner branding')
    before,after=frame(opener,3),frame(opener,11)
    require(np.array_equal(np.array(scenes.compose_opener(3))[300:620],np.array(scenes.compose_opener(11))[300:620]),
            'Neutral cutaway leaves the source storefront pixels exactly unchanged')
    require(float(np.abs(before[300:620]-after[300:620]).mean())<.7,'Encoded neutral cutaway preserves the public storefronts')
    require(float(np.abs(before[700:900]-after[700:900]).mean())>15,'Neutral cutaway visibly reveals back doors')
    night=frame(opener,18)
    require(count(night,scenes.RED)>7500,'Cue reveals the red outlined title')
    require(float(night.mean())<float(after.mean())*.3,'Cue changes the whole mall to the night palette')
    # Transition begins with the exact previous hold so the click never jumps.
    require(np.array_equal(np.array(scenes.compose_opener(11.99)),np.array(scenes.compose_opener(12))),
            'Spooky cue starts on the preceding neutral hold')

    mcp=scenes.OUT/'mcp_directory.mp4'
    useful,large,wrong,retry=frame(mcp,2),frame(mcp,12),frame(mcp,22),frame(mcp,33)
    wing=np.s_[314:657,92:439,:]
    require(float(np.abs(useful[wing]-large[wing]).mean())>15,'Directory physically expands with additional tool descriptions')
    gauge=np.s_[837:858,1488:1687,:]
    filled=lambda im:count(im[gauge],scenes.CYAN)+count(im[gauge],scenes.GOLD)
    require(filled(large)>filled(useful)*2.6,'Expanded descriptions visibly consume more context')
    require(filled(retry)>=filled(large),'Retry does not magically empty the context window')
    require(count(wrong[520:607,477:1222],scenes.GOLD)>1800,'Wrong-tool beat selects the comments tool')
    require(count(retry[421:508,477:1222],scenes.PINK)>1800,'Retry selects the issue-details tool')
    parcel=np.s_[770:832,124:356,:]
    require(float(np.abs(wrong[parcel]-retry[parcel]).mean())>8,'Wrong comments parcel changes to the requested issue')

    cli=scenes.OUT/'cli_terminal.mp4'
    typed,result,error,recovered=frame(cli,1.5),frame(cli,11),frame(cli,23),frame(cli,34)
    paper=np.s_[578:885,1290:1770,:]
    pale=lambda im:int((im[paper].min(axis=2)>185).sum())
    require(pale(result)>100000 and pale(typed)<2000,'CLI response prints only after a service result')
    require(pale(error)<2000 and pale(recovered)>100000,'Invalid command produces no receipt; corrected command does')
    door=np.s_[331:475,1463:1688,:]
    require(float(np.abs(typed[door]-error[door]).mean())<.5,'Invalid command leaves the endpoint closed')
    require(float(np.abs(error[door]-recovered[door]).mean())>20,'Corrected command reaches the service endpoint')
    pipe=np.s_[393:518,1169:1400,:]
    base=np.array(scenes.compose_cli(20))[pipe]
    require(all(np.array_equal(base,np.array(scenes.compose_cli(t))[pipe]) for t in np.arange(17,25,.2)),
            'No request packet travels during the invalid-command beat')
    require(float(np.abs(frame(cli,12)[675:711,1310:1750]-frame(cli,16)[675:711,1310:1750]).mean())>10,
            'Result-reading correction highlights the actual issue status')
    for name,path in [('MCP',scenes.MCP_PATH),('CLI',scenes.CLI_PATH)]:
        require(all(300<y<925 and 80<x<1840 for x,y in path),f'{name} request stays in the backstage set')


if __name__=='__main__':main()
