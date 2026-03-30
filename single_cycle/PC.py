from manim import *
import numpy as np


class PCComponent(VGroup):
    """
    Program Counter register for the RISC-V single-cycle datapath.
    Small rectangle with input on the left and output on the right.
    """

    def __init__(
        self,
        width: float = 1.0,
        height: float = 2.0,
        body_color: str = "#DDDDDD",
        label: str = "PC",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._color = body_color
        self._offset = port_offset

        self.shape = Rectangle(
            width=width, height=height,
            color=body_color, stroke_width=3,
        )
        self.shape.set_fill(body_color, opacity=0.06)
        self.add(self.shape)

        lbl = Text(label, font_size=16, weight=BOLD, color=body_color)
        lbl.move_to(self.shape.get_center())
        self.add(lbl)

    def get_input(self) -> np.ndarray:
        """Left — next PC value."""
        x = self.shape.get_left()[0] - self._offset
        y = self.get_center()[1]
        return np.array([x, y, 0])

    def get_output(self) -> np.ndarray:
        """Right — current PC value."""
        x = self.shape.get_right()[0] + self._offset
        y = self.get_center()[1]
        return np.array([x, y, 0])
