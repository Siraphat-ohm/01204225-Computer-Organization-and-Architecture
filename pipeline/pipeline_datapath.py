import os
import sys

import numpy as np
from manim import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "single_cycle")))

from ALU import ALUComponent
from DataMemory import DataMemoryComponent
from InstructionMemory import InstructionMemoryComponent
from MUX import MuxComponent
from PC import PCComponent
from RegFile import RegFileComponent
from utils import CTRL_COLOR, SIGNAL_COLOR

config.frame_width  = 28.0
config.frame_height = 15.75

STAGE_NAMES   = ["IF",   "ID",     "EX",    "MEM",   "WB"]
STAGE_COLORS  = [BLUE_C, PURPLE_C, GREEN_C, ORANGE,  TEAL_C]
STAGE_X       = [-10.4,  -5.2,     0.0,     5.2,     10.4]
STAGE_W       = 5.2
STAGE_H       = 8.0
PIPE_REG_X    = [-7.8, -2.6, 2.6, 7.8]
PIPE_REG_LBLS = ["IF/ID", "ID/EX", "EX/MEM", "MEM/WB"]
CENTER_Y      = 0.8


def _lshape(p1, p2, color=SIGNAL_COLOR, sw=2.0):
    """L-shaped wire: horizontal from p1, then vertical to p2's y, then horizontal to p2."""
    mid_x = (p1[0] + p2[0]) / 2
    pts = [
        np.array(p1),
        np.array([mid_x, p1[1], 0]),
        np.array([mid_x, p2[1], 0]),
        np.array(p2),
    ]
    m = VMobject(color=color, stroke_width=sw)
    m.set_points_as_corners(pts)
    tip = Triangle(color=color, fill_color=color, fill_opacity=1).scale(0.08)
    tip.rotate(-PI / 2).move_to(np.array(p2) + LEFT * 0.04)
    return VGroup(m, tip)


def _harrow(p1, p2, label=None, color=SIGNAL_COLOR, sw=2.0):
    """Simple horizontal Arrow with optional label above."""
    arr = Arrow(
        np.array(p1), np.array(p2),
        color=color, stroke_width=sw,
        tip_length=0.14, buff=0.04,
        max_tip_length_to_length_ratio=0.35,
    )
    g = VGroup(arr)
    if label:
        t = Text(label, font_size=16, color=color)
        t.next_to(arr.get_center(), UP, buff=0.10)
        g.add(t)
    return g


class PipelinedDatapathScene(Scene):
    """Simple 5-stage pipelined RISC-V datapath."""

    def construct(self):
        title = Text(
            "RISC-V Pipelined Datapath",
            font_size=42, color=WHITE, weight=BOLD,
        ).to_edge(UP, buff=0.22)
        subtitle = Text(
            "vs. Single-Cycle: components reused across overlapping instructions",
            font_size=24, color=GRAY_A,
        ).next_to(title, DOWN, buff=0.12)
        self.play(Write(title), FadeIn(subtitle), run_time=0.5)

        self._draw_stages()
        self._draw_pipeline_regs()
        self._place_components()
        self._draw_wires()
        self._explain_pipeline_regs()
        self._animate_instruction()
        self._show_throughput_note()
        self.wait(2)

    def _draw_stages(self):
        self.stage_bg = []
        lbls = VGroup()
        for x, name, col in zip(STAGE_X, STAGE_NAMES, STAGE_COLORS):
            bg = Rectangle(
                width=STAGE_W, height=STAGE_H,
                fill_color=col, fill_opacity=0.06,
                stroke_color=col, stroke_width=0.8, stroke_opacity=0.5,
            ).move_to([x, CENTER_Y, 0])
            lbl = Text(name, font_size=36, color=col, weight=BOLD).move_to(
                [x, CENTER_Y + STAGE_H / 2 - 0.55, 0]
            )
            self.stage_bg.append(bg)
            lbls.add(lbl)
        self.stage_lbls = lbls
        self.add(*self.stage_bg)
        self.play(FadeIn(lbls), run_time=0.4)

    def _draw_pipeline_regs(self):
        self.pipe_reg_groups = []
        bar_h = STAGE_H * 0.72
        for x, name in zip(PIPE_REG_X, PIPE_REG_LBLS):
            bar = Rectangle(
                width=0.38, height=bar_h,
                fill_color=GRAY_B, fill_opacity=0.28,
                stroke_color=GRAY_B, stroke_width=1.5,
            ).move_to([x, CENTER_Y, 0])
            lbl = Text(name, font_size=18, color=GRAY_B).next_to(bar, UP, buff=0.12)
            g = VGroup(bar, lbl)
            self.pipe_reg_groups.append(g)
        self.play(*[FadeIn(g) for g in self.pipe_reg_groups], run_time=0.4)

    def _place_components(self):
        self.im = InstructionMemoryComponent(
            width=1.8, height=2.8, show_port_labels=False,
        ).move_to([STAGE_X[0] + 0.35, CENTER_Y, 0])
        self.pc = PCComponent(width=0.72, height=1.3).move_to(
            [STAGE_X[0] - 1.5, self.im.get_read_address()[1], 0]
        )

        self.rf = RegFileComponent(width=2.4, height=3.4).move_to(
            [STAGE_X[1], CENTER_Y, 0]
        )

        self.alu = ALUComponent(label="ALU").scale(0.72).move_to(
            [STAGE_X[2] + 0.7, CENTER_Y, 0]
        )
        self.alu_mux = MuxComponent().scale(0.78).move_to(
            [STAGE_X[2] - 0.9, CENTER_Y, 0]
        )
        self.alu_mux.shift(
            UP * (self.alu.get_input_b()[1] - self.alu_mux.get_output()[1])
        )

        self.dm = DataMemoryComponent(width=2.0, height=2.8).move_to(
            [STAGE_X[3], CENTER_Y, 0]
        )

        self.wb_mux = MuxComponent(label="WB").scale(0.78).move_to(
            [STAGE_X[4], CENTER_Y, 0]
        )
        self.wb_mux.shift(
            UP * (self.dm.get_read_data()[1] - self.wb_mux.get_input_1()[1])
        )

        comps = VGroup(
            self.pc, self.im, self.rf,
            self.alu_mux, self.alu,
            self.dm, self.wb_mux,
        )
        self.play(FadeIn(comps), run_time=0.7)

    def _draw_wires(self):
        S = SIGNAL_COLOR
        wires = VGroup()

        wires.add(_harrow(self.pc.get_output(), self.im.get_read_address()))

        wires.add(_harrow(
            [self.im.shape.get_right()[0], self.rf.shape.get_center()[1], 0],
            [self.rf.shape.get_left()[0],  self.rf.shape.get_center()[1], 0],
            label="Instruction",
        ))

        rd1 = self.rf.get_read_data1()
        ala = self.alu.get_input_a()
        wires.add(_lshape(rd1, ala, color=S))
        lbl_rs1 = Text("rs1", font_size=16, color=S).move_to(
            [(rd1[0] + ala[0]) / 2, max(rd1[1], ala[1]) + 0.28, 0]
        )
        wires.add(lbl_rs1)

        rd2  = self.rf.get_read_data2()
        am0  = self.alu_mux.get_input_0()
        wires.add(_lshape(rd2, am0, color=S))
        lbl_rs2 = Text("rs2", font_size=16, color=S).move_to(
            [(rd2[0] + am0[0]) / 2, min(rd2[1], am0[1]) - 0.28, 0]
        )
        wires.add(lbl_rs2)

        wires.add(_harrow(self.alu_mux.get_output(), self.alu.get_input_b()))

        wires.add(_harrow(
            self.alu.get_output(), self.dm.get_address(), label="ALU result",
        ))

        # rs2 bypass routed below components to DM write data
        dm_wd  = self.dm.get_write_data()
        bot_y  = min(self.alu_mux.shape.get_bottom()[1], self.dm.shape.get_bottom()[1]) - 0.7
        bypass = VMobject(color=S, stroke_width=1.6)
        bypass.set_points_as_corners([
            np.array(rd2),
            np.array([rd2[0],    bot_y, 0]),
            np.array([dm_wd[0],  bot_y, 0]),
            np.array(dm_wd),
        ])
        wires.add(bypass)
        wires.add(
            Text("rs2 (store)", font_size=15, color=S).move_to(
                [(rd2[0] + dm_wd[0]) / 2, bot_y - 0.25, 0]
            )
        )

        wires.add(_harrow(
            self.dm.get_read_data(), self.wb_mux.get_input_1(), label="read data",
        ))

        # ALU result bypass routed below MEM to WB MUX input 0
        alu_pt = np.array([self.alu.get_output()[0] + 0.15, self.alu.get_output()[1], 0])
        wb0    = self.wb_mux.get_input_0()
        lo_y   = min(self.dm.shape.get_bottom()[1], bot_y) - 0.4
        alu_bypass = VMobject(color=YELLOW_B, stroke_width=1.6)
        alu_bypass.set_points_as_corners([
            alu_pt,
            np.array([alu_pt[0], lo_y, 0]),
            np.array([wb0[0],    lo_y, 0]),
            np.array(wb0),
        ])
        wires.add(alu_bypass)
        wires.add(
            Text("ALU result", font_size=15, color=YELLOW_B).move_to(
                [(alu_pt[0] + wb0[0]) / 2, lo_y - 0.25, 0]
            )
        )

        # WB → RF writeback routed above all stages (dashed)
        wb_out = self.wb_mux.get_output()
        rf_wd  = self.rf.get_write_data()
        top_y  = max(
            self.im.shape.get_top()[1],
            self.rf.shape.get_top()[1],
        ) + 0.8
        fb_path = VMobject(color=TEAL_C, stroke_width=1.6)
        fb_path.set_points_as_corners([
            np.array(wb_out),
            np.array([wb_out[0], top_y, 0]),
            np.array([rf_wd[0],  top_y, 0]),
            np.array(rf_wd),
        ])
        fb_dashed = DashedVMobject(fb_path, num_dashes=22, dashed_ratio=0.6)
        wires.add(fb_dashed)
        wires.add(
            Text("WB → RF", font_size=16, color=TEAL_C).move_to(
                [(wb_out[0] + rf_wd[0]) / 2, top_y + 0.28, 0]
            )
        )

        self.play(Create(wires), run_time=1.2)
        self.wires_group = wires

    def _explain_pipeline_regs(self):
        stage_bottom_y = CENTER_Y - STAGE_H / 2

        header = Text(
            "Key difference from single-cycle:",
            font_size=28, color=YELLOW, weight=BOLD,
        )
        body = Text(
            "Pipeline registers (gray bars) latch each stage's outputs at the\n"
            "clock edge — allowing a new instruction to enter IF while the\n"
            "previous one is already in ID, EX, MEM, or WB simultaneously.",
            font_size=22, color=GRAY_A,
            line_spacing=1.4,
        )

        explanation = VGroup(header, body).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        explanation.next_to([0, stage_bottom_y, 0], DOWN, buff=0.40)

        bar_pos = self.pipe_reg_groups[0][0].get_center()
        ptr = Arrow(
            header.get_top() + LEFT * 0.5,
            bar_pos + DOWN * 0.5,
            color=YELLOW, stroke_width=1.5, tip_length=0.12, buff=0.05,
        )

        self.play(FadeIn(explanation), GrowArrow(ptr), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(explanation), FadeOut(ptr), run_time=0.4)

    def _show_throughput_note(self):
        lines = [
            ("Single-cycle:", "1 instr / N-unit clock period  →  low throughput",  RED_B),
            ("Pipelined:",    "1 instr / 1-stage clock period  →  ~5× throughput", GREEN_B),
            ("Trade-off:",    "each instruction still takes 5 cycles (latency unchanged)", GRAY_A),
        ]

        grp = VGroup()
        for lbl, val, col in lines:
            row = VGroup(
                Text(lbl, font_size=22, color=col, weight=BOLD),
                Text(val, font_size=22, color=col)
            ).arrange(RIGHT, buff=0.4)
            grp.add(row)

        grp.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        grp.to_edge(DOWN, buff=0.35)

        self.play(FadeIn(grp), run_time=0.5)
        self.wait(2.2)
        self.play(FadeOut(grp), run_time=0.4)

    def _animate_instruction(self):
        """Highlight each pipeline stage in turn for an ADD instruction."""
        self.wait(0.3)

        inst_txt = Text(
            "Tracing:  add x1, x2, x3",
            font_size=26, color=YELLOW,
        ).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(inst_txt), run_time=0.4)

        STAGE_DETAILS = {
            "IF":  "Fetch instruction from IM.  In single-cycle this stage\n"
                   "occupies the whole clock period; here the clock is\n"
                   "tuned to the *slowest single stage* instead.",
            "ID":  "Decode & read registers.  The IF/ID register\n"
                   "holds the fetched instruction while a new one\n"
                   "already enters IF — impossible in single-cycle.",
            "EX":  "Execute in ALU.  The ID/EX register preserves\n"
                   "rs1, rs2 and control bits; three instructions\n"
                   "are now in flight simultaneously.",
            "MEM": "Access data memory.  EX/MEM holds ALU result\n"
                   "and store data.  Single-cycle uses the same DM\n"
                   "sequentially; the pipeline reuses it every cycle.",
            "WB":  "Write back to register file.  MEM/WB latches\n"
                   "the result.  A hazard unit (not shown) handles\n"
                   "data/control hazards absent in single-cycle.",
        }

        prev_hl   = None
        prev_note = None
        prev_detail = None

        for bg, name, col in zip(self.stage_bg, STAGE_NAMES, STAGE_COLORS):
            hl = bg.copy().set(fill_opacity=0.32, stroke_width=3.0, stroke_opacity=1.0)
            note = Text(f"● {name} stage", font_size=28, color=col, weight=BOLD)
            note.next_to(inst_txt, UP, buff=0.18)

            detail = Text(
                STAGE_DETAILS[name], font_size=20, color=LIGHT_GRAY,
                line_spacing=1.4,
            ).next_to(note, UP, buff=0.16).align_to(note, LEFT)

            anims = [FadeIn(hl), Write(note), FadeIn(detail)]
            if prev_hl:
                anims += [FadeOut(prev_hl), FadeOut(prev_note), FadeOut(prev_detail)]
            self.play(*anims, run_time=0.45)
            self.wait(0.90)

            prev_hl, prev_note, prev_detail = hl, note, detail

        self.play(
            FadeOut(prev_hl), FadeOut(prev_note),
            FadeOut(prev_detail), FadeOut(inst_txt),
            run_time=0.4,
        )