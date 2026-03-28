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
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._color = body_color
        self._label_str = label
        self._offset = port_offset

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
        pt = (v[0] + v[5]) / 2
        return pt + LEFT * self._offset

    def get_input_b(self) -> np.ndarray:
        v = self._verts()
        pt = (v[5] + v[4]) / 2
        return pt + LEFT * self._offset

    def get_output(self) -> np.ndarray:
        return self._verts()[2] + RIGHT * self._offset

    def get_zero_port(self) -> np.ndarray:
        v = self._verts()
        return (v[1] + v[2]) / 2 + UP * self._offset + RIGHT * self._offset

    def get_ctrl_port(self) -> np.ndarray:
        return self.shape.get_bottom() + DOWN * self._offset

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
