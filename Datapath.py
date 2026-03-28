from manim import *
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from InstructionMemory import InstructionMemoryComponent
from MUX               import MuxComponent
from RegFile           import RegFileComponent
from SignExtend        import SignExtendComponent
from ALU               import ALUComponent
from ALUControl        import ALUControlComponent
from utils             import (
    make_bus_split, animate_bus,
    make_ortho_wire, make_straight_wire, make_junction,
    make_connection, draw_connections, animate_data_path, make_v_h_v_wire,
    SIGNAL_COLOR, CTRL_COLOR,
)

# Wider frame for full single-cycle datapath
config.frame_width  = 20
config.frame_height = 11


class DatapathTest(Scene):
    def construct(self):

        im  = InstructionMemoryComponent(
                  width=2.6, height=3.8,
                  show_port_labels=False,
              ).move_to(LEFT * 4.8)

        mux = MuxComponent(
              ).move_to(LEFT * 0.9 + DOWN * 0.63)

        rf  = RegFileComponent(width=3.0, height=4.2
              ).move_to(RIGHT * 2.8)

        se  = SignExtendComponent(width=1.8, height=1.2
              ).move_to(LEFT * 0.5 + DOWN * 3.5)

        # ALU placed so input_a aligns horizontally with Read data 1
        alu = ALUComponent(label="ALU").scale(0.85).move_to(RIGHT * 8.0)
        alu.shift(UP * (rf.get_read_data1()[1] - alu.get_input_a()[1]))

        # ALU MUX placed so output aligns horizontally with ALU input B
        alu_mux = MuxComponent().move_to(RIGHT * 5.8)
        alu_mux.shift(UP * (alu.get_input_b()[1] - alu_mux.get_output()[1]))

        alu_control = ALUControlComponent(
              ).move_to(RIGHT * 7.0 + DOWN * 3.5)

        self.play(FadeIn(im), FadeIn(mux), FadeIn(rf), FadeIn(se),
                  FadeIn(alu_mux), FadeIn(alu), FadeIn(alu_control),
                  run_time=0.9)
        self.wait(0.3)

        rr1  = rf.get_read_reg1()
        rr2  = rf.get_read_reg2()
        wr   = rf.get_write_reg()

        m0   = mux.get_input_0()
        m1   = mux.get_input_1()
        mout = mux.get_output()
        msel = mux.get_ctrl_port()

        se_in  = se.get_input()
        se_out = se.get_output()

        rd2    = rf.get_read_data2()
        am0    = alu_mux.get_input_0()
        am1    = alu_mux.get_input_1()
        amout  = alu_mux.get_output()
        amsel  = alu_mux.get_ctrl_port()

        rd1    = rf.get_read_data1()
        alu_a  = alu.get_input_a()
        alu_b  = alu.get_input_b()
        alu_out = alu.get_output()
        alu_zero = alu.get_zero_port()
        alu_ctrl = alu.get_ctrl_port()

        ac_funct = alu_control.get_funct_input()
        ac_aluop = alu_control.get_aluop_input()
        ac_out   = alu_control.get_alu_ctrl_output()

        origin  = im.inst_bus_origin()
        trunk_x = origin[0] + 0.5

        # ── 3. main instruction bus (5 branches) ──────────────────────────
        mux_tap_x = m0[0] - 0.4

        bus = make_bus_split(
            origin  = origin,
            trunk_x = trunk_x,
            branches = [
                {
                    "y":          rr1[1] + 0.5,
                    "dest":       np.array([trunk_x + 1.6,
                                            rr1[1] + 0.5, 0]),
                    "label":      "Inst[31–26]",
                    "label_side": UP,
                    "dot":        False,
                },
                {
                    "y":          rr1[1],
                    "dest":       rr1,
                    "label":      "Inst[25–21]",
                    "label_side": UP,
                },
                {
                    "y":          rr2[1],
                    "dest":       rr2,
                    "bend_x":     mux_tap_x,
                    "label":      "Inst[20–16]",
                    "label_side": UP,
                    "dot":        True,
                },
                {
                    "y":          m1[1],
                    "dest":       m1,
                    "bend_x":     mux_tap_x,
                    "label":      "Inst[15–11]",
                    "label_side": UP,
                },
                {
                    "y":          se_in[1],
                    "dest":       se_in,
                    "label":      "Inst[15–0]",
                    "label_side": UP,
                },
            ],
        )

        # ── 4. Inst[5-0] junction (tap from [15-0] wire) ────────────────
        funct_junc = np.array([se_in[0] - 0.3, se_in[1], 0])
        dot_funct  = make_junction(funct_junc, color=CTRL_COLOR)
        # Horizontal corridor below Sign-extend for Inst[5-0] routing
        funct_corridor_y = se_in[1] - 1.2

        # ── 5. extra wires via make_connection ────────────────────────────
        wires = {
            "to_m0": make_connection(
                np.array([mux_tap_x, rr2[1], 0]), m0,
                bend_x=m0[0] - 0.3,
            ),
            "mux_wr": make_connection(mout, wr, bend_ratio=0.5),
            # Read data 2 → ALU MUX input 0
            "rd2_am0": make_connection(rd2, am0, label="Read data 2"),
            # Sign-extend output → ALU MUX input 1
            "se_am1": make_connection(se_out, am1, label="Imm32", bend_x=am1[0] - 0.3),
            # ALUSrc control → ALU MUX select
            "alusrc": make_connection(
                amsel + DOWN * 0.5, amsel,
                arrow=False, ctrl=True, label="ALUSrc",
                wire_func=make_straight_wire,
            ),
            # Read data 1 → ALU input A
            "rd1_alu": make_connection(rd1, alu_a, label="Read data 1"),
            # ALU MUX output → ALU input B
            "amux_alu": make_connection(amout, alu_b),
            # Inst[5-0] junction → down below Sign-extend → right → up to ALU Control top
            "funct_ac": make_connection(
                funct_junc, ac_funct,
                ctrl=True, label="Inst[5–0]",
                tip_dir=DOWN,
                wire_func=make_v_h_v_wire,
                bend_y=funct_corridor_y,
            ),
            # ALUOp → ALU Control (from top, Control Unit stub)
            "aluop_ac": make_connection(
                ac_aluop + UP * 0.6, ac_aluop,
                arrow=True, ctrl=True, label="ALUOp",
                tip_dir=UP,
                wire_func=make_straight_wire,
            ),
            # ALU Control output → ALU ctrl port
            "ac_alu": make_connection(
                ac_out, alu_ctrl,
                ctrl=True,
            ),
            # ALU output → stub (to DataMem)
            "alu_out": make_connection(
                alu_out, alu_out + RIGHT * 1.0,
                arrow=False, label="ALU result",
                wire_func=make_straight_wire,
            ),
            # ALU Zero flag → stub
            "alu_zero": make_connection(
                alu_zero, alu_zero + UP * 0.6 + RIGHT * 0.5,
                arrow=False, ctrl=True, label="Zero",
                wire_func=make_straight_wire,
            ),
            "regdst": make_connection(
                msel + DOWN * 0.5, msel,
                arrow=False, ctrl=True, label="RegDst",
                wire_func=make_straight_wire,
            ),
        }

        dot_to_m0 = make_junction(np.array([mux_tap_x, rr2[1], 0]))

        # ── 5. draw everything ─────────────────────────────────────────────
        animate_bus(self, bus, trunk_rt=0.5, branch_rt=0.7, stagger=0.15)
        draw_connections(self, wires, run_time=0.8)
        self.play(FadeIn(dot_to_m0), FadeIn(dot_funct), run_time=0.3)
        self.wait(0.5)

        # ── 6. signal flow animation ───────────────────────────────────────
        animate_data_path(self, [
            {"component": im.shape, "label": "Fetch"},
            {"wire": bus["entry"]},
            {"wire": bus["spine"]},
            *[{"wire": w} for w in bus["branches"]],
            # Sign-extend path
            {"component": se.shape, "label": "Sign-extend"},
            {"wire": wires["se_am1"]["wire"]},
            # RegDst MUX → Write register
            {"wire": wires["to_m0"]["wire"]},
            {"ctrl": wires["regdst"]["wire"]},
            {"component": mux.shape, "label": "RegDst MUX"},
            {"wire": wires["mux_wr"]["wire"]},
            {"component": rf.shape, "label": "Registers"},
            # Read data 1 → ALU input A
            {"wire": wires["rd1_alu"]["wire"]},
            # Read data 2 → ALU MUX → ALU input B
            {"wire": wires["rd2_am0"]["wire"]},
            {"ctrl": wires["alusrc"]["wire"]},
            {"component": alu_mux.shape, "label": "ALUSrc MUX"},
            {"wire": wires["amux_alu"]["wire"]},
            # ALU Control decodes
            {"ctrl": wires["funct_ac"]["wire"]},
            {"ctrl": wires["aluop_ac"]["wire"]},
            {"component": alu_control.shape, "label": "ALU Control"},
            {"ctrl": wires["ac_alu"]["wire"]},
            # ALU executes
            {"component": alu.shape, "label": "ALU"},
            {"wire": wires["alu_out"]["wire"]},
        ])

        self.wait(1.5)
