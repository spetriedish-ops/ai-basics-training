"""Append a staged portfolio edit, disk save, and explicit reload in other rooms.

All names and account details are the user's fictional teaching example.
The first eight approved clips are reused without re-encoding.
"""
import argparse
import json
import math
import subprocess
from functools import lru_cache
from PIL import Image
from render_context_portability import Portability, FULL, CLOSE, STARTS, lerpbox
from render_context_portfolio import PLAYER, SOURCE, HERE, PAPER, INK, TEAL, TOPICS, icon, fittext
from render_context_entry import smooth, clamp
from render_context_volume import project
from render_computer_control_bonus import Sketch, encode, font

VERSION = 'portfolio-6'
GREEN = (55, 126, 97)
ACCOUNT = 'The Industrial Nugget Factory'
EDITS = [
    (5, ['# Identity', 'Name: Alex', 'Role: Account lead', f'Account: {ACCOUNT}'],
     ['Account: United Nugget Corp.']),
    (1, ['# Current projects', f'## {ACCOUNT}', '- Account onboarding and support', '- Coordinate with the supporting account team'],
     ['## United Nugget Corp.']),
    (4, ['# Goals and priorities', f'- Support {ACCOUNT}', '- Align with the new supporting account team'],
     ['- Support United Nugget Corp.']),
    (7, ['# Team and relationships', f'## {ACCOUNT}', '- Jack Sparrow: Account Manager', '- Ted Lasso: Solutions Engineer', '- David Beckham: Customer Success Manager'],
     ['## Previous account team']),
    (6, ['# Role and responsibilities', 'Role: Account lead', f'Account: {ACCOUNT}', "- Coordinate the account's supporting team", '- Partner with Jack, Ted, and David'],
     ['Account: United Nugget Corp.']),
]
CHANGED = tuple(row[0] for row in EDITS)
REQUEST = [
    "I have a new account that I'm working to support.",
    f"It's called {ACCOUNT}.",
    'The supporting account team includes:',
    'Jack Sparrow — Account Manager',
    'Ted Lasso — Solutions Engineer',
    'David Beckham — Customer Success Manager.',
    'Please update my personal context portfolio.',
]
BEATS = [('A new account and supporting team', 0, 3)] + [
    (f'Update {TOPICS[i][0]}.md', 3 + j * 4, 7 + j * 4) for j, (i, _, _) in enumerate(EDITS)
] + [
    ('Updated context in our classroom', 23, 26),
    ('Save the five files to the computer', 26, 30.5),
    ('The saved portfolio is ready to reuse', 30.5, 33.5),
    ('Other agents load the revised files', 33.5, 40.5),
]
CUES = [
    'A new fiscal year brings a new account and team. The user asks their agent to maintain the portfolio.',
    'Identity retains Alex’s name and role, and updates the account.',
    'Current projects reflects the new account and supporting team.',
    'Goals and priorities now point to supporting The Industrial Nugget Factory.',
    'Team and relationships records Jack Sparrow, Ted Lasso, and David Beckham with the exact supplied roles.',
    'Role and responsibilities reflects coordination with the new account team.',
    'Five existing context boxes now carry a green revision seal. The other five are unchanged.',
    'The five revised Markdown files are saved to the portfolio folder on the computer.',
    'The classroom has the new information. The other three rooms still have their earlier copies.',
    'The other agents now read the revised files and refresh their own context. Saving a file alone does not refresh an already-running conversation. Existing boxes update in place; no extra tower is added.',
]


def blend(a, b, amount):
    return Image.blend(a.convert('RGB'), b.convert('RGB'), clamp(amount)).convert('RGBA')


class PortfolioUpdate:
    def __init__(self):
        self.p = Portability()
        self.base = self.p.base
        self.saved_monitors = [self.saved_monitor(v, 1) for v in range(3)]

    @lru_cache(maxsize=36)
    def classroom(self, v, revisions=()):
        return self.p.room(0, 29.5, v, revisions=revisions).convert('RGBA')

    def bubble(self, im, lines, v, human=False):
        sk = Sketch(im, v)
        if human:
            box = (630, 105, 1770, 413)
            tail = [(1030, 410), (1090, 487), (1105, 410)]
            x, y, size, step = 665, 125, 34, 39
        else:
            box = (1150, 155, 1775, 320)
            tail = [(1460, 317), (1480, 590), (1515, 317)]
            x, y, size, step = 1180, 184, 31, 44
        sk.poly(tail, PAPER, INK, 2)
        sk.rect(box, PAPER, INK, 3, radius=23)
        for j, line in enumerate(lines):
            fittext(sk, (x, y + j * step), line, size, box[2] - x - 28, anchor='lt')

    def request(self, t, v):
        im = self.classroom(v).copy()
        layer = Image.new('RGBA', im.size)
        self.bubble(layer, REQUEST, v, human=True)
        # A speech bubble draws into view, then holds for the narration.
        layer.putalpha(layer.getchannel('A').point(lambda a: round(a * smooth(t / .55))))
        im.alpha_composite(layer)
        return im

    def pencil(self, im, x, y, v):
        sk = Sketch(im, v)
        sk.poly([(x, y), (x+14, y-31), (x+74, y-91), (x+88, y-77), (x+28, y-17)], (232, 191, 94), INK, 2)
        sk.poly([(x, y), (x+14, y-31), (x+28, y-17)], (238, 216, 177), INK, 2)
        sk.poly([(x, y), (x+5, y-12), (x+11, y-7)], INK, INK, 1)
        sk.poly([(x+74, y-91), (x+86, y-103), (x+100, y-89), (x+88, y-77)], (211, 140, 130), INK, 2)

    def editor(self, j, t, v):
        i, lines, old = EDITS[j]
        done = t >= 3.15
        revisions = CHANGED[:j+int(done)]
        im = self.classroom(v, revisions).copy()
        sk = Sketch(im, v)
        # A text document is held beside the agent, clear of both characters.
        sk.rect((174, 163, 1047, 914), (215, 205, 184), (215, 205, 184), 1, radius=18)
        sk.rect((155, 145, 1030, 895), (255, 252, 239), INK, 3, radius=18)
        sk.rect((170, 159, 1015, 222), (218, 232, 219), INK, 2, radius=9)
        im.alpha_composite(icon(i, v).resize((65, 43), Image.Resampling.LANCZOS), (185, 170))
        fittext(sk, (270, 173), TOPICS[i][0]+'.md', 36, 720, anchor='lt')
        sk.text((194, 249), 'BEFORE', 23, (135, 122, 109))
        for n, line in enumerate(old):
            sk.text((194, 285+n*38), line, 30, (151, 137, 124))
            w = sk.d.textlength(line, font=font(30))
            sk.line([(194, 304+n*38), (194+w, 304+n*38)], (171, 117, 102), 2)
        sk.line([(193, 342), (990, 342)], (205, 202, 180), 2)
        sk.text((194, 359), 'REVISED TEXT', 23, GREEN)
        total = sum(len(line) for line in lines)
        budget = round(total * clamp((t-.48)/2.35))
        cursor = None
        for n, line in enumerate(lines):
            shown = line[:max(0, budget)]
            if shown:
                size = 34
                while sk.d.textlength(line, font=font(size)) > 786: size -= 1
                sk.text((194, 403+n*61), shown, size, GREEN if not line.startswith('#') else INK)
                cursor = (194+sk.d.textlength(shown, font=font(size)), 444+n*61)
            budget -= len(line)
        if not done and cursor is not None:
            self.pencil(im, cursor[0]+8, cursor[1]+math.sin(t*16)*2, v)
        sk.line([(193, 810), (990, 810)], (205, 202, 180), 2)
        sk.text((194, 832), 'Edit ready' if done else 'Editing…', 29, GREEN)
        sk.text((990, 836), f'{j+1} / 5 files', 27, (124, 120, 104), anchor='rt')
        self.bubble(im, ['That file is updated.' if done else 'Let me update',
                         TOPICS[i][0]+'.md'], v)
        return im

    def context(self, t, v):
        crop = lerpbox(FULL, CLOSE, smooth((t-.35)/2.1))
        im = self.p.room(0, 29.5, v, crop, CHANGED).convert('RGBA')
        if t < .35:
            im = blend(self.editor(4, 4, v), im, smooth(t/.35))
        return im

    def saved_monitor(self, v, progress=1):
        im = self.base.desktop(False, v, 7, transparent=True)
        sk = Sketch(im, v)
        y = 315+7*35
        sk.rect((319, y-4, 905, y+30), None, TEAL, 2, radius=6)
        sk.rect((945, 309, 1436, 677), (255, 253, 244), (185, 185, 164), 2, radius=9)
        sk.text((967, 326), 'team-and-relationships.md', 28, TEAL)
        sk.line([(965, 366), (1413, 366)], (198, 204, 183), 2)
        rows = ['# Account team', ACCOUNT, 'Jack Sparrow', '  Account Manager', 'Ted Lasso', '  Solutions Engineer', 'David Beckham', '  Customer Success Manager']
        for j, line in enumerate(rows):
            fittext(sk, (967, 380+j*32), line, 25, 442, anchor='lt')
        # Save status is part of the folder UI, not narration outside the scene.
        sk.rect((314, 241, 1454, 290), (211, 225, 208), INK, 2, radius=9)
        sk.text((333, 247), 'personal-context-portfolio', 34, INK)
        count = min(5, int(progress*5+.00001))
        sk.text((1429, 254), '5 files saved' if count == 5 else 'Saving…', 26, GREEN, anchor='rt')
        for i in CHANGED[:count]:
            y = 326+i*35
            sk.oval((873, y-9, 894, y+12), GREEN, GREEN, 1)
            sk.line([(877, y+1), (882, y+6), (890, y-4)], (255, 251, 228), 2)
        return im

    def monitor(self, im, v, width, progress=1, opacity=1):
        source = self.saved_monitors[v] if progress >= 1 else self.saved_monitor(v, progress)
        width = round(width);height = round(width*1080/1920)
        art = source.resize((width, height), Image.Resampling.LANCZOS)
        if opacity < 1:
            art.putalpha(art.getchannel('A').point(lambda a: round(a*opacity)))
        im.alpha_composite(art, ((1920-width)//2, (1080-height)//2))

    def save(self, t, v):
        if t < .9:
            return self.p.room(0, 29.5, v, lerpbox(CLOSE, FULL, smooth(t/.9)), CHANGED).convert('RGBA')
        if t < 2.3:
            q = smooth((t-.9)/1.4)
            im = self.p.grid(29.5, v, 2-q, revisions=[CHANGED, (), (), ()])
            self.monitor(im, v, 220, progress=0, opacity=q)
            return im
        q = smooth((t-2.3)/1.4)
        im = blend(self.p.grid(29.5, v, revisions=[CHANGED, (), (), ()]), self.base.monitor.paper, q)
        self.monitor(im, v, 220+1700*q, progress=clamp((t-3.55)/.65))
        return im

    def overview(self, t, v):
        q = smooth(t/2.6)
        im = blend(self.base.monitor.paper, self.p.grid(29.5, v, revisions=[CHANGED, (), (), ()]), q)
        self.monitor(im, v, 1920-1700*q)
        return im

    @staticmethod
    def reload_age(t, k, j):
        # Starts are drop-crests; departure is 1.2 seconds earlier.
        return t-(1.3+j*.68+(k-1)*.22)

    def reload(self, t, v):
        revisions = [CHANGED] + [tuple(i for j, i in enumerate(CHANGED) if self.reload_age(t, k, j) >= .62) for k in range(1, 4)]
        im = self.p.grid(29.5, v, revisions=revisions)
        for k in range(1, 4):
            ox=(k%2)*1920;oy=(k//2)*1080
            def moving(age, i, x, z, support, k=k):
                if i not in CHANGED:return None
                elapsed=self.reload_age(t, k, CHANGED.index(i))
                if elapsed >= .62:return None
                return self.p.delivery_motion(k, elapsed, i, x, z, support)
            # The incoming revision meets the old cube at identical coordinates
            # and becomes its green seal; the stack never grows or jumps.
            self.base.room(0, v, (-ox, -oy, 3840-ox, 2160-oy), self.p.rooms[k][v], self.p.offsets[k],
                           canvas=im, motion_override=moving, revisions=CHANGED)
        self.monitor(im, v, 220)
        return im

    def frame(self, t, v=None):
        v=int(t*30)//5%3 if v is None else v
        if t < 3:return self.request(t, v).convert('RGB')
        if t < 23:
            j=min(4, int((t-3)//4));local=t-(3+j*4)
            im=self.editor(j, local, v)
            if local < .35:
                previous=self.request(3, v) if j == 0 else self.editor(j-1, 4, v)
                im=blend(previous, im, smooth(local/.35))
            return im.convert('RGB')
        if t < 26:return self.context(t-23, v).convert('RGB')
        if t < 30.5:return self.save(t-26, v).convert('RGB')
        if t < 33.5:return self.overview(t-30.5, v).convert('RGB')
        return self.reload(t-33.5, v).convert('RGB')

    def prepare(self):
        for j, (_, start, end) in enumerate(BEATS, 1):
            self.frame(end-1/30, 0).save(PLAYER/f'update-hold-{j:02}.jpg', quality=97)
        sheet=Image.new('RGB', (1920, 1440), PAPER)
        for j, t in enumerate([2.9, 6.9, 10.9, 14.9, 18.9, 22.9, 25.9, 30.4, 33.4, 35.5, 37, 40.4]):
            sheet.paste(self.frame(t, 0).resize((640, 360), Image.Resampling.LANCZOS), ((j%3)*640, (j//3)*360))
        sheet.save(SOURCE/'update-storyboard.jpg', quality=96)

    def render(self):
        # Preserve the eight approved opening beats and all existing controls.
        existing=json.loads((PLAYER/'manifest.json').read_text())
        first=existing['beats'][:8]
        assert all((PLAYER/b['src']).exists() for b in first)
        self.prepare()
        added=[]
        for j, ((label, start, end), cue) in enumerate(zip(BEATS, CUES), 1):
            src=f'update-beat-{j:02}.mp4';hold=f'update-hold-{j:02}.mp4'
            encode(PLAYER/src, (self.frame(start+n/30) for n in range(round((end-start)*30))))
            frames=[self.frame(end-1/30, v) for v in range(3)]
            encode(PLAYER/hold, (frames[n//5] for n in range(15)))
            added.append({'id':f'portfolio-update-{j}', 'section':'Keep the portfolio up to date', 'label':label,
                          'src':src, 'hold':hold, 'poster':f'update-hold-{j:02}.jpg', 'cue':cue, 'note':None})
        data={'title':'One portfolio, four agents — keep it up to date', 'version':VERSION, 'ready':'ready.jpg', 'beats':first+added}
        inputs=SOURCE/'concat.txt'
        inputs.write_text(''.join(f"file '{(PLAYER/b['src']).as_posix()}'\n" for b in data['beats']))
        try:
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(inputs), '-c', 'copy', '-movflags', '+faststart', str(HERE/'out/context_portfolio.mp4')], check=True)
        finally:inputs.unlink()
        (PLAYER/'manifest.json').write_text(json.dumps(data, indent=2)+'\n')
        (PLAYER/'sequence.js').write_text('const sequence = '+json.dumps(data, indent=2)+';\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    args=parser.parse_args()
    scene=PortfolioUpdate()
    scene.prepare() if args.prepare_only else scene.render()
