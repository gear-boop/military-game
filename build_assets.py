import bpy, math, os, sys, json
from mathutils import Vector, Euler


argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else os.path.join(os.getcwd(), 'assets')
os.makedirs(OUT, exist_ok=True)

D = math.radians


def clean():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)


def mat(name, color, metallic=0.0, rough=0.8, emit=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = rough
    if emit > 0:
        bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emit
    return m

def box(name, size, origin=(0,0,0), rot=(0,0,0), material=None, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=origin, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], size[2])  
    if material: o.data.materials.append(material)
    if parent: o.parent = parent
    return o

def cyl(name, r1, r2, depth, origin=(0,0,0), rot=(0,0,0), verts=12, material=None, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r1, depth=depth, location=origin, rotation=rot)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if parent: o.parent = parent
    return o

def cone(name, r, depth, origin=(0,0,0), rot=(0,0,0), verts=12, material=None, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=0, depth=depth, location=origin, rotation=rot)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if parent: o.parent = parent
    return o

def sph(name, r, origin=(0,0,0), material=None, parent=None, seg=12, ring=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=origin)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if parent: o.parent = parent
    return o

def torus(name, R, r, origin=(0,0,0), rot=(0,0,0), material=None, parent=None, maj=16, mino=8):
    bpy.ops.mesh.primitive_torus_add(major_segments=maj, minor_segments=mino, major_radius=R, minor_radius=r, location=origin, rotation=rot)
    o = bpy.context.object
    o.name = name
    if material: o.data.materials.append(material)
    if parent: o.parent = parent
    return o

def empty(name, origin=(0,0,0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = origin
    e.empty_display_size = 0.1
    bpy.context.scene.collection.objects.link(e)
    if parent: e.parent = parent
    return e

def group(name, origin=(0,0,0)):
    e = empty(name, origin)
    return e


def zup(obj):
    obj.rotation_euler = Euler((D(-90), 0, 0), 'XYZ')
    return obj


M = {}
M['gun_black']   = mat('gun_black',   (0.055,0.06,0.065), metallic=0.75, rough=0.38)
M['gun_steel']   = mat('gun_steel',   (0.16,0.17,0.18),  metallic=0.85, rough=0.32)
M['gun_dark']    = mat('gun_dark',    (0.09,0.10,0.09),  metallic=0.6,  rough=0.5)
M['gun_poly']    = mat('gun_poly',    (0.10,0.11,0.095), metallic=0.15, rough=0.65)
M['gun_poly_tan']= mat('gun_poly_tan',(0.42,0.36,0.25),  metallic=0.1,  rough=0.7)
M['gun_wood']    = mat('gun_wood',    (0.28,0.16,0.07),  metallic=0.0,  rough=0.75)
M['gun_green']   = mat('gun_green',   (0.13,0.17,0.10),  metallic=0.25, rough=0.6)
M['lens']        = mat('lens',        (0.35,0.65,1.0),   metallic=0.0,  rough=0.1, emit=2.5)
M['olive']       = mat('olive',       (0.16,0.20,0.11),  metallic=0.1,  rough=0.8)
M['olive_dark']  = mat('olive_dark',  (0.10,0.13,0.07),  metallic=0.1,  rough=0.85)
M['sand']        = mat('sand',        (0.45,0.39,0.24),  metallic=0.0,  rough=0.95)
M['concrete']    = mat('concrete',    (0.32,0.33,0.31),  metallic=0.0,  rough=0.95)
M['concrete_d']  = mat('concrete_d',  (0.22,0.23,0.21),  metallic=0.0,  rough=0.95)
M['metal']       = mat('metal',       (0.30,0.33,0.30),  metallic=0.8,  rough=0.45)
M['metal_d']     = mat('metal_d',     (0.16,0.18,0.16),  metallic=0.75, rough=0.55)
M['rust_red']    = mat('rust_red',    (0.38,0.10,0.06),  metallic=0.4,  rough=0.7)
M['tire']        = mat('tire',        (0.03,0.03,0.03),  metallic=0.0,  rough=0.95)
M['glass']       = mat('glass',       (0.55,0.70,0.78),  metallic=0.9,  rough=0.15)
M['crate']       = mat('crate',       (0.34,0.29,0.17),  metallic=0.0,  rough=0.9)
M['skin']        = mat('skin',        (0.65,0.48,0.34),  metallic=0.0,  rough=0.8)
M['vest_f']      = mat('vest_f',      (0.13,0.16,0.10),  metallic=0.05, rough=0.9)
M['vest_h']      = mat('vest_h',      (0.23,0.14,0.10),  metallic=0.05, rough=0.9)
M['cloth_f']     = mat('cloth_f',     (0.18,0.24,0.13),  metallic=0.0,  rough=0.95)
M['cloth_h']     = mat('cloth_h',     (0.30,0.22,0.14),  metallic=0.0,  rough=0.95)
M['helmet_f']    = mat('helmet_f',    (0.15,0.19,0.12),  metallic=0.1,  rough=0.7)
M['helmet_h']    = mat('helmet_h',    (0.28,0.20,0.13),  metallic=0.1,  rough=0.7)
M['boot']        = mat('boot',        (0.06,0.06,0.05),  metallic=0.0,  rough=0.9)
M['frag']        = mat('frag',        (0.20,0.25,0.10),  metallic=0.3,  rough=0.6)
M['med']         = mat('med',         (0.15,0.55,0.25),  metallic=0.0,  rough=0.5, emit=0.4)
M['armor']       = mat('armor',       (0.18,0.38,0.60),  metallic=0.0,  rough=0.5, emit=0.4)
M['ammo']        = mat('ammo',        (0.65,0.45,0.15),  metallic=0.0,  rough=0.5, emit=0.4)
M['red_glow']    = mat('red_glow',    (1.0,0.15,0.1),    metallic=0.0,  rough=0.5, emit=3.0)


def g_group(name):
    return group(name)

def add_receiver(g, L, H=0.05, W=0.032, mtl=None, yoff=0.0):
    return box('receiver', (W, L, H), origin=(0, yoff, 0), material=mtl or M['gun_poly'], parent=g)

def add_barrel(g, L, r=0.010, y0=None, mtl=None):
    y0 = (y0 if y0 is not None else -L/2)
    c = cyl('barrel', r, r, L, origin=(0, y0, 0.004), rot=(D(90),0,0), verts=10, material=mtl or M['gun_steel'], parent=g)
    return c

def add_grip(g, mtl=None, h=0.075):
    b = box('grip', (0.026, 0.03, h), origin=(0, 0.03, -h/2-0.01), rot=(D(-18),0,0), material=mtl or M['gun_poly'], parent=g)
    return b

def add_mag(g, h=0.09, curved=False, mtl=None, yoff=0.0):
    if curved:
        m = box('mag', (0.024, 0.03, h), origin=(0, -0.005+yoff, -h/2-0.045), rot=(D(-12),0,0), material=mtl or M['gun_dark'], parent=g)
    else:
        m = box('mag', (0.024, 0.032, h), origin=(0, -0.01+yoff, -h/2-0.05), material=mtl or M['gun_dark'], parent=g)
    return m

def add_stock(g, L=0.16, mtl=None):
    return box('stock', (0.03, L, 0.05), origin=(0, L/2+0.05, -0.005), material=mtl or M['gun_poly'], parent=g)

def add_scope(g, L=0.14, r=0.017, y=-0.02, mtl=None):
    s = cyl('scope', r, r, L, origin=(0, y, 0.045), rot=(D(90),0,0), verts=10, material=mtl or M['gun_black'], parent=g)
    lens = cyl('lens', r*0.8, r*0.8, 0.004, origin=(0, y-L/2-0.002, 0.045), rot=(D(90),0,0), verts=10, material=M['lens'], parent=g)
    mnt = box('scope_mount', (0.012, 0.05, 0.02), origin=(0, y, 0.03), material=M['gun_black'], parent=g)
    return s

def add_iron_sights(g):
    f = box('sight_front', (0.006, 0.008, 0.02), origin=(0, -0.14, 0.032), material=M['gun_black'], parent=g)
    r = box('sight_rear', (0.024, 0.008, 0.012), origin=(0, 0.06, 0.03), material=M['gun_black'], parent=g)

def add_rail(g, L=0.3):
    box('rail', (0.016, L, 0.008), origin=(0, -L/2+0.06, 0.028), material=M['gun_black'], parent=g)

def add_handguard(g, L=0.24, mtl=None):
    return box('handguard', (0.036, L, 0.04), origin=(0, -0.10-L/2, 0.002), material=mtl or M['gun_poly'], parent=g)

def add_pump(g):
    return box('pump', (0.03, 0.09, 0.03), origin=(0, -0.20, -0.02), material=M['gun_wood'], parent=g)

def add_muzzle_brake(g, r=0.016, L=0.05):
    return cyl('brake', r, r, L, origin=(0, -0.36, 0.004), rot=(D(90),0,0), verts=10, material=M['gun_black'], parent=g)

def add_ammo_box(g):
    return box('ammobox', (0.07, 0.10, 0.07), origin=(-0.055, 0.02, -0.02), material=M['gun_green'], parent=g)

def add_belt(g):=
    for i in range(6):
        a = i/5
        y = 0.02 - a*0.06
        z = -0.02 - math.sin(a*math.pi)*0.03
        box('belt%d'%i, (0.008, 0.012, 0.012), origin=(-0.045+ (0.02*a), y, z), material=M['brass'] if 'brass' in M else M['ammo'], parent=g)

def add_trigger(g):
    box('trigger_guard', (0.008, 0.03, 0.012), origin=(0, 0.045, -0.025), material=M['gun_black'], parent=g)
    box('trigger', (0.006, 0.008, 0.02), origin=(0, 0.045, -0.02), material=M['gun_steel'], parent=g)


def build_pistol(g, big=False, tan=False):
    mtl = M['gun_poly_tan'] if tan else M['gun_poly']
    L = 0.24 if big else 0.19
    box('slide', (0.03, L, 0.032), origin=(0, -L*0.18, 0.014), material=M['gun_steel'] if not tan else M['gun_poly_tan'], parent=g)
    box('frame', (0.028, L*0.75, 0.026), origin=(0, -L*0.10, -0.012), material=mtl, parent=g)
    add_grip(g, mtl)
    add_mag(g, h=0.05 if not big else 0.06)
    add_trigger(g)
    add_iron_sights(g)
    if big: add_muzzle_brake(g, r=0.012, L=0.03)

def build_smg(g, bullpup=False, helical=False, drum=False):
    add_receiver(g, 0.30)
    add_barrel(g, 0.14, r=0.009, y0=-0.20)
    add_handguard(g, 0.12)
    add_grip(g)
    add_trigger(g)
    if helical:
        cyl('helimag', 0.022, 0.022, 0.13, origin=(0, 0.02, -0.05), rot=(D(90),0,0), verts=10, material=M['gun_black'], parent=g)
    elif drum:
        cyl('drum', 0.045, 0.045, 0.03, origin=(0, -0.01, -0.075), rot=(0,D(0),0), verts=14, material=M['gun_dark'], parent=g)
    else:
        add_mag(g, h=0.14)
    if not bullpup:
        add_stock(g, 0.14)
    else:
        box('bullpup_shell', (0.05, 0.16, 0.06), origin=(0, 0.14, 0.0), material=M['gun_poly'], parent=g)
    add_rail(g, 0.22)
    add_iron_sights(g)

def build_rifle(g, wood=False, tan=False, bullpup=False, heavy=False):
    mtl = M['gun_wood'] if wood else (M['gun_poly_tan'] if tan else M['gun_poly'])
    add_receiver(g, 0.26, H=0.055 if heavy else 0.05)
    add_barrel(g, 0.30, r=0.011 if not heavy else 0.013, y0=-0.26)
    add_handguard(g, 0.20, mtl)
    add_grip(g, mtl)
    add_trigger(g)
    add_mag(g, h=0.11 if not heavy else 0.08)
    add_stock(g, 0.17, mtl)
    if bullpup:
        box('bullpup', (0.05, 0.14, 0.065), origin=(0, 0.10, 0.0), material=mtl, parent=g)
    add_rail(g, 0.26)
    add_iron_sights(g)
    if heavy:
        add_muzzle_brake(g)

def build_dmr(g, wood=False):
    mtl = M['gun_wood'] if wood else M['gun_poly']
    add_receiver(g, 0.30)
    add_barrel(g, 0.38, r=0.012, y0=-0.32)
    add_handguard(g, 0.22, mtl)
    add_grip(g, mtl)
    add_trigger(g)
    add_mag(g, h=0.09)
    add_stock(g, 0.20, mtl)
    add_scope(g, 0.16, y=-0.03)
    if wood: add_iron_sights(g)

def build_sniper(g, big=False):
    add_receiver(g, 0.32)
    add_barrel(g, 0.46 if not big else 0.56, r=0.013 if not big else 0.017, y0=-0.38 if not big else -0.46)
    add_handguard(g, 0.24)
    add_grip(g)
    add_trigger(g)
    add_mag(g, h=0.07)
    add_stock(g, 0.22)
    box('cheekrest', (0.03, 0.08, 0.02), origin=(0, 0.22, 0.02), material=M['gun_poly'], parent=g)
    add_scope(g, 0.20, r=0.02, y=-0.05)
    if big: add_muzzle_brake(g, r=0.022, L=0.08)

def build_shotgun(g, auto=False):
    add_receiver(g, 0.28)
    add_barrel(g, 0.34, r=0.014, y0=-0.30)
    add_pump(g)
    add_grip(g)
    add_trigger(g)
    add_mag(g, h=0.05)
    add_stock(g, 0.17, M['gun_poly'])
    box('tube', (0.024, 0.30, 0.024), origin=(0, -0.30, -0.022), material=M['gun_dark'], parent=g)
    if auto: add_mag(g, h=0.10)

def build_lmg(g):
    add_receiver(g, 0.32, H=0.06)
    add_barrel(g, 0.36, r=0.014, y0=-0.32)
    box('heatshield', (0.05, 0.24, 0.05), origin=(0, -0.24, 0.0), material=M['gun_dark'], parent=g)
    add_grip(g)
    add_trigger(g)
    add_ammo_box(g)
    add_belt(g)
    add_stock(g, 0.16)
    b1 = cyl('bipodL', 0.005, 0.005, 0.16, origin=(-0.02, -0.30, -0.09), rot=(D(20),0,D(14)), verts=6, material=M['gun_black'], parent=g)
    b2 = cyl('bipodR', 0.005, 0.005, 0.16, origin=(0.02, -0.30, -0.09), rot=(D(20),0,D(-14)), verts=6, material=M['gun_black'], parent=g)

def build_minigun(g):
    box('body', (0.09, 0.24, 0.11), origin=(0, 0.10, 0.0), material=M['gun_dark'], parent=g)
    for i in range(6):
        a = i/6*math.tau
        x = math.cos(a)*0.033
        z = math.sin(a)*0.033
        cyl('gbarrel%d'%i, 0.009, 0.009, 0.46, origin=(x, -0.28, z), rot=(D(90),0,0), verts=8, material=M['gun_steel'], parent=g)
    cyl('housing', 0.05, 0.05, 0.08, origin=(0, -0.06, 0), rot=(D(90),0,0), verts=12, material=M['gun_black'], parent=g)
    add_ammo_box(g)
    box('handleL', (0.02, 0.03, 0.10), origin=(-0.07, 0.20, -0.04), material=M['gun_poly'], parent=g)
    box('handleR', (0.02, 0.03, 0.10), origin=(0.07, 0.20, -0.04), material=M['gun_poly'], parent=g)

def build_hmg(g):
    add_receiver(g, 0.36, H=0.07, W=0.045)
    add_barrel(g, 0.50, r=0.019, y0=-0.44)
    add_muzzle_brake(g, r=0.026, L=0.09)
    add_grip(g)
    add_trigger(g)
    add_ammo_box(g)
    add_belt(g)
    box('spade', (0.02, 0.10, 0.16), origin=(0, 0.26, -0.05), material=M['gun_green'], parent=g)

def build_glm(g):
    add_receiver(g, 0.34, H=0.08, W=0.05)
    add_barrel(g, 0.34, r=0.024, y0=-0.36)
    box('barrel_hous', (0.07, 0.14, 0.07), origin=(0, -0.22, 0), material=M['gun_dark'], parent=g)
    add_grip(g)
    add_trigger(g)
    add_ammo_box(g)
    add_belt(g)
    add_stock(g, 0.14)

def build_launcher(g, rpg=False, stinger=False):
    cyl('tube', 0.045, 0.05, 1.0, origin=(0, -0.10, 0.02), rot=(D(90),0,0), verts=14,
        material=M['gun_wood'] if rpg else M['gun_green'], parent=g)
    if rpg:
        cone('warhead', 0.055, 0.22, origin=(0, -0.68, 0.02), rot=(D(-90),0,0), verts=12, material=M['rust_red'], parent=g)
        cyl('rear flare', 0.05, 0.075, 0.12, origin=(0, 0.44, 0.02), rot=(D(90),0,0), verts=12, material=M['gun_wood'], parent=g)
        add_grip(g)
        box('sight_block', (0.03, 0.05, 0.06), origin=(0.03, -0.05, 0.06), material=M['gun_steel'], parent=g)
    elif stinger:
        box('grip_unit', (0.06, 0.10, 0.12), origin=(0, 0.05, -0.10), material=M['gun_dark'], parent=g)
        box('sight_unit', (0.05, 0.14, 0.10), origin=(0, -0.05, 0.10), material=M['gun_dark'], parent=g)
        cyl('iff_antenna', 0.004, 0.004, 0.18, origin=(0.05, 0.10, 0.18), verts=6, material=M['gun_black'], parent=g)
    else:
        add_grip(g)
        box('front_grip', (0.024, 0.03, 0.08), origin=(0, -0.30, -0.06), material=M['gun_poly'], parent=g)

BUILDERS = {

  'p_m9':      lambda g: build_pistol(g),
  'p_1911':    lambda g: build_pistol(g, big=False),
  'p_m17':     lambda g: build_pistol(g, tan=True),
  'p_deagle':  lambda g: build_pistol(g, big=True),
  'p_mk23':    lambda g: build_pistol(g, big=True, tan=True),
  'p_g18':     lambda g: build_pistol(g) and None or (add_mag(g, h=0.09), add_stock(g, 0.10)),

  's_mp5':     lambda g: build_smg(g),
  's_mp7':     lambda g: build_smg(g),
  's_p90':     lambda g: build_smg(g, bullpup=True, helical=True),
  's_thompson':lambda g: (build_smg(g), [setattr(o, 'active_material', M['gun_wood']) for o in g.children if o.name.startswith(('receiver','stock','handguard'))]),
  's_bizon':   lambda g: build_smg(g, helical=True),
  's_vector':  lambda g: build_smg(g),

  'r_m4a1':    lambda g: build_rifle(g),
  'r_m16a4':   lambda g: build_rifle(g) and None or add_scope(g, 0.12, r=0.014, y=-0.02),
  'r_ak47':    lambda g: build_rifle(g, wood=True) or add_mag(g, h=0.13, curved=True, yoff=0.01),
  'r_ak74':    lambda g: build_rifle(g, wood=True) or add_mag(g, h=0.12, curved=True, yoff=0.01),
  'r_scarl':   lambda g: build_rifle(g, tan=True),
  'r_scarh':   lambda g: build_rifle(g, tan=True, heavy=True),
  'r_hk416':   lambda g: build_rifle(g),
  'r_fal':     lambda g: build_rifle(g, wood=True, heavy=True),
  'r_aug':     lambda g: build_rifle(g, bullpup=True) or add_scope(g, 0.16, y=0.02),
  'r_famas':   lambda g: build_rifle(g, bullpup=True),
  'r_g36c':    lambda g: build_rifle(g) and None or add_scope(g, 0.10, r=0.013, y=-0.01),
  'r_an94':    lambda g: build_rifle(g) or add_mag(g, h=0.12, curved=True),
  
  'd_m14':     lambda g: build_dmr(g, wood=True),
  'd_svd':     lambda g: build_dmr(g, wood=True) or add_mag(g, h=0.10, curved=True),

  'n_m24':     lambda g: build_sniper(g),
  'n_awm':     lambda g: build_sniper(g) or None,
  'n_m82':     lambda g: build_sniper(g, big=True),
 
  'sh_benelli':lambda g: build_shotgun(g),
  'sh_aa12':   lambda g: build_shotgun(g, auto=True) or add_mag(g, h=0.12),

  'l_m249':    lambda g: build_lmg(g),
  'l_m60':     lambda g: build_lmg(g),
  'l_pkm':     lambda g: build_lmg(g),

  'h_m134':    lambda g: build_minigun(g),
  'h_m2':      lambda g: build_hmg(g),
  'h_mk19':    lambda g: build_glm(g),
  
  'la_rpg7':   lambda g: build_launcher(g, rpg=True),
  'la_at4':    lambda g: build_launcher(g),
  'la_stinger':lambda g: build_launcher(g, stinger=True),
}


def build_soldier(hostile):
    root = group('hostile_soldier' if hostile else 'player_soldier')
    hip = empty('hip', (0, 0, 0.98), parent=root)
    torso = box('torso', (0.40, 0.22, 0.58), origin=(0, 0, 0.28), material=M['vest_h'] if hostile else M['vest_f'], parent=hip)
    pouchL = box('pouchL', (0.10, 0.04, 0.12), origin=(-0.12, -0.13, 0.22), material=M['gun_dark'], parent=hip)
    pouchR = box('pouchR', (0.10, 0.04, 0.12), origin=(0.12, -0.13, 0.22), material=M['gun_dark'], parent=hip)
    pack = box('pack', (0.30, 0.14, 0.36), origin=(0, 0.16, 0.26), material=M['olive'] if not hostile else M['sand'], parent=hip)
    neck = empty('neck', (0, 0, 0.60), parent=hip)
    head = box('head', (0.20, 0.20, 0.22), origin=(0, 0, 0.12), material=M['skin'], parent=neck)
    helmet = box('helmet', (0.24, 0.25, 0.13), origin=(0, 0, 0.235), material=M['helmet_h'] if hostile else M['helmet_f'], parent=neck)
    brim = box('brim', (0.24, 0.12, 0.03), origin=(0, -0.07, 0.185), material=M['helmet_h'] if hostile else M['helmet_f'], parent=neck)

    def arm(side):
        sgn = -1 if side == 'L' else 1
        sh = empty('shoulder_'+side, (sgn*0.26, 0, 0.48), parent=hip)
        upper = box('upperarm_'+side, (0.10, 0.10, 0.30), origin=(sgn*0.02, 0, -0.15), material=M['vest_h'] if hostile else M['vest_f'], parent=sh)
        elbow = empty('elbow_'+side, (0, 0, -0.30), parent=sh)
        fore = box('forearm_'+side, (0.085, 0.085, 0.26), origin=(0, -0.02, -0.13), material=M['skin'], parent=elbow)
        hand = box('hand_'+side, (0.08, 0.08, 0.10), origin=(0, -0.02, -0.30), material=M['skin'], parent=elbow)
        return sh, elbow
    shL, elL = arm('L'); shR, elR = arm('R')
   
    def leg(side):
        sgn = -1 if side == 'L' else 1
        hp = empty('hipjoint_'+side, (sgn*0.11, 0, 0.0), parent=hip)
        thigh = box('thigh_'+side, (0.13, 0.14, 0.42), origin=(0, 0, -0.21), material=M['cloth_h'] if hostile else M['cloth_f'], parent=hp)
        knee = empty('knee_'+side, (0, 0, -0.44), parent=hp)
        shin = box('shin_'+side, (0.11, 0.12, 0.40), origin=(0, 0, -0.20), material=M['olive_dark'], parent=knee)
        foot = box('boot_'+side, (0.11, 0.26, 0.10), origin=(0, -0.05, -0.44), material=M['boot'], parent=knee)
        return hp, knee
    hpL, knL = leg('L'); hpR, knR = leg('R')

    gm = empty('gun_mount', (0.02, -0.06, -0.32), parent=elR)
    return root


def build_container(x=0, y=0, ry=0):
    root = group('container')
    body = box('body', (2.44, 6.06, 2.59), origin=(0, 0, 1.295), material=M['crate'], parent=root)
    for i in range(6):
        box('rib%d'%i, (2.5, 0.08, 2.4), origin=(0, -2.5+i, 1.29), material=M['olive_dark'], parent=root)
    root.location = (x, y, 0)
    root.rotation_euler = Euler((0, 0, ry), 'XYZ')
    return root

def build_crate(x=0, y=0, s=1.2):
    root = group('crate')
    b = box('b', (s, s, s), origin=(0, 0, s/2), material=M['crate'], parent=root)
    lid = box('lid', (s*1.04, s*1.04, 0.06), origin=(0, 0, s+0.03), material=M['olive_dark'], parent=root)
    root.location = (x, y, 0)
    return root

def build_barrel(x=0, y=0):
    root = group('barrel')
    c = cyl('c', 0.30, 0.30, 0.90, origin=(0, 0, 0.45), verts=14, material=M['rust_red'], parent=root)
    t1 = torus('t1', 0.30, 0.02, origin=(0, 0, 0.30), rot=(D(90),0,0), material=M['metal_d'], parent=root)
    t2 = torus('t2', 0.30, 0.02, origin=(0, 0, 0.62), rot=(D(90),0,0), material=M['metal_d'], parent=root)
    root.location = (x, y, 0)
    return root

def build_sandbag_line(x=0, y=0, ry=0):
    root = group('sandbags')
    n = 5
    for i in range(n):
        row = i % 2
        b = box('bag%d'%i, (0.85, 0.5, 0.30), origin=(i*0.88 - n*0.44, 0, 0.15 + row*0.28), rot=(0, 0, rnd(-0.08, 0.08)), material=M['sand'], parent=root)
    root.location = (x, y, 0)
    root.rotation_euler = Euler((0, 0, ry), 'XYZ')
    return root

def build_truck():
    root = group('truck')
    root.rotation_euler = Euler((0, 0, D(180)), 'XYZ')  # authored +Y front -> game -Y forward
    chassis = box('chassis', (2.2, 6.4, 0.25), origin=(0, 0, 0.75), material=M['metal_d'], parent=root)
    hood = box('hood', (2.0, 1.6, 0.9), origin=(0, 2.3, 1.35), material=M['olive'], parent=root)
    cab = box('cab', (2.2, 1.7, 1.3), origin=(0, 0.9, 1.75), material=M['olive'], parent=root)
    winF = box('winF', (1.9, 0.06, 0.6), origin=(0, 1.72, 1.85), material=M['glass'], parent=root)
    winL = box('winL', (0.06, 1.4, 0.5), origin=(-1.08, 0.9, 1.85), material=M['glass'], parent=root)
    winR = box('winR', (0.06, 1.4, 0.5), origin=(1.08, 0.9, 1.85), material=M['glass'], parent=root)
    bed = box('bed', (2.3, 3.4, 0.7), origin=(0, -1.2, 1.35), material=M['olive_dark'], parent=root)
    canopy = box('canopy', (2.3, 3.4, 1.2), origin=(0, -1.2, 2.3), material=M['sand'], parent=root)
    bumper = box('bumper', (2.3, 0.2, 0.4), origin=(0, 3.25, 0.9), material=M['metal_d'], parent=root)
    wheels = []
    for (wx, wy) in [(-1.05, 2.3), (1.05, 2.3), (-1.05, -0.3), (1.05, -0.3), (-1.05, -2.0), (1.05, -2.0)]:
        w = cyl('wheel', 0.55, 0.55, 0.35, origin=(wx, wy, 0.55), rot=(0,D(90),0), verts=14, material=M['tire'], parent=root)
        wheels.append(w)
    return root

def build_radar():
    root = group('radar_station')
    base = cyl('base', 1.7, 2.0, 5.5, origin=(0, 0, 2.75), verts=14, material=M['concrete_d'], parent=root)
    mast = cyl('mast', 0.22, 0.22, 4.5, origin=(0, 0, 7.7), verts=10, material=M['metal'], parent=root)
    dish_root = empty('dish_root', (0, 0, 10.2), parent=root)
    dish = sph('dish', 2.6, origin=(0, 0, 0), material=M['metal'], parent=dish_root, seg=18, ring=10)
  
    dish.scale = (1, 1, 0.45)
    dish.rotation_euler = Euler((D(-40), 0, 0), 'XYZ')
    arm = box('arm', (0.1, 0.1, 1.6), origin=(0, 0, -0.9), material=M['metal_d'], parent=dish_root)
    return root

def build_watchtower():
    root = group('watchtower')
    for (lx, ly) in [(-1.4, -1.4), (1.4, -1.4), (-1.4, 1.4), (1.4, 1.4)]:
        leg = cyl('leg', 0.12, 0.16, 8.5, origin=(lx, ly, 4.25), verts=8, material=M['metal_d'], parent=root)
        brace = box('brace', (0.08, 0.08, 2.6), origin=(lx*0.6, ly*0.6, 2.2), rot=(D(30 if lx>0 else -30), 0, D(30 if ly>0 else -30)), material=M['metal_d'], parent=root)
    cab = box('cab', (3.4, 3.4, 0.25), origin=(0, 0, 8.6), material=M['crate'], parent=root)
    for (wx, wy, w, d) in [(-1.72, 0, 0.08, 3.4), (1.72, 0, 0.08, 3.4), (0, -1.72, 3.4, 0.08), (0, 1.72, 3.4, 0.08)]:
        rail = box('rail', (w, d, 1.0), origin=(wx, wy, 9.2), material=M['metal_d'], parent=root)
    roof = box('roof', (3.8, 3.8, 0.15), origin=(0, 0, 11.2), material=M['olive_dark'], parent=root)
    posts = [box('post%d'%i, (0.1, 0.1, 2.2), origin=(sx*1.7, sy*1.7, 10.1), material=M['metal_d'], parent=root) for i,(sx,sy) in enumerate([(-1,-1),(1,-1),(-1,1),(1,1)])]
    return root

def build_bunker():
    root = group('bunker')
    walls = [
        box('w_south', (10, 0.6, 3.2), origin=(0, -4.7, 1.6), material=M['concrete'], parent=root),
        box('w_north', (10, 0.6, 3.2), origin=(0, 4.7, 1.6), material=M['concrete'], parent=root),
        box('w_west', (0.6, 10, 3.2), origin=(-4.7, 0, 1.6), material=M['concrete'], parent=root),
        box('w_east', (0.6, 10, 3.2), origin=(4.7, 0, 1.6), material=M['concrete'], parent=root),
    ]
    roof = box('roof', (10.6, 10.6, 0.5), origin=(0, 0, 3.45), material=M['concrete_d'], parent=root)
    return root

def build_fence_post(x=0, y=0):
    root = group('fence_post')
    p = box('p', (0.12, 0.12, 2.6), origin=(0, 0, 1.3), material=M['metal_d'], parent=root)
    return root

def build_ground_patch(r=6):
    root = group('patch')
    c = cyl('c', r, r, 0.04, origin=(0, 0, 0.02), verts=24, material=M['olive_dark'], parent=root)
    return root

def rnd(a, b):
    import random
    return a + random.random() * (b - a)


def export_glb(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    def sel(o):
        o.select_set(True)
        for c in o.children:
            sel(c)
    for o in objs:
        sel(o)
    bpy.context.view_layer.objects.active = objs[0]
    path = os.path.join(OUT, name + '.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_yup=True, export_apply=True,
                              export_animations=False, export_cameras=False, export_lights=False)
    return path

results = {}

for key, builder in BUILDERS.items():
    clean()
    root = g_group('gun_' + key)
    builder(root)
    p = export_glb([root], 'gun_' + key)
    results[key] = p
    bpy.data.objects.remove(root, do_unlink=True)

clean()
sol = build_soldier(False)
p = export_glb([sol], 'soldier_player')
results['soldier_player'] = p
clean()
sol_h = build_soldier(True)
p = export_glb([sol_h], 'soldier_hostile')
results['soldier_hostile'] = p


clean()
cont = build_container()
p = export_glb([cont], 'container')
results['container'] = p

clean()
crate = build_crate()
p = export_glb([crate], 'crate')
results['crate'] = p

clean()
bar = build_barrel()
p = export_glb([bar], 'barrel')
results['barrel'] = p

clean()
sb = build_sandbag_line()
p = export_glb([sb], 'sandbags')
results['sandbags'] = p

clean()
truck = build_truck()
p = export_glb([truck], 'truck')
results['truck'] = p

clean()
radar = build_radar()
p = export_glb([radar], 'radar')
results['radar'] = p

clean()
tower = build_watchtower()
p = export_glb([tower], 'watchtower')
results['watchtower'] = p

clean()
bunk = build_bunker()
p = export_glb([bunk], 'bunker')
results['bunker'] = p

clean()
fence = build_fence_post()
p = export_glb([fence], 'fence_post')
results['fence_post'] = p
-
WEAPON_MODEL_MAP = {
  'm9':'p_m9','m1911':'p_1911','m17':'p_m17','deagle':'p_deagle','mk23':'p_mk23','g18':'p_g18',
  'mp5':'s_mp5','mp7':'s_mp7','p90':'s_p90','thompson':'s_thompson','bizon':'s_bizon','vector':'s_vector',
  'm4a1':'r_m4a1','m16a4':'r_m16a4','ak47':'r_ak47','ak74':'r_ak74','scarl':'r_scarl','scarh':'r_scarh',
  'hk416':'r_hk416','fal':'r_fal','aug':'r_aug','famas':'r_famas','g36c':'r_g36c','an94':'r_an94',
  'm14':'d_m14','svd':'d_svd',
  'm24':'n_m24','awm':'n_awm','m82':'n_m82',
  'benelli':'sh_benelli','aa12':'sh_aa12',
  'm249':'l_m249','m60':'l_m60','pkm':'l_pkm',
  'm134':'h_m134','m2':'h_m2','mk19':'h_mk19',
  'rpg7':'la_rpg7','at4':'la_at4','stinger':'la_stinger'
}
manifest = {
  'models': results,
  'weaponModelMap': WEAPON_MODEL_MAP,
  'enemyGunModels': { 'RIFLE':'r_m4a1', 'SNIPER':'n_m24', 'LMG':'l_m249', 'HEAVY':'h_m134' }
}
with open(os.path.join(OUT, 'manifest.json'), 'w') as f:
    json.dump(manifest, f, indent=1)

print('EXPORTED', len(results), 'models to', OUT)
