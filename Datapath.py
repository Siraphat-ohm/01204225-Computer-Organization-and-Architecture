from manim import *
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from InstructionMemory import InstructionMemoryComponent
from PC                import PCComponent
from MUX               import MuxComponent
from RegFile           import RegFileComponent
from SignExtend        import SignExtendComponent
from ALU               import ALUComponent
from ALUControl        import ALUControlComponent
from DataMemory        import DataMemoryComponent
from utils             import (
    make_bus_split, animate_bus,
    make_ortho_wire, make_straight_wire, make_junction,
    make_connection, draw_connections, animate_data_path, make_v_h_v_wire,
    make_feedback_wire,
    SIGNAL_COLOR, CTRL_COLOR,
)

# Wider frame for full single-cycle datapath

# config frame 16:9
config.frame_width  = 30
config.frame_height = 16.875

class DatapathTest(Scene):
    def construct(self):

        pc  = PCComponent(
                  width=1.0, height=2.0,
              ).move_to(LEFT * 8.0)

        im  = InstructionMemoryComponent(
                  width=2.6, height=3.8,
                  show_port_labels=False,
              ).move_to(LEFT * 4.8)

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

        dm = DataMemoryComponent(width=2.6, height=3.8).move_to(RIGHT * 12.0)
        dm.shift(UP * (alu.get_output()[1] - dm.get_address()[1]))

        # WB MUX: input_1 aligned with DM read data, input_0 will receive ALU result
        wb_mux = MuxComponent().move_to(RIGHT * 15.2)
        wb_mux.shift(UP * (dm.get_read_data()[1] - wb_mux.get_input_1()[1]))

        # Shift all components to align to left of frame
        everything = VGroup(pc, im, rf, se, alu_mux, alu, alu_control, dm, wb_mux)
        everything.to_edge(LEFT, buff=0.3)

        self.add(pc, im, rf, se, alu_mux, alu, alu_control, dm, wb_mux)

        pc_in  = pc.get_input()
        pc_out = pc.get_output()
        im_ra  = im.get_read_address()

        rr1  = rf.get_read_reg1()
        rr2  = rf.get_read_reg2()
        wr   = rf.get_write_reg()

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

        dm_addr  = dm.get_address()
        dm_wd    = dm.get_write_data()
        dm_rd    = dm.get_read_data()
        dm_mr    = dm.get_mem_read()
        dm_mw    = dm.get_mem_write()

        # Junction just left of DM — ALU result splits here to DM addr and WB MUX bypass
        alu_junc = np.array([dm.shape.get_left()[0] - 0.5, alu_out[1], 0])

        wb_in0   = wb_mux.get_input_0()
        wb_in1   = wb_mux.get_input_1()
        wb_out   = wb_mux.get_output()
        wb_sel   = wb_mux.get_ctrl_port()

        origin  = im.inst_bus_origin()
        trunk_x = origin[0] + 0.5

        # ── 3. main instruction bus (5 branches) ──────────────────────────
        bus = make_bus_split(
            origin  = origin,
            trunk_x = trunk_x,
            branches = [
                {
                    "y":          rr1[1] + 0.5,
                    "dest":       np.array([trunk_x + 1.6,
                                            rr1[1] + 0.5, 0]),
                    "label":      "Inst[6–0]",
                    "label_side": UP,
                    "dot":        False,
                },
                {
                    "y":          rr1[1],
                    "dest":       rr1,
                    "label":      "Inst[19–15]",
                    "label_side": UP,
                },
                {
                    "y":          rr2[1],
                    "dest":       rr2,
                    "label":      "Inst[24–20]",
                    "label_side": UP,
                },
                {
                    "y":          wr[1],
                    "dest":       wr,
                    "label":      "Inst[11–7]",
                    "label_side": UP,
                },
                {
                    "y":          se_in[1],
                    "dest":       se_in,
                    "label":      "Inst[31–20]",
                    "label_side": UP,
                },
            ],
        )

        # ── 4. funct3/funct7 junction (tap from Inst[31-20] wire) ───────
        funct_junc = np.array([se_in[0] - 0.3, se_in[1], 0])
        dot_funct  = make_junction(funct_junc, color=SIGNAL_COLOR)
        # Horizontal corridor below Sign-extend for Inst[5-0] routing
        funct_corridor_y = se_in[1] - 1.2
        funct_label = Text("Inst[14–12]\nInst[31–25]", font_size=10, color=WHITE, line_spacing=0.8)
        funct_label.move_to(np.array([
            (funct_junc[0] + ac_funct[0]) / 2,
            funct_corridor_y + 0.18,
            0,
        ]))

        # ── 5. extra wires via make_connection ────────────────────────────
        wires = {
            # PC output -> Instruction memory read address
            "pc_im": make_connection(
                pc_out, im_ra, label="PC",
            ),
            # Next PC input stub
            "pc_in": make_connection(
                pc_in + LEFT * 0.8, pc_in,
                arrow=False, label="Next PC",
                wire_func=make_straight_wire,
            ),
            # Read data 2 → ALU MUX input 0
            "rd2_am0": make_connection(rd2, am0, label="Read data 2"),
            # Sign-extend output → ALU MUX input 1
            "se_am1": make_connection(se_out, am1, label="Imm32", bend_x=am1[0] - 0.3),
            # ALUSrc control → ALU MUX select
            "alusrc": make_connection(
                amsel + DOWN * 0.5, amsel,
                arrow=False, ctrl=True, label="ALUSrc", label_color=CTRL_COLOR, label_side=DOWN,
                wire_func=make_straight_wire,
            ),
            # Read data 1 → ALU input A
            "rd1_alu": make_connection(rd1, alu_a, label="Read data 1"),
            # ALU MUX output → ALU input B
            "amux_alu": make_connection(amout, alu_b),
            # Inst[5-0] junction → down below Sign-extend → right → up to ALU Control top
            "funct_ac": make_connection(
                funct_junc, ac_funct,
                tip_dir=DOWN,
                wire_func=make_v_h_v_wire,
                bend_y=funct_corridor_y,
            ),
            # ALUOp → ALU Control (from top, Control Unit stub)
            "aluop_ac": make_connection(
                ac_aluop + UP * 0.6, ac_aluop,
                arrow=True, ctrl=True, label="ALUOp", label_color=CTRL_COLOR, label_side=DOWN,
                tip_dir=UP,
                wire_func=make_straight_wire,
            ),
            # ALU Control output → ALU ctrl port (arrives at bottom of ALU from below)
            "ac_alu": make_connection(
                ac_out, alu_ctrl,
                ctrl=True,
                tip_dir=UP,
            ),
            # ALU output → junction just left of DM
            "alu_junc": make_connection(
                alu_out, alu_junc,
                arrow=False, label="ALU result",
                wire_func=make_straight_wire,
            ),
            # Junction → DM address (short horizontal, open space)
            "junc_dm": make_connection(alu_junc, dm_addr),
            # Read data 2 junction → Data Memory write data (routes below ALU)
            "rd2_dm": make_connection(
                rd2, dm_wd,
                bend_y=alu_ctrl[1] - 1.0,
                wire_func=make_v_h_v_wire,
            ),
            # MemRead control stub
            "mem_read": make_connection(
                dm_mr + UP * 0.6, dm_mr,
                arrow=True, ctrl=True, label="MemRead", label_color=CTRL_COLOR, label_side=DOWN,
                tip_dir=UP,
                wire_func=make_straight_wire,
            ),
            # MemWrite control stub
            "mem_write": make_connection(
                dm_mw + UP * 0.6, dm_mw,
                arrow=True, ctrl=True, label="MemWrite", label_color=CTRL_COLOR, label_side=DOWN,
                tip_dir=UP,
                wire_func=make_straight_wire,
            ),
            # Data Memory read data → WB MUX input 1
            "dm_wb": make_connection(dm_rd, wb_in1, label="Read data"),
            # Junction → WB MUX input 0: down in open space left of DM, under DM, up to WB MUX
            "alu_wb": make_connection(
                alu_junc, wb_in0,
                wire_func=make_v_h_v_wire,
                bend_y=dm.shape.get_bottom()[1] - 0.5,
            ),
            # WB MUX output → RegFile write data (feedback loop under datapath)
            # corridor must clear funct_corridor_y (lowest wire in scene)
            "wb_rf": make_connection(
                wb_out, rf.get_write_data(),
                wire_func=make_feedback_wire,
                offset_y=(funct_corridor_y - 1.0) - min(wb_out[1], rf.get_write_data()[1]),
            ),
            # MemtoReg control → WB MUX select
            "mem_to_reg": make_connection(
                wb_sel + DOWN * 0.5, wb_sel,
                arrow=False, ctrl=True, label="MemtoReg", label_color=CTRL_COLOR, label_side=DOWN,
                wire_func=make_straight_wire,
            ),
            # ALU Zero flag → stub
            "alu_zero": make_connection(
                alu_zero, alu_zero + UP * 0.6 + RIGHT * 0.5,
                arrow=False, ctrl=True, label="Zero", label_color=CTRL_COLOR, label_side=DOWN,
                wire_func=make_straight_wire,
            ),
        }

        dot_rd2    = make_junction(rd2)
        dot_alu    = make_junction(alu_junc)

        # ── 5. draw everything (static — animations added later) ───────────
        self.add(*bus["all"])
        for conn in wires.values():
            self.add(conn["all"])
        self.add(funct_label, dot_funct, dot_rd2, dot_alu)
        self.wait(1)
