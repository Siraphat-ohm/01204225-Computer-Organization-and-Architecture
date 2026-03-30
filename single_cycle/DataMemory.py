from manim import *
import numpy as np


class DataMemoryComponent(VGroup):
    """
    Data Memory for the RISC-V single-cycle datapath.
    Patterson & Hennessy style rectangle with left-side inputs
    (Address, Write data) and right-side output (Read data).
    Control signals MemRead and MemWrite enter from the top.
    """

    def __init__(
        self,
        width: float = 2.8,
        height: float = 3.8,
        body_color: str = "#DDDDDD",
        ctrl_color: str = "#4A90D9",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._body_color = body_color
        self._ctrl_color = ctrl_color
        self._offset = port_offset

        self.shape = Rectangle(
            width=width, height=height,
            color=body_color, stroke_width=3,
        )
        self.shape.set_fill(body_color, opacity=0.06)
        self.add(self.shape)
        self._build_inner_labels()

    def _build_inner_labels(self):
        w = self.shape.get_width()
        h = self.shape.get_height()
        col = self._body_color
        x_l = -w / 2 + 0.18
        x_r = w / 2 - 0.18

        for text, y_frac in [("Address", 0.28), ("Write\ndata", -0.10)]:
            lbl = Text(text, font_size=13, color=col, line_spacing=0.8)
            lbl.move_to([x_l, y_frac * h, 0]).align_to([x_l, 0, 0], LEFT)
            self.add(lbl)

        rd_lbl = Text("Read\ndata", font_size=13, color=col, line_spacing=0.8)
        rd_lbl.move_to([x_r, 0.10 * h, 0]).align_to([x_r, 0, 0], RIGHT)
        self.add(rd_lbl)

        bold = Text("Data\nmemory", font_size=14, weight=BOLD,
                     color=col, line_spacing=0.85)
        bold.move_to([0, -h / 2 + 0.35, 0])
        self.add(bold)

    def get_address(self) -> np.ndarray:
        x = self.shape.get_left()[0] - self._offset
        y = self.get_center()[1] + self.shape.get_height() * 0.28
        return np.array([x, y, 0])

    def get_write_data(self) -> np.ndarray:
        x = self.shape.get_left()[0] - self._offset
        y = self.get_center()[1] - self.shape.get_height() * 0.10
        return np.array([x, y, 0])

    def get_read_data(self) -> np.ndarray:
        x = self.shape.get_right()[0] + self._offset
        y = self.get_center()[1] + self.shape.get_height() * 0.10
        return np.array([x, y, 0])

    def get_mem_read(self) -> np.ndarray:
        """Top — MemRead control signal."""
        x = self.get_center()[0] - self.shape.get_width() / 4
        y = self.shape.get_top()[1] + self._offset
        return np.array([x, y, 0])

    def get_mem_write(self) -> np.ndarray:
        """Top — MemWrite control signal."""
        x = self.get_center()[0] + self.shape.get_width() / 4
        y = self.shape.get_top()[1] + self._offset
        return np.array([x, y, 0])
