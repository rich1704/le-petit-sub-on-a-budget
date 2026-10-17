"""Le Petit Sub: every dimension and driver value in one place, plus the checks that keep them honest.

The drawings (make_building_plan.py, make_cut_layout.py) and the diagrams (make_diagrams.py) import
this module, so a change here reaches every page. The 3D model (docs/3d/index.html) uses the same
numbers.

    python tools/sub.py          prints the design numbers and runs the geometry checks
"""

# ------------------------------------------------------------------ material and box (mm)
T = 22                          # OSB thickness - measure yours; everything inside follows from it
W, H, D = 340, 530, 350         # outside: width (front face), height, depth
IW, IH, ID = W - 2 * T, H - 2 * T, D - 2 * T     # inside clear: 296 x 486 x 306

# panels: (name, length, width, qty, note) - front and back are full plates over everything,
# sides sit between them, top and bottom between the plates and the sides
PANELS = [
    ("Front", H, W, 1, "plain"),
    ("Back", H, W, 1, "M20 cable gland"),
    ("Side", H, ID, 2, "driver"),
    ("Top / bottom", ID, IW, 2, ""),
]

# ------------------------------------------------------------------ driver: SB Acoustics SB26SFCL38-4
# datasheet "10\" SB26SFCL38-4, Preliminary data, REV. 1 (16.09.2022)"
DRIVER_NAME = "SB Acoustics SB26SFCL38-4"
DRIVER: dict[str, float] = dict(
    Z=4, Re=3.3, Le=1.0e-3, Sd=346e-4, Bl=8.2, Mms=55.2e-3,
    Cms=0.61e-3, Rms=1.7, Fs=27.4, Qms=5.59, Qes=0.47, Qts=0.43, Vas=104.0, xmax=15.8e-3 / 2,
    P=80, spl=91.0,
    od=265.0, basket=228.9, flange=3.56, depth=116.8, depth_total=128.1, magnet=120.0,
    pcd=250.0, holes=6, hole=5.3,
)
N_DRV = 2
DRV_U = ID / 2                  # driver centre across the side panel (from its front edge): 153
DRV_V = 175                     # driver centre below the top of the box
CUTOUT = 231                    # basket Ø228.9 + 1 mm per side
RECESS = 267                    # frame Ø265 ±0.5 + 1 mm per side
RECESS_DEPTH = 4.5              # flange 3.56 + ≈1 mm compressed gasket: the frame sits flush
HOLE_ANGLES = (0, 60, 120, 180, 240, 300)   # degrees from 3 o'clock, as on the datasheet
INSERT_OD = 8                   # M5 insert for wood, outer thread Ø ≈ 8 (drill Ø6.5)

# ------------------------------------------------------------------ braces (22 mm OSB strips, 40 wide)
STRIP = 40
TIE = dict(length=ID, top=155, bottom=195)          # on edge, front to back, centred left-right
WIN_TOP = 330                                       # window brace laid flat, top face below the box top
WIN = dict(fb=IW, side=ID - 2 * STRIP)              # front/back members 296, side members 226

# ------------------------------------------------------------------ joints: biscuits, size 20
BIS_PLATE_SIDE = (45, 133, 221, 309, 397, 485)      # along the 530 edges, from the top
BIS_PLATE_TB = (70, 170, 270)                       # along the 340 plate edges onto top/bottom
BIS_SIDE_TB = (50, 153, 256)                        # sides onto top/bottom ends, from the front edge

# ------------------------------------------------------------------ cable gland
GLAND_SIZE = "M20"
GLAND: dict[str, float] = dict(hole=20.5, u=W / 2, from_bottom=100)

# ------------------------------------------------------------------ sheet and cutting
SHEET = (2000, 1000)
KERF, TRIM = 3, 10

# ------------------------------------------------------------------ volume
DRIVER_DISPLACEMENT = 1.5       # litres per driver (basket + magnet), estimated from the drawing


def volumes():
    gross = IW * IH * ID / 1e6
    tie = TIE["length"] * STRIP * T / 1e6
    win = (2 * WIN["fb"] + 2 * WIN["side"]) * STRIP * T / 1e6
    net = gross - tie - win - N_DRV * DRIVER_DISPLACEMENT
    return dict(gross=gross, braces=tie + win, drivers=N_DRV * DRIVER_DISPLACEMENT, net=net)


def magnet_clearance():
    """Gap between each magnet's back and the tie strip, mm."""
    mount = RECESS_DEPTH                     # mounting plane, from the outside face of the side
    back = mount + DRIVER["depth"]           # back of the magnet, from the outside face
    strip_face = T + IW / 2 - T / 2          # tie strip face, from the outside face
    return strip_face - back


def check():
    v = volumes()
    assert (IW, IH, ID) == (296, 486, 306), (IW, IH, ID)
    assert abs(v["gross"] - 44.0) < 0.05, v
    assert WIN["side"] == 226 and WIN["fb"] == 296
    # driver on the side panel: recess clear of the panel edges (and the biscuit slots), screws clear of the hole
    assert DRV_U - RECESS / 2 >= 19, "recess too close to the plate joints"
    assert DRV_V - RECESS / 2 >= T + 15, "recess runs into the top panel"
    wall = DRIVER["pcd"] / 2 - INSERT_OD / 2 - CUTOUT / 2
    assert wall >= 5, f"only {wall:.1f} mm between insert and cutout"
    assert CUTOUT >= DRIVER["basket"] + 1 and RECESS >= DRIVER["od"] + 1.5
    assert RECESS_DEPTH > DRIVER["flange"]
    # braces clear of the drivers
    assert magnet_clearance() >= 30, magnet_clearance()
    assert WIN_TOP > DRV_V + RECESS / 2 + 15, "window brace hits the driver frame"
    assert TIE["top"] < DRV_V < TIE["bottom"]
    # gland below the window brace
    assert H - GLAND["from_bottom"] > WIN_TOP + T + 30
    # biscuits stay inside their edges with room to spare
    assert min(BIS_PLATE_SIDE) >= 40 and H - max(BIS_PLATE_SIDE) >= 40
    assert min(BIS_SIDE_TB) - 28 >= 15 and ID - max(BIS_SIDE_TB) - 28 >= 15
    assert all(T + 28 + 10 <= b <= W - T - 28 - 10 for b in BIS_PLATE_TB)
    return True


if __name__ == "__main__":
    check()
    v = volumes()
    print(f"inside {IW} x {IH} x {ID} mm: gross {v['gross']:.1f} l, braces {v['braces']:.2f} l, "
          f"drivers {v['drivers']:.1f} l -> net {v['net']:.1f} l")
    print(f"magnet to tie strip: {magnet_clearance():.0f} mm; "
          f"wall insert-cutout {DRIVER['pcd'] / 2 - INSERT_OD / 2 - CUTOUT / 2:.1f} mm")
    print("geometry checks passed")
