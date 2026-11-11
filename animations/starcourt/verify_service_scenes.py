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

    elevator=scenes.OUT/'secret_elevator.mp4'
    upper,lower=frame(elevator,2),frame(elevator,10.5)
    require(float(np.abs(upper[286:902,645:1275]-lower[286:902,645:1275]).mean())>8,
            'Secret elevator visibly descends through the service levels')
    require(count(upper[588:884,1350:1787],scenes.CYAN)<300 and
            count(lower[588:884,1350:1787],scenes.CYAN)>1000,
            'Underground lab gag appears only after the descent')

    overlap=scenes.OUT/'mcp_cli_overlap.mp4'
    mcp_only,shared,final=frame(overlap,2),frame(overlap,10),frame(overlap,24)
    require(count(shared[523:548,1300:1390],scenes.PINK)>70 and
            count(shared[578:603,1300:1390],scenes.CYAN)>70,
            'Both colored lanes physically reach the SAME shared tool door')
    require(count(mcp_only[580:790,80:500],scenes.CYAN)<500 and
            count(shared[580:790,80:500],scenes.CYAN)>2500,
            'CLI entrance activates separately after the MCP entrance')
    require(count(final[822:910,800:1735],scenes.GREEN)>700,
            'Overlap film ends on the one, the other, or both caption')

    agency=scenes.OUT/'agency_guardrails.mp4'
    fixed,choices,risk,restored=frame(agency,3),frame(agency,12),frame(agency,27),frame(agency,30.5)
    require(float(np.abs(fixed[388:531,1430:1668]-choices[388:531,1430:1668]).mean())>1,
            'Agency beat opens multiple approved choices after the fixed action')
    at_door,at_origin=frame(agency,3.8),frame(agency,7)
    require(count(at_door[456:520,630:710],scenes.CREAM)>80 and
            count(at_origin[456:520,217:303],scenes.CREAM)>80 and
            count(at_origin[451:485,275:304],scenes.GREEN)>150,
            'Fixed request reaches the door and returns a checked response to its origin')
    denied=np.s_[708:848,1430:1668,:]
    require(count(choices[denied],(122,59,67))>800 and count(restored[denied],(122,59,67))>800,
            'Out-of-bounds action remains visibly denied')
    require(count(restored[698:704,1390:1758],scenes.GREEN)>600 and
            count(restored[701:847,1385:1392],scenes.GREEN)>250,
            'Approved-zone boundary visibly excludes the denied door')
    left_gate=np.s_[374:848,940:965,:]
    require(count(restored[left_gate],(99,40,52))>count(risk[left_gate],(99,40,52))+4000,
            'Guardrails return after the unsafe counterfactual')

    context=scenes.OUT/'context_handoff.mp4'
    light,loaded=frame(context,3),frame(context,12)
    meter=np.s_[730:764,820:1100,:]
    require(count(loaded[meter],scenes.GOLD)>4000,
            'Near-full context meter remains visible after the scale appears')
    scale=np.s_[644:799,1380:1750,:]
    require(count(light[scale],scenes.CYAN)<100 and count(loaded[scale],scenes.CYAN)>1500,
            'Separate NEXT: CONTEXT scale display appears beside the backpack')


if __name__=='__main__':main()
