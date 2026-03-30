from manim import *
import numpy as np


class ShiftLeft1Component(VGroup):
    """
    Shift-left-1 unit for the RISC-V single-cycle datapath.
    Small trapezoid (like Sign Extend) with input on the left, output on the right.
    """

    def __init__(
        self,
        width: float = 1.2,
        height: float = 0.9,
        body_color: str = "#DDDDDD",
        port_offset: float = 0.12,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._color = body_color
        self._offset = port_offset

        self.shape = self._build_shape()
        lbl = Text("Shift\nleft 1", font_size=10, color=body_color, weight=BOLD,
                    line_spacing=0.8)
        lbl.move_to(self.shape.get_center())
        self.add(self.shape, lbl)

    def _build_shape(self) -> Polygon:
        w, h = self._w, self._h
        # Trapezoid: narrow left, wider right (like sign-extend direction)
        TL = np.array([-w / 2,  h * 0.35, 0])
        TR = np.array([ w / 2,  h / 2,    0])
        BR = np.array([ w / 2, -h / 2,    0])
        BL = np.array([-w / 2, -h * 0.35, 0])

        poly = Polygon(
            TL, TR, BR, BL,
            color=self._color,
            stroke_width=2.5,
        )
        poly.set_fill(self._color, opacity=0.06)
        return poly

    def get_input(self) -> np.ndarray:
        return np.array([
            self.shape.get_left()[0] - self._offset,
            self.get_center()[1],
            0,
        ])

    def get_output(self) -> np.ndarray:
        return np.array([
            self.shape.get_right()[0] + self._offset,
            self.get_center()[1],
            0,
        ])
