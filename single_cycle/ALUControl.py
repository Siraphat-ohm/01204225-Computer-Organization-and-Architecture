from manim import *
import numpy as np


class ALUControlComponent(VGroup):
    """
    ALU Control unit for the RISC-V single-cycle datapath.
    Small rounded box that decodes ALUOp + funct3/funct7 fields
    into the 4-bit ALU control signal.
    Matches the Patterson & Hennessy schematic style.
    """

    def __init__(
        self,
        width: float = 2.0,
        height: float = 1.0,
        body_color: str = "#4A90D9",
        label: str = "ALU\ncontrol",
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

    def _build_shape(self, width, height) -> RoundedRectangle:
        rect = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=height / 2,
            color=self._color,
            stroke_width=3,
        )
        rect.set_fill(self._color, opacity=0.08)
        return rect

    def _build_inner_labels(self):
        lbl = Text(
            self._label_str,
            font_size=12,
            weight=BOLD,
            color=self._color,
            line_spacing=0.7,
        )
        lbl.move_to(self.shape.get_center())
        self.add(lbl)

    def get_funct_input(self) -> np.ndarray:
        """Bottom center — funct3/funct7 fields from instruction."""
        x = self.get_center()[0]
        y = self.shape.get_bottom()[1] - self._offset
        return np.array([x, y, 0])

    def get_aluop_input(self) -> np.ndarray:
        """Top-left — ALUOp from main Control Unit."""
        y = self.shape.get_top()[1] + self._offset
        x = self.get_center()[0] - self.shape.get_width() / 4
        return np.array([x, y, 0])

    def get_alu_ctrl_output(self) -> np.ndarray:
        """Top-right — 4-bit ALU control signal to ALU."""
        y = self.shape.get_top()[1] + self._offset
        x = self.get_center()[0] + self.shape.get_width() / 4
        return np.array([x, y, 0])
