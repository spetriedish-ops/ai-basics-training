"""Physical continuity checks for the compactor's separately rendered pieces."""
import itertools
import numpy as np
from PIL import ImageChops
from render_context_compaction import Compaction
from context_press_mechanics import HEIGHT,FINAL_HEIGHT,BED_FRONT,ROW_DEPTH,project

scene=Compaction();press=scene.mechanics
initial={b['id']:b for b in press.layout(0)}
assert len(initial)==49 and sum(b['armor'] for b in initial.values())==1
expected_corners=[(150,970),(500,650),(150,130),(500,275)]
for xyz,expected in zip([(0,0,0),(0,6,0),(0,0,4),(0,6,4)],expected_corners):
    assert np.allclose(project(*xyz),expected)

def check(q,ceiling):
    boxes=press.layout(q,ceiling);left,right=press.wall_limits(q)
    assert {b['id'] for b in boxes}==set(initial)
    for b in boxes:
        assert left-1e-8<=b['x'] and b['x']+b['w']<=right+1e-8
        assert b['h']>=0 and b['h']+b['dy']<=ceiling+1e-8
        assert (b['z'],b['d'])==(initial[b['id']]['z'],initial[b['id']]['d'])
        if b['level']:
            support=next(c for c in boxes if (c['row'],c['col'],c['level'])==(b['row'],b['col'],b['level']-1))
            assert abs(b['h']-support['h']-support['dy'])<1e-8
            assert abs(b['x']-support['x'])<1e-8 and abs(b['w']-support['w'])<1e-8
        else:assert b['h']==0
    for a,b in itertools.combinations(boxes,2):
        overlaps=[min(a[p]+a[s],b[p]+b[s])-max(a[p],b[p]) for p,s in [('x','w'),('z','d'),('h','dy')]]
        assert not all(o>1e-8 for o in overlaps),(a['id'],b['id'],overlaps)

for q in np.linspace(0,1,211):check(float(q),HEIGHT)
for h in np.linspace(3.55,FINAL_HEIGHT,211):check(1,float(h))
untouched={b['id']:b for b in press.layout(.08)}
assert all(untouched[i]['x']==initial[i]['x'] and untouched[i]['w']==initial[i]['w'] for i in initial)
early={b['id']:b for b in press.layout(.12)}
outer=next(i for i,b in initial.items() if b['row']==0 and b['col']==0 and b['level']==0)
middle=next(i for i,b in initial.items() if b['row']==0 and b['col']==3 and b['level']==0)
assert early[outer]['x']>initial[outer]['x']
assert early[middle]['x']==initial[middle]['x']
assert all(early[i]['w']==initial[i]['w'] for i in initial),'no crushing while air gaps remain'
touch=press.layout(1,3.0)
assert any(b['crush_y']>0 for b in touch if b['row']==1)
assert all(b['crush_y']==0 for b in touch if b['row']==0),'shorter stacks wait for contact'
for a,b in [(2.9666667,3),(9.9666667,10),(16.5,18)]:
    assert ImageChops.difference(scene.compactor(a,0),scene.compactor(b,0)).getbbox() is None
print('PASS: shared room corners; 422 pressure states; all 49 identities and fixed depths; no wall/floor/ceiling penetration; no interpenetrating pieces; every stack supported; outer-first contact; tallest-first press contact; stable manual holds.')

for index in range(49):
    for damage in np.linspace(0,1,41):
        us,vs,mesh=press.fold_mesh(index,float(damage))
        assert all(0<=x<=1 and 0<=y<=1 for x,y in mesh.values())
        for j in range(5):
            for i in range(3):
                quad=np.array([mesh[i,j],mesh[i+1,j],mesh[i+1,j+1],mesh[i,j+1]])
                edges=np.roll(quad,-1,axis=0)-quad;next_edges=np.roll(edges,-1,axis=0)
                cross=edges[:,0]*next_edges[:,1]-edges[:,1]*next_edges[:,0]
                assert min(cross)>0,(index,damage,i,j)
print('PASS: 30,135 crumple panels stay convex and inside their contact bounds')
