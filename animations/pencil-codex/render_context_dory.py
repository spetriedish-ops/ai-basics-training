"""Animate Sarah's supplied Dory artwork between the final hold and coins.

The original image preserves its supplied pose and white background. Native animation gives it a descending
swim path and a gentle looping hover; the classroom retains its pencil boil.
"""
from pathlib import Path
from functools import lru_cache
import argparse,math,shutil
from PIL import Image
from render_context_minecart import Minecart,HERE
from render_context_entry import boil,smooth,clamp
from render_context_fill import fitted,INK,PAPER
from render_computer_control_bonus import Sketch,encode

class DoryFinale:
    def __init__(self,sprite_path):
        raw=Image.open(sprite_path).convert('RGBA')
        bbox=raw.getchannel('A').getbbox()
        if bbox is None:raise ValueError('The character image is empty.')
        art=fitted(raw.crop(bbox),(290,220))
        self.sprites=[boil(art,v) for v in range(3)]
        self.scene=Minecart()

    def character(self,im,phase,variant,arrival=1,dialogue=True):
        # Descend from above through the empty gap, clear of the room, cart, and model.
        q=smooth(clamp(arrival))
        cx=1135+38*math.sin(q*math.pi)*(1-q)
        cy=-220+(515+220)*q
        hover=phase*math.tau/2
        if arrival>=1:
            cy+=4*math.sin(hover)
        art=self.sprites[variant]
        angle=(1-q)*-18+1.8*math.sin(hover)*q
        art=art.rotate(angle,Image.Resampling.BICUBIC,expand=True)
        im.alpha_composite(art,(round(cx-art.width/2),round(cy-art.height/2)))
        if dialogue:
            p=Sketch(im,variant)
            p.rect((942,290,1344,407),fill=PAPER,color=INK,width=3,radius=18)
            p.poly([(1190,404),(1213,441),(1230,404)],fill=PAPER,color=INK,width=2)
            p.text((1143,311),"Hi, I'm Dory.",34,INK,anchor='mt')
            p.text((1143,356),"What's your name?",34,INK,anchor='mt')
        return im.convert('RGB')

    @lru_cache(maxsize=3)
    def background(self,variant):
        return self.scene.frame('train',34.5,variant).convert('RGBA')

    def entrance(self,t,variant=None):
        variant=int(t*30)//5%3 if variant is None else variant
        # Clip duration 4.4s; hover has completed one two-second cycle at end.
        return self.character(self.background(variant).copy(),max(0,t-2.4),variant,
                              arrival=t/2.4,dialogue=t>=2.6)

    def hold(self,t,variant=None):
        variant=int(t*30)//5%3 if variant is None else variant
        return self.character(self.background(variant).copy(),t,variant)

    def coins(self,t,variant=None):
        variant=int(t*30)//5%3 if variant is None else variant
        # Four seconds completes two hover cycles, matching the return hold.
        return self.character(self.scene.coin_frame(t,variant).convert('RGBA'),t,variant)

    def render(self):
        player=HERE/'interactive/context_transport/train'
        out=HERE/'out'
        player.mkdir(parents=True,exist_ok=True)
        (HERE/'source/context_transport/train').mkdir(parents=True,exist_ok=True)
        for name,duration,draw in [('dory',4.4,self.entrance),('dory-hold',2,self.hold),('dory-coins',4,self.coins)]:
            master=out/f'context_train_{name}.mp4'
            encode(master,(draw(i/30) for i in range(round(duration*30))))
            shutil.copy2(master,player/f'{name}.mp4')
        self.hold(0,0).save(player/'dory-hold.jpg',quality=96)
        self.hold(0,0).save(HERE/'source/context_transport/train/dory.png')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Render the prepared finale from supplied Dory artwork.')
    parser.add_argument('--sprite',type=Path,default=HERE/'assets/context_transport/dory/supplied.png')
    args=parser.parse_args()
    if not args.sprite.is_file():parser.error('Attach or provide the character artwork first.')
    DoryFinale(args.sprite).render()
