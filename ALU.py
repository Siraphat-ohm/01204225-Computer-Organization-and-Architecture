from manim import *
import numpy as np

RV32I_ALU_OPS: dict[str, str] = {
    "ADD":  "A + B",
    "SUB":  "A - B",
    "AND":  "A & B",
    "OR":   "A | B",
    "XOR":  "A ^ B",
    "SLL":  "A << B[4:0]",
    "SRL":  "A >> B[4:0]",
    "SRA":  "A >>> B[4:0]",
    "SLT":  "A <s B ? 1 : 0",
    "SLTU": "A <u B ? 1 : 0",
    "PASS": "B",
}

class ALUComponent(VGroup):
    """
    RV32I ALU shape matched to the Patterson & Hennessy / RISC-V
    single-cycle datapath schematic.
    """

    OPS = RV32I_ALU_OPS

    def __init__(
        self,
        width: float = 2.2,
        height: float = 3.0,
        body_color: str = "#4A90D9",
        label: str = "ALU",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._color = body_color
        self._label_str = label

        self.shape    = self._build_shape()
        self.lbl      = self._build_label()
        self.op_label = VMobject()

        self.add(self.shape, self.lbl)

    def _build_shape(self) -> Polygon:
        w, h = self._w, self._h
        notch = h * 0.35

        x_left  = -w / 2
        x_notch = x_left + notch
        x_right = w / 2
        x_tip   = w / 2 + h * 0.28

        y_top    =  h / 2
        y_bot    = -h / 2
        y_mid    =  0

        cut = h * 0.15

        TL = np.array([x_left + cut,  y_top, 0])
        TR = np.array([x_right,       y_top, 0])
        R  = np.array([x_tip,         y_mid, 0])
        BR = np.array([x_right,       y_bot, 0])
        BL = np.array([x_left + cut,  y_bot, 0])
        ML = np.array([x_notch,       y_mid, 0])

        poly = Polygon(
            TL, TR, R, BR, BL, ML,
            color=self._color,
            stroke_width=3,
        )
        poly.set_fill(self._color, opacity=0.08)
        return poly

    def _build_label(self) -> Text:
        lbl = Text(self._label_str, font_size=22, weight=BOLD, color=self._color)
        lbl.move_to(self.shape.get_center() + RIGHT * 0.15)
        return lbl

    def _verts(self) -> np.ndarray:
        return self.shape.get_vertices()

    def get_input_a(self) -> np.ndarray:
        v = self._verts()
        return (v[0] + v[5]) / 2

    def get_input_b(self) -> np.ndarray:
        v = self._verts()
        return (v[5] + v[4]) / 2

    def get_output(self) -> np.ndarray:
        return self._verts()[2]

    def get_zero_port(self) -> np.ndarray:
        v = self._verts()
        return (v[1] + v[2]) / 2

    def get_ctrl_port(self) -> np.ndarray:
        return self.shape.get_bottom()

    def set_operation(self, op: str) -> "ALUComponent":
        expr = self.OPS.get(op.upper(), op)
        new_lbl = Text(
            f"{op}  {expr}", font_size=13, color=YELLOW, slant=ITALIC
        )
        new_lbl.next_to(self.lbl, DOWN, buff=0.1)
        self.remove(self.op_label)
        self.op_label = new_lbl
        self.add(self.op_label)
        return self

    def animate_operation(
        self, scene: "Scene", op: str, run_time: float = 0.6
    ) -> None:
        self.set_operation(op)
        scene.play(
            Indicate(self.shape, color=YELLOW, scale_factor=1.04),
            FadeIn(self.op_label, shift=UP * 0.1),
            run_time=run_time,
        )

class TestALUScene(Scene):
    def construct(self):
        alu = ALUComponent().scale(1.4)
        self.play(Create(alu), run_time=0.8)
        self.wait(0.3)

        arrow_kw = dict(buff=0, stroke_width=2.5)
        lbl_kw   = dict(font_size=15)

        a_end   = alu.get_input_a()
        a_arrow = Arrow(a_end + LEFT * 1.2, a_end, color=GRAY, **arrow_kw)
        a_lbl   = Text("Read data 1", **lbl_kw).next_to(a_arrow, LEFT, buff=0.1)

        b_end   = alu.get_input_b()
        b_arrow = Arrow(b_end + LEFT * 1.2, b_end, color=GRAY, **arrow_kw)
        b_lbl   = Text("Mux output", **lbl_kw).next_to(b_arrow, LEFT, buff=0.1)

        o_start = alu.get_output()
        o_arrow = Arrow(o_start, o_start + RIGHT * 1.2, color=GRAY, **arrow_kw)
        o_lbl   = Text("ALU result", **lbl_kw).next_to(o_arrow, RIGHT, buff=0.1)

        z_pt    = alu.get_zero_port()
        z_arrow = Arrow(z_pt, z_pt + RIGHT * 0.6 + UP * 0.5, color=BLUE, **arrow_kw)
        z_lbl   = Text("Zero", font_size=15, color=BLUE).next_to(z_arrow.get_end(), RIGHT, buff=0.05)

        c_pt    = alu.get_ctrl_port()
        c_arrow = Arrow(c_pt + DOWN * 0.9, c_pt, color=BLUE, **arrow_kw)
        c_lbl   = Text("ALU control", font_size=15, color=BLUE).next_to(c_arrow, DOWN, buff=0.05)

        self.play(
            GrowArrow(a_arrow), Write(a_lbl),
            GrowArrow(b_arrow), Write(b_lbl),
            GrowArrow(o_arrow), Write(o_lbl),
            GrowArrow(z_arrow), Write(z_lbl),
            GrowArrow(c_arrow), Write(c_lbl),
        )
        self.wait(1)

        for op in ["ADD", "SUB", "AND", "SLT", "SRL"]:
            alu.animate_operation(self, op, run_time=0.5)
            self.wait(0.8)

        self.wait(1)
