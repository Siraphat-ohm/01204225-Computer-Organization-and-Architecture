from manim import *
import numpy as np

class RegFileComponent(VGroup):
    """
    RISC-V Register File matched to the Patterson & Hennessy (2020)
    single-cycle datapath schematic.
    """

    def __init__(
        self,
        width: float = 3.2,
        height: float = 4.2,
        body_color: str = "#DDDDDD",
        ctrl_color: str = "#4A90D9",
        label: str = "Registers",
        port_offset: float = 0.15,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._w = width
        self._h = height
        self._body_color = body_color
        self._ctrl_color = ctrl_color
        self._label_str = label
        self._offset = port_offset

        self.shape = self._build_shape()
        self._build_inner_labels()

        self.add(self.shape)

    def _build_shape(self) -> Rectangle:
        rect = Rectangle(
            width=self._w,
            height=self._h,
            color=self._body_color,
            stroke_width=3,
        )
        rect.set_fill(self._body_color, opacity=0.06)
        return rect

    def _build_inner_labels(self):
        w, h = self._w, self._h
        x_left  = -w / 2 + 0.18
        x_right =  w / 2 - 0.18

        font   = 14
        color  = self._body_color

        label_data = [
            ("Read\nregister 1", self._port_y("rr1")),
            ("Read\nregister 2", self._port_y("rr2")),
            ("Write\nregister",  self._port_y("wr")),
            ("Write\ndata",      self._port_y("wd")),
        ]
        for text, y in label_data:
            lbl = Text(text, font_size=font, color=color, line_spacing=0.8)
            lbl.move_to(np.array([x_left, y, 0]))
            lbl.align_to(np.array([x_left, y, 0]), LEFT)
            self.add(lbl)

        out_data = [
            ("Read\ndata 1", self._port_y("rd1")),
            ("Read\ndata 2", self._port_y("rd2")),
        ]
        for text, y in out_data:
            lbl = Text(text, font_size=font, color=color, line_spacing=0.8)
            lbl.move_to(np.array([x_right, y, 0]))
            lbl.align_to(np.array([x_right, y, 0]), RIGHT)
            self.add(lbl)

        main_lbl = Text(
            self._label_str,
            font_size=18,
            weight=BOLD,
            color=self._body_color,
        )
        main_lbl.move_to(
            np.array([x_right, -self._h / 2 + 0.25, 0])
        )
        main_lbl.align_to(np.array([x_right, 0, 0]), RIGHT)
        self.add(main_lbl)

    def _port_y(self, name: str) -> float:
        h = self.shape.get_height()
        positions = {
            "rr1": h * 0.34,
            "rr2": h * 0.11,
            "wr":  -h * 0.15,
            "wd":  -h * 0.36,
            "rd1":  h * 0.22,
            "rd2": -h * 0.25,
        }
        return positions[name]

    def get_read_reg1(self) -> np.ndarray:
        return np.array([self.shape.get_left()[0] - self._offset, self.get_center()[1] + self._port_y("rr1"), 0])

    def get_read_reg2(self) -> np.ndarray:
        return np.array([self.shape.get_left()[0] - self._offset, self.get_center()[1] + self._port_y("rr2"), 0])

    def get_write_reg(self) -> np.ndarray:
        return np.array([self.shape.get_left()[0] - self._offset, self.get_center()[1] + self._port_y("wr"), 0])

    def get_write_data(self) -> np.ndarray:
        return np.array([self.shape.get_left()[0] - self._offset, self.get_center()[1] + self._port_y("wd"), 0])

    def get_read_data1(self) -> np.ndarray:
        return np.array([self.shape.get_right()[0] + self._offset, self.get_center()[1] + self._port_y("rd1"), 0])

    def get_read_data2(self) -> np.ndarray:
        return np.array([self.shape.get_right()[0] + self._offset, self.get_center()[1] + self._port_y("rd2"), 0])

    def get_reg_write(self) -> np.ndarray:
        return np.array([self.get_center()[0], self.shape.get_top()[1] + self._offset, 0])
