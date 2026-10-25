# -*- coding: utf-8 -*-
# Tracked (tank-style) rover chassis - FreeCAD macro (v2, matches the 3D web viewer)
# Run: FreeCAD > Macro > Macros... > rover_chassis > Execute
# Units: mm.  X = forward (idler end), Y = left/right, Z = up.  Ground = Z0.
import math, os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

GUI = App.GuiUp

# ---------------- PARAMETERS ----------------
TRACK_W, TRACK_T = 20.0, 5.0
WHEEL_T = 12.0
SPR = (-120.0, 55.0, 25.0)              # drive sprocket (x, z, r)
IDL = (120.0, 55.0, 25.0)               # idler wheel
RW = [(-60.0, 25.0, 20.0), (0.0, 25.0, 20.0), (60.0, 25.0, 20.0)]   # road wheels
CIRCLES = [SPR] + RW + [IDL]            # counter-clockwise order
TRACK_IN = 100.0
CLEAT_PITCH, CLEAT_L, CLEAT_H = 20.0, 6.0, 4.0

HULL_X, HULL_Y, HULL_Z0, HULL_Z1, WALL = 135.0, 96.0, 20.0, 92.0, 3.0
DECK_X, DECK_Y, DECK_Z0, DECK_Z1 = 135.0, 125.0, 92.0, 96.0
PI_BOX = (-35.0, 65.0, -35.0, 35.0, DECK_Z1, DECK_Z1 + 30.0)       # moved forward
POST_H = 40.0
SHIELD_Z0 = DECK_Z1 + POST_H            # 136
SHIELD_T = 3.0
TOP_Z = SHIELD_Z0 + SHIELD_T            # 139

doc = App.newDocument("RoverChassis")

def add(name, shape, color=(0.7, 0.7, 0.7), label=None, transp=0):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.Label = label or name
    if GUI:
        try:
            o.ViewObject.ShapeColor = color
            if transp:
                o.ViewObject.Transparency = transp
        except Exception:
            pass
    return o

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def cyl_y(x, y0, z, r, h):
    return Part.makeCylinder(r, h, V(x, y0, z), V(0, 1, 0))

def cyl_x(x0, y, z, r, h):
    return Part.makeCylinder(r, h, V(x0, y, z), V(1, 0, 0))

# ---------------- TRACK PATH (convex hull of the wheels) ----------------
n = len(CIRCLES)
PSI = []
for i in range(n):
    ax_, az_, ar_ = CIRCLES[i]
    bx_, bz_, br_ = CIRCLES[(i + 1) % n]
    dx, dz = bx_ - ax_, bz_ - az_
    L = math.hypot(dx, dz)
    PSI.append(math.atan2(dz, dx) - math.acos((ar_ - br_) / L))

def pt(i, ang, off):
    cx, cz, r = CIRCLES[i]
    return V(cx + (r + off) * math.cos(ang), 0, cz + (r + off) * math.sin(ang))

def track_wire(off):
    edges = []
    for i in range(n):
        p_in, p_out = PSI[i - 1], PSI[i]
        d = (p_out - p_in) % (2 * math.pi)
        a, b = pt(i, p_in, off), pt(i, p_out, off)
        if d > 1e-6:
            m = pt(i, p_in + d / 2.0, off)
            edges.append(Part.Arc(a, m, b).toShape())
        nxt = (i + 1) % n
        edges.append(Part.makeLine(b, pt(nxt, PSI[i], off)))
    return Part.Wire(Part.__sortEdges__(edges))

w_in = track_wire(0.0)
w_out = track_wire(TRACK_T)
ring = Part.Face(w_out).cut(Part.Face(w_in))

def make_track(y0):
    belt = ring.extrude(V(0, TRACK_W, 0))
    belt.translate(V(0, y0, 0))
    cleats = []
    cen = V(0, 0, 35)
    for e in w_out.Edges:
        ln = e.Length
        k = max(1, int(round(ln / CLEAT_PITCH)))
        for j in range(k):
            par = e.getParameterByLength(ln * (j + 0.5) / k)
            p, t = e.valueAt(par), e.tangentAt(par)
            ang = math.atan2(t.z, t.x)
            nx, nz = math.sin(ang), -math.cos(ang)
            if nx * (p.x - cen.x) + nz * (p.z - cen.z) < 0:
                ang += math.pi
            c = Part.makeBox(CLEAT_L, TRACK_W, CLEAT_H, V(-CLEAT_L / 2, 0, -CLEAT_H))
            c.rotate(V(0, 0, 0), V(0, 1, 0), -math.degrees(ang))
            c.translate(V(p.x, y0, p.z))
            cleats.append(c)
    return belt, Part.makeCompound(cleats)

# ---------------- WHEELS ----------------
def holes_cut(shape, x, y0, z, r, count, pr, hr):
    hs = []
    for k in range(count):
        a = 2 * math.pi * k / count
        hs.append(cyl_y(x + pr * math.cos(a), y0 - 1, z + pr * math.sin(a), hr, WHEEL_T + 2))
    return shape.cut(Part.makeCompound(hs))

def road_wheel(x, z, r, y0):
    return holes_cut(cyl_y(x, y0, z, r, WHEEL_T), x, y0, z, r, 6, r * 0.6, 3.5)

def idler(x, z, r, y0):
    return holes_cut(cyl_y(x, y0, z, r, WHEEL_T), x, y0, z, r, 8, r * 0.6, 4.0)

def sprocket(x, z, r, y0):
    root = r - 4.0
    parts = [cyl_y(x, y0, z, root, WHEEL_T)]
    for k in range(12):
        t = Part.makeBox(4.0, WHEEL_T, 5.0, V(root, 0, -2.5))
        t.rotate(V(0, 0, 0), V(0, 1, 0), -k * 30.0)
        t.translate(V(x, y0, z))
        parts.append(t)
    s = Part.makeCompound(parts)
    hs = []
    for k in range(8):
        a = 2 * math.pi * k / 8
        hs.append(cyl_y(x + 0.55 * root * math.cos(a), y0 - 1, z + 0.55 * root * math.sin(a), 3.5, WHEEL_T + 2))
    return s.cut(Part.makeCompound(hs))

# ---------------- TRACKS, WHEELS, SIDE PLATES, MOTORS, ENCODERS ----------------
GREY, DARK, ALU = (0.65, 0.65, 0.68), (0.15, 0.16, 0.18), (0.78, 0.78, 0.80)
for side, tag in ((1, "R"), (-1, "L")):
    ty0 = TRACK_IN if side == 1 else -(TRACK_IN + TRACK_W)
    wy0 = ty0 + (TRACK_W - WHEEL_T) / 2.0
    belt, cleats = make_track(ty0)
    add("Track_" + tag, belt, DARK)
    add("TrackCleats_" + tag, cleats, DARK)
    add("DriveSprocket_" + tag, sprocket(SPR[0], SPR[1], SPR[2], wy0), GREY)
    add("IdlerWheel_" + tag, idler(IDL[0], IDL[1], IDL[2], wy0), GREY)
    for i, (x, z, r) in enumerate(RW, 1):
        add("RoadWheel%d_%s" % (i, tag), road_wheel(x, z, r, wy0), GREY)
    ay0 = HULL_Y if side == 1 else -(TRACK_IN + TRACK_W - 2)
    axl = [cyl_y(c[0], ay0, c[1], 4.0, TRACK_W + (TRACK_IN - HULL_Y)) for c in CIRCLES]
    add("Axles_" + tag, Part.makeCompound(axl), ALU)
    py0, py1 = (HULL_Y, TRACK_IN) if side == 1 else (-TRACK_IN, -HULL_Y)
    add("SidePlate_" + tag, box(-135, 135, py0, py1, 15, 80), ALU)
    # drive motor + encoder directly on the sprocket axle (inside the hull)
    my0 = 60.0 if side == 1 else -93.0
    ey0 = 53.0 if side == 1 else -60.0
    sy0 = 93.0 if side == 1 else -100.0
    add("DriveMotor_" + tag, cyl_y(SPR[0], my0, SPR[1], 12.5, 33.0), (0.42, 0.44, 0.47), "Drive Motor " + tag)
    add("Encoder_" + tag, Part.makeCompound([cyl_y(SPR[0], ey0, SPR[1], 12.0, 7.0),
                                             box(-126, -114, ey0, ey0 + 7.0, 42, 47)]),
        (0.12, 0.65, 0.63), "Encoder " + tag)
    add("MotorShaft_" + tag, cyl_y(SPR[0], sy0, SPR[1], 4.0, 7.0), (0.48, 0.49, 0.51))

# ---------------- HULL (see-through) + DECK ----------------
hull = box(-HULL_X, HULL_X, -HULL_Y, HULL_Y, HULL_Z0, HULL_Z1)
hull = hull.cut(box(-HULL_X + WALL, HULL_X - WALL, -HULL_Y + WALL, HULL_Y - WALL, HULL_Z0 + WALL, HULL_Z1 + 1))
add("Hull", hull, (0.60, 0.63, 0.65), transp=75)
add("Base_Deck", box(-DECK_X, DECK_X, -DECK_Y, DECK_Y, DECK_Z0, DECK_Z1), (0.30, 0.32, 0.35), transp=40)

# ---------------- INSIDE THE HULL ----------------
add("Power_Supply", Part.makeCompound([box(-10, 90, -30, 30, 24, 56), box(-10, 90, -30, 30, 56, 58)]),
    (0.88, 0.63, 0.10), "Power Supply (Battery)")
add("Motor_Driver", box(-100, -60, -25, 25, 24, 36), (0.76, 0.23, 0.23), "Motor Driver")

# ---------------- ON THE DECK ----------------
add("ESP32", Part.makeCompound([box(-116, -64, -14, 14, 96, 106), box(-112, -100, -9, 9, 106, 108)]),
    (0.11, 0.13, 0.19), "ESP32")
add("Gas_Sensor", Part.makeCompound([box(-105, -75, -61, -39, 96, 116), Part.makeCylinder(8, 3, V(-90, -50, 116), V(0, 0, 1))]),
    (0.48, 0.36, 0.71), "Gas Sensor")
add("Temp_Humidity_Sensor", box(-102, -78, 39, 59, 96, 108), (0.87, 0.90, 0.93), "Temperature + Humidity Sensor")
add("Raspberry_Pi_Box", box(*PI_BOX), (0.10, 0.45, 0.20), "Raspberry Pi Box")

# ---------------- PROTECTIVE LAYER ----------------
posts = [box(sx * 110 - 4, sx * 110 + 4, sy * 95 - 4, sy * 95 + 4, DECK_Z1, SHIELD_Z0)
         for sx in (-1, 1) for sy in (-1, 1)]
add("Shield_Posts", Part.makeCompound(posts), ALU)
add("Protective_Layer", box(-120, 120, -105, 105, SHIELD_Z0, TOP_Z), (0.25, 0.27, 0.30), "Protective Layer", transp=70)

# ---------------- ON TOP: LIDAR (grey mount box + two black circles), THERMAL CAM, CAM ----------------
add("LiDAR_Mount_Box", box(-80, 0, -40, 40, TOP_Z, TOP_Z + 16), (0.55, 0.56, 0.58), "LiDAR Mount Box (grey)")
add("LiDAR_Box", box(-75, -5, -35, 35, TOP_Z + 16, TOP_Z + 61), (0.23, 0.24, 0.26), "LiDAR Box")
for s, nm in ((-1, "L"), (1, "R")):
    add("LiDAR_Ring_" + nm, cyl_x(-5, s * 17, TOP_Z + 38.5, 13, 2), (0.44, 0.46, 0.48))
    add("LiDAR_Eye_" + nm, cyl_x(-5, s * 17, TOP_Z + 38.5, 10, 3), (0.0, 0.0, 0.0), "LiDAR black circle " + nm)

CAM_X0, CAM_X1, CAM_H = 85.0, 115.0, 25.0
for nm, yc, col in (("Thermal_Cam_Box", -25.0, (0.85, 0.35, 0.10)), ("Cam_Box", 25.0, (0.15, 0.25, 0.60))):
    add(nm, box(CAM_X0, CAM_X1, yc - 22, yc + 22, TOP_Z, TOP_Z + CAM_H), col, nm.replace("_", " "))
    add(nm + "_Lens", cyl_x(CAM_X1, yc, TOP_Z + CAM_H / 2.0, 8, 5), (0.02, 0.02, 0.02))

# ---------------- WIRES (straight segments) ----------------
def wire_shape(pts, r):
    segs = []
    for a, b in zip(pts[:-1], pts[1:]):
        p, q = V(*a), V(*b)
        d = q - p
        if d.Length > 1e-6:
            segs.append(Part.makeCylinder(r, d.Length, p, d))
    return Part.makeCompound(segs)

GREEN, BLUE, RED, YEL = (0.18, 0.80, 0.44), (0.23, 0.51, 0.96), (0.88, 0.11, 0.28), (0.96, 0.85, 0.04)
W_GREEN = [([(-100, -8, 106), (-100, -8, 90), (-100, -8, 60), (-85, -8, 36)], 1.0),
           ([(-95, 8, 106), (-95, 8, 90), (-95, 8, 60), (-80, 8, 36)], 1.0)]
W_BLUE = [([(-90, -50, 100), (-90, -30, 103), (-90, -14, 102)], 1.0),        # gas -> ESP32
          ([(-90, 49, 100), (-90, 30, 103), (-90, 14, 102)], 1.0),           # temp+humidity -> ESP32
          ([(-20, 0, 126), (-22, 0, 134), (-30, 0, 139)], 1.2),              # Pi -> LiDAR
          ([(50, -20, 126), (62, -22, 134), (92, -25, 139)], 1.2),           # Pi -> thermal cam
          ([(55, 10, 126), (70, 18, 134), (92, 25, 139)], 1.2)]              # Pi -> cam
W_RED = [([(-10, 0, 40), (-35, 0, 34), (-60, 0, 30)], 2.0),                  # power supply -> driver
         ([(50, -20, 56), (50, -20, 90), (50, -35, 100), (50, -35, 112)], 1.4)]   # power supply -> Pi
W_YEL = [([(-64, 0, 101), (-50, 0, 100), (-35, 0, 102)], 1.0)]               # ESP32 <-> Pi serial
for s in (1, -1):
    W_BLUE.append(([(-72, s * 10, 106), (-72, s * 45, 94), (-108, s * 52, 80), (-120, s * 56.5, 67)], 1.0))  # encoder -> ESP32
    W_RED.append(([(-80, s * 24, 30), (-108, s * 45, 30), (-120, s * 70, 43)], 1.6))                          # driver -> motor
for nm, grp, col in (("Wires_Control_Green", W_GREEN, GREEN), ("Wires_Signal_Blue", W_BLUE, BLUE),
                     ("Wires_Power_Red", W_RED, RED), ("Wires_Serial_Yellow", W_YEL, YEL)):
    add(nm, Part.makeCompound([wire_shape(p, r) for p, r in grp]), col)

# ---------------- TEXT LABELS (flat on box tops; skipped if no font found) ----------------
FONTS = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"]
FONT = next((f for f in FONTS if os.path.exists(f)), None)

def label(name, text, size, cx, cy, ztop, rot=0.0):
    if not FONT:
        return
    try:
        import Draft
        ss = Draft.make_shapestring(String=text, FontFile=FONT, Size=size, Tracking=0)
        doc.recompute()
        shp = ss.Shape.copy().extrude(V(0, 0, 0.8))
        doc.removeObject(ss.Name)
        if rot:
            shp.rotate(V(0, 0, 0), V(0, 0, 1), rot)
        bb = shp.BoundBox
        shp.translate(V(cx - (bb.XMin + bb.XMax) / 2, cy - (bb.YMin + bb.YMax) / 2, ztop - bb.ZMin))
        add(name, shp, (1, 1, 1))
    except Exception as e:
        App.Console.PrintWarning("Label '%s' skipped: %s\n" % (text, e))

label("Txt_RPi", "RASPBERRY PI", 9, (PI_BOX[0] + PI_BOX[1]) / 2, 0, PI_BOX[5])
label("Txt_ESP32", "ESP32", 6, -90, 0, 106)
label("Txt_Gas", "GAS", 4, -90, -50, 119)
label("Txt_TempHum", "TEMP+HUM", 3.5, -90, 49, 108)
label("Txt_LiDAR", "LIDAR", 8, -40, 0, TOP_Z + 61)
label("Txt_Thermal", "THERMAL", 5, 100, -25, TOP_Z + CAM_H, 90)
label("Txt_Cam", "CAM", 6, 100, 25, TOP_Z + CAM_H, 90)

doc.recompute()

# ---------------- SAVE + STEP EXPORT ----------------
out = os.path.join(os.path.expanduser("~"), "Documents")
if not os.path.isdir(out):
    out = os.path.expanduser("~")
try:
    doc.saveAs(os.path.join(out, "rover_chassis.FCStd"))
    import Import
    Import.export([o for o in doc.Objects if hasattr(o, "Shape")], os.path.join(out, "rover_chassis.step"))
    App.Console.PrintMessage("Saved to %s\n" % out)
except Exception as e:
    App.Console.PrintWarning("Save/export skipped: %s\n" % e)

if GUI:
    import FreeCADGui as Gui
    Gui.SendMsgToActiveView("ViewFit")
    Gui.activeDocument().activeView().viewIsometric()
