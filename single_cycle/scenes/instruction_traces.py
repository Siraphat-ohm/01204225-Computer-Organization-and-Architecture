"""
Instruction-trace scenes for the RISC-V single-cycle datapath.

Each scene inherits DatapathBase, builds the full static datapath, then
animates the 5-stage pipeline (IF → ID → EX → MEM → WB) for one
instruction type, highlighting only the active wires and components.

Render commands (low quality / preview):
    manim -pql scenes/instruction_traces.py TraceRType
    manim -pql scenes/instruction_traces.py TraceLW
    manim -pql scenes/instruction_traces.py TraceSW
    manim -pql scenes/instruction_traces.py TraceBeq
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from manim import *
from utils import CTRL_COLOR, SIGNAL_COLOR, animate_data_path
from scenes.datapath_base import DatapathBase


from scenes.timing_data import CRITICAL_PATH_PS, INST_TIMINGS  # re-exported for back-compat

# ── Shared control-signal tables ──────────────────────────────────────────────

_CTRL_R = {
    "RegWrite": "1", "ALUSrc": "0", "ALUOp": "10",
    "MemRead":  "0", "MemWrite": "0", "MemtoReg": "0", "Branch": "0",
}
_ACTIVE_R = {"RegWrite", "ALUOp"}

_CTRL_LW = {
    "RegWrite": "1", "ALUSrc": "1", "ALUOp": "00",
    "MemRead":  "1", "MemWrite": "0", "MemtoReg": "1", "Branch": "0",
}
_ACTIVE_LW = {"RegWrite", "ALUSrc", "MemRead", "MemtoReg"}

_CTRL_SW = {
    "RegWrite": "0", "ALUSrc": "1", "ALUOp": "00",
    "MemRead":  "0", "MemWrite": "1", "MemtoReg": "X", "Branch": "0",
}
_ACTIVE_SW = {"ALUSrc", "MemWrite"}

_CTRL_BEQ = {
    "RegWrite": "0", "ALUSrc": "0", "ALUOp": "01",
    "MemRead":  "0", "MemWrite": "0", "MemtoReg": "X", "Branch": "1",
}
_ACTIVE_BEQ = {"Branch", "ALUOp"}


# ── Helper: bus branch wires by field ────────────────────────────────────────

def _bus_wires_for(bus, *field_indices):
    """Return bus branch wires at the given indices (0=opcode,1=rs1,…,4=imm)."""
    return [bus["branches"][i] for i in field_indices]


# ─────────────────────────────────────────────────────────────────────────────
# R-type: add x1, x2, x3
# ─────────────────────────────────────────────────────────────────────────────

class TraceRType(DatapathBase):
    """
    Traces an R-type instruction (add x1, x2, x3) through the datapath.

    Active path: PC → IM → RF(rs1,rs2) → ALU → WB MUX → RF(rd)
    Control:     RegWrite=1, ALUSrc=0, ALUOp=10, MemRead=0, MemWrite=0
    """

    def construct(self):
        self.setup_datapath()

        banner = self.show_instruction_banner(
            "R-type:  add x1, x2, x3",
            subtitle="rd ← rs1 + rs2",
        )
        ctrl_table = self.show_ctrl_table(_CTRL_R, _ACTIVE_R)

        active_wire_keys = {
            "pc_to_dot", "junc_im",
            "rd1_alu", "rd2_am0", "amux_alu",
            "ctrl_aluop", "ac_alu",
            "alu_wb", "wb_rf",
            "ctrl_regwrite",
        }
        self.dim_inactive_wires(active_wire_keys)            # New Header Positioning: 
            # Place it strictly between the Title and the Table
        self.wait(0.3)

        # ── IF: Instruction Fetch ──────────────────────────────────────────
        self.stage_banner("IF — Instruction Fetch")
        animate_data_path(self, [
            {"wire":      self.wires["pc_to_dot"]["wire"]},
            {"wire":      self.wires["junc_im"]["wire"], "label": "PC"},
            {"component": self.im.shape, "label": "Fetch"},
        ])

        # ── ID: Instruction Decode / Register Read ─────────────────────────
        self.stage_banner("ID — Decode / Register Read")
        animate_data_path(self, [
            {"wire": bus_w} for bus_w in _bus_wires_for(self.bus, 1, 2, 3)
        ] + [
            {"component": self.rf.shape, "label": "RegFile"},
            {"ctrl": self.wires["ctrl_regwrite"]["wire"], "label": "RegWrite=1"},
        ])

        # ── EX: Execute ───────────────────────────────────────────────────
        self.stage_banner("EX — Execute (ALU)")
        animate_data_path(self, [
            {"wire":      self.wires["rd1_alu"]["wire"],  "label": "rs1"},
            {"wire":      self.wires["rd2_am0"]["wire"],  "label": "rs2"},
            {"wire":      self.wires["amux_alu"]["wire"]},
            {"ctrl":      self.wires["ctrl_aluop"]["wire"], "label": "ALUOp=10"},
            {"ctrl":      self.wires["ac_alu"]["wire"],     "label": "ALU ctrl"},
            {"component": self.alu.shape},
        ])
        self.alu.animate_operation(self, "ADD")

        # ── MEM: skipped (MemRead=0, MemWrite=0) ──────────────────────────
        self.stage_banner("MEM — (not used)")
        self.wait(0.4)

        # ── WB: Write Back ────────────────────────────────────────────────
        self.stage_banner("WB — Write Back")
        animate_data_path(self, [
            {"wire":      self.wires["alu_wb"]["wire"]},
            {"wire":      self.wires["wb_rf"]["wire"],  "label": "ALU result → rd"},
            {"component": self.rf.shape, "label": "Write rd"},
        ])

        self.wait(2)
        self.clear_stage_banner()
        self.play(FadeOut(banner), FadeOut(ctrl_table))
        self.wait(0.5)


# ─────────────────────────────────────────────────────────────────────────────
# I-type Load: lw x1, 0(x2)
# ─────────────────────────────────────────────────────────────────────────────

class TraceLW(DatapathBase):
    """
    Traces a load-word instruction (lw x1, 0(x2)) through the datapath.

    Active path: PC → IM → RF(rs1) + SE(imm) → ALUSrc MUX → ALU → DM → WB MUX → RF(rd)
    Control:     RegWrite=1, ALUSrc=1, ALUOp=00, MemRead=1, MemtoReg=1
    """

    def construct(self):
        self.setup_datapath()

        banner = self.show_instruction_banner(
            "I-type Load:  lw x1, 0(x2)",
            subtitle="rd ← MEM[ rs1 + imm ]",
        )
        ctrl_table = self.show_ctrl_table(_CTRL_LW, _ACTIVE_LW)

        active_wire_keys = {
            "pc_to_dot", "junc_im",
            "rd1_alu", "se_am1", "amux_alu",
            "ctrl_alusrc", "ctrl_aluop", "ac_alu",
            "alu_dm", "ctrl_memread", "dm_wb",
            "ctrl_memtoreg", "wb_rf",
            "ctrl_regwrite",
        }
        self.dim_inactive_wires(active_wire_keys)
        self.wait(0.3)

        # ── IF ────────────────────────────────────────────────────────────
        self.stage_banner("IF — Instruction Fetch")
        animate_data_path(self, [
            {"wire":      self.wires["pc_to_dot"]["wire"]},
            {"wire":      self.wires["junc_im"]["wire"], "label": "PC"},
            {"component": self.im.shape, "label": "Fetch"},
        ])

        # ── ID ────────────────────────────────────────────────────────────
        self.stage_banner("ID — Decode / Register Read")
        animate_data_path(self, [
            {"wire": bus_w} for bus_w in _bus_wires_for(self.bus, 1, 3, 4)
        ] + [
            {"component": self.rf.shape, "label": "RegFile"},
            {"component": self.se.shape, "label": "Sign-Extend"},
        ])

        # ── EX ────────────────────────────────────────────────────────────
        self.stage_banner("EX — Execute (ALU)")
        animate_data_path(self, [
            {"wire":      self.wires["rd1_alu"]["wire"],   "label": "rs1 (base)"},
            {"wire":      self.wires["se_am1"]["wire"],    "label": "imm (offset)"},
            {"ctrl":      self.wires["ctrl_alusrc"]["wire"], "label": "ALUSrc=1"},
            {"wire":      self.wires["amux_alu"]["wire"]},
            {"ctrl":      self.wires["ctrl_aluop"]["wire"], "label": "ALUOp=00"},
            {"ctrl":      self.wires["ac_alu"]["wire"]},
            {"component": self.alu.shape},
        ])
        self.alu.animate_operation(self, "ADD")

        # ── MEM ───────────────────────────────────────────────────────────
        self.stage_banner("MEM — Memory Read")
        animate_data_path(self, [
            {"wire":      self.wires["alu_dm"]["wire"],       "label": "address"},
            {"ctrl":      self.wires["ctrl_memread"]["wire"], "label": "MemRead=1"},
            {"component": self.dm.shape, "label": "Load"},
            {"wire":      self.wires["dm_wb"]["wire"],        "label": "read data"},
        ])

        # ── WB ────────────────────────────────────────────────────────────
        self.stage_banner("WB — Write Back")
        animate_data_path(self, [
            {"ctrl":      self.wires["ctrl_memtoreg"]["wire"], "label": "MemtoReg=1"},
            {"wire":      self.wires["wb_rf"]["wire"],         "label": "mem data → rd"},
            {"component": self.rf.shape, "label": "Write rd"},
        ])

        self.wait(2)
        self.clear_stage_banner()
        self.play(FadeOut(banner), FadeOut(ctrl_table))
        self.wait(0.5)


# ─────────────────────────────────────────────────────────────────────────────
# S-type Store: sw x2, 0(x1)
# ─────────────────────────────────────────────────────────────────────────────

class TraceSW(DatapathBase):
    """
    Traces a store-word instruction (sw x2, 0(x1)) through the datapath.

    Active path: PC → IM → RF(rs1,rs2) + SE(imm) → ALUSrc MUX → ALU → DM(write)
    Control:     ALUSrc=1, ALUOp=00, MemWrite=1, RegWrite=0
    """

    def construct(self):
        self.setup_datapath()

        banner = self.show_instruction_banner(
            "S-type Store:  sw x2, 0(x1)",
            subtitle="MEM[ rs1 + imm ] ← rs2",
        )
        ctrl_table = self.show_ctrl_table(_CTRL_SW, _ACTIVE_SW)

        active_wire_keys = {
            "pc_to_dot", "junc_im",
            "rd1_alu", "se_am1", "amux_alu",
            "ctrl_alusrc", "ctrl_aluop", "ac_alu",
            "alu_dm", "rd2_dm", "ctrl_memwrite",
        }
        self.dim_inactive_wires(active_wire_keys)
        self.wait(0.3)

        # ── IF ────────────────────────────────────────────────────────────
        self.stage_banner("IF — Instruction Fetch")
        animate_data_path(self, [
            {"wire":      self.wires["pc_to_dot"]["wire"]},
            {"wire":      self.wires["junc_im"]["wire"], "label": "PC"},
            {"component": self.im.shape, "label": "Fetch"},
        ])

        # ── ID ────────────────────────────────────────────────────────────
        self.stage_banner("ID — Decode / Register Read")
        animate_data_path(self, [
            {"wire": bus_w} for bus_w in _bus_wires_for(self.bus, 1, 2, 4)
        ] + [
            {"component": self.rf.shape, "label": "RegFile (rs1, rs2)"},
            {"component": self.se.shape, "label": "Sign-Extend"},
        ])

        # ── EX ────────────────────────────────────────────────────────────
        self.stage_banner("EX — Execute (ALU: compute address)")
        animate_data_path(self, [
            {"wire":      self.wires["rd1_alu"]["wire"],     "label": "rs1 (base)"},
            {"wire":      self.wires["se_am1"]["wire"],      "label": "imm (offset)"},
            {"ctrl":      self.wires["ctrl_alusrc"]["wire"], "label": "ALUSrc=1"},
            {"wire":      self.wires["amux_alu"]["wire"]},
            {"ctrl":      self.wires["ctrl_aluop"]["wire"],  "label": "ALUOp=00"},
            {"ctrl":      self.wires["ac_alu"]["wire"]},
            {"component": self.alu.shape},
        ])
        self.alu.animate_operation(self, "ADD")

        # ── MEM ───────────────────────────────────────────────────────────
        self.stage_banner("MEM — Memory Write")
        animate_data_path(self, [
            {"wire":      self.wires["alu_dm"]["wire"],        "label": "address"},
            {"wire":      self.wires["rd2_dm"]["wire"],        "label": "rs2 (store data)"},
            {"ctrl":      self.wires["ctrl_memwrite"]["wire"], "label": "MemWrite=1"},
            {"component": self.dm.shape, "label": "Store"},
        ])

        # ── WB: not used (RegWrite=0) ─────────────────────────────────────
        self.stage_banner("WB — (not used)")
        self.wait(0.4)

        self.wait(2)
        self.clear_stage_banner()
        self.play(FadeOut(banner), FadeOut(ctrl_table))
        self.wait(0.5)


# ─────────────────────────────────────────────────────────────────────────────
# B-type Branch: beq x1, x2, label
# ─────────────────────────────────────────────────────────────────────────────

class TraceBeq(DatapathBase):
    """
    Traces a branch-if-equal instruction (beq x1, x2, label).

    Active path (branch taken):
      PC → IM → RF(rs1,rs2) → ALU(SUB) → Zero=1 → AND gate → PCSrc=1
      PC + (imm << 1) → Branch Adder → PCSrc MUX → PC

    Control: Branch=1, ALUSrc=0, ALUOp=01, RegWrite=0
    """

    def construct(self):
        self.setup_datapath()

        banner = self.show_instruction_banner(
            "B-type Branch:  beq x1, x2, label",
            subtitle="if rs1 == rs2 → PC ← PC + (imm << 1)",
        )
        ctrl_table = self.show_ctrl_table(_CTRL_BEQ, _ACTIVE_BEQ)

        active_wire_keys = {
            "pc_to_dot", "junc_im",
            "rd1_alu", "rd2_am0", "amux_alu",
            "ctrl_aluop", "ac_alu",
            "zero_and", "ctrl_branch", "pcsrc_sel",
            "se_sl", "sl_bra", "pc_bra", "bra_pcsrc",
            "pcsrc_pc",
        }
        self.dim_inactive_wires(active_wire_keys)
        self.wait(0.3)

        # ── IF ────────────────────────────────────────────────────────────
        self.stage_banner("IF — Instruction Fetch")
        animate_data_path(self, [
            {"wire":      self.wires["pc_to_dot"]["wire"]},
            {"wire":      self.wires["junc_im"]["wire"], "label": "PC"},
            {"component": self.im.shape, "label": "Fetch"},
        ])

        # ── ID ────────────────────────────────────────────────────────────
        self.stage_banner("ID — Decode / Register Read")
        animate_data_path(self, [
            {"wire": bus_w} for bus_w in _bus_wires_for(self.bus, 1, 2, 4)
        ] + [
            {"component": self.rf.shape, "label": "RegFile (rs1, rs2)"},
            {"component": self.se.shape, "label": "Sign-Extend imm"},
        ])

        # ── EX ────────────────────────────────────────────────────────────
        self.stage_banner("EX — Execute (ALU: subtract / compare)")
        animate_data_path(self, [
            {"wire":      self.wires["rd1_alu"]["wire"],  "label": "rs1"},
            {"wire":      self.wires["rd2_am0"]["wire"],  "label": "rs2"},
            {"wire":      self.wires["amux_alu"]["wire"]},
            {"ctrl":      self.wires["ctrl_aluop"]["wire"], "label": "ALUOp=01"},
            {"ctrl":      self.wires["ac_alu"]["wire"]},
            {"component": self.alu.shape},
        ])
        self.alu.animate_operation(self, "SUB")

        # ── Branch target address (runs in parallel with EX conceptually) ──
        self.stage_banner("EX — Branch Target Address")
        animate_data_path(self, [
            {"wire":      self.wires["se_sl"]["wire"],   "label": "imm"},
            {"component": self.shift_left.shape, "label": "<<1"},
            {"wire":      self.wires["sl_bra"]["wire"]},
            {"wire":      self.wires["pc_bra"]["wire"],  "label": "PC"},
            {"component": self.branch_add.shape, "label": "PC + imm<<1"},
            {"wire":      self.wires["bra_pcsrc"]["wire"], "label": "branch target"},
        ])

        # ── Branch logic ──────────────────────────────────────────────────
        self.stage_banner("Branch Logic — Zero & PCSrc")
        animate_data_path(self, [
            {"ctrl":      self.wires["zero_and"]["wire"],   "label": "Zero=1 (equal)"},
            {"ctrl":      self.wires["ctrl_branch"]["wire"], "label": "Branch=1"},
            {"component": self.and_gate.shape, "label": "AND"},
            {"ctrl":      self.wires["pcsrc_sel"]["wire"],  "label": "PCSrc=1"},
            {"component": self.pcsrc_mux.shape, "label": "Select branch"},
        ])

        # ── WB / PC update ────────────────────────────────────────────────
        self.stage_banner("PC Update — Branch Taken")
        animate_data_path(self, [
            {"wire":      self.wires["pcsrc_pc"]["wire"], "label": "next PC"},
            {"component": self.pc.shape, "label": "PC ← target"},
        ])

        self.wait(2)
        self.clear_stage_banner()
        self.play(FadeOut(banner), FadeOut(ctrl_table))
        self.wait(0.5)

class DebugTrace(TraceRType):
    """
    Static snapshot — no animation, no wait.
    ใช้สำหรับ debug layout/UI เท่านั้น
    """

    def construct(self):
        # monkey-patch ทุก animation ออก
        self.play = lambda *a, **kw: None
        self.wait = lambda *a, **kw: None

        # เรียก construct ของ TraceRType ปกติ
        super().construct()