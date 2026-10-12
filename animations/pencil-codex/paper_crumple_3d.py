"""Blender scene: one continuously deformed, UV-textured sheet of paper.

Run through render_paper_transition.py. No image swap or opacity animation.
"""
from pathlib import Path
import math
import sys
import struct
import bpy
import numpy as np

HERE=Path(__file__).resolve().parent
FRAMES=HERE/'source/paper_transition/frames'
FRAMES.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
preview='--preview' in args
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=16
scene.cycles.use_denoising=True
devices=bpy.context.preferences.addons['cycles'].preferences
try:
    devices.compute_device_type='METAL';devices.get_devices()
    for device in devices.devices:device.use=device.type=='METAL'
    scene.cycles.device='GPU'
except (TypeError,RuntimeError):
    scene.cycles.device='CPU'
scene.render.resolution_x=1920;scene.render.resolution_y=1080
scene.render.resolution_percentage=50 if preview else 100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.view_settings.exposure=0
scene.view_settings.gamma=1
scene.render.fps=30
scene.world.color=(.65,.65,.65)

bpy.ops.object.camera_add(location=(0,0,30))
camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=19.2
scene.camera=camera

def area(name,location,power,size):
    bpy.ops.object.light_add(type='AREA',location=location)
    light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size

area('Broad soft light',(-5,6,12),1600,9)
area('Soft fill',(5,-3,10),550,10)

cols,rows=180,110
uv=np.array([(i/cols,j/rows) for j in range(rows+1) for i in range(cols+1)])
u,v=(uv*2-1).T
flat=np.column_stack((u*9.6,v*5.4,np.zeros(len(u))))
faces=[]
for j in range(rows):
    for i in range(cols):
        a=j*(cols+1)+i
        faces.append((a,a+1,a+cols+2,a+cols+1))
mesh=bpy.data.meshes.new('Continuous paper surface')
mesh.from_pydata(flat.tolist(),[],faces);mesh.update()
paper=bpy.data.objects.new('One sheet, from flat to crumpled',mesh)
scene.collection.objects.link(paper)
layer=mesh.uv_layers.new(name='Original drawing')
for poly in mesh.polygons:
    poly.use_smooth=True
    for loop in poly.loop_indices:
        layer.data[loop].uv=uv[mesh.loops[loop].vertex_index]

material=bpy.data.materials.new('Ivory notebook paper');material.use_nodes=True
nodes=material.node_tree.nodes;links=material.node_tree.links
nodes.clear()
output=nodes.new('ShaderNodeOutputMaterial')
texture=nodes.new('ShaderNodeTexImage')
texture.image=bpy.data.images.load(str(HERE/'source/harness_mind_map/stage_06_context.jpg'))
principled=nodes.new('ShaderNodeBsdfPrincipled')
principled.inputs['Roughness'].default_value=.92
links.new(texture.outputs['Color'],principled.inputs['Base Color'])
emission=nodes.new('ShaderNodeEmission');links.new(texture.outputs['Color'],emission.inputs['Color'])
geometry=nodes.new('ShaderNodeNewGeometry')
side=nodes.new('ShaderNodeMixRGB');side.inputs[2].default_value=(.95,.93,.88,1)
links.new(geometry.outputs['Backfacing'],side.inputs[0]);links.new(texture.outputs['Color'],side.inputs[1])
links.new(side.outputs[0],principled.inputs['Base Color']);links.new(side.outputs[0],emission.inputs['Color'])
mix=nodes.new('ShaderNodeMixShader')
links.new(emission.outputs[0],mix.inputs[1]);links.new(principled.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs[0])
paper.data.materials.append(material)
solid=paper.modifiers.new('Thin visible paper edge','SOLIDIFY');solid.thickness=.004

# Domain-warped folds at several scales avoid a grid of identical creases.
warp=.43*np.sin(3.7*u+2.4*v)+.19*np.cos(6.1*v-1.8*u)
a=5.4*v+2.1*u+warp
b=5.9*u-2.8*v+.9+.36*np.sin(4.2*v)
c=12.3*v-6*u+.7*np.sin(3.1*u+v)
d=9.1*u+6.5*v+1.3
def ridge(x):
    s=np.sin(x)
    return np.sign(s)*np.abs(s)**.72

bundle=np.column_stack((1.12*u+.22*v+.48*np.sin(a)+.18*np.sin(c),
                       1.08*v-.12*u+.45*np.sin(b)+.21*np.sin(d),
                       .64*ridge(a)+.56*ridge(b)+.20*ridge(c)+.17*ridge(d)+.30*(1-u*u-v*v)))
bundle[:,2]+=.055*ridge(27*u+15*v+warp*3)+.038*ridge(19*v-23*u+warp*2)
# Distinct free corners project out of the compressed center.
corner=np.exp(-((u+.93)**2+(v-.96)**2)/.055)
bundle+=corner[:,None]*np.array([-.48,.80,.35])
corner=np.exp(-((u+.95)**2+(v+.94)**2)/.075)
bundle+=corner[:,None]*np.array([-.60,-.37,.60])
corner=np.exp(-((u-.98)**2+(v-.20)**2)/.045)
bundle+=corner[:,None]*np.array([.68,.18,.12])

def ease(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)

def pose(t):
    p=float(ease((t-.65)/1.95))
    # Folds rise before the silhouette contracts; the edges gather at slightly
    # different rates. Vertex identity and drawing UVs never change.
    rate=ease(np.clip(p+.16*math.sin(p*math.pi)*(np.maximum(abs(u),abs(v))-.4),0,1))
    vertices=flat*(1-rate[:,None])+bundle*rate[:,None]
    vertices[:,2]+=math.sin(p*math.pi)*(.16*ridge(a)+.10*ridge(b))
    mesh.vertices.foreach_set('co',vertices.astype(np.float32).ravel());mesh.update()
    toss=float(np.clip((t-2.82)/.83,0,1))
    dip=.14*math.sin(math.pi*float(np.clip((t-2.6)/.22,0,1)))
    paper.location=(12.8*toss**1.15,6*toss-1.7*toss*toss-dip,0)
    paper.rotation_euler=(.22*math.sin(toss*math.pi),.65*toss,6.4*toss)
    mix.inputs[0].default_value=.92*float(ease(p*2))

for frame in ([23,42,55,79,94] if preview else range(20,110)):
    destination=FRAMES/f'{frame:04}.png'
    if '--resume' in args and destination.exists():
        with destination.open('rb') as existing:header=existing.read(24)
        if len(header)==24 and struct.unpack('>II',header[16:24])==(1920,1080):continue
    pose(frame/30)
    scene.render.filepath=str(destination)
    bpy.ops.render.render(write_still=True)
    print(f'Completed frame {frame}',flush=True)
if not preview:
    pose(2.65)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'source/paper_transition/paper-crumple.blend'))
