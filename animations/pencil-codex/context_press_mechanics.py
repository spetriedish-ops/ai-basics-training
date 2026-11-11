"""A contact-driven cartoon press with one coordinate system for every surface.

Forty-nine persistent cartons occupy two shallow rows. Side platens first close
the air gaps, then deform touching cartons. The overhead platen compresses each
supported column only after contact. No depth scaling, replacement bale, or
independent sprite motion is used at the end.
"""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw
from render_context_entry import smooth, clamp
from render_context_portfolio import INK, icon, fittext
from render_computer_control_bonus import Sketch

WIDTH=8.0
HEIGHT=4.0
DEPTH=6.0
FINAL_WIDTH=1.40
FINAL_HEIGHT=1.30
BED_FRONT=1.05
ROW_DEPTH=.70


def project(x,z,h=0):
    """Match all eight illustrated room corners, for walls AND contents."""
    depth=z/DEPTH
    return (960+(x-4)*(202.5-87.5*depth),
            970-320*depth-h*(210-116.25*depth))


def coefficients(dest,source):
    rows=[];values=[]
    for (x,y),(u,v) in zip(dest,source):
        rows.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        values.extend([u,v])
    return tuple(np.linalg.solve(np.asarray(rows),np.asarray(values)))


def crush_lengths(base,available,thresholds,softness):
    """Quasi-static compressible contacts: empty space closes before crushing."""
    base=np.asarray(base,dtype=float)
    if available>=base.sum():return base.copy()
    assert available>sum(base*.075)
    def sizes(force):return np.maximum(base*.075,base-np.asarray(softness)*np.maximum(0,force-np.asarray(thresholds)))
    low,high=0.,10.
    for _ in range(48):
        mid=(low+high)/2
        if sum(sizes(mid))>available:low=mid
        else:high=mid
    return sizes(high)


class MechanicalCompactor:
    def __init__(self,parent):
        self.parent=parent
        self.rows=[];self.cartons=[]
        widths=[[.90,.86,.97,.90,.96,.88,.91],
                [.94,.89,.85,.96,.88,.95,.89]]
        n=0
        for row in range(2):
            initial=[];x=.28;gap=(8-.56-sum(widths[row]))/6
            for col,w in enumerate(widths[row]):
                initial.append(x);x+=w+gap
                for level in range(3+row):
                    self.cartons.append(dict(id=n,row=row,col=col,level=level,
                        height=.82+.055*math.sin(n*2.1),
                        armor=(row==0 and col==1 and level==1),
                        item=self.parent.mono.items[(n*19)%len(self.parent.mono.items)]))
                    n+=1
            self.rows.append(dict(widths=np.array(widths[row]),initial=np.array(initial)))

    @staticmethod
    def wall_limits(q):
        left=(WIDTH-FINAL_WIDTH)*q/2
        return left,WIDTH-left

    @lru_cache(maxsize=900)
    def layout(self,q,ceiling=HEIGHT):
        """Persistent object bounds; horizontal chains and supported columns."""
        left,right=self.wall_limits(q);result=[]
        for row,r in enumerate(self.rows):
            thresholds=[.02+.14*min(i,6-i)+.025*row for i in range(7)]
            softness=[.70+.13*math.sin(i*1.8+row) for i in range(7)]
            widths=crush_lengths(r['widths'],right-left,thresholds,softness)
            positions=r['initial'].copy()
            edge=left
            for i in range(7):positions[i]=max(positions[i],edge);edge=positions[i]+widths[i]
            edge=right
            for i in reversed(range(7)):positions[i]=min(positions[i],edge-widths[i]);edge=positions[i]
            for col in range(7):
                members=[c for c in self.cartons if c['row']==row and c['col']==col]
                base=[c['height'] for c in members]
                # The top carton yields first. Pressure reaches the lower ones
                # as their neighbors run out of space, rather than scaling h.
                heights=crush_lengths(base,ceiling,
                    [.17*(len(base)-1-i)+.025*math.sin(col+i) for i in range(len(base))],
                    [.68+.11*math.cos(col*2+i) for i in range(len(base))])
                h=0
                for c,dy in zip(members,heights):
                    result.append(dict(c,x=float(positions[col]),z=BED_FRONT+row*ROW_DEPTH,
                        h=h,w=float(widths[col]),d=ROW_DEPTH,dy=float(dy),
                        crush_x=1-float(widths[col])/r['widths'][col],
                        crush_y=1-float(dy)/c['height']))
                    h+=float(dy)
        return result

    @lru_cache(maxsize=147)
    def face_art(self,index,v):
        c=self.cartons[index]
        if c['armor']:
            return self.parent.armor(v).resize((256,256),Image.Resampling.LANCZOS)
        item=c['item'];im=Image.new('RGBA',(256,256));s=Sketch(im,v)
        s.rect((0,0,255,255),item['color'],INK,2)
        graphic=icon(item['original'],v) if item['original'] is not None else self.parent.mono.graphic(item['topic'],item['kind'],v)
        im.alpha_composite(graphic.resize((220,146),Image.Resampling.LANCZOS),(18,12))
        for j,line in enumerate(item['label'].split('\n')):
            fittext(s,(128,167+j*33),line,28,230)
        return im

    def texture_quad(self,im,art,quad):
        left=math.floor(min(x for x,y in quad))-2;top=math.floor(min(y for x,y in quad))-2
        right=math.ceil(max(x for x,y in quad))+3;bottom=math.ceil(max(y for x,y in quad))+3
        target=[(x-left,y-top) for x,y in quad]
        source=[(0,0),(art.width,0),(art.width,art.height),(0,art.height)]
        mapped=art.transform((right-left,bottom-top),Image.Transform.PERSPECTIVE,
            coefficients(target,source),Image.Resampling.BICUBIC)
        mask=Image.new('L',mapped.size);ImageDraw.Draw(mask).polygon(target,fill=255)
        mapped.putalpha(Image.fromarray(np.minimum(np.asarray(mask),np.asarray(mapped.getchannel('A')))))
        im.alpha_composite(mapped,(left,top))

    @staticmethod
    def fold_mesh(index,damage):
        us=[0,.31,.68,1];vs=[0,.17,.36,.58,.80,1]
        mesh={}
        for j,t in enumerate(vs):
            for i,u in enumerate(us):
                seed=index*2.731+i*4.17+j*1.93
                xx=u;yy=t
                if 0<i<3:
                    xx+=damage*.095*math.sin(seed)
                elif 0<j<5:
                    dent=damage*(.10+.13*(.5+.5*math.sin(seed)))
                    xx=dent if i==0 else 1-dent
                if 0<j<5:
                    yy+=damage*.038*math.cos(seed*1.7)
                elif 0<i<3:
                    dent=damage*(.025+.04*(.5+.5*math.cos(seed)))
                    yy=dent*.45 if j==0 else 1-dent
                mesh[i,j]=(xx,yy)
        for j in range(6):
            xx,yy=mesh[1,j];mesh[1,j]=(max(mesh[0,j][0]+.065,min(.47,xx)),yy)
            xx,yy=mesh[2,j];mesh[2,j]=(min(mesh[3,j][0]-.065,max(.53,xx)),yy)
        return us,vs,mesh

    def carton(self,im,b,v,projection=project):
        x,z,h,w,d,dy=(b[k] for k in ['x','z','h','w','d','dy'])
        damage=smooth((1-(1-b['crush_x'])*(1-b['crush_y'])-.035)/.83);s=Sketch(im,v)
        def p(a,c,y):return projection(x+a*w,z+c*d,h+y*dy)
        color=b['item']['color']
        # A persistent, irregular fold mesh. Its vertices buckle inward, so
        # dramatically crumpled faces still respect the established contacts.
        us,vs,mesh=self.fold_mesh(b['id'],damage)
        def f(i,j):return p(mesh[i,j][0],0,mesh[i,j][1])
        if not b['armor']:
            side=1 if x+w/2<4 else 0
            si=3 if side else 0
            sidepoints=[f(si,j) for j in range(6)]+[p(side,1,1),p(side,1,0)]
            s.poly(sidepoints,tuple(max(0,c-38) for c in color),INK,1)
            roof=[f(i,5) for i in range(4)]+[p(1,1,1),p(0,1,1)]
            s.poly(roof,tuple(min(255,c+19) for c in color),INK,1)
            if damage>.04:
                # Deep roof dents and bright folded lips break the clean lid.
                for i in range(3):
                    mid=p((us[i]+us[i+1])*.5,.48,1-.12*damage)
                    s.poly([f(i,5),mid,f(i+1,5)],tuple(max(0,c-round(48*damage)) for c in color),tuple(max(0,c-55) for c in color),1)
                    s.line([f(i,5),mid,p(us[i+1],1,1)],tuple(max(0,c-65) for c in color),1)
                for j in [1,3]:
                    s.line([f(si,j),p(side,.37,vs[j]+.08),p(side,1,vs[j])],tuple(max(0,c-70) for c in color),1)
        art=self.face_art(b['id'],v)
        for j in range(5):
            for i in range(3):
                quad=[f(i,j+1),f(i+1,j+1),f(i+1,j),f(i,j)]
                patch=art.crop((round(us[i]*256),round((1-vs[j+1])*256),round(us[i+1]*256),round((1-vs[j])*256)))
                # Alternating light and dark fold planes retain the original
                # illustration while making its crumpled relief readable.
                shade=damage*(.08+.21*(.5+.5*math.sin(b['id']*1.9+i*2.4+j*3.3)))
                tint=(39,44,35,255) if (i+j+b['id'])%3 else (255,250,224,255)
                alpha=patch.getchannel('A')
                patch=Image.blend(patch,Image.new('RGBA',patch.size,tint),shade)
                patch.putalpha(alpha)
                self.texture_quad(im,patch,quad)
                if damage>.08:
                    a,bp=quad[3],quad[1]
                    mid=(a[0]+(bp[0]-a[0])*.43+2*damage*math.sin(b['id']+j),a[1]+(bp[1]-a[1])*.59)
                    crease=[a,mid,bp]
                    s.line(crease,tuple(max(0,c-round(95*damage)) for c in color),1)
                    s.line([(xx,yy-1.4*damage) for xx,yy in crease],tuple(min(255,c+40) for c in color),1)
        if damage>.15:
            # A few doubled-over paper lips sit inside the piece's envelope.
            for j in [1,3]:
                a=f(0,j);bp=f(1,j);tip=f(1,j+1)
                lip=(a[0]+(bp[0]-a[0])*.65,a[1]+(tip[1]-a[1])*.23*damage)
                s.poly([a,bp,lip],tuple(min(255,c+26) for c in color),tuple(max(0,c-58) for c in color),1)
        if not b['armor']:
            outline=[f(i,0) for i in range(4)]+[f(3,j) for j in range(1,6)]+[f(i,5) for i in [2,1,0]]+[f(0,j) for j in [4,3,2,1,0]]
            s.line(outline,INK,1)

    def wall_surfaces(self,im,q,v):
        if q<=0:return
        left,right=self.wall_limits(q);s=Sketch(im,v)
        for side,x in enumerate([left,right]):
            target=[project(x,0,HEIGHT),project(x,DEPTH,HEIGHT),project(x,DEPTH,0),project(x,0,0)]
            coeff=coefficients(target,self.parent.plate_sources[side])
            face=self.parent.plates[v][side].transform((1920,1080),Image.Transform.PERSPECTIVE,coeff,Image.Resampling.BICUBIC)
            im.alpha_composite(face)
            # Front ram bodies end at the SAME plane as the inner wall.
            front_x=target[0][0];outer=150 if side==0 else 1770
            a,b=round(min(front_x,outer)),round(max(front_x,outer))
            if b>a:
                im.alpha_composite(self.parent.press_texture.crop((a,130,b,970)),(a,130))
                s=Sketch(im,v)
                for i in range(1,5):
                    xx=a+(b-a)*i/5;s.line([(xx,143),(xx,952)],(95,101,85),3)
                for yy in [180,895]:s.line([(a+4,yy),(b-4,yy)],(178,126,77),10)
                s.line([(front_x,130),(front_x,970)],INK,3)
        if q>.18:
            x=(150+project(left,0,0)[0])*.5;y=540;s=Sketch(im,v)
            s.oval((x-37,y-37,x+37,y+37),(235,220,177),INK,2)
            angle=math.radians(215+125*q)
            s.line([(x,y),(x+28*math.cos(angle),y+28*math.sin(angle))],(167,67,46),3)

    def platen(self,im,q,height,v):
        layer=Image.new('RGBA',(1920,1080));s=Sketch(layer,v)
        left,right=self.wall_limits(q);left+=.035;right-=.035
        z0,z1=BED_FRONT-.045,BED_FRONT+2*ROW_DEPTH+.045
        top=[project(left,z0,height+.19),project(right,z0,height+.19),project(right,z1,height+.19),project(left,z1,height+.19)]
        stem=project(4,(z0+z1)/2,height+.19)[1]
        if stem>130:
            s.rect((931,130,989,stem),(118,132,114),INK,2)
            s.rect((942,130,978,stem),(186,192,167),INK,1)
            for yy in range(150,round(stem),32):s.line([(932,yy),(988,yy)],(77,89,76),2)
        s.poly(top,(157,164,137),INK,2)
        a,b=project(left,z0,height),project(right,z0,height)
        s.poly([a,b,top[1],top[0]],(190,139,67),INK,2)
        def mix(a,b,u):return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
        for i in range(8):
            u=i/8;s.poly([mix(a,b,u),mix(a,b,u+.05),mix(top[0],top[1],min(1,u+.10)),mix(top[0],top[1],u+.05)],(64,74,61),(64,74,61),1)
        im.alpha_composite(layer.crop((150,130,1770,970)),(150,130))

    def brace(self,im,q,v):
        if q>.78:return
        left,right=self.wall_limits(min(q,.59));e=smooth((q-.59)/.19)
        pts=[]
        for k in range(25):
            u=k/24;x,y=project(left+(right-left)*u,2.7,3.70+.22*q*math.sin(math.pi*u))
            dx=x-960;dy=y-220;angle=e*1.7
            pts.append((960+dx*math.cos(angle)-dy*math.sin(angle),220+dx*math.sin(angle)+dy*math.cos(angle)-600*e))
        s=Sketch(im,v);s.line(pts,(67,76,65),12);s.line(pts,(178,180,150),7)

    def scene(self,q,v,ceiling=HEIGHT,wall_q=None,ram=None,tag=0,impact=-1):
        im=self.parent.background[v].copy()
        self.wall_surfaces(im,q if wall_q is None else wall_q,v)
        self.brace(im,q,v)
        boxes=self.layout(q,ceiling)
        # Side walls are behind the chamber contents, not an overlay that
        # erases valid boxes near the front of the room.
        for b in sorted(boxes,key=lambda b:(-b['z'],b['h'])):self.carton(im,b,v)
        if tag>0:
            s=Sketch(im,v);left,right=self.wall_limits(1)
            corners=[project(x,BED_FRONT-.005,h) for x,h in [(left+.13,.91),(right-.13,.91),(right-.13,.64),(left+.13,.64)]]
            s.poly(corners,(242,229,191),INK,1)
            cx=sum(x for x,y in corners)/4;cy=sum(y for x,y in corners)/4
            s.text((cx,cy-14),'SUMMARY',26,INK,anchor='mt')
        if ram is not None:self.platen(im,1,ram,v)
        if 0<impact<.65:
            layer=Image.new('RGBA',(1920,1080));s=Sketch(layer,v);u=impact/.65
            for side in [-1,1]:
                for j in range(3):
                    x=960+side*(150+u*(45+j*23));y=905-u*(18+j*18);r=(15+j*5)*math.sin(math.pi*u)
                    s.oval((x-r,y-r,x+r,y+r),(225,207,169),(174,153,116),1)
            layer.putalpha(layer.getchannel('A').point(lambda a:round(a*(1-u))))
            im.alpha_composite(layer)
        return im.convert('RGB')

    def frame(self,t,v):
        if t<3:
            if t<.75:
                im=self.parent.mono.frame(54.5,v).convert('RGBA');self.parent.shutter(im,smooth(t/.75),v)
            else:
                im=self.scene(0,v).convert('RGBA');self.parent.shutter(im,1-smooth((t-.85)/1.1),v)
            return im.convert('RGB')
        if t<10:
            a=t-3;q=.30*smooth(a/1.65)+.28*smooth((a-2.05)/1.35)+.42*smooth((a-3.85)/1.8)
            return self.scene(q,v)
        a=t-10
        # First touch the tallest column, then sequentially load shorter ones.
        approach=smooth(a/.8)
        crush=clamp((a-1.2)/.85)**2
        ceiling=3.55-(3.55-FINAL_HEIGHT)*crush
        ram=4.8-(4.8-3.55)*approach-(3.55-FINAL_HEIGHT)*crush
        if a>=2.05:
            # The crushed pieces stay crushed when pressure is released.
            ceiling=FINAL_HEIGHT
            ram=FINAL_HEIGHT+(4.8-FINAL_HEIGHT)*smooth((a-2.70)/1.1)
        wall_q=1-smooth((a-3.20)/1.90)
        return self.scene(1,v,ceiling,wall_q,ram,clamp((a-5.1)/.5),a-2.05)
