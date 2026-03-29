import os
import sys

import numpy as np
from manim import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Adder import AdderComponent
from ALU import ALUComponent
from ALUControl import ALUControlComponent
from AndGate import AndGateComponent
from Control import ControlComponent
from DataMemory import DataMemoryComponent
from InstructionMemory import InstructionMemoryComponent
from MUX import MuxComponent
from PC import PCComponent
from RegFile import RegFileComponent
from ShiftLeft1 import ShiftLeft1Component
from SignExtend import SignExtendComponent
from utils import (
    CTRL_COLOR,
    INACTIVE_COLOR,
    SIGNAL_COLOR,
    animate_data_path,
    make_bus_split,
    make_connection,
    make_feedback_wire,
    make_junction,
    make_ortho_wire,
    make_routed_wire,
    make_straight_wire,
    make_v_h_v_wire,
)

# 16:9 wide frame for full single-cycle datapath
config.frame_width = 30
config.frame_height = 16.875


class DatapathBase(Scene):
    """
    Base Scene that builds the complete RISC-V single-cycle datapath.

    Subclasses call self.setup_datapath() in construct() to get:
      - Component refs: self.pc, self.im, self.rf, self.se, self.alu_mux,
                        self.alu, self.alu_control, self.dm, self.wb_mux,
                        self.control, self.pc4_add, self.branch_add,
                        self.shift_left, self.and_gate, self.pcsrc_mux
      - self.bus   — instruction bus dict from make_bus_split()
      - self.wires — dict of all named connections from make_connection()
    """

    def setup_datapath(self) -> None:
        # ── 1. Instantiate all components ────────────────────────────────────
        self.pc = PCComponent(width=1.0, height=2.0).move_to(LEFT * 13.0)

        self.im = InstructionMemoryComponent(
            width=2.6,
            height=3.8,
            show_port_labels=False,
        ).move_to(LEFT * 10.0)

        # Align PC output with IM read address
        self.pc.shift(
            UP * (self.im.get_read_address()[1] - self.pc.get_output()[1])
        )

        self.rf = RegFileComponent(width=3.0, height=4.2).move_to(LEFT * 4.5)

        self.se = SignExtendComponent(width=1.8, height=1.2).move_to(
            LEFT * 0.5 + DOWN * 4.0
        )

        self.alu_mux = MuxComponent().move_to(RIGHT * 3.5)

        self.alu = ALUComponent(label="ALU").scale(0.85).move_to(RIGHT * 6.0)
        self.alu.shift(
            UP * (self.rf.get_read_data1()[1] - self.alu.get_input_a()[1])
        )
        # Align alu_mux output with RF read data 2
        self.alu_mux.shift(
            UP * (self.rf.get_read_data2()[1] - self.alu_mux.get_output()[1])
        )

        self.alu_control = ALUControlComponent().move_to(RIGHT * 6.0 + DOWN * 4.0)
        self.alu_control.shift(
            RIGHT * (
                self.alu.get_ctrl_port()[0]
                - self.alu_control.get_alu_ctrl_output()[0]
            )
        )

        self.dm = DataMemoryComponent(width=2.6, height=3.8).move_to(RIGHT * 10.5)
        self.dm.shift(
            UP * (self.alu.get_output()[1] - self.dm.get_address()[1])
        )

        self.wb_mux = MuxComponent().move_to(RIGHT * 13.5)
        self.wb_mux.shift(
            UP * (self.dm.get_read_data()[1] - self.wb_mux.get_input_1()[1])
        )

        self.control = ControlComponent(width=2.2, height=3.0).move_to(
            LEFT * 1.5 + UP * 6.5
        )

        self.pc4_add = AdderComponent().move_to(LEFT * 10.0 + UP * 5.5)

        self.shift_left = ShiftLeft1Component().move_to(RIGHT * 4.5 + UP * 5.5)

        self.branch_add = AdderComponent().move_to(RIGHT * 7.5 + UP * 5.5)

        self.and_gate = AndGateComponent().move_to(RIGHT * 11.5 + UP * 5.5)

        self.pcsrc_mux = MuxComponent().move_to(RIGHT * 14.0 + UP * 5.5)

        # ── 2. Centre all components ──────────────────────────────────────────
        everything = VGroup(
            self.pc, self.im, self.rf, self.se,
            self.alu_mux, self.alu, self.alu_control,
            self.dm, self.wb_mux, self.control,
            self.pc4_add, self.branch_add, self.shift_left,
            self.and_gate, self.pcsrc_mux,
        )
        everything.move_to(ORIGIN)
        self.add(everything)

        # ── 3. Cache port positions ───────────────────────────────────────────
        pc_in,  pc_out = self.pc.get_input(),  self.pc.get_output()
        im_ra          = self.im.get_read_address()

        rr1, rr2, wr   = (
            self.rf.get_read_reg1(),
            self.rf.get_read_reg2(),
            self.rf.get_write_reg(),
        )
        rd1, rd2        = self.rf.get_read_data1(), self.rf.get_read_data2()
        rf_rw, rf_wd    = self.rf.get_reg_write(),  self.rf.get_write_data()

        se_in, se_out   = self.se.get_input(), self.se.get_output()

        am0, am1, amout, amsel = (
            self.alu_mux.get_input_0(),
            self.alu_mux.get_input_1(),
            self.alu_mux.get_output(),
            self.alu_mux.get_ctrl_port_top(),
        )

        alu_a, alu_b, alu_out = (
            self.alu.get_input_a(),
            self.alu.get_input_b(),
            self.alu.get_output(),
        )
        alu_zero, alu_ctrl = self.alu.get_zero_port(), self.alu.get_ctrl_port()

        ac_funct, ac_aluop, ac_out = (
            self.alu_control.get_funct_input(),
            self.alu_control.get_aluop_input(),
            self.alu_control.get_alu_ctrl_output(),
        )

        dm_addr, dm_wd, dm_rd = (
            self.dm.get_address(),
            self.dm.get_write_data(),
            self.dm.get_read_data(),
        )
        dm_mr, dm_mw = self.dm.get_mem_read(), self.dm.get_mem_write()

        wb_in0, wb_in1, wb_out, wb_sel = (
            self.wb_mux.get_input_0(),
            self.wb_mux.get_input_1(),
            self.wb_mux.get_output(),
            self.wb_mux.get_ctrl_port_top(),
        )

        ctrl_branch                    = self.control.get_branch()
        ctrl_memread, ctrl_memtoreg    = self.control.get_mem_read(), self.control.get_mem_to_reg()
        ctrl_aluop,   ctrl_memwrite    = self.control.get_alu_op(),   self.control.get_mem_write()
        ctrl_alusrc,  ctrl_regwrite    = self.control.get_alu_src(),  self.control.get_reg_write()
        ctrl_opcode                    = self.control.get_opcode_input()

        p4a_in, p4b_in, p4_out = (
            self.pc4_add.get_input_a(),
            self.pc4_add.get_input_b(),
            self.pc4_add.get_output(),
        )
        bra_ina, bra_inb, bra_out = (
            self.branch_add.get_input_a(),
            self.branch_add.get_input_b(),
            self.branch_add.get_output(),
        )

        sl_in,  sl_out  = self.shift_left.get_input(), self.shift_left.get_output()
        ag_ina, ag_inb, ag_out = (
            self.and_gate.get_input_a(),
            self.and_gate.get_input_b(),
            self.and_gate.get_output(),
        )

        ps_in0, ps_in1, ps_out, ps_ctrl = (
            self.pcsrc_mux.get_input_0(),
            self.pcsrc_mux.get_input_1(),
            self.pcsrc_mux.get_output(),
            self.pcsrc_mux.get_ctrl_port_bottom(),
        )

        # ── 4. Instruction bus ────────────────────────────────────────────────
        origin   = self.im.inst_bus_origin()
        trunk_x  = origin[0] + 0.6
        label_bx = self.rf.shape.get_left()[0] - 0.8

        self.bus = make_bus_split(
            origin=origin,
            trunk_x=trunk_x,
            branches=[
                {
                    "y":          ctrl_opcode[1],
                    "dest":       ctrl_opcode,
                    "label":      "Inst[6–0]",
                    "bend_x":     ctrl_opcode[0],
                    "label_side": DOWN,
                    "dot":        True,
                },
                {
                    "y":      rr1[1],
                    "dest":   rr1,
                    "label":  "Inst[19–15]",
                    "bend_x": label_bx,
                },
                {
                    "y":      rr2[1],
                    "dest":   rr2,
                    "label":  "Inst[24–20]",
                    "bend_x": label_bx,
                },
                {
                    "y":      wr[1],
                    "dest":   wr,
                    "label":  "Inst[11–7]",
                    "bend_x": label_bx,
                },
                {
                    "y":      se_in[1],
                    "dest":   se_in,
                    "label":  "Inst[31–0]",
                    "bend_x": label_bx,
                },
            ],
        )

        # ── 5. Corridor bands ─────────────────────────────────────────────────
        _top_roof = max(
            self.pc4_add.shape.get_top()[1],
            self.branch_add.shape.get_top()[1],
            self.control.shape.get_top()[1],
            self.pcsrc_mux.shape.get_top()[1],
            self.and_gate.shape.get_top()[1],
        )
        _sl1_bot      = self.shift_left.shape.get_bottom()[1]
        _bot_floor    = min(
            self.se.shape.get_bottom()[1],
            self.alu_control.shape.get_bottom()[1],
        )
        _frame_bot    = -(config.frame_height / 2) + 0.4

        TC = [_top_roof + 0.55 + i * 0.40 for i in range(6)]
        CC = [_sl1_bot  - 0.40 - i * 0.40 for i in range(7)]
        BC = [max(_bot_floor - 0.45 - i * 0.55, _frame_bot) for i in range(5)]

        # ── 6. Junction dots ──────────────────────────────────────────────────
        self.dot_pc     = make_junction(pc_out + RIGHT * 0.5)
        self.dot_pc_top = make_junction(
            np.array([self.dot_pc.get_center()[0], p4a_in[1], 0])
        )
        self.dot_p4     = make_junction(p4_out)
        self.dot_rd2    = make_junction(rd2)
        self.dot_se     = make_junction(se_out, color=SIGNAL_COLOR)
        self.dot_alu    = make_junction(
            np.array([self.dm.shape.get_left()[0] - 0.5, alu_out[1], 0])
        )

        # ── 7. Wires ──────────────────────────────────────────────────────────
        def ctrl_route(corridor_y):
            return lambda s, e, **kw: make_v_h_v_wire(s, e, bend_y=corridor_y, **kw)

        self.wires = {
            # PC / PC+4 / Branch Adder inputs
            "pc_to_dot": make_connection(pc_out, self.dot_pc.get_center(), arrow=False),
            "junc_im":   make_connection(self.dot_pc.get_center(), im_ra, label="PC"),
            "pc_p4a": make_connection(
                self.dot_pc.get_center(), p4a_in,
                wire_func=make_ortho_wire,
                bend_x=self.dot_pc.get_center()[0],
            ),
            "const4": make_connection(
                np.array([p4b_in[0] - 0.6, p4b_in[1], 0]),
                p4b_in,
                label="4",
                wire_func=make_straight_wire,
            ),
            "pc_bra": make_connection(
                self.dot_pc.get_center(), bra_ina,
                wire_func=make_feedback_wire,
                corridor_y=TC[0],
                turn_up_x=bra_ina[0] - 0.5,
            ),
            # PC adders → PCSrc Mux
            "p4_pcsrc": make_connection(
                p4_out, ps_in0,
                wire_func=make_feedback_wire,
                corridor_y=TC[1],
                turn_up_x=ps_in0[0] - 0.5,
            ),
            "bra_pcsrc": make_connection(
                bra_out, ps_in1,
                label="Sum",
                wire_func=make_ortho_wire,
                bend_x=bra_out[0] + 0.5,
            ),
            # Feedback: PCSrc Mux → PC
            "pcsrc_pc": make_connection(
                ps_out, pc_in,
                wire_func=make_feedback_wire,
                corridor_y=TC[2],
                turn_up_x=pc_in[0] - 0.6,
            ),
            # Sign-extend → Shift Left 1 → Branch Adder
            "se_sl": make_connection(
                self.dot_se.get_center(), sl_in,
                arrow=True,
                wire_func=make_ortho_wire,
                bend_x=se_out[0],
            ),
            "sl_bra": make_connection(
                sl_out, bra_inb,
                arrow=True,
                wire_func=make_ortho_wire,
                bend_x=sl_out[0],
            ),
            # Control signals
            "ctrl_branch": make_connection(
                ctrl_branch, ag_ina,
                ctrl=True,
                label="Branch",
                wire_func=make_ortho_wire,
                bend_x=ag_ina[0],
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_memread": make_connection(
                ctrl_memread, dm_mr,
                ctrl=True,
                label="MemRead",
                wire_func=ctrl_route(CC[1]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_memtoreg": make_connection(
                ctrl_memtoreg, wb_sel,
                ctrl=True,
                label="MemtoReg",
                wire_func=ctrl_route(CC[2]),
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_aluop": make_connection(
                ctrl_aluop, ac_aluop,
                ctrl=True,
                label="ALUOp",
                wire_func=ctrl_route(CC[3]),
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_memwrite": make_connection(
                ctrl_memwrite, dm_mw,
                ctrl=True,
                label="MemWrite",
                wire_func=ctrl_route(CC[4]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_alusrc": make_connection(
                ctrl_alusrc, amsel,
                ctrl=True,
                label="ALUSrc",
                wire_func=ctrl_route(CC[5]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_regwrite": make_connection(
                ctrl_regwrite, rf_rw,
                ctrl=True,
                label="RegWrite",
                wire_func=make_ortho_wire,
                bend_x=ctrl_regwrite[0],
                tip_dir=LEFT,
                label_side=UP,
            ),
            # Branch logic
            "zero_and": make_connection(
                alu_zero, ag_inb,
                ctrl=True,
                label="Zero",
                wire_func=make_ortho_wire,
                bend_x=self.branch_add.shape.get_right()[0] + 0.3,
                tip_dir=UP,
                label_side=DOWN,
            ),
            "pcsrc_sel": make_connection(
                ag_out, ps_ctrl,
                ctrl=True,
                label="PCSrc",
                wire_func=make_v_h_v_wire,
                bend_y=CC[0] - 0.25,
                tip_dir=UP,
            ),
            # Data path
            "rd1_alu":   make_connection(rd1, alu_a, label="Read data 1"),
            "rd2_am0":   make_connection(rd2, am0, label="Read data 2"),
            "se_am1":    make_connection(
                se_out, am1,
                label="Imm32",
                bend_x=am1[0] - 0.4,
            ),
            "amux_alu":  make_connection(amout, alu_b),
            "ac_alu":    make_connection(
                ac_out, alu_ctrl,
                ctrl=True,
                tip_dir=DOWN,
                wire_func=make_straight_wire,
            ),
            "alu_dm":    make_connection(alu_out, dm_addr, label="ALU result"),
            "rd2_dm":    make_connection(
                rd2, dm_wd,
                wire_func=make_feedback_wire,
                corridor_y=BC[1],
                turn_up_x=dm_wd[0] - 0.6,
                tip_dir=LEFT,
            ),
            "alu_wb":    make_connection(
                self.dot_alu.get_center(), wb_in0,
                wire_func=make_feedback_wire,
                corridor_y=self.dm.shape.get_bottom()[1] - 0.5,
                turn_up_x=wb_in0[0] - 0.5,
            ),
            "dm_wb":     make_connection(dm_rd, wb_in1, label="Read data"),
            "wb_rf":     make_connection(
                wb_out, rf_wd,
                wire_func=make_feedback_wire,
                corridor_y=BC[2],
                turn_up_x=rf_wd[0] - 0.6,
                tip_dir=LEFT,
            ),
            "funct_ac":  make_connection(
                np.array([se_in[0] - 0.3, se_in[1], 0]),
                ac_funct,
                label="Inst[30,14-12]",
                wire_func=make_v_h_v_wire,
                bend_y=BC[0],
                tip_dir=DOWN,
            ),
        }

        # ── 8. Add wires and dots to scene ────────────────────────────────────
        self.add(*self.bus["all"])
        for conn in self.wires.values():
            self.add(conn["all"])
        self.add(
            self.dot_pc, self.dot_pc_top, self.dot_p4,
            self.dot_rd2, self.dot_alu, self.dot_se,
        )

    # ── Shared animation helpers ──────────────────────────────────────────────

    def show_instruction_banner(self, text: str, subtitle: str = "") -> VGroup:
        """Show an instruction label at the top of the screen."""
        title = Text(text, font_size=20, color=YELLOW, weight=BOLD)
        title.to_edge(UP, buff=0.18)
        group = VGroup(title)
        if subtitle:
            sub = Text(subtitle, font_size=14, color=WHITE)
            sub.next_to(title, DOWN, buff=0.06)
            group.add(sub)
        self.play(FadeIn(group, shift=DOWN * 0.1), run_time=0.5)
        return group

    def show_ctrl_table(
        self,
        signals: dict,
        active_signals: set,
        position=None,
    ) -> VGroup:
        """
        Display a compact control-signal table.

        signals        — dict of {signal_name: value_str}
        active_signals — set of signal names that are '1' / active (highlighted)
        position       — Manim position; defaults to bottom-right corner
        """
        rows = VGroup()
        for name, val in signals.items():
            color = YELLOW if name in active_signals else "#888888"
            row = Text(f"{name} = {val}", font_size=11, color=color)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.05)

        box = SurroundingRectangle(
            rows, color=GRAY, buff=0.12, corner_radius=0.08
        )
        title = Text("Control", font_size=11, color=GRAY, weight=BOLD)
        title.next_to(box, UP, buff=0.04)

        group = VGroup(box, rows, title)
        if position is not None:
            group.move_to(position)
        else:
            group.to_corner(DR, buff=0.25)

        self.play(FadeIn(group), run_time=0.4)
        return group

    def dim_inactive_wires(self, active_keys: set) -> None:
        """Dim every wire whose key is NOT in active_keys."""
        anims = []
        for key, conn in self.wires.items():
            if key not in active_keys:
                anims.append(conn["wire"].animate.set_color(INACTIVE_COLOR))
        if anims:
            self.play(*anims, run_time=0.5)

    def stage_banner(self, label: str) -> None:
        """Flash a brief stage label (IF / ID / EX / MEM / WB)."""
        txt = Text(label, font_size=18, color=YELLOW)
        txt.to_edge(LEFT, buff=0.3).shift(DOWN * 3.5)
        self.play(FadeIn(txt, shift=RIGHT * 0.15), run_time=0.3)
        self.wait(0.2)
        self.play(FadeOut(txt), run_time=0.25)
