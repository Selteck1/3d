"""Retro PC low-poly generator for Blender 3.6+.

Run from Blender > Scripting > Open > Run Script.
Creates a retro desktop tower, unwraps all geometry together, bakes one
4096px Base Color atlas and exports GLB + PNG + BLEND.
"""
import bpy
import math
import os

# ---------- Settings ----------
ATLAS_SIZE = 4096
UV_MARGIN = 0.008
BAKE_MARGIN = 12
SEPARATE_LOOSE_PARTS = True
OUT = bpy.path.abspath("//") if bpy.data.filepath else os.path.join(os.path.expanduser("~"), "Desktop")
os.makedirs(OUT, exist_ok=True)

# ---------- Scene reset ----------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def make_mat(name, color, metal=0.0, rough=0.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    return m

M = {
    "case": make_mat("src_case_powdercoat", (0.105, 0.115, 0.135), 0.55, 0.72),
    "black": make_mat("src_black_plastic", (0.025, 0.028, 0.034), 0.04, 0.82),
    "silver": make_mat("src_brushed_aluminium", (0.48, 0.50, 0.54), 0.78, 0.40),
    "dark": make_mat("src_dark_anodized", (0.18, 0.19, 0.22), 0.72, 0.55),
    "mesh": make_mat("src_grille_metal", (0.23, 0.25, 0.28), 0.70, 0.58),
    "rubber": make_mat("src_rubber", (0.012, 0.014, 0.016), 0.0, 0.92),
    "blue": make_mat("src_blue_led", (0.035, 0.16, 0.48), 0.18, 0.35),
    "red": make_mat("src_red_badge", (0.42, 0.035, 0.028), 0.12, 0.48),
}

def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    obj.data.name = name + "_mesh"
    obj.data.materials.append(M[mat])
    if bevel > 0:
        mod = obj.modifiers.new("Small chamfers", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

def box(name, loc, size, mat="black", bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat, bevel)

def cyl(name, loc, radius, depth, mat="dark", axis="Y", sides=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    if axis == "Y":
        o.rotation_euler[0] = math.radians(90)
    elif axis == "X":
        o.rotation_euler[1] = math.radians(90)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return finish(o, name, mat, 0.003)

def ring(name, loc, major, minor, mat="dark"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                    major_segments=32, minor_segments=6, location=loc)
    o = bpy.context.object
    o.rotation_euler[0] = math.radians(90)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return finish(o, name, mat)

# Coordinate system: front -Y, rear +Y, top +Z.
# ---------- Chassis ----------
box("Main chassis", (0, 0, 1.82), (2.0, 3.55, 3.58), "case", 0.085)
box("Front bezel", (0, -1.79, 1.82), (1.96, 0.12, 3.45), "black", 0.025)
box("Left side cover", (-1.015, 0.02, 1.83), (0.035, 3.32, 3.34), "case", 0.018)
box("Right side cover", (1.015, 0.02, 1.83), (0.035, 3.32, 3.34), "case", 0.018)
box("Top trim", (0, 0, 3.63), (1.86, 3.32, 0.028), "dark")

# ---------- Front ----------
box("Silver fascia", (0, -1.865, 2.46), (1.78, 0.075, 1.48), "silver", 0.018)
box("Lower front bezel", (0, -1.865, 0.78), (1.82, 0.065, 1.50), "black", 0.018)
box("Optical drive", (0, -1.918, 2.96), (1.53, 0.055, 0.42), "dark", 0.012)
box("Drive slot", (0, -1.952, 2.96), (1.30, 0.012, 0.035), "black")
box("Drive lip", (0, -1.955, 3.055), (1.40, 0.010, 0.012), "black")
box("Drive eject button", (0.66, -1.958, 2.91), (0.075, 0.025, 0.065), "silver", 0.006)
box("Drive LED", (0.53, -1.958, 2.91), (0.022, 0.012, 0.022), "blue")
box("Drive pinhole", (-0.62, -1.958, 2.91), (0.018, 0.012, 0.018), "black")
box("Brand badge", (0, -1.919, 2.47), (0.24, 0.025, 0.25), "dark", 0.012)
box("Brand mark", (0, -1.937, 2.49), (0.075, 0.012, 0.09), "red")
box("Upper bay", (0, -1.918, 2.18), (1.50, 0.035, 0.29), "silver", 0.008)
box("Lower bay", (0, -1.918, 1.81), (1.50, 0.035, 0.29), "silver", 0.008)
box("Bay separator", (0, -1.944, 1.995), (1.48, 0.012, 0.018), "dark")

# Real grille bars with gaps between them.
box("Front grille shadow", (0, -1.923, 0.78), (1.64, 0.018, 1.22), "black")
box("Front grille backing", (0, -1.936, 0.78), (1.56, 0.012, 1.14), "rubber")
for x in (-0.83, 0.83):
    box("Front grille side rail", (x, -1.963, 0.78), (0.035, 0.035, 1.24), "dark")
for z in (0.16, 1.40):
    box("Front grille edge rail", (0, -1.963, z), (1.69, 0.035, 0.035), "dark")
for i in range(29):
    box("Front grille vertical", (-0.77 + i*0.055, -1.965, 0.78), (0.008, 0.025, 1.16), "mesh")
for i in range(22):
    box("Front grille horizontal", (0, -1.966, 0.20 + i*0.055), (1.58, 0.025, 0.008), "mesh")

box("Power control bezel", (0, -1.965, 1.48), (0.38, 0.07, 0.48), "dark", 0.012)
box("Power control inset", (0, -2.005, 1.49), (0.28, 0.018, 0.36), "black")
box("Power button", (0, -2.021, 1.60), (0.20, 0.025, 0.16), "blue", 0.012)
box("Power button rim", (0, -2.025, 1.60), (0.235, 0.008, 0.19), "silver")
box("Power LED", (0, -2.022, 1.34), (0.025, 0.012, 0.065), "blue")
for x in (-0.34, -0.12, 0.12, 0.34):
    cyl("Front port rim", (x, -1.972, 0.15), 0.055, 0.024, "dark", "Y")
    cyl("Front port hole", (x, -1.990, 0.15), 0.034, 0.014, "black", "Y")
for x in (-0.12, 0.12):
    box("USB insert", (x, -2.001, 0.15), (0.036, 0.009, 0.010), "blue")

# ---------- Side vents ----------
box("Side vent well", (-1.049, -0.25, 1.88), (0.018, 1.17, 1.70), "black")
for y in (-0.84, 0.34):
    box("Side vent frame", (-1.075, y, 1.88), (0.045, 0.045, 1.74), "dark")
for z in (1.02, 2.74):
    box("Side vent frame", (-1.075, -0.25, z), (0.045, 1.22, 0.045), "dark")
for i in range(22):
    box("Side grille vertical", (-1.078, -0.78+i*0.052, 1.88), (0.022, 0.008, 1.66), "mesh")
for i in range(31):
    box("Side grille horizontal", (-1.079, -0.25, 1.08+i*0.052), (0.022, 1.10, 0.008), "mesh")
box("Lower side vent well", (-1.048, -0.20, 0.55), (0.018, 1.02, 0.65), "black")
for i in range(21):
    box("Lower side grille vertical", (-1.08, -0.67+i*0.045, 0.55), (0.02, 0.008, 0.65), "mesh")
for i in range(14):
    box("Lower side grille horizontal", (-1.081, -0.20, 0.24+i*0.045), (0.02, 1.00, 0.008), "mesh")
for y in (-1.52, 1.52):
    for z in (0.22, 3.40):
        cyl("Panel screw", (-1.05, y, z), 0.026, 0.018, "dark", "X", 12)
cyl("Thumb screw", (-1.05, 1.38, 3.12), 0.085, 0.025, "dark", "X", 24)

# ---------- Top vents ----------
box("Top vent well", (0, 1.22, 3.645), (1.18, 0.62, 0.018), "black")
for i in range(18):
    box("Top vent slat", (-0.51+i*0.06, 1.22, 3.657), (0.025, 0.48, 0.012), "mesh")

# ---------- Rear fan, ports, slots and PSU ----------
box("Rear panel", (0, 1.795, 1.82), (1.88, 0.07, 3.40), "dark")
box("Rear fan well", (-0.48, 1.842, 2.78), (0.78, 0.025, 0.78), "black")
ring("Rear fan ring", (-0.48, 1.865, 2.78), 0.31, 0.025, "silver")
cyl("Rear fan hub", (-0.48, 1.87, 2.78), 0.075, 0.028, "black", "Y")
for a_deg in (0, 45, 90, 135):
    a = math.radians(a_deg)
    x = -0.48 + math.cos(a)*0.18
    z = 2.78 + math.sin(a)*0.18
    s = box("Rear fan spoke", (x, 1.873, z), (0.36, 0.025, 0.035), "mesh")
    s.rotation_euler[1] = -a
    bpy.context.view_layer.objects.active = s
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

box("Rear IO recess", (0.50, 1.842, 2.88), (0.70, 0.025, 0.94), "black")
for i in range(3):
    x = 0.30+i*0.18
    box("Rear USB port", (x, 1.867, 3.17), (0.12, 0.025, 0.10), "dark")
    box("Rear USB insert", (x, 1.883, 3.17), (0.075, 0.012, 0.05), "blue")
box("Ethernet port", (0.48, 1.868, 2.83), (0.23, 0.035, 0.19), "dark")
box("Audio stack", (0.68, 1.87, 2.50), (0.16, 0.035, 0.38), "black")
for z in (2.61, 2.50, 2.39):
    cyl("Audio socket", (0.68, 1.897, z), 0.035, 0.025, "blue", "Y", 16)

box("Expansion bay recess", (0.52, 1.842, 1.47), (0.83, 0.025, 1.10), "black")
for i in range(7):
    z = 1.91-i*0.145
    box("Expansion slot", (0.53, 1.867, z), (0.77, 0.035, 0.11), "dark")
    for x in (0.22, 0.84):
        box("Expansion screw", (x, 1.891, z), (0.035, 0.018, 0.035), "silver")

box("PSU recess", (-0.46, 1.842, 0.52), (0.82, 0.025, 0.76), "black")
box("PSU face", (-0.46, 1.865, 0.52), (0.74, 0.025, 0.68), "dark")
ring("PSU fan ring", (-0.46, 1.89, 0.52), 0.23, 0.018, "black")
cyl("PSU fan hub", (-0.46, 1.892, 0.52), 0.045, 0.020, "black", "Y", 16)
for z in (0.30, 0.52, 0.74):
    box("PSU grille bar", (-0.46, 1.894, z), (0.58, 0.018, 0.012), "mesh")
box("PSU socket", (-0.46, 1.895, 0.93), (0.28, 0.025, 0.10), "black")
box("PSU switch", (-0.22, 1.895, 0.93), (0.10, 0.025, 0.10), "dark")

# ---------- Feet and trim ----------
for x in (-0.72, 0.72):
    for y in (-1.28, 1.28):
        box("Rubber foot", (x, y, 0.035), (0.38, 0.48, 0.14), "rubber", 0.025)
        box("Foot mount", (x, y, 0.11), (0.30, 0.38, 0.08), "dark", 0.012)
for x in (-0.94, 0.94):
    box("Front corner trim", (x, -1.858, 1.82), (0.035, 0.025, 3.30), "dark")

# ---------- Join and UV unwrap ----------
parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
pc = bpy.context.object
pc.name = "Retro PC | Single Atlas Mesh"

bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=UV_MARGIN,
                          area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")

# ---------- Bake one Base Color image ----------
atlas = bpy.data.images.new("Retro PC | One Texture Atlas", ATLAS_SIZE, ATLAS_SIZE, alpha=False)
atlas.generated_color = (0.035, 0.04, 0.05, 1.0)
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for n in nodes:
        n.select = False
    target = nodes.new("ShaderNodeTexImage")
    target.name = "Shared bake target"
    target.image = atlas
    target.select = True
    nodes.active = target

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.render.bake.margin = BAKE_MARGIN
scene.render.bake.use_clear = True
bpy.ops.object.select_all(action="DESELECT")
pc.select_set(True)
bpy.context.view_layer.objects.active = pc
bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})

atlas_path = os.path.join(OUT, "retro_pc_single_texture_atlas.png")
atlas.filepath_raw = atlas_path
atlas.file_format = "PNG"
atlas.save()

# One final material, one texture image for all polygons.
final_mat = bpy.data.materials.new("Retro PC | Single Atlas Material")
final_mat.use_nodes = True
nodes = final_mat.node_tree.nodes
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
image_node = nodes.new("ShaderNodeTexImage")
image_node.image = atlas
final_mat.node_tree.links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])
final_mat.node_tree.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
bsdf.inputs["Metallic"].default_value = 0.28
bsdf.inputs["Roughness"].default_value = 0.58

pc.data.materials.clear()
pc.data.materials.append(final_mat)
for p in pc.data.polygons:
    p.material_index = 0

# Optionally split disconnected components back into separate selectable objects.
if SEPARATE_LOOSE_PARTS:
    bpy.ops.object.select_all(action="DESELECT")
    pc.select_set(True)
    bpy.context.view_layer.objects.active = pc
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
        o.data.materials.clear()
        o.data.materials.append(final_mat)
        for p in o.data.polygons:
            p.material_index = 0

atlas.pack()
blend_path = os.path.join(OUT, "retro_pc_single_atlas.blend")
glb_path = os.path.join(OUT, "retro_pc_single_atlas.glb")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = next(o for o in bpy.context.scene.objects if o.type == "MESH")
bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB", use_selection=True,
                           export_materials="EXPORT", export_texcoords=True,
                           export_normals=True, export_apply=True)

print("Created one-texture PC:", glb_path)
print("Texture atlas:", atlas_path)
print("Editable Blender project:", blend_path)
