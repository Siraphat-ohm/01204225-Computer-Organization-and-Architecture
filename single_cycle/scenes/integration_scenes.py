import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from manim import *
import numpy as np
from ALU import ALUComponent
from MUX import MuxComponent
from utils import *

class IfALUMuxScene(Scene):
    """
    Visualises:
        if A + B > 5:
            do_something_true()
        else:
            do_something_false()

    Datapath:
        ALU 1  →  ADD  →  A+B
        ALU 2  →  SLT  →  flag  (1 when A+B > 5)
        MUX    →  select=flag  →  picks branch
    """

    def construct(self):
        alu1 = ALUComponent(label="ALU 1").scale(0.85)
        alu2 = ALUComponent(label="ALU 2").scale(0.85)
        mux  = MuxComponent().scale(0.90)

        alu1.move_to(LEFT  * 4.5)
        alu2.move_to(LEFT  * 0.8)
        mux .move_to(RIGHT * 4.0)

        self.play(Create(alu1), Create(alu2), Create(mux), run_time=1.0)
        self.wait(0.3)

        code_lines = VGroup(
            Text("if A + B > 5:",           font_size=14, color=YELLOW),
            Text("    do_something_true()",  font_size=14, color=GREEN),
            Text("else:",                   font_size=14, color=YELLOW),
            Text("    do_something_false()", font_size=14, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        code_box   = SurroundingRectangle(code_lines, color=GRAY,
                                          buff=0.15, corner_radius=0.1)
        code_group = VGroup(code_lines, code_box).to_corner(UL, buff=0.3)
        self.play(FadeIn(code_group))
        self.wait(0.3)

        draw_stub(self, alu1.get_input_a(), text="A", length=1.1)
        draw_stub(self, alu1.get_input_b(), text="B", length=1.1)
        alu1.animate_operation(self, "ADD", run_time=0.5)
        self.wait(0.2)

        w_sum = draw_wire(
            self,
            alu1.get_output(), alu2.get_input_a(),
            text="A+B", text_dir=UP,
        )

        draw_stub(self, alu2.get_input_b(), text="5", length=1.0)
        alu2.animate_operation(self, "SLT", run_time=0.5)
        self.wait(0.2)

        flag_start = alu2.get_output()
        ctrl_pt    = mux.get_ctrl_port()

        w_flag = VMobject(stroke_width=2.5, color="#4A90D9")
        w_flag.set_points_as_corners([
            flag_start,
            flag_start + RIGHT * 0.5,
            np.array([flag_start[0] + 0.5, ctrl_pt[1] - 0.5, 0]),
            np.array([ctrl_pt[0],           ctrl_pt[1] - 0.5, 0]),
            ctrl_pt,
        ])
        flag_lbl = label_below(w_flag, "flag  (A+B > 5 ?)",
                               font_size=12, color="#4A90D9")
        self.play(Create(w_flag), Write(flag_lbl), run_time=0.7)
        self.wait(0.3)

        p0 = mux.get_input_0()
        p1 = mux.get_input_1()

        false_arrow = Arrow(p0 + LEFT * 2.2, p0,
                            buff=0, stroke_width=2, color=GRAY)
        true_arrow  = Arrow(p1 + LEFT * 2.2, p1,
                            buff=0, stroke_width=2, color=GRAY)

        false_lbl = Text("do_something_false()", font_size=12, color=RED)
        true_lbl  = Text("do_something_true()",  font_size=12, color=GREEN)
        false_lbl.next_to(false_arrow, UP,   buff=0.10)
        true_lbl .next_to(true_arrow,  DOWN, buff=0.10)

        self.play(
            GrowArrow(false_arrow), Write(false_lbl),
            GrowArrow(true_arrow),  Write(true_lbl),
        )

        out_pt    = mux.get_output()
        out_arrow = Arrow(out_pt, out_pt + RIGHT * 1.1,
                          buff=0, stroke_width=2, color=GRAY)
        out_lbl   = label_right(out_arrow, "Execute", font_size=14)
        self.play(GrowArrow(out_arrow), Write(out_lbl))
        self.wait(0.5)

        self.play(FadeOut(code_group))

        case1 = Text("A=3, B=1  →  3+1=4  ≤ 5  →  flag=0",
                     font_size=15, color=YELLOW).to_corner(UL, buff=0.3)
        self.play(Write(case1))

        signal_flow(self, [
            {"wire": w_sum,  "component": alu1,
             "label": "ADD",  "value": "4",   "pause": 0.3},
            {"wire": w_sum,  "component": alu2,
             "label": "SLT",  "value": "flag=0", "pause": 0.3},
            {"wire": w_flag, "component": mux,
             "label": "SELECT=0", "ctrl": True,  "pause": 0.3},
        ])

        self.play(
            false_arrow.animate.set_color(GREEN),
            true_arrow .animate.set_color(GRAY),
            run_time=0.4,
        )
        taken1 = Text("→ do_something_false() taken",
                      font_size=14, color=RED).next_to(case1, DOWN, buff=0.12)
        self.play(Write(taken1))
        self.wait(1.2)

        self.play(FadeOut(taken1))
        case2 = Text("A=4, B=3  →  4+3=7  > 5  →  flag=1",
                     font_size=15, color=YELLOW)
        case2.to_corner(UL, buff=0.3)
        self.play(Transform(case1, case2))

        signal_flow(self, [
            {"wire": w_sum,  "component": alu1,
             "label": "ADD",  "value": "7",      "pause": 0.3},
            {"wire": w_sum,  "component": alu2,
             "label": "SLT",  "value": "flag=1", "pause": 0.3},
            {"wire": w_flag, "component": mux,
             "label": "SELECT=1", "ctrl": True,   "pause": 0.3},
        ])

        self.play(
            false_arrow.animate.set_color(GRAY),
            true_arrow .animate.set_color(GREEN),
            run_time=0.4,
        )
        taken2 = Text("→ do_something_true() taken",
                      font_size=14, color=GREEN).next_to(case1, DOWN, buff=0.12)
        self.play(Write(taken2))
        self.wait(2)
