"""
Standalone timing constants for the RISC-V single-cycle datapath.

Kept in a separate module so performance.py can import these without
pulling in DatapathBase (which sets config.frame_width at module level).
"""

from manim import BLUE, GREEN, ORANGE, RED, YELLOW_B

INST_TIMINGS = [
    {
        "type": "R-type (add, sub)",
        "if": 200, "id": 100, "ex": 200, "mem": 0,   "wb": 100,
        "total": 600, "color": GREEN,
    },
    {
        "type": "I-type (lw \u2014 Load)",   # Critical path
        "if": 200, "id": 100, "ex": 200, "mem": 200, "wb": 100,
        "total": 800, "color": RED,
    },
    {
        "type": "S-type (sw \u2014 Store)",
        "if": 200, "id": 100, "ex": 200, "mem": 200, "wb": 0,
        "total": 700, "color": ORANGE,
    },
    {
        "type": "B-type (beq \u2014 Branch)",
        "if": 200, "id": 100, "ex": 200, "mem": 0,   "wb": 0,
        "total": 500, "color": YELLOW_B,
    },
    {
        "type": "J-type (jal \u2014 Jump)",
        "if": 200, "id": 100, "ex": 200, "mem": 0,   "wb": 100,
        "total": 600, "color": BLUE,
    },
]

CRITICAL_PATH_PS = max(t["total"] for t in INST_TIMINGS)  # 800 ps (lw)
