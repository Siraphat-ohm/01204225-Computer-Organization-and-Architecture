import numpy as np
from manim import *


class AdderComponent(VGroup):
    """
    Patterson & Hennessy style adder for the RISC-V single-cycle datapath.
    Trapezoid shape (like a smaller ALU without the notch).
    Two inputs on the left (top=a, bottom=b), one output on the right.
    """

    def __init__(
        self,
        width: float = 0.7,
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
        lbl = Text("Add", font_size=11, color=body_color, weight=BOLD)
        lbl.move_to(self.shape.get_center() + RIGHT * 0.05)
        self.add(self.shape, lbl)

    def _build_shape(self) -> Polygon:
        w, h = self._w, self._h

        x_left = -w / 2
        x_right = w / 2
        x_tip = w / 2 + h * 0.20

        y_top = h / 2
        y_bot = -h / 2

        TL = np.array([x_left, y_top, 0])
        TR = np.array([x_right, y_top, 0])
        R = np.array([x_tip, 0, 0])
        BR = np.array([x_right, y_bot, 0])
        BL = np.array([x_left, y_bot, 0])

        poly = Polygon(
            TL,
            TR,
            R,
            BR,
            BL,
            color=self._color,
            stroke_width=2.5,
        )
        poly.set_fill(self._color, opacity=0.08)
        return poly

    def _verts(self) -> np.ndarray:
        return self.shape.get_vertices()

    def get_input_a(self) -> np.ndarray:
        """Left-top input."""
        v = self._verts()
        # Midpoint of top-left quadrant of left edge
        mid_y = (v[0][1] + self.get_center()[1]) / 2
        return np.array(
            [
                v[0][0] - self._offset,
                mid_y,
                0,
            ]
        )

    def get_input_b(self) -> np.ndarray:
        """Left-bottom input."""
        v = self._verts()
        # Midpoint of bottom-left quadrant of left edge
        mid_y = (v[4][1] + self.get_center()[1]) / 2
        return np.array(
            [
                v[4][0] - self._offset,
                mid_y,
                0,
            ]
        )

    def get_output(self) -> np.ndarray:
        """Right output (tip of trapezoid)."""
        v = self._verts()
        return np.array(
            [
                v[2][0] + self._offset,
                v[2][1],
                0,
            ]
        )
