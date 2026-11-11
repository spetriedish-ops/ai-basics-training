"""Assemble the approved context-nugget clips into one presenter-paced sequence."""
import json,subprocess
from pathlib import Path
from PIL import Image
from render_context_entry import boil
from render_computer_control_bonus import encode

HERE=Path(__file__).resolve().parent
PLAYER=HERE/'interactive/context_nugget'
ASSETS=PLAYER/'assets'

def command(*args):subprocess.run(args,check=True)
def frame(src,dst,last=False):
    command('ffmpeg','-y','-v','error',*(['-sseof','-0.04'] if last else []),'-i',str(src),'-frames:v','1',str(dst))

def build():
    ASSETS.mkdir(parents=True,exist_ok=True)
    mind=HERE/'interactive/harness_mind_map'
    stages=json.loads((mind/'manifest.json').read_text())['stages']
    concat=ASSETS/'recap-inputs.txt'
    concat.write_text(''.join(f"file '{(mind/s['src']).as_posix()}'\n" for s in stages[:5]))
    command('ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(ASSETS/'mind-map-recap.mp4'))
    concat.unlink()
    frame(ASSETS/'mind-map-recap.mp4',ASSETS/'ready.jpg')
    # The legacy factory player has no native holds. Freeze completed action
    # and reuse our low-amplitude line-displacement animation for these holds.
    factory=HERE.parent/'interactive/engine_factory'
    factory_stages=json.loads((factory/'manifest.json').read_text())['stages'][:4]
    for i,stage in enumerate(factory_stages,1):
        poster=ASSETS/f'factory-{i}.png'
        frame(factory/stage['src'],poster,last=True)
        art=Image.open(poster).convert('RGBA')
        variants=[boil(art,v).convert('RGB') for v in range(3)]
        encode(ASSETS/f'factory-{i}-hold.mp4',(variants[j//5] for j in range(15)))
    beats=[]
    def add(id,section,label,src,hold,cue,poster=None,note=None):
        beats.append(dict(id=id,section=section,label=label,src=src,hold=hold,cue=cue,poster=poster,note=note))
    add('recap','Opening','The harness so far','assets/mind-map-recap.mp4','../harness_mind_map/holds/05-tools.mp4',
        '“So far in this series…” Recap intelligence, the harness, and ways to interact with the world.')
    add('context','Opening','Reveal Context','../harness_mind_map/stages/06-context.mp4','../harness_mind_map/holds/06-context.mp4',
        '“For months now, AI agents have been marketed as teammates…” Hold here through “the next component of the harness: Context.”')
    add('crumple','Opening','Crumple and toss','../../out/paper_crumple.mp4',None,
        'Turn the page before “Are you surprised that context is part of the harness…?”', '../paper_transition/fresh.jpg')
    factory_cues=[
        '“In nugget 3, we talked about the model lifecycle…” Pre-training gives the model its general capabilities.',
        '“Some labs post-train models before release…” Specialized training remains different from this conversation’s context.',
        '“On day one…” The trained model is released.',
        '“The rest is up to the harness.” The finished engine goes to work; its training factory closes.'
    ]
    for i,stage in enumerate(factory_stages,1):
        add(f'factory-{i}','Training recap',stage['label'],'../../../interactive/engine_factory/'+stage['src'],f'assets/factory-{i}-hold.mp4',factory_cues[i-1],f'assets/factory-{i}.png')
    for i,(label,cue) in enumerate([
        ('Open the agent chat','“Context shows up in a couple different forms.” Introduce the familiar chat surface.'),
        ('Say hello','“The harness generally has a baseline amount of context baked in…” The user asks who the agent is.'),
        ('The agent knows its role','The agent introduces itself, then asks who you are. Hold through the explanation of separate conversation windows.')],1):
        add(f'chat-{i}','Agent identity',label,f'../agent_chat/beat-{i:02}.mp4',f'../agent_chat/hold-{i:02}.mp4',cue,f'../agent_chat/hold-{i:02}.jpg')
    for i,(label,cue) in enumerate([
        ('Sketch the classroom','“Imagine you’re in a room with your agent…” Draw the edges of the context window.'),
        ('Paint in the room','The room has a fixed size. Hold through the explanation of adding information and using up space.')],1):
        add(f'room-{i}','The context room',label,f'../context_room/beat-{i:02}.mp4',f'../context_room/hold-{i:02}.mp4',cue,f'../context_room/hold-{i:02}.jpg')
    add('entry','The context room','The user and agent walk in','../context_entry/beat-01.mp4','../context_entry/hold-01.mp4',
        '“The room is your context window. You and your agent walk in…” The agent carries its role-instruction pamphlet.','../context_entry/hold-01.jpg')
    fill=[
        ('Introduce yourself','“So the first thing you might do is introduce yourself…” Role, team, work, and preferences become small cubes.'),
        ('Ask the agent to research you','“A different way for the agent to learn about you…” Include the Confluence link; the prompt also takes space.'),
        ('MCP tools take up space','“It calls the Rovo MCP server…” Rovo, Gmail, and Calendar tool definitions enter before retrieved information.'),
        ('Research results arrive','“Then comes the actual information it pulls back in.” Pages, email, and calendar information enter the room.'),
        ('The initial context is assembled','“All of a sudden, your room is filling up…” The approved small pile leaves space for later work.')]
    for i,(label,cue) in enumerate(fill,1):
        add(f'fill-{i}','Building context',label,f'../context_fill/beat-{i:02}.mp4',f'../context_fill/hold-{i:02}.mp4',cue,f'../context_fill/hold-{i:02}.jpg')
    add('unc','Put context to work','The UNC work request',None,'../context_fill/hold-05.mp4',
        '“But we persevere…” Read two weeks of UNC Slack activity, identify workstreams, and create a Confluence tracking page.',
        '../context_fill/hold-05.jpg','Narration pause on the filled room. A dedicated UNC Slack-to-Confluence visual has not been built.')
    transport=[
        ('Load copies into the mine cart','“You give your agent the prompt…” The harness gathers the relevant context and loads copies with the prompt.'),
        ('Take context to the model','“This is one of the key areas where the model as a brain analogy falls apart…” Reveal the separate model and continuous track.'),
        ('The model works and replies','“The model is sitting in its own little world…” The machine processes the load; its reply returns to the room.'),
        ('Send context again on the next turn','“The harness has to send all the relevant context… with each prompt.” Include the earlier reply in the next load.')]
    for i,(label,cue) in enumerate(transport,1):
        add(f'transport-{i}','Each model call',label,f'../context_transport/train/beat-{i:02}.mp4',f'../context_transport/train/hold-{i:02}.mp4',cue,f'../context_transport/train/hold-{i:02}.jpg')
    add('dory','Memory and cost','Hi, I’m Dory','../context_transport/train/dory.mp4','../context_transport/train/dory-hold.mp4',
        '“It might as well be Dory from Finding Nemo…” Reintroduce yourself and resend what the model needs.','../context_transport/train/dory-hold.jpg')
    add('coins','Memory and cost','Inference costs tokens','../context_transport/train/dory-coins.mp4','../context_transport/train/dory-hold.mp4',
        '“Going back to the model lifecycle… inference costs tokens.” Trigger coins here, after Dory.','../context_transport/train/dory-hold.jpg')
    add('tradeoff','Wrap-up','Context versus cost',None,'../context_transport/train/dory-hold.mp4',
        '“Seems like you’re stuck between a rock and a hard place…” Balance useful context with cost and the risk of an unhelpful answer.',
        '../context_transport/train/dory-hold.jpg','Narration pause on the final view; no separate cost-versus-quality visual has been built.')
    add('next-nugget','Wrap-up','Next nugget',None,'../context_transport/train/dory-hold.mp4',
        '“In the next nugget…” Tease growing context and the mechanisms for managing it.',
        '../context_transport/train/dory-hold.jpg','Closing hold. Context overflow is reserved for the next nugget.')
    data={'title':'Context · full narration walkthrough','version':'context-sequence-1','ready':'assets/ready.jpg','beats':beats}
    (PLAYER/'manifest.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data,indent=2,ensure_ascii=False)+';\n')
    for beat in beats:
        for field in ('src','hold','poster'):
            if beat[field]:assert (PLAYER/beat[field]).is_file(), (beat['id'],field)
    print(f'Assembled {len(beats)} narration beats; all referenced media exist.')

if __name__=='__main__':build()
