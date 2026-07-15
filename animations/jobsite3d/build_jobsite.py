"""
Jobsite 3D — Blender world builder (headless).

Builds the AI Basics presentation as a walkable 3D jobsite: thirteen
stations along a winding path, one per run-of-show beat. Jobsite scenes
become low-poly props in the deck's palette; Sarah's pencil pages stand
as textured exhibit boards. Exports a single GLB for the web walkthrough
plus a preview render for review.

Run:
  /Applications/Blender.app/Contents/MacOS/Blender --background \
      --python jobsite3d/build_jobsite.py
Outputs:
  jobsite3d/walkthrough/jobsite.glb
  jobsite3d/preview.png
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = os.path.dirname(HERE)

# ------------------------------------------------------------- palette ----
PAPER = (0.980, 0.968, 0.937, 1.0)
INK = (0.200, 0.196, 0.243, 1.0)
INK_SOFT = (0.545, 0.541, 0.592, 1.0)
TEAL = (0.180, 0.655, 0.604, 1.0)
TEAL_DARK = (0.122, 0.478, 0.443, 1.0)
AMBER = (1.000, 0.788, 0.302, 1.0)
CORAL = (1.000, 0.541, 0.361, 1.0)
LILAC = (0.765, 0.694, 0.882, 1.0)
SAGE = (0.659, 0.835, 0.635, 1.0)
ALERT = (0.894, 0.341, 0.180, 1.0)
GREY = (0.906, 0.886, 0.839, 1.0)

_mats = {}


def mat(color, name=None):
    key = tuple(round(c, 3) for c in color)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name or f"mat{len(_mats)}")
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.95
    _mats[key] = m
    return m


def box(name, size, loc, color, rot=(0, 0, 0), parent=None, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat(color))
    if bevel:
        b = o.modifiers.new("bevel", 'BEVEL')
        b.width = bevel
        b.segments = 2
    if parent:
        o.parent = parent
    return o


def cyl(name, r, depth, loc, color, rot=(0, 0, 0), parent=None, verts=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc,
                                        rotation=rot, vertices=verts)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat(color))
    if parent:
        o.parent = parent
    return o


def empty(name, loc, rot_z=0.0):
    bpy.ops.object.empty_add(location=loc, rotation=(0, 0, rot_z))
    o = bpy.context.object
    o.name = name
    return o


def label3d(name, text, loc, parent=None, size=0.55, color=INK,
            rot=(math.radians(90), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.body = text
    o.data.size = size
    o.data.align_x = 'CENTER'
    o.data.extrude = 0.02
    o.data.materials.append(mat(color))
    if parent:
        o.parent = parent
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object


# ------------------------------------------------------------ props -------

def truck(parent, with_crane=True, scale=1.0, body=TEAL):
    """Proportions ported from src/jobsite.py's 2D truck (side profile)."""
    s = scale
    # 2D: chassis 4.6x0.32 at z -1.95; ground at -2.55; wheels r 0.40
    box("chassis", (4.6 * s, 1.4 * s, 0.32 * s), (0, 0, 0.60 * s), INK,
        parent=parent)
    # bed: back panel tall (3.55 x 1.45), front panel shorter (x 0.85)
    box("bed_back", (3.55 * s, 1.30 * s, 1.45 * s),
        (-0.85 * s, 0, 1.50 * s), TEAL_DARK, parent=parent)
    box("bed_front", (3.55 * s, 1.42 * s, 0.85 * s),
        (-0.85 * s, 0, 1.20 * s), body, parent=parent)
    # cab 1.35 x 1.45 with paper window + ink eye
    box("cab", (1.35 * s, 1.42 * s, 1.45 * s), (2.05 * s, 0, 1.45 * s),
        body, parent=parent)
    box("window", (0.72 * s, 1.46 * s, 0.52 * s), (2.07 * s, 0, 1.73 * s),
        PAPER, bevel=0.03, parent=parent)
    cyl("eye", 0.07 * s, 1.50 * s, (2.21 * s, 0, 1.73 * s), INK,
        rot=(math.radians(90), 0, 0), parent=parent)
    for i, (x, y) in enumerate([(-2.10, 0.72), (-2.10, -0.72),
                                (-0.55, 0.72), (-0.55, -0.72),
                                (1.95, 0.72), (1.95, -0.72)]):
        cyl(f"wheel{i}", 0.40 * s, 0.30 * s, (x * s, y * s, 0.40 * s), INK,
            rot=(math.radians(90), 0, 0), parent=parent)
        cyl(f"hub{i}", 0.18 * s, 0.32 * s, (x * s, y * s, 0.40 * s),
            INK_SOFT, rot=(math.radians(90), 0, 0), parent=parent)
    if with_crane:
        # 2D crane: mast at x -2.45 (h 1.35), joint z 0.85, boom 48deg
        box("mast", (0.44 * s, 0.40 * s, 1.35 * s),
            (-2.45 * s, 0, 2.85 * s), TEAL_DARK, parent=parent)
        box("boom", (1.45 * s, 0.30 * s, 0.30 * s),
            (-2.95 * s, 0, 4.05 * s), body,
            rot=(0, math.radians(-48), 0), parent=parent)
        cyl("cable", 0.025 * s, 0.85 * s, (-3.42 * s, 0, 3.7 * s), INK,
            parent=parent)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.16 * s, minor_radius=0.045 * s,
            location=(-3.42 * s, 0, 3.15 * s),
            rotation=(math.radians(90), 0, 0))
        hook = bpy.context.object
        hook.name = "hook"
        hook.data.materials.append(mat(INK))
        hook.parent = parent


def cargo_row(parent, colors, z=2.0, s=1.0):
    for i, c in enumerate(colors):
        box(f"cargo{i}", (0.7 * s, 1.2 * s, 0.5 * s),
            ((-1.6 + i * 0.8) * s, 0, z * s), c, parent=parent)


def paver(parent):
    box("pbody", (1.8, 1.4, 1.0), (0, 0, 1.3), TEAL, parent=parent)
    box("hopper", (0.9, 1.0, 0.7), (-0.7, 0, 2.1), TEAL_DARK, parent=parent)
    cyl("roller", 0.5, 1.5, (1.2, 0, 0.5), INK_SOFT,
        rot=(math.radians(90), 0, 0), parent=parent)
    cyl("pwheel", 0.35, 1.4, (-0.7, 0, 0.35), INK,
        rot=(math.radians(90), 0, 0), parent=parent)
    # laid brick road behind
    bricks = [AMBER, CORAL, LILAC, SAGE]
    for i in range(8):
        box(f"brick{i}", (0.75, 1.3, 0.16), (-2.2 - i * 0.85, 0, 0.08),
            bricks[i % 4], parent=parent)


def toolbox_chest(parent, color, loc, label):
    base = box("chest", (1.6, 1.0, 0.6), loc, color, parent=parent)
    box("lid", (1.6, 1.0, 0.25), (loc[0], loc[1], loc[2] + 0.45), color,
        parent=parent)
    label3d("chestlbl", label, (loc[0], loc[1] - 0.55, loc[2] + 0.05),
            parent=parent, size=0.28, color=INK)
    return base


def factory(parent):
    box("hall", (5.0, 3.4, 2.6), (0, 0, 1.3), GREY, parent=parent)
    box("roof", (5.4, 3.8, 0.3), (0, 0, 2.75), TEAL_DARK, parent=parent)
    cyl("stack", 0.35, 2.2, (1.8, -1.0, 3.6), INK_SOFT, parent=parent)
    box("door", (0.2, 1.6, 1.6), (2.55, 0.4, 0.8), INK, parent=parent)
    # the engine on a pedestal out front
    box("pedestal", (1.2, 1.2, 0.5), (4.2, 0, 0.25), INK_SOFT, parent=parent)
    box("engine", (1.0, 0.8, 0.7), (4.2, 0, 0.9), TEAL_DARK, parent=parent)
    for i in range(3):
        cyl(f"piston{i}", 0.12, 0.25, (3.95 + i * 0.25, 0, 1.35), TEAL,
            parent=parent)


def garage(parent):
    box("gwall", (6.0, 4.0, 2.8), (0, -1.0, 1.4), GREY, parent=parent)
    box("groof", (6.5, 4.4, 0.3), (0, -1.0, 2.85), CORAL, parent=parent)
    box("gdoor", (2.6, 0.25, 2.2), (0, 0.95, 1.1), TEAL_DARK, parent=parent)


def shed(parent, loc):
    box("swall", (2.0, 1.6, 1.3), loc, AMBER, parent=parent)
    box("sroof", (2.4, 2.0, 0.25),
        (loc[0], loc[1], loc[2] + 0.8), CORAL, parent=parent)
    box("sdoor", (0.1, 0.6, 0.9),
        (loc[0] + 1.02, loc[1], loc[2] - 0.2), SAGE, parent=parent)


def van(parent, loc, s=0.6, rot_z=0.0):
    p = empty("vanroot", loc, rot_z)
    p.parent = parent
    box("vbody", (2.4 * s, 1.3 * s, 1.2 * s), (0, 0, 1.0 * s), TEAL,
        parent=p)
    box("vcab", (0.8 * s, 1.3 * s, 0.9 * s), (1.5 * s, 0, 0.85 * s),
        TEAL_DARK, parent=p)
    for i, (x, y) in enumerate([(-0.7, 0.7), (-0.7, -0.7), (1.4, 0.7),
                                (1.4, -0.7)]):
        cyl(f"vwheel{i}", 0.3 * s, 0.25 * s, (x * s, y * s, 0.3 * s), INK,
            rot=(math.radians(90), 0, 0), parent=p)


def exhibit(parent, image_path, loc, rot_z, w=5.0):
    """Sarah's pencil page on a standing board."""
    img = bpy.data.images.load(image_path)
    h = w * img.size[1] / img.size[0]
    root = empty("exhibit", loc, rot_z)
    root.parent = parent
    # legs + frame
    for dx in (-w / 2 + 0.15, w / 2 - 0.15):
        box("leg", (0.15, 0.15, 2.2), (dx, 0.05, 1.1), INK, parent=root)
    board = box("board", (w + 0.3, 0.12, h + 0.3), (0, 0, 2.2 + h / 2 - 1.0),
                INK, parent=root)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.08,
                                                       2.2 + h / 2 - 1.0),
                                     rotation=(math.radians(90), 0, 0))
    plane = bpy.context.object
    plane.name = "page"
    plane.scale = (w / 2, h / 2, 1)
    plane.parent = root
    m = bpy.data.materials.new("page_" + os.path.basename(image_path))
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    tex = m.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 1.0
    plane.data.materials.append(m)
    return root


def signpost(parent, number, title, loc):
    p = empty("sign", loc)
    p.parent = parent
    cyl("pole", 0.07, 2.0, (0, 0, 1.0), INK, parent=p)
    box("plank", (2.6, 0.12, 0.7), (0, 0, 2.15), PAPER, parent=p)
    label3d("num", f"{number}", (0, -0.1, 2.28), parent=p, size=0.34,
            color=ALERT)
    label3d("ttl", title, (0, -0.1, 1.92), parent=p, size=0.26, color=INK)


# ------------------------------------------------------------ build -------

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images,
                  bpy.data.curves):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def station_loc(i):
    """Gentle S-curve path, one station every 14 units."""
    return (math.sin(i * 0.55) * 10.0, i * 14.0, 0.0)


def main():
    clear()

    # ground + path
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 84, -0.05))
    g = bpy.context.object
    g.name = "ground"
    g.scale = (60, 120, 1)
    g.data.materials.append(mat(PAPER, "paper"))
    for i in range(12):
        a, b = station_loc(i), station_loc(i + 1)
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0.0)
        ang = math.atan2(b[0] - a[0], b[1] - a[1])
        seg = box(f"path{i}", (2.2, 14.6, 0.02), mid, GREY,
                  rot=(0, 0, -ang))

    SRC = os.path.join(ANIM, "pencil-codex", "source")
    stations = [
        ("00", "THE GARAGE", "garage"),
        ("01", "ENGINE FACTORY", "factory"),
        ("02", "THE PAVER", "paver"),
        ("03", "AGENTIC LOOP", ("exhibit", os.path.join(SRC, "cleaned_page.png"))),
        ("04", "FRONTIER LABS", ("exhibit", os.path.join(SRC, "frontier_labs", "cleaned_page.png"))),
        ("05", "THE HARNESS MAP", ("exhibit", os.path.join(SRC, "harness_mind_map", "cleaned_page.png"))),
        ("06", "THE TOOLBOX", "toolboxes"),
        ("07", "MCP CLI API", ("exhibit", os.path.join(SRC, "mcp_cli_api", "cleaned_page.png"))),
        ("08", "CONTEXT TRUCK", "truck_loaded"),
        ("09", "POP THE HOOD", "truck_crane"),
        ("10", "WHAT IS AN AGENT", ("exhibit", os.path.join(SRC, "what_is_an_agent", "cleaned_page.png"))),
        ("11", "THE FLEET", "fleet"),
        ("12", "ORCHESTRATION", ("exhibit", os.path.join(SRC, "multi_agent_orchestration", "cleaned_page.png"))),
    ]

    for i, (num, title, kind) in enumerate(stations):
        loc = station_loc(i)
        root = empty(f"station{num}", loc)
        # face the path: rotate exhibits/props toward walk direction
        if isinstance(kind, tuple) and kind[0] == "exhibit":
            exhibit(root, kind[1], (3.8, 0, 0), math.radians(-20))
        elif kind == "garage":
            g2 = empty("garage_root", (0, 0, 0))
            g2.parent = root
            garage(g2)
            g2.location = (-5.0, 0, 0)
        elif kind == "factory":
            f = empty("factory_root", (-5.5, 0, 0))
            f.parent = root
            factory(f)
        elif kind == "paver":
            p = empty("paver_root", (4.5, 0, 0), math.radians(90))
            p.parent = root
            paver(p)
        elif kind == "toolboxes":
            t = empty("tb_root", (4.0, 0, 0))
            t.parent = root
            toolbox_chest(t, LILAC, (0, 0, 0.3), "TICKETS")
            toolbox_chest(t, AMBER, (2.0, 0.6, 0.3), "CALENDAR")
            toolbox_chest(t, SAGE, (1.0, -0.9, 0.3), "WIKI")
        elif kind == "truck_loaded":
            t = empty("truck_root", (-5.0, 0, 0), math.radians(90))
            t.parent = root
            truck(t, with_crane=False)
            cargo_row(t, [AMBER, LILAC, SAGE, CORAL])
        elif kind == "truck_crane":
            t = empty("truck2_root", (-5.0, 0, 0), math.radians(90))
            t.parent = root
            truck(t, with_crane=True)
        elif kind == "fleet":
            t = empty("fleet_root", (-5.5, 0, 0), math.radians(90))
            t.parent = root
            truck(t, with_crane=True)
            van(root, (4.0, -2.0, 0), rot_z=math.radians(60))
            van(root, (5.5, 0.5, 0), rot_z=math.radians(90))
            van(root, (4.2, 3.0, 0), rot_z=math.radians(120))
            shed(root, (8.0, 1.0, 0.65))
        signpost(root, num, title, (-2.8 if isinstance(kind, tuple) else 2.8,
                                    -1.5, 0))

    # a doodle sun: emissive sphere high above
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.0, location=(-30, 40, 35))
    sun_ball = bpy.context.object
    sun_ball.name = "sunball"
    sm = bpy.data.materials.new("sunmat")
    sm.use_nodes = True
    sb = sm.node_tree.nodes["Principled BSDF"]
    sb.inputs["Base Color"].default_value = AMBER
    sb.inputs["Emission Color"].default_value = AMBER
    sb.inputs["Emission Strength"].default_value = 3.0
    sun_ball.data.materials.append(sm)

    bpy.ops.object.light_add(type='SUN', location=(20, 40, 60))
    sun = bpy.context.object
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(35), math.radians(15), 0)
    bpy.ops.object.light_add(type='SUN', location=(-20, 100, 60))
    fill = bpy.context.object
    fill.data.energy = 1.2
    fill.rotation_euler = (math.radians(60), math.radians(-25),
                           math.radians(180))

    world = bpy.data.worlds["World"]
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = \
        (0.92, 0.95, 0.98, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

    # ---------------------------------------------------------- export ----
    out_dir = os.path.join(HERE, "walkthrough")
    os.makedirs(out_dir, exist_ok=True)
    glb = os.path.join(out_dir, "jobsite.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB',
                              export_yup=True, export_apply=True)
    print("EXPORTED", glb, os.path.getsize(glb), "bytes")

    # --------------------------------------------------------- preview ----
    bpy.ops.object.camera_add(location=(16, -22, 14),
                              rotation=(math.radians(70), 0,
                                        math.radians(32)))
    cam = bpy.context.object
    bpy.context.scene.camera = cam
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_EEVEE_NEXT' \
        if hasattr(bpy.types, 'RenderSettings') and \
        'BLENDER_EEVEE_NEXT' in \
        scn.render.bl_rna.properties['engine'].enum_items else 'BLENDER_EEVEE'
    scn.render.resolution_x = 1280
    scn.render.resolution_y = 720
    scn.view_settings.view_transform = 'Standard'  # honest palette colors
    scn.render.filepath = os.path.join(HERE, "preview.png")
    bpy.ops.render.render(write_still=True)
    print("PREVIEW", scn.render.filepath)


if __name__ == "__main__":
    main()
