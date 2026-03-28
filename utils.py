from manim import *
import numpy as np

SIGNAL_COLOR   = YELLOW
INACTIVE_COLOR = "#444444"
ACTIVE_COMP    = YELLOW
CTRL_COLOR     = "#4A90D9"

def make_wire(start: np.ndarray, end: np.ndarray,
              color=WHITE, stroke_width: float = 2.5) -> VMobject:
    """
    L-shaped wire: horizontal from start, then vertical, then horizontal to end.
    """
    mid_x = (start[0] + end[0]) / 2
    pts = [
        start,
        np.array([mid_x, start[1], 0]),
        np.array([mid_x, end[1],   0]),
        end,
    ]
    v = VMobject(stroke_width=stroke_width, color=color)
    v.set_points_as_corners(pts)
    return v


def make_straight_wire(start: np.ndarray, end: np.ndarray,
                       color=WHITE, stroke_width: float = 2.5) -> VMobject:
    """Direct straight wire between two points."""
    v = VMobject(stroke_width=stroke_width, color=color)
    v.set_points_as_corners([start, end])
    return v


def make_stub_arrow(port: np.ndarray, direction=LEFT,
                    length: float = 1.0, color=GRAY) -> Arrow:
    """Short stub arrow pointing into a component port."""
    return Arrow(
        port + direction * length, port,
        buff=0, stroke_width=2, color=color,
    )


def label_above(mobject: Mobject, text: str,
                font_size: int = 13, color=WHITE) -> Text:
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mobject, UP, buff=0.08)
    return lbl


def label_below(mobject: Mobject, text: str,
                font_size: int = 13, color=WHITE) -> Text:
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mobject, DOWN, buff=0.08)
    return lbl


def label_left(mobject: Mobject, text: str,
               font_size: int = 13, color=WHITE) -> Text:
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mobject, LEFT, buff=0.08)
    return lbl


def label_right(mobject: Mobject, text: str,
                font_size: int = 13, color=WHITE) -> Text:
    lbl = Text(text, font_size=font_size, color=color)
    lbl.next_to(mobject, RIGHT, buff=0.08)
    return lbl


def pulse_wire(scene: Scene, wire: VMobject,
               run_time: float = 0.4, restore: bool = True) -> None:
    """Flash a wire yellow then restore its original colour."""
    original_color = wire.get_color()
    scene.play(wire.animate.set_color(SIGNAL_COLOR), run_time=run_time)
    if restore:
        scene.play(wire.animate.set_color(original_color), run_time=run_time * 0.6)


def highlight_component(scene: Scene, component: VMobject,
                        label: str = "", run_time: float = 0.5) -> None:
    """Indicate a component as 'active' via a scale flash and optional label."""
    anims = [Indicate(component, color=ACTIVE_COMP, scale_factor=1.06)]

    banner = None
    if label:
        banner = Text(label, font_size=15, color=ACTIVE_COMP)
        banner.next_to(component, UP, buff=0.15)
        anims.append(FadeIn(banner, shift=UP * 0.1))

    scene.play(*anims, run_time=run_time)

    if banner:
        scene.play(FadeOut(banner), run_time=0.3)


def signal_flow(scene: Scene,
                steps: list[dict],
                default_run_time: float = 0.45) -> None:
    """
    Animate a signal travelling through a sequence of components and wires.
    """
    for step in steps:
        rt    = step.get("run_time", default_run_time)
        pause = step.get("pause",    0.2)
        color = CTRL_COLOR if step.get("ctrl") else SIGNAL_COLOR

        if "wire" in step:
            w = step["wire"]
            original = w.get_color()
            scene.play(w.animate.set_color(color), run_time=rt)

            if "value" in step:
                val_lbl = Text(step["value"], font_size=12, color=color)
                val_lbl.move_to(w.get_center() + UP * 0.22)
                scene.play(FadeIn(val_lbl, shift=RIGHT * 0.2), run_time=rt * 0.4)
                scene.play(FadeOut(val_lbl),                   run_time=rt * 0.3)

            scene.play(w.animate.set_color(original), run_time=rt * 0.4)

        if "component" in step:
            highlight_component(
                scene,
                step["component"],
                label=step.get("label", ""),
                run_time=rt,
            )

        scene.wait(pause)


def draw_wire(scene: Scene,
              start: np.ndarray, end: np.ndarray,
              text: str = "",
              color=WHITE,
              text_color=WHITE,
              text_dir=UP,
              run_time: float = 0.5) -> VMobject:
    """Create, animate and optionally label a wire."""
    w = make_wire(start, end, color=color)
    anims = [Create(w, run_time=run_time)]
    if text:
        lbl = Text(text, font_size=13, color=text_color)
        lbl.next_to(w, text_dir, buff=0.08)
        anims.append(Write(lbl))
    scene.play(*anims)
    return w


def draw_stub(scene: Scene,
              port: np.ndarray,
              text: str = "",
              direction=LEFT,
              length: float = 1.0,
              color=GRAY,
              text_color=WHITE) -> Arrow:
    """Grow a stub arrow into a port and label it."""
    arrow = make_stub_arrow(port, direction=direction, length=length, color=color)
    anims = [GrowArrow(arrow)]
    if text:
        lbl = Text(text, font_size=14, color=text_color)
        lbl.next_to(arrow, direction, buff=0.08)
        anims.append(Write(lbl))
    scene.play(*anims)
    return arrow
