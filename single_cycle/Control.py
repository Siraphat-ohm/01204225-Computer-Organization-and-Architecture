from manim import *
import numpy as np


class ControlComponent(VGroup):
    """
    Main Control Unit for the RISC-V single-cycle datapath.
    Oval shape (P&H style) that decodes opcode into control signals.

    Input:  opcode from instruction [6:0] (left)
    Outputs (right, spaced vertically):
        RegDst, Branch, MemRead, MemtoReg, ALUOp, MemWrite, ALUSrc, RegWrite
    """

    SIGNALS = [
        "Branch",
        "MemRead",
        "MemtoReg",
        "ALUOp",
        "MemWrite",
        "ALUSrc",
        "RegWrite",
    ]

    def __init__(
        self,
        width: float = 2.4,
        height: float = 3.6,
        body_color: str = "#4A90D9",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._color = body_color
        self._offset = port_offset

        self.shape = Ellipse(
            width=width, height=height,
            color=body_color, stroke_width=3,
        )
        self.shape.set_fill(body_color, opacity=0.08)
        self.add(self.shape)
        self._build_inner_labels()

    def _build_inner_labels(self):
        lbl = Text("Control", font_size=14, weight=BOLD, color=self._color)
        lbl.move_to(self.shape.get_center())
        self.add(lbl)


    def get_opcode_input(self) -> np.ndarray:
        """Bottom-centre — opcode / Inst[6:0], wire enters from below."""
        x = self.get_center()[0]
        y = self.shape.get_bottom()[1] - self._offset
        return np.array([x, y, 0])

    def _signal_port(self, index: int) -> np.ndarray:
        """Right-side port for the i-th control signal (0 = top).
        Signals are spread over 70% of the ellipse height."""
        n = len(self.SIGNALS)
        h = self.shape.get_height()
        span = h * 0.7
        top_y = self.get_center()[1] + span / 2
        step = span / (n - 1) if n > 1 else 0
        y = top_y - index * step
        x = self.shape.get_right()[0] + self._offset
        return np.array([x, y, 0])

    def get_branch(self) -> np.ndarray:
        return self._signal_port(0)

    def get_mem_read(self) -> np.ndarray:
        return self._signal_port(1)

    def get_mem_to_reg(self) -> np.ndarray:
        return self._signal_port(2)

    def get_alu_op(self) -> np.ndarray:
        return self._signal_port(3)

    def get_mem_write(self) -> np.ndarray:
        return self._signal_port(4)

    def get_alu_src(self) -> np.ndarray:
        return self._signal_port(5)

    def get_reg_write(self) -> np.ndarray:
        return self._signal_port(6)
