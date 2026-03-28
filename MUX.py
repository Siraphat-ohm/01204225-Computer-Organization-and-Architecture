from manim import *
import numpy as np

class MuxComponent(VGroup):
    """
    2-to-1 Multiplexer matched to the RISC-V single-cycle datapath schematic.
    """

    def __init__(
        self,
        width: float = 0.6,
        height: float = 1.5,
        body_color: str = "#555555",
        ctrl_color: str = "#4A90D9",
        label: str = "MUX",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._body_color = body_color
        self._ctrl_color = ctrl_color
        self._label_str  = label
        self._offset = port_offset
        self.shape = self._build_shape()
        self._build_labels()

        self.add(self.shape)

    def _build_shape(self) -> RoundedRectangle:
        rect = RoundedRectangle(
            width=self._w,
            height=self._h,
            corner_radius=self._w / 2,
            color=self._body_color,
            stroke_width=3,
        )
        rect.set_fill(self._body_color, opacity=0.06)
        return rect

    def _build_labels(self):
        mid_y_0 = (self.shape.get_top()[1] + self.shape.get_center()[1]) / 2
        mid_y_1 = (self.shape.get_bottom()[1] + self.shape.get_center()[1]) / 2
        cx = self.shape.get_center()[0]

        self.lbl_0 = Text("0", font_size=14, weight=BOLD, color=self._body_color)
        self.lbl_0.move_to(np.array([cx, mid_y_0, 0]))

        # Vertical M-U-X label
        self.lbl_mux = Text(
            "\n".join(self._label_str),
            font_size=12, weight=BOLD, color=self._body_color,
            line_spacing=0.6,
        )
        self.lbl_mux.move_to(self.shape.get_center())

        self.lbl_1 = Text("1", font_size=14, weight=BOLD, color=self._body_color)
        self.lbl_1.move_to(np.array([cx, mid_y_1, 0]))

        self.add(self.lbl_0, self.lbl_mux, self.lbl_1)

    def get_input_0(self) -> np.ndarray:
        mid_y = (self.shape.get_top()[1] + self.shape.get_center()[1]) / 2
        x = self.shape.get_left()[0] - self._offset
        return np.array([x, mid_y, 0])

    def get_input_1(self) -> np.ndarray:
        mid_y = (self.shape.get_bottom()[1] + self.shape.get_center()[1]) / 2
        x = self.shape.get_left()[0] - self._offset
        return np.array([x, mid_y, 0])

    def get_output(self) -> np.ndarray:
        return self.shape.get_right() + RIGHT * self._offset

    def get_ctrl_port(self) -> np.ndarray:
        return self.shape.get_bottom() + DOWN * self._offset

class TestMuxScene(Scene):
    def construct(self):
        mux = MuxComponent(port_offset=0.2).scale(1.4)
        self.play(Create(mux), run_time=0.7)
        self.wait(0.3)

        arrow_kw = dict(buff=0, stroke_width=2.5)
        lbl_kw   = dict(font_size=15)

        p0 = mux.get_input_0()
        a0 = Arrow(p0 + LEFT * 1.1, p0, color=GRAY, **arrow_kw)
        l0 = Text("Input 0", **lbl_kw).next_to(a0, LEFT, buff=0.1)

        p1 = mux.get_input_1()
        a1 = Arrow(p1 + LEFT * 1.1, p1, color=GRAY, **arrow_kw)
        l1 = Text("Input 1", **lbl_kw).next_to(a1, LEFT, buff=0.1)

        po = mux.get_output()
        ao = Arrow(po, po + RIGHT * 1.1, color=GRAY, **arrow_kw)
        lo = Text("Output", **lbl_kw).next_to(ao, RIGHT, buff=0.1)

        pc = mux.get_ctrl_port()
        ac = Arrow(pc + DOWN * 0.9, pc, color=BLUE, **arrow_kw)
        lc = Text("Select", font_size=15, color=BLUE).next_to(ac, DOWN, buff=0.05)

        self.play(
            GrowArrow(a0), Write(l0),
            GrowArrow(a1), Write(l1),
            GrowArrow(ao), Write(lo),
            GrowArrow(ac), Write(lc),
        )
        self.wait(2)
