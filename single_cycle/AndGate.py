import numpy as np
from manim import *


class AndGateComponent(VGroup):
    """
    Patterson & Hennessy style AND gate for the RISC-V single-cycle datapath.
    D-shape: flat left edge with a curved right side.
    Two inputs on the left (top=a, bottom=b), one output on the right.
    """

    def __init__(
        self,
        width: float = 0.55,
        height: float = 0.50,
        body_color: str = "#DDDDDD",
        port_offset: float = 0.10,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._color = body_color
        self._offset = port_offset

        self.shape = self._build_shape()
        lbl = Text("&", font_size=10, color=body_color)
        lbl.move_to(self.shape.get_center())
        self.add(self.shape, lbl)

    def _build_shape(self) -> VMobject:
        w, h = self._w, self._h

        x_left = -w / 2
        x_mid = 0
        y_top = h / 2
        y_bot = -h / 2

        # Build as a path: left edge + top + arc + bottom
        shape = VMobject(color=self._color, stroke_width=2)
        shape.set_fill(self._color, opacity=0.08)

        TL = np.array([x_left, y_top, 0])
        BL = np.array([x_left, y_bot, 0])
        TM = np.array([x_mid, y_top, 0])
        BM = np.array([x_mid, y_bot, 0])
        R = np.array([x_mid + h / 2, 0, 0])

        shape.set_points_as_corners([BL, TL, TM])
        arc = ArcBetweenPoints(TM, BM, angle=-PI, color=self._color, stroke_width=2)
        shape.append_points(arc.get_points())
        shape.add_line_to(BL)

        return shape

    def get_input_a(self) -> np.ndarray:
        """Left-top input."""
        return np.array(
            [
                self.get_center()[0] - self._w / 2 - self._offset,
                self.get_center()[1] + self._h * 0.25,
                0,
            ]
        )

    def get_input_b(self) -> np.ndarray:
        """Left-bottom input."""
        return np.array(
            [
                self.get_center()[0] - self._w / 2 - self._offset,
                self.get_center()[1] - self._h * 0.25,
                0,
            ]
        )

    def get_output(self) -> np.ndarray:
        """Right output."""
        return np.array(
            [
                self.get_center()[0] + self._h / 2 + self._offset,
                self.get_center()[1],
                0,
            ]
        )
