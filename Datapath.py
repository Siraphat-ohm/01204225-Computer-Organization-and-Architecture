import os
import sys

import numpy as np
from manim import *

sys.path.insert(0, os.path.dirname(__file__))

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
    SIGNAL_COLOR,
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


class SingleDatapath(Scene):
    def construct(self):

        # 1. Instantiate all components (Textbook Layout)
        pc = PCComponent(width=1.0, height=2.0).move_to(LEFT * 13.0)

        im = InstructionMemoryComponent(
            width=2.6,
            height=3.8,
            show_port_labels=False,
        ).move_to(LEFT * 10.0)

        # Align PC output with IM Read address
        pc.shift(UP * (im.get_read_address()[1] - pc.get_output()[1]))

        rf = RegFileComponent(width=3.0, height=4.2).move_to(LEFT * 4.5)

        se = SignExtendComponent(width=1.8, height=1.2).move_to(LEFT * 0.5 + DOWN * 4.0)

        # ALU MUX: output aligns with ALU input B
        alu_mux = MuxComponent().move_to(RIGHT * 3.5)

        # ALU aligned so input_a is at same y as RF Read data 1
        alu = ALUComponent(label="ALU").scale(0.85).move_to(RIGHT * 6.0)
        alu.shift(UP * (rf.get_read_data1()[1] - alu.get_input_a()[1]))
        # align alu_mux to read data 2 directly
        alu_mux.shift(UP * (rf.get_read_data2()[1] - alu_mux.get_output()[1]))

        # ALU Control: positioned below the ALU, shifted to align top-right output with ALU bottom input
        alu_control = ALUControlComponent().move_to(RIGHT * 6.0 + DOWN * 4.0)
        alu_control.shift(
            RIGHT * (alu.get_ctrl_port()[0] - alu_control.get_alu_ctrl_output()[0])
        )

        dm = DataMemoryComponent(width=2.6, height=3.8).move_to(RIGHT * 10.5)
        dm.shift(UP * (alu.get_output()[1] - dm.get_address()[1]))

        # WB MUX: input_1 aligned with DM read data
        wb_mux = MuxComponent().move_to(RIGHT * 13.5)
        wb_mux.shift(UP * (dm.get_read_data()[1] - wb_mux.get_input_1()[1]))

        # Control unit: above pipeline (raised to clear upper row)
        control = ControlComponent(width=2.2, height=3.0).move_to(LEFT * 1.5 + UP * 6.5)

        # PC+4 adder: above PC/IM area
        pc4_add = AdderComponent().move_to(LEFT * 10.0 + UP * 5.5)

        # Shift Left 1: upper pipeline row, feeding into Branch Adder
        shift_left = ShiftLeft1Component().move_to(RIGHT * 4.5 + UP * 5.5)

        # Branch target adder ("Add Sum"): upper right area
        branch_add = AdderComponent().move_to(RIGHT * 7.5 + UP * 5.5)

        # AND gate: upper row, aligned with branch adder
        and_gate = AndGateComponent().move_to(RIGHT * 11.5 + UP * 5.5)

        # PCSrc Mux: upper row, right side
        pcsrc_mux = MuxComponent().move_to(RIGHT * 14.0 + UP * 5.5)

        # 2. Move everything to center
        everything = VGroup(
            pc,
            im,
            rf,
            se,
            alu_mux,
            alu,
            alu_control,
            dm,
            wb_mux,
            control,
            pc4_add,
            branch_add,
            shift_left,
            and_gate,
            pcsrc_mux,
        )
        everything.move_to(ORIGIN)

        self.add(everything)

        # 3. Read all port positions
        pc_in, pc_out = pc.get_input(), pc.get_output()
        im_ra = im.get_read_address()

        rr1, rr2, wr = rf.get_read_reg1(), rf.get_read_reg2(), rf.get_write_reg()
        rd1, rd2 = rf.get_read_data1(), rf.get_read_data2()
        rf_rw, rf_wd = rf.get_reg_write(), rf.get_write_data()

        se_in, se_out = se.get_input(), se.get_output()

        am0, am1, amout, amsel = (
            alu_mux.get_input_0(),
            alu_mux.get_input_1(),
            alu_mux.get_output(),
            alu_mux.get_ctrl_port_top(),
        )

        alu_a, alu_b, alu_out = alu.get_input_a(), alu.get_input_b(), alu.get_output()
        alu_zero, alu_ctrl = alu.get_zero_port(), alu.get_ctrl_port()

        ac_funct, ac_aluop, ac_out = (
            alu_control.get_funct_input(),
            alu_control.get_aluop_input(),
            alu_control.get_alu_ctrl_output(),
        )

        dm_addr, dm_wd, dm_rd = (
            dm.get_address(),
            dm.get_write_data(),
            dm.get_read_data(),
        )
        dm_mr, dm_mw = dm.get_mem_read(), dm.get_mem_write()

        wb_in0, wb_in1, wb_out, wb_sel = (
            wb_mux.get_input_0(),
            wb_mux.get_input_1(),
            wb_mux.get_output(),
            wb_mux.get_ctrl_port_top(),
        )

        ctrl_branch = control.get_branch()
        ctrl_memread, ctrl_memtoreg = control.get_mem_read(), control.get_mem_to_reg()
        ctrl_aluop, ctrl_memwrite = control.get_alu_op(), control.get_mem_write()
        ctrl_alusrc, ctrl_regwrite = control.get_alu_src(), control.get_reg_write()
        ctrl_opcode = control.get_opcode_input()

        p4a_in, p4b_in, p4_out = (
            pc4_add.get_input_a(),
            pc4_add.get_input_b(),
            pc4_add.get_output(),
        )
        bra_ina, bra_inb, bra_out = (
            branch_add.get_input_a(),
            branch_add.get_input_b(),
            branch_add.get_output(),
        )

        sl_in, sl_out = shift_left.get_input(), shift_left.get_output()
        ag_ina, ag_inb, ag_out = (
            and_gate.get_input_a(),
            and_gate.get_input_b(),
            and_gate.get_output(),
        )

        ps_in0, ps_in1, ps_out, ps_ctrl = (
            pcsrc_mux.get_input_0(),
            pcsrc_mux.get_input_1(),
            pcsrc_mux.get_output(),
            pcsrc_mux.get_ctrl_port_bottom(),
        )

        # 4. Instruction bus
        origin = im.inst_bus_origin()
        trunk_x = origin[0] + 0.6
        label_bx = rf.shape.get_left()[0] - 0.8

        # Opcode tap at the lowest IM field; bend_x = ctrl_opcode[0] gives
        # right → up L-shape entering the control unit from below (right-side approach)
        opcode_tap_y = im.get_inst_6_0()[1]

        bus = make_bus_split(
            origin=origin,
            trunk_x=trunk_x,
            branches=[
                {
                    "y": ctrl_opcode[1],
                    "dest": ctrl_opcode,
                    "label": "Inst[6–0]",
                    "bend_x": ctrl_opcode[0],
                    "label_side": DOWN,
                    "dot": True,
                },
                {
                    "y": rr1[1],
                    "dest": rr1,
                    "label": "Inst[19–15]",
                    "bend_x": label_bx,
                },
                {
                    "y": rr2[1],
                    "dest": rr2,
                    "label": "Inst[24–20]",
                    "bend_x": label_bx,
                },
                {
                    "y": wr[1],
                    "dest": wr,
                    "label": "Inst[11–7]",
                    "bend_x": label_bx,
                },
                {
                    "y": se_in[1],
                    "dest": se_in,
                    "label": "Inst[31–0]",
                    "bend_x": label_bx,
                },
            ],
        )

        # 5. Dynamic corridor bands
        _top_roof = max(
            pc4_add.shape.get_top()[1],
            branch_add.shape.get_top()[1],
            control.shape.get_top()[1],
            pcsrc_mux.shape.get_top()[1],
            and_gate.shape.get_top()[1],
        )
        _sl1_bot = shift_left.shape.get_bottom()[1]
        _bot_floor = min(se.shape.get_bottom()[1], alu_control.shape.get_bottom()[1])
        _frame_bot = -(config.frame_height / 2) + 0.4
        _sl1_branch_gap = (
            shift_left.shape.get_top()[1] + branch_add.shape.get_bottom()[1]
        ) / 2

        TC = [_top_roof + 0.55 + i * 0.40 for i in range(6)]
        CC = [_sl1_bot - 0.40 - i * 0.40 for i in range(7)]
        BC = [max(_bot_floor - 0.45 - i * 0.55, _frame_bot) for i in range(5)]
        
        # 6. Junction dots
        dot_pc = make_junction(pc_out + RIGHT * 0.5)
        # Where PC vertical wire splits left (PC+4) and right (Branch)
        dot_pc_top = make_junction(np.array([dot_pc.get_center()[0], p4a_in[1], 0]))
        dot_p4 = make_junction(p4_out)
        dot_rd2 = make_junction(rd2)
        dot_se = make_junction(se_out, color=SIGNAL_COLOR)
        dot_alu = make_junction(np.array([dm.shape.get_left()[0] - 0.5, alu_out[1], 0]))

        def ctrl_route(corridor_y):
            """V → H → V: drop straight down to corridor, run right, drop into port."""
            return lambda s, e, **kwargs: make_v_h_v_wire(
                s, e, bend_y=corridor_y, **kwargs
            )

        # 7. All wires
        wires = {
            # PC / PC+4 / Branch Adder inputs
            "pc_to_dot": make_connection(pc_out, dot_pc.get_center(), arrow=False),
            "junc_im": make_connection(dot_pc.get_center(), im_ra, label="PC"),
            "pc_p4a": make_connection(
                dot_pc.get_center(),
                p4a_in,
                wire_func=make_ortho_wire,
                bend_x=dot_pc.get_center()[0],
            ),
            "const4": make_connection(
                np.array([p4b_in[0] - 0.6, p4b_in[1], 0]),
                p4b_in,
                label="4",
                wire_func=make_straight_wire,
            ),
            "pc_bra": make_connection(
                dot_pc.get_center(),
                bra_ina,
                wire_func=make_feedback_wire,
                corridor_y=TC[0],
                turn_up_x=bra_ina[0] - 0.5,
            ),
            # PC Adders to PCSrc Mux — routed above Control via TC corridor
            "p4_pcsrc": make_connection(
                p4_out,
                ps_in0,
                wire_func=make_feedback_wire,
                corridor_y=TC[1],
                turn_up_x=ps_in0[0] - 0.5,
            ),
            "bra_pcsrc": make_connection(
                bra_out,
                ps_in1,
                label="Sum",
                wire_func=make_ortho_wire,
                bend_x=bra_out[0] + 0.5,
            ),
            # Feedback Loop: PCSrc Mux to PC — outermost TC corridor
            "pcsrc_pc": make_connection(
                ps_out,
                pc_in,
                wire_func=make_feedback_wire,
                corridor_y=TC[2],
                turn_up_x=pc_in[0] - 0.6,
            ),
            # Sign-extend to Shift Left 1 — route vertically then right
            "se_sl": make_connection(
                dot_se.get_center(),
                sl_in,
                arrow=True,
                wire_func=make_ortho_wire,
                bend_x=se_out[0],
            ),
            "sl_bra": make_connection(
                sl_out, bra_inb, arrow=True, wire_func=make_ortho_wire, bend_x=sl_out[0]
            ),
            # Control signals
            "ctrl_branch": make_connection(
                ctrl_branch,
                ag_ina,
                ctrl=True,
                label="Branch",
                wire_func=make_ortho_wire,
                bend_x=ag_ina[0],  
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_memread": make_connection(
                ctrl_memread,
                dm_mr,
                ctrl=True,
                label="MemRead",
                wire_func=ctrl_route(CC[1]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_memtoreg": make_connection(
                ctrl_memtoreg,
                wb_sel,
                ctrl=True,
                label="MemtoReg",
                wire_func=ctrl_route(CC[2]),
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_aluop": make_connection(
                ctrl_aluop,
                ac_aluop,
                ctrl=True,
                label="ALUOp",
                wire_func=ctrl_route(CC[3]),
                tip_dir=UP,
                label_side=UP,
            ),
            "ctrl_memwrite": make_connection(
                ctrl_memwrite,
                dm_mw,
                ctrl=True,
                label="MemWrite",
                wire_func=ctrl_route(CC[4]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_alusrc": make_connection(
                ctrl_alusrc,
                amsel,
                ctrl=True,
                label="ALUSrc",
                wire_func=ctrl_route(CC[5]),
                tip_dir=UP,
                label_side=DOWN,
            ),
            "ctrl_regwrite": make_connection(
                ctrl_regwrite,
                rf_rw,
                ctrl=True,
                label="RegWrite",
                wire_func=make_ortho_wire,
                bend_x=ctrl_regwrite[0],
                tip_dir=LEFT,
                label_side=UP,
            ),
            # Branch Logic
            "zero_and": make_connection(
                alu_zero,
                ag_inb,
                ctrl=True,
                label="Zero",
                wire_func=make_ortho_wire,
                bend_x=branch_add.shape.get_right()[0] + 0.3,
                tip_dir=UP,
                label_side=DOWN,
            ),
            # AND gate → PCSrc MUX control: H right, then V up to bottom of MUX
            "pcsrc_sel": make_connection(
                ag_out,
                ps_ctrl,
                ctrl=True,
                label="PCSrc",
                wire_func=make_v_h_v_wire,
                bend_y=CC[0] - 0.25,
                tip_dir=UP,
            ),
            # Data Path
            "rd1_alu": make_connection(rd1, alu_a, label="Read data 1"),
            "rd2_am0": make_connection(rd2, am0, label="Read data 2"),
            "se_am1": make_connection(se_out, am1, label="Imm32", bend_x=am1[0] - 0.4),
            "amux_alu": make_connection(amout, alu_b),
            "ac_alu": make_connection(
                ac_out, alu_ctrl, ctrl=True, tip_dir=DOWN, wire_func=make_straight_wire
            ),
            "alu_dm": make_connection(alu_out, dm_addr, label="ALU result"),
            "rd2_dm": make_connection(
                rd2,
                dm_wd,
                wire_func=make_feedback_wire,
                corridor_y=BC[1],
                turn_up_x=dm_wd[0] - 0.6,
                tip_dir=LEFT,
            ),
            "alu_wb": make_connection(
                dot_alu.get_center(),
                wb_in0,
                wire_func=make_feedback_wire,
                corridor_y=dm.shape.get_bottom()[1] - 0.5,
                turn_up_x=wb_in0[0] - 0.5,
            ),
            "dm_wb": make_connection(dm_rd, wb_in1, label="Read data"),
            "wb_rf": make_connection(
                wb_out,
                rf_wd,
                wire_func=make_feedback_wire,
                corridor_y=BC[2],
                turn_up_x=rf_wd[0] - 0.6,
                tip_dir=LEFT,
            ),
            "funct_ac": make_connection(
                np.array([se_in[0] - 0.3, se_in[1], 0]),
                ac_funct,
                label="Inst[30,14-12]",
                wire_func=make_v_h_v_wire,
                bend_y=BC[0],
                tip_dir=DOWN,
            ),
        }
        
        # 8. Draw everything
        self.add(*bus["all"])
        for conn in wires.values():
            self.add(conn["all"])
        self.add(dot_pc, dot_pc_top, dot_p4, dot_rd2, dot_alu, dot_se)
        self.wait(1)
