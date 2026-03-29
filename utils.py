from manim import *
import numpy as np

# constants
SIGNAL_COLOR   = YELLOW
INACTIVE_COLOR = "#444444"
ACTIVE_COMP    = YELLOW
CTRL_COLOR     = "#4A90D9"

DOT_RADIUS     = 0.07
STROKE_WIDTH   = 2.5
LABEL_FONT     = 14
LABEL_OFFSET   = 0.13   # gap between wire and label text


# ------------------------------------------------------------------------------
# PRIMITIVE HELPERS
# ------------------------------------------------------------------------------

def h(pt: np.ndarray, x: float) -> np.ndarray:
    """Same y/z as pt, move to x."""
    return np.array([x, pt[1], 0])

def v(pt: np.ndarray, y: float) -> np.ndarray:
    """Same x/z as pt, move to y."""
    return np.array([pt[0], y, 0])

def midpoint(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a + b) / 2


class _Polyline(TipableVMobject):
    """Open polyline that supports add_tip()."""
    def __init__(self, *points, **kwargs):
        super().__init__(**kwargs)
        self.set_points_as_corners([np.array(p, dtype=float) for p in points])


def make_polyline(*pts, color=WHITE, stroke_width=STROKE_WIDTH) -> _Polyline:
    """Raw polyline through any number of points. Supports add_tip()."""
    polyline = _Polyline(
        *pts, 
        stroke_width=stroke_width, 
        color=color,
    )
    polyline.joint_type = LineJointType.ROUND
    polyline.cap_style = CapStyleType.ROUND
    return polyline


def make_straight_wire(start, end, color=WHITE,
                       stroke_width=STROKE_WIDTH) -> VMobject:
    """Direct straight wire (no bends)."""
    return Line(start, end, color=color, stroke_width=stroke_width)


def make_routed_wire(*waypoints, color=WHITE,
                     stroke_width=STROKE_WIDTH) -> VMobject:
    """Wire through explicit waypoints — you control every corner."""
    return make_polyline(*waypoints, color=color, stroke_width=stroke_width)


def make_junction(pos, radius=DOT_RADIUS, color=WHITE) -> Dot:
    """Filled dot marking a T/cross junction."""
    return Dot(pos, radius=radius, color=color)


# ------------------------------------------------------------------------------
# 1. ORTHOGONAL (MANHATTAN) WIRE — fixes staircase-bend problem
# ------------------------------------------------------------------------------

def make_ortho_wire(
    start: np.ndarray,
    end:   np.ndarray,
    *,
    bend_x:     float | None = None,
    bend_ratio: float        = 0.5,
    color                    = WHITE,
    stroke_width: float      = STROKE_WIDTH,
) -> VMobject:
    """
    Smart H → V → H orthogonal wire between two ports.
    """
    same_y = abs(start[1] - end[1]) < 1e-3
    same_x = abs(start[0] - end[0]) < 1e-3

    if same_y or same_x:
        return make_straight_wire(start, end, color=color,
                                  stroke_width=stroke_width)

    bx = bend_x if bend_x is not None else (
        start[0] + (end[0] - start[0]) * bend_ratio
    )

    return make_polyline(
        start,
        h(start, bx),
        np.array([bx, end[1], 0]),
        end,
        color=color, stroke_width=stroke_width,
    )


# labelled version

def _label_on_segment(
    seg_start: np.ndarray,
    seg_end:   np.ndarray,
    text:      str,
    side       = UP,
    font_size: int   = LABEL_FONT,
    color            = WHITE,
    offset:    float = LABEL_OFFSET,
) -> Text:
    lbl = Text(text, font_size=font_size, color=color)
    mid = midpoint(seg_start, seg_end)
    nudge = np.array([0, offset + lbl.height / 2, 0])
    if np.array_equal(side, DOWN):
        nudge *= -1
    lbl.move_to(mid + nudge)
    return lbl


def make_wire_labelled(
    start: np.ndarray,
    end:   np.ndarray,
    label: str = "",
    *,
    bend_x:      float | None = None,
    bend_ratio:  float        = 0.5,
    label_side                = UP,
    label_color               = WHITE,
    label_font:  int          = LABEL_FONT,
    color                     = WHITE,
    stroke_width: float       = STROKE_WIDTH,
) -> tuple[VMobject, Text | None]:
    wire = make_ortho_wire(start, end, bend_x=bend_x,
                           bend_ratio=bend_ratio, color=color,
                           stroke_width=stroke_width)
    lbl = None
    if label:
        bx = bend_x if bend_x is not None else (
            start[0] + (end[0] - start[0]) * bend_ratio
        )
        lbl = _label_on_segment(
            start, h(start, bx),
            label,
            side=label_side, font_size=label_font, color=label_color,
        )
    return wire, lbl


# ------------------------------------------------------------------------------
# 2. BUS SPLITTER — fixes crowded/misplaced label problem
# ------------------------------------------------------------------------------

def make_bus_split(
    origin:       np.ndarray,
    trunk_x:      float,
    branches:     list[dict],
    *,
    trunk_color               = WHITE,
    stroke_width: float       = STROKE_WIDTH,
    label_font:   int         = LABEL_FONT,
) -> dict:
    ys    = [b["y"] for b in branches]
    top_y = max(ys)
    bot_y = min(ys)

    entry = make_straight_wire(
        origin, h(origin, trunk_x),
        color=trunk_color, stroke_width=stroke_width,
    )
    spine = make_straight_wire(
        np.array([trunk_x, top_y, 0]),
        np.array([trunk_x, bot_y, 0]),
        color=trunk_color, stroke_width=stroke_width,
    )

    out_branches, out_dots, out_labels = [], [], []

    for b in branches:
        tap  = np.array([trunk_x, b["y"], 0])
        dest = np.array(b["dest"],  dtype=float)
        col  = b.get("color", trunk_color)

        bx = b.get("bend_x", None)

        wire, lbl = make_wire_labelled(
            tap, dest,
            label      = b.get("label", ""),
            bend_x     = bx,
            label_side = b.get("label_side",  UP),
            label_color= b.get("label_color", WHITE),
            label_font = b.get("label_font",  label_font),
            color      = col,
            stroke_width = stroke_width,
        )
        out_branches.append(wire)
        if lbl:
            out_labels.append(lbl)

        if b.get("dot", True):
            out_dots.append(make_junction(
                tap,
                color=b.get("dot_color", trunk_color),
            ))

    all_mobs = [entry, spine] + out_branches + out_dots + out_labels
    return {
        "entry":    entry,
        "spine":    spine,
        "branches": out_branches,
        "dots":     out_dots,
        "labels":   out_labels,
        "all":      all_mobs,
    }


def animate_bus(
    scene:       "Scene",
    bus:         dict,
    trunk_rt:    float = 0.5,
    branch_rt:   float = 0.6,
    stagger:     float = 0.12,
) -> None:
    scene.play(Create(bus["entry"]), Create(bus["spine"]), run_time=trunk_rt)

    if bus["branches"]:
        scene.play(
            LaggedStart(
                *[AnimationGroup(Create(w)) for w in bus["branches"]],
                lag_ratio=stagger,
            ),
            run_time=branch_rt,
        )

    pop = [FadeIn(d) for d in bus["dots"]] + [Write(l) for l in bus["labels"]]
    if pop:
        scene.play(*pop, run_time=0.35)


# ------------------------------------------------------------------------------
# 3. ANIMATION HELPERS
# ------------------------------------------------------------------------------

def pulse_wire(scene, wire, color=SIGNAL_COLOR, run_time=0.4, restore=True):
    orig = wire.get_color()
    scene.play(wire.animate.set_color(color), run_time=run_time)
    if restore:
        scene.play(wire.animate.set_color(orig), run_time=run_time * 0.5)


def pulse_wires(scene, wires, color=SIGNAL_COLOR, run_time=0.35, restore=True):
    origs = [w.get_color() for w in wires]
    scene.play(*[w.animate.set_color(color) for w in wires], run_time=run_time)
    if restore:
        scene.play(*[w.animate.set_color(o) for w, o in zip(wires, origs)],
                   run_time=run_time * 0.5)


def flash_component(scene, mob, color=SIGNAL_COLOR, scale=1.05, run_time=0.4):
    scene.play(Indicate(mob, color=color, scale_factor=scale), run_time=run_time)


def highlight_component(scene, component, label="", run_time=0.5):
    anims = [Indicate(component, color=ACTIVE_COMP, scale_factor=1.06)]
    banner = None
    if label:
        banner = Text(label, font_size=15, color=ACTIVE_COMP)
        banner.next_to(component, UP, buff=0.15)
        anims.append(FadeIn(banner, shift=UP * 0.1))
    scene.play(*anims, run_time=run_time)
    if banner:
        scene.play(FadeOut(banner), run_time=0.3)


def signal_flow(scene, steps, default_run_time=0.45):
    for step in steps:
        rt    = step.get("run_time", default_run_time)
        pause = step.get("pause", 0.2)
        color = CTRL_COLOR if step.get("ctrl") else SIGNAL_COLOR

        if "wire" in step:
            w    = step["wire"]
            orig = w.get_color()
            scene.play(w.animate.set_color(color), run_time=rt)
            if "value" in step:
                val = Text(step["value"], font_size=12, color=color)
                val.move_to(w.get_center() + UP * 0.22)
                scene.play(FadeIn(val, shift=RIGHT * 0.2), run_time=rt * 0.4)
                scene.play(FadeOut(val),                   run_time=rt * 0.3)
            scene.play(w.animate.set_color(orig), run_time=rt * 0.4)

        if "component" in step:
            highlight_component(scene, step["component"],
                                label=step.get("label", ""), run_time=rt)
        scene.wait(pause)


# ------------------------------------------------------------------------------
# 4. V-H-V WIRE — for control lines dropping from above
# ------------------------------------------------------------------------------

def make_v_h_v_wire(
    start: np.ndarray,
    end:   np.ndarray,
    *,
    bend_y:     float | None = None,
    bend_ratio: float        = 0.5,
    color                    = WHITE,
    stroke_width: float      = STROKE_WIDTH,
) -> VMobject:
    """
    V → H → V orthogonal wire. Mirror of make_ortho_wire.

    Ideal for control lines that drop from a Control Unit above,
    run horizontally over components, then drop into a port below.

    bend_y sets the horizontal corridor's y-position (absolute).
    If omitted, defaults to halfway between start and end y.
    """
    same_y = abs(start[1] - end[1]) < 1e-3
    same_x = abs(start[0] - end[0]) < 1e-3

    if same_y or same_x:
        return make_straight_wire(start, end, color=color,
                                  stroke_width=stroke_width)

    by = bend_y if bend_y is not None else (
        start[1] + (end[1] - start[1]) * bend_ratio
    )

    return make_polyline(
        start,
        v(start, by),
        np.array([end[0], by, 0]),
        end,
        color=color, stroke_width=stroke_width,
    )


# ------------------------------------------------------------------------------
# 5. FEEDBACK (U-TURN) WIRE — for writeback / PC loops
# ------------------------------------------------------------------------------

def make_feedback_wire(
    start: np.ndarray,
    end:   np.ndarray,
    *,
    corridor_y:  float,
    turn_up_x:   float,
    color                    = WHITE,
    stroke_width: float      = STROKE_WIDTH,
) -> VMobject:
    """
    Flexible feedback/U-turn wire with explicit routing control.

    Route: start → V(corridor_y) → H(turn_up_x) → V(end_y) → H→ end

    corridor_y — absolute Y for the long horizontal run. Set below all
                 components so the wire clears them without calculation.
    turn_up_x  — absolute X where the wire turns vertical to reach end's
                 Y-level. Set this to the LEFT of the destination port so
                 the final segment is always horizontal (→ correct arrowhead
                 angle; no vertical "stabbing" of the port from below).

    The final segment is always horizontal, so Manim arrowheads render
    correctly regardless of which component or port is the destination.
    """
    return make_polyline(
        start,
        v(start,      corridor_y),                # V down to corridor
        np.array([turn_up_x, corridor_y, 0]),     # H along corridor
        np.array([turn_up_x, end[1],     0]),     # V up to port height
        end,                                      # H into port — horizontal entry ✓
        color=color, stroke_width=stroke_width,
    )


# ------------------------------------------------------------------------------
# 6. DATAPATH ANIMATION MACRO
# ------------------------------------------------------------------------------

def animate_data_path(
    scene,
    path: list[dict],
    *,
    wire_rt:      float = 0.35,
    comp_rt:      float = 0.40,
    pause:        float = 0.15,
    data_color           = SIGNAL_COLOR,
    ctrl_color           = CTRL_COLOR,
) -> None:
    """
    Fire a signal through a sequence of wires and components.

    Each entry in *path* is a dict with ONE of:
      - {"wire": w}                      — pulse the wire
      - {"wire": w, "label": "A+B"}      — pulse + show value label
      - {"component": c}                 — flash the component
      - {"component": c, "label": "ALU"} — flash + show banner text
      - {"ctrl": w}                      — pulse wire in control color

    Optional per-step overrides: "run_time", "pause", "color".

    Example:
        animate_data_path(scene, [
            {"wire": w_pc},
            {"component": im.shape, "label": "Fetch"},
            {"wire": w_bus},
            {"component": rf.shape},
            {"wire": w_rd1},
            {"ctrl": w_alu_ctrl},
            {"component": alu.shape, "label": "ADD"},
        ])
    """
    for step in path:
        rt = step.get("run_time", wire_rt if "wire" in step or "ctrl" in step else comp_rt)
        p  = step.get("pause", pause)

        if "ctrl" in step:
            w = step["ctrl"]
            col = step.get("color", ctrl_color)
            orig = w.get_color()
            scene.play(w.animate.set_color(col), run_time=rt)
            scene.play(w.animate.set_color(orig), run_time=rt * 0.5)

        elif "wire" in step:
            w = step["wire"]
            col = step.get("color", data_color)
            orig = w.get_color()
            scene.play(w.animate.set_color(col), run_time=rt)
            if "label" in step:
                val = Text(step["label"], font_size=12, color=col)
                val.move_to(w.get_center() + UP * 0.22)
                scene.play(FadeIn(val, shift=RIGHT * 0.15), run_time=rt * 0.4)
                scene.play(FadeOut(val), run_time=rt * 0.3)
            scene.play(w.animate.set_color(orig), run_time=rt * 0.5)

        elif "component" in step:
            c = step["component"]
            col = step.get("color", data_color)
            anims = [Indicate(c, color=col, scale_factor=1.05)]
            banner = None
            if "label" in step:
                banner = Text(step["label"], font_size=15, color=col)
                banner.next_to(c, UP, buff=0.15)
                anims.append(FadeIn(banner, shift=UP * 0.1))
            scene.play(*anims, run_time=rt)
            if banner:
                scene.play(FadeOut(banner), run_time=0.2)

        if p > 0:
            scene.wait(p)


# ------------------------------------------------------------------------------
# 7. PORT-TO-PORT CONNECTION — wire + arrow + label in one call
# ------------------------------------------------------------------------------

def make_connection(
    start: np.ndarray,
    end:   np.ndarray,
    *,
    label:        str   = "",
    arrow:        bool  = True,
    tip_length:   float = 0.15,
    tip_dir              = LEFT,
    label_side           = UP,
    label_color          = WHITE,
    color                = WHITE,
    ctrl:         bool  = False,
    wire_func            = None,
    **wire_kwargs,
) -> dict:
    """
    One-call port-to-port connection.

    Returns dict:
      "wire"  — the wire VMobject
      "arrow" — stub Arrow at destination (or None)
      "label" — Text label (or None)
      "all"   — VGroup of everything (for single Create)

    wire_func defaults to make_ortho_wire. Pass make_v_h_v_wire,
    make_straight_wire, etc. for other routing.
    """
    col = CTRL_COLOR if ctrl else color
    wf  = wire_func or make_ortho_wire

    wire = wf(start, end, color=col, **wire_kwargs)

    arr = None
    if arrow:
        arr = make_stub_arrow(end, direction=tip_dir,
                              length=tip_length, color=col)
        
    lbl = None
    if label:
        lbl = Text(label, font_size=12, color=label_color or col)

        # หา segment แนวนอนที่ยาวที่สุดใน polyline แล้ววาง label ตรงกลาง
        anchors = wire.get_anchors()
        best_mid = wire.point_from_proportion(0.5)  # fallback
        best_len = -1

        for i in range(len(anchors) - 1):
            a, b = anchors[i], anchors[i + 1]
            # เช็กว่าเป็น segment แนวนอน (y ต่างกันน้อยมาก)
            if abs(a[1] - b[1]) < 1e-2:
                seg_len = abs(b[0] - a[0])
                if seg_len > best_len:
                    best_len = seg_len
                    best_mid = (a + b) / 2

        if np.array_equal(label_side, UP):
            lbl.next_to(best_mid, UP, buff=0.08)
        else:
            lbl.next_to(best_mid, DOWN, buff=0.08)
        

    parts = [wire]
    if arr:
        parts.append(arr)
    if lbl:
        parts.append(lbl)

    return {
        "wire":  wire,
        "arrow": arr,
        "label": lbl,
        "all":   VGroup(*parts),
    }


def draw_connections(
    scene,
    connections: dict,
    run_time: float = 0.8,
) -> None:
    """
    Batch-animate a dict of named connections in one play() call.

    connections = {"w_sum": conn1, "w_rd1": conn2, ...}
    Each value is a dict returned by make_connection().
    """
    anims = []
    for conn in connections.values():
        anims.append(Create(conn["wire"]))
        if conn.get("arrow"):
            anims.append(GrowArrow(conn["arrow"]))
        if conn.get("label"):
            anims.append(Write(conn["label"]))
    if anims:
        scene.play(*anims, run_time=run_time)


# ------------------------------------------------------------------------------
# 8. LEGACY / CONVENIENCE
# ------------------------------------------------------------------------------

def make_wire(start, end, color=WHITE, stroke_width=STROKE_WIDTH) -> VMobject:
    mid_x = (start[0] + end[0]) / 2
    return make_polyline(start, h(start, mid_x), v(end, mid_x), end,
                         color=color, stroke_width=stroke_width)


def make_stub_arrow(port, direction=LEFT, length=1.0, color=GRAY) -> Arrow:
    return Arrow(port + direction * length, port,
                 buff=0, stroke_width=2, color=color)


def label_above(mob, text, font_size=13, color=WHITE):
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mob, UP, buff=0.08);  return lbl

def label_below(mob, text, font_size=13, color=WHITE):
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mob, DOWN, buff=0.08); return lbl

def label_left(mob, text, font_size=13, color=WHITE):
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mob, LEFT, buff=0.08); return lbl

def label_right(mob, text, font_size=13, color=WHITE):
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mob, RIGHT, buff=0.08); return lbl


def draw_stub(scene, port, text="", direction=LEFT,
              length=1.0, color=GRAY, text_color=WHITE) -> Arrow:
    arrow = make_stub_arrow(port, direction=direction, length=length, color=color)
    anims = [GrowArrow(arrow)]
    if text:
        lbl = Text(text, font_size=14, color=text_color)
        lbl.next_to(arrow, direction, buff=0.08)
        anims.append(Write(lbl))
    scene.play(*anims)
    return arrow


def debug_wire_crossings(scene: Scene, connections: dict):
    """
    ฟังก์ชันผู้ช่วยสำหรับ Debug: จะวาดวงกลมสีแดงกะพริบตรงจุดที่สายไฟตัดกันแนวดิ่ง-แนวนอน
    ช่วยให้เห็นว่าสายไหนทับกันบ้าง จะได้ปรับ bend_x, bend_y หลบได้ง่ายขึ้น
    """
    segments = []
    
    # 1. แตกสายไฟทั้งหมดออกเป็นเส้นตรงย่อยๆ
    for conn in connections.values():
        if "wire" in conn and conn["wire"] is not None:
            # ดึงจุดมุมทั้งหมดของสายไฟ
            anchors = conn["wire"].get_anchors()
            for i in range(len(anchors) - 1):
                segments.append((anchors[i], anchors[i+1]))
                
    cross_points = []
    
    # 2. เช็กจุดตัดของทุกเส้นคู่
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            A, B = segments[i]
            C, D = segments[j]
            
            # กรณีที่ 1: AB แนวนอน, CD แนวตั้ง
            if abs(A[1] - B[1]) < 1e-3 and abs(C[0] - D[0]) < 1e-3:
                # เช็กว่าแกน X ของเส้นแนวตั้ง ทะลุผ่านแกน X ของเส้นแนวนอนไหม
                if (min(A[0], B[0]) + 1e-3 < C[0] < max(A[0], B[0]) - 1e-3) and \
                   (min(C[1], D[1]) + 1e-3 < A[1] < max(C[1], D[1]) - 1e-3):
                    cross_points.append(np.array([C[0], A[1], 0]))
                    
            # กรณีที่ 2: AB แนวตั้ง, CD แนวนอน
            elif abs(A[0] - B[0]) < 1e-3 and abs(C[1] - D[1]) < 1e-3:
                if (min(C[0], D[0]) + 1e-3 < A[0] < max(C[0], D[0]) - 1e-3) and \
                   (min(A[1], B[1]) + 1e-3 < C[1] < max(A[1], B[1]) - 1e-3):
                    cross_points.append(np.array([A[0], C[1], 0]))

    # 3. วาดวงกลมสีแดงตรงจุดที่ตัดกัน
    if cross_points:
        print(f"⚠️ Debugger: พบสายไฟตัดกัน {len(cross_points)} จุด!")
        for pt in cross_points:
            circle = Circle(radius=0.15, color=RED, stroke_width=4).move_to(pt)
            scene.add(circle)
            # ทำให้กะพริบเพื่อสะดุดตา
            scene.play(Indicate(circle, color=RED, scale_factor=1.5), run_time=0.3)