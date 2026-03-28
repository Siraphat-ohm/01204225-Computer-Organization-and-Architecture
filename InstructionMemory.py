from manim import *
import numpy as np

DEFAULT_PORT_Y: dict[str, float] = {
    "31_26":  0.38,   # Control
    "25_21":  0.20,   # Read register 1
    "20_16":  0.02,   # Read register 2 / MUX
    "15_11": -0.18,   # MUX (write register)
    "15_0":  -0.36,   # Sign-extend
}


class InstructionMemoryComponent(VGroup):

    def __init__(
        self,
        width: float = 2.8,
        height: float = 3.2,
        body_color: str = "#DDDDDD",
        port_offset: float = 0.15,
        output_offset: float = 0.15,
        port_y_overrides: dict = None,
        show_port_labels: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w       = width
        self._h       = height
        self._color   = body_color
        self._in_off  = port_offset
        self._out_off = output_offset
        self._port_y  = {**DEFAULT_PORT_Y, **(port_y_overrides or {})}

        self.shape = Rectangle(
            width=self._w, height=self._h,
            color=self._color, stroke_width=3,
        )
        self.shape.set_fill(self._color, opacity=0.06)
        self.add(self.shape)
        self._build_inner_labels()
        if show_port_labels:
            self._build_port_labels()

    def _build_inner_labels(self):
        x_l = -self._w / 2 + 0.15
        for text, y_frac in [("Read\naddress", 0.28),
                              ("Instruction\n[31–0]", -0.10)]:
            lbl = Text(text, font_size=13, color=self._color, line_spacing=0.8)
            lbl.move_to([x_l, y_frac * self._h, 0]).align_to([x_l, 0, 0], LEFT)
            self.add(lbl)
        bold = Text("Instruction\nmemory", font_size=14, weight=BOLD,
                    color=self._color, line_spacing=0.85)
        bold.move_to([0, -self._h / 2 + 0.35, 0])
        self.add(bold)

    def _build_port_labels(self):
        x_r = self._w / 2 - 0.12
        for key, name in [("31_26","[31–26]"),("25_21","[25–21]"),
                           ("20_16","[20–16]"),("15_11","[15–11]"),("15_0","[15–0]")]:
            y = self._port_y[key] * self._h
            lbl = Text(name, font_size=10, color=self._color)
            lbl.move_to([x_r, y, 0]).align_to([x_r, 0, 0], RIGHT)
            self.add(lbl)

    # ── port helpers ───────────────────────────────────────────────────────

    def _left_port(self, y_frac):
        x = self.shape.get_left()[0] - self._in_off
        y = self.get_center()[1] + y_frac * self.shape.get_height()
        return np.array([x, y, 0])

    def _right_port(self, key):
        x = self.shape.get_right()[0] + self._out_off
        y = self.get_center()[1] + self._port_y[key] * self.shape.get_height()
        return np.array([x, y, 0])

    def get_read_address(self) -> np.ndarray:
        """Left – PC in."""
        return self._left_port(0.32)

    def inst_bus_origin(self) -> np.ndarray:
        """
        Right edge at Instruction[31-0] label height.
        Use as 'origin' for make_bus_split().
        Intentionally NOT prefixed with get_ to avoid Manim attribute magic.
        """
        x = self.shape.get_right()[0] + self._out_off
        y = self.get_center()[1] - 0.10 * self.shape.get_height()
        return np.array([x, y, 0])

    def get_inst_31_26(self) -> np.ndarray:
        return self._right_port("31_26")

    def get_inst_25_21(self) -> np.ndarray:
        return self._right_port("25_21")

    def get_inst_20_16(self) -> np.ndarray:
        return self._right_port("20_16")

    def get_inst_15_11(self) -> np.ndarray:
        return self._right_port("15_11")

    def get_inst_15_0(self) -> np.ndarray:
        return self._right_port("15_0")