import sys
import os
# Add parent directory to path so we can import components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manim import *
from ALU import ALUComponent
from MUX import MuxComponent

class TestALUScene(Scene):
    def construct(self):
        alu = ALUComponent().scale(1.4)
        self.play(Create(alu), run_time=0.8)
        self.wait(0.3)

        arrow_kw = dict(buff=0, stroke_width=2.5)
        lbl_kw   = dict(font_size=15)

        a_end   = alu.get_input_a()
        a_arrow = Arrow(a_end + LEFT * 1.2, a_end, color=GRAY, **arrow_kw)
        a_lbl   = Text("Read data 1", **lbl_kw).next_to(a_arrow, LEFT, buff=0.1)

        b_end   = alu.get_input_b()
        b_arrow = Arrow(b_end + LEFT * 1.2, b_end, color=GRAY, **arrow_kw)
        b_lbl   = Text("Mux output", **lbl_kw).next_to(b_arrow, LEFT, buff=0.1)

        o_start = alu.get_output()
        o_arrow = Arrow(o_start, o_start + RIGHT * 1.2, color=GRAY, **arrow_kw)
        o_lbl   = Text("ALU result", **lbl_kw).next_to(o_arrow, RIGHT, buff=0.1)

        z_pt    = alu.get_zero_port()
        z_arrow = Arrow(z_pt, z_pt + RIGHT * 0.6 + UP * 0.5, color=BLUE, **arrow_kw)
        z_lbl   = Text("Zero", font_size=15, color=BLUE).next_to(z_arrow.get_end(), RIGHT, buff=0.05)

        c_pt    = alu.get_ctrl_port()
        c_arrow = Arrow(c_pt + DOWN * 0.9, c_pt, color=BLUE, **arrow_kw)
        c_lbl   = Text("ALU control", font_size=15, color=BLUE).next_to(c_arrow, DOWN, buff=0.05)

        self.play(
            GrowArrow(a_arrow), Write(a_lbl),
            GrowArrow(b_arrow), Write(b_lbl),
            GrowArrow(o_arrow), Write(o_lbl),
            GrowArrow(z_arrow), Write(z_lbl),
            GrowArrow(c_arrow), Write(c_lbl),
        )
        self.wait(1)

        for op in ["ADD", "SUB", "AND", "SLT", "SRL"]:
            alu.animate_operation(self, op, run_time=0.5)
            self.wait(0.8)

        self.wait(1)

class TestMuxScene(Scene):
    def construct(self):
        mux = MuxComponent(input_offset=0.2).scale(1.4)
        self.play(Create(mux), run_time=0.7)
        self.wait(0.3)

        arrow_kw = dict(buff=0, stroke_width=2.5)
        lbl_kw   = dict(font_size=15)

        p0 = mux.get_input_0()
        a0 = Arrow(p0 + LEFT * 1.1, p0, color=GRAY, **arrow_kw)
        l0 = Text("Input 0", **lbl_kw).next_to(a0, LEFT, buff=0.1)

        p1 = mux.get_input_1()
        a1 = Arrow(p1 + LEFT * 1.1, p1, color=GRAY, **arrow_kw)
        l1 = Text("Input 1", **lbl_kw).next_to(a1, LEFT, buff=0.1)

        po = mux.get_output()
        ao = Arrow(po, po + RIGHT * 1.1, color=GRAY, **arrow_kw)
        lo = Text("Output", **lbl_kw).next_to(ao, RIGHT, buff=0.1)

        pc = mux.get_ctrl_port()
        ac = Arrow(pc + DOWN * 0.9, pc, color=BLUE, **arrow_kw)
        lc = Text("Select", font_size=15, color=BLUE).next_to(ac, DOWN, buff=0.05)

        self.play(
            GrowArrow(a0), Write(l0),
            GrowArrow(a1), Write(l1),
            GrowArrow(ao), Write(lo),
            GrowArrow(ac), Write(lc),
        )
        self.wait(2)

class TestRegFileScene(Scene):
    def construct(self):
        from RegFile import RegFileComponent
        rf = RegFileComponent(input_offset=0.2).scale(1.1)
        self.play(Create(rf), run_time=0.9)
        self.wait(0.3)

        arrow_kw = dict(buff=0, stroke_width=2.5)
        lbl_kw   = dict(font_size=14)

        inputs = [
            (rf.get_read_reg1(),  "Read register 1"),
            (rf.get_read_reg2(),  "Read register 2"),
            (rf.get_write_reg(),  "Write register"),
            (rf.get_write_data(), "Write data"),
        ]
        in_anims = []
        for port, name in inputs:
            arr = Arrow(port + LEFT * 1.4, port, color=GRAY, **arrow_kw)
            lbl = Text(name, **lbl_kw).next_to(arr, LEFT, buff=0.08)
            in_anims += [GrowArrow(arr), Write(lbl)]

        outputs = [
            (rf.get_read_data1(), "Read data 1"),
            (rf.get_read_data2(), "Read data 2"),
        ]
        out_anims = []
        for port, name in outputs:
            arr = Arrow(port, port + RIGHT * 1.4, color=GRAY, **arrow_kw)
            lbl = Text(name, **lbl_kw).next_to(arr, RIGHT, buff=0.08)
            out_anims += [GrowArrow(arr), Write(lbl)]

        rw_pt  = rf.get_reg_write()
        rw_arr = Arrow(rw_pt + UP * 0.9, rw_pt, color="#4A90D9", **arrow_kw)
        rw_lbl = Text("RegWrite", font_size=14, color="#4A90D9").next_to(
            rw_arr, UP, buff=0.08
        )

        self.play(*in_anims, *out_anims, GrowArrow(rw_arr), Write(rw_lbl))
        self.wait(2)

