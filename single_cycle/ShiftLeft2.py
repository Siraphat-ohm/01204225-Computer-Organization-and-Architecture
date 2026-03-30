from manim import *
import numpy as np


class ShiftLeft2Component(VGroup):
    """
    Shift-left-2 unit for the RISC-V single-cycle datapath.
    Trapezoid shape (narrow input, wider output) similar to Sign-extend.
    """

    def __init__(
        self,
        width: float = 1.6,
        height: float = 1.2,
        body_color: str = "#DDDDDD",
        label: str = "Shift\nleft 2",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._color = body_color
        self._label_str = label
        self._offset = port_offset

        self.shape = self._build_shape(width, height)
        self._build_inner_labels()
        self.add(self.shape)

    def _build_shape(self, w, h) -> Polygon:
        TL = np.array([-w / 2,  h * 0.35, 0])
        TR = np.array([ w / 2,  h / 2,    0])
        BR = np.array([ w / 2, -h / 2,    0])
        BL = np.array([-w / 2, -h * 0.35, 0])
        poly = Polygon(TL, TR, BR, BL,
                        color=self._color, stroke_width=3)
        poly.set_fill(self._color, opacity=0.06)
        return poly

    def _build_inner_labels(self):
        lbl = Text(self._label_str, font_size=12, weight=BOLD,
                    color=self._color, line_spacing=0.8)
        lbl.move_to(self.shape.get_center())
        self.add(lbl)

    def get_input(self) -> np.ndarray:
        x = self.shape.get_left()[0] - self._offset
        y = self.get_center()[1]
        return np.array([x, y, 0])

    def get_output(self) -> np.ndarray:
        x = self.shape.get_right()[0] + self._offset
        y = self.get_center()[1]
        return np.array([x, y, 0])
