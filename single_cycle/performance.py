import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from manim import *
from scenes.timing_data import CRITICAL_PATH_PS, INST_TIMINGS

# ── Stage metadata ─────────────────────────────────────────────────────────────
STAGE_KEYS   = ["if", "id", "ex", "mem", "wb"]
STAGE_LABELS = ["IF", "ID", "EX", "MEM", "WB"]
STAGE_COLS   = [BLUE_C, PURPLE_C, GREEN_C, ORANGE, TEAL_C]

# ── Timing-diagram layout constants (left panel) ───────────────────────────────
BAR_ORIGIN_X = -5.1    # x position of t = 0
PS_SCALE     = 0.0055  # Manim units per picosecond  (800 ps → 4.4 units)
ROW_H        = 0.50
ROW_GAP      = 0.92   # increased row spacing
TOP_ROW_Y    = 2.30

SHORT_NAMES = ["R-type", "lw  (Load)", "sw  (Store)", "beq  (Branch)", "jal  (Jump)"]


class PerformanceScene(Scene):

    def construct(self):
        self._left_panel()
        self._right_panel()

        self.wait(3)
        self.play(FadeOut(Group(*self.mobjects)))

    # ─── LEFT: instruction timing diagram ─────────────────────────────────────

    def _left_panel(self):
        # Title
        title = (
            Text("Instruction Timing Diagram", font_size=21, color=YELLOW, weight=BOLD)
            .move_to(np.array([-3.3, 3.72, 0]))
        )
        self.play(Write(title))

        # Stage colour legend
        legend = VGroup(*[
            VGroup(
                Rectangle(width=0.32, height=0.20,
                          color=c, fill_color=c, fill_opacity=0.8, stroke_width=1),
                Text(s, font_size=12, color=WHITE),
            ).arrange(RIGHT, buff=0.06)
            for s, c in zip(STAGE_LABELS, STAGE_COLS)
        ]).arrange(RIGHT, buff=0.22).next_to(title, DOWN, buff=0.10).align_to(title, LEFT)
        self.play(FadeIn(legend))
        self.wait(0.2)

        # ── Instruction rows ──────────────────────────────────────────────────
        row_bar_groups = []   # store bars VGroup per row for later highlight
        for i, (inst, short) in enumerate(zip(INST_TIMINGS, SHORT_NAMES)):
            y = TOP_ROW_Y - i * ROW_GAP

            name_txt = (
                Text(short, font_size=14, color=inst["color"], weight=BOLD)
                .next_to(np.array([BAR_ORIGIN_X, y, 0]), LEFT, buff=0.12)
            )

            bars_vg = VGroup()
            cum = 0
            for key, lbl, col in zip(STAGE_KEYS, STAGE_LABELS, STAGE_COLS):
                t = inst[key]
                if t == 0:
                    cum += t
                    continue
                w = t * PS_SCALE
                cx = BAR_ORIGIN_X + cum * PS_SCALE + w / 2
                bar = Rectangle(
                    width=w - 0.03, height=ROW_H,
                    color=col, fill_color=col, fill_opacity=0.55, stroke_width=1.5,
                ).move_to(np.array([cx, y, 0]))
                bar_lbl = Text(lbl, font_size=10, color=WHITE).move_to(bar.get_center())
                bars_vg.add(VGroup(bar, bar_lbl))
                cum += t

            end_x = BAR_ORIGIN_X + inst["total"] * PS_SCALE
            total_txt = (
                Text(f"{inst['total']} ps", font_size=12, color=inst["color"])
                .next_to(np.array([end_x, y, 0]), RIGHT, buff=0.08)
            )

            self.play(
                FadeIn(name_txt, shift=RIGHT * 0.08),
                AnimationGroup(
                    *[FadeIn(b, shift=RIGHT * 0.04) for b in bars_vg],
                    lag_ratio=0.25,
                ),
                FadeIn(total_txt),
                run_time=0.5,
            )
            row_bar_groups.append(bars_vg)

        # ── Time axis ─────────────────────────────────────────────────────────
        axis_y = TOP_ROW_Y - len(INST_TIMINGS) * ROW_GAP + 0.10
        max_t  = 900
        axis   = Line(
            np.array([BAR_ORIGIN_X, axis_y, 0]),
            np.array([BAR_ORIGIN_X + max_t * PS_SCALE, axis_y, 0]),
            color=GRAY_B,
        )
        ticks = VGroup()
        for t in range(0, max_t + 1, 200):
            x = BAR_ORIGIN_X + t * PS_SCALE
            tick = Line(
                np.array([x, axis_y - 0.08, 0]),
                np.array([x, axis_y + 0.08, 0]),
                color=GRAY_B,
            )
            lbl = Text(str(t), font_size=11, color=GRAY_B).move_to(
                np.array([x, axis_y - 0.25, 0])
            )
            ticks.add(tick, lbl)
        axis_unit = Text("ps", font_size=12, color=GRAY_B).next_to(axis, RIGHT, buff=0.08)
        self.play(Create(axis), FadeIn(ticks), Write(axis_unit), run_time=0.5)

        # ── Clock waveform ────────────────────────────────────────────────────
        clk_y  = axis_y - 0.65
        cp_w   = CRITICAL_PATH_PS * PS_SCALE
        h      = 0.17
        x0     = BAR_ORIGIN_X

        clk_lbl = (
            Text("CLK", font_size=12, color=WHITE)
            .move_to(np.array([x0 - 0.38, clk_y, 0]))
        )
        wave = VMobject(color=YELLOW_B)
        wave.set_points_as_corners([
            np.array([x0,           clk_y - h, 0]),
            np.array([x0,           clk_y + h, 0]),
            np.array([x0 + cp_w/2,  clk_y + h, 0]),
            np.array([x0 + cp_w/2,  clk_y - h, 0]),
            np.array([x0 + cp_w,    clk_y - h, 0]),
        ])
        brace = BraceBetweenPoints(
            np.array([x0,        clk_y - h - 0.10, 0]),
            np.array([x0 + cp_w, clk_y - h - 0.10, 0]),
            direction=DOWN, color=YELLOW_B,
        )
        brace_lbl = (
            Text(f"T_c ≥ {CRITICAL_PATH_PS} ps", font_size=12, color=YELLOW_B)
            .next_to(brace, DOWN, buff=0.07)
        )
        self.play(
            FadeIn(clk_lbl),
            Create(wave),
            GrowFromCenter(brace),
            Write(brace_lbl),
            run_time=0.6,
        )

        # ── Highlight critical-path row ───────────────────────────────────────
        self.wait(0.3)
        crit_i    = next(i for i, t in enumerate(INST_TIMINGS) if t["total"] == CRITICAL_PATH_PS)
        crit_rect = SurroundingRectangle(
            row_bar_groups[crit_i], color=RED, stroke_width=2.5, buff=0.07,
        )
        crit_note = (
            Text("▲ Critical Path", font_size=13, color=RED)
            .next_to(crit_rect, UP, buff=0.10)
        )
        self.play(Create(crit_rect), Write(crit_note), run_time=0.4)
        self.play(Indicate(crit_rect, scale_factor=1.04, color=RED), run_time=0.8)

    # ─── RIGHT: performance calculations ──────────────────────────────────────

    def _right_panel(self):
        f_ghz = round(1e12 / CRITICAL_PATH_PS / 1e9, 2)

        right_x = 3.4   # x-anchor for the right panel content

        # ── Title ─────────────────────────────────────────────────────────────
        title = (
            Text("Performance Analysis", font_size=21, color=YELLOW, weight=BOLD)
            .move_to(np.array([right_x, 3.72, 0]))
        )
        self.play(Write(title))
        cursor_y = 3.72

        def _section_head(text, color, y):
            return Text(text, font_size=16, color=color, weight=BOLD).move_to(
                np.array([right_x, y, 0])
            )

        def _math(tex, size, y, color=WHITE):
            return MathTex(tex, font_size=size, color=color).move_to(
                np.array([right_x, y, 0])
            )

        # ── 1. CPI ────────────────────────────────────────────────────────────
        cursor_y -= 0.65
        h1 = _section_head("① Cycles Per Instruction (CPI)", BLUE_B, cursor_y)
        self.play(FadeIn(h1, shift=UP * 0.08))

        cursor_y -= 0.62
        eq_cpi = _math(r"\text{CPI} = 1", 40, cursor_y)
        self.play(Write(eq_cpi))

        cursor_y -= 0.60
        note_cpi = (
            Text("One instruction completes per clock cycle\n(single-cycle design guarantee).",
                 font_size=13, color=GRAY_A, line_spacing=1.3)
            .move_to(np.array([right_x, cursor_y, 0]))
        )
        self.play(FadeIn(note_cpi))
        self.wait(0.4)

        # ── separator ─────────────────────────────────────────────────────────
        cursor_y -= 0.62
        sep1 = Line(
            np.array([right_x - 2.8, cursor_y, 0]),
            np.array([right_x + 2.8, cursor_y, 0]),
            color=GRAY, stroke_opacity=0.4,
        )
        self.play(Create(sep1), run_time=0.3)

        # ── 2. Critical path ──────────────────────────────────────────────────
        cursor_y -= 0.55
        h2 = _section_head("② Critical Path", ORANGE, cursor_y)
        self.play(FadeIn(h2, shift=UP * 0.08))

        cursor_y -= 0.60
        eq_cp1 = _math(r"T_{crit} = \max\{T_{instr}\} = T_{lw}", 30, cursor_y)
        self.play(Write(eq_cp1))
        self.wait(0.5)

        cursor_y -= 0.58
        eq_cp2 = _math(
            rf"T_{{crit}} = {CRITICAL_PATH_PS}\text{{ ps}}", 34, cursor_y, color=RED
        )
        self.play(Write(eq_cp2))
        self.wait(0.4)

        # ── separator ─────────────────────────────────────────────────────────
        cursor_y -= 0.62
        sep2 = Line(
            np.array([right_x - 2.8, cursor_y, 0]),
            np.array([right_x + 2.8, cursor_y, 0]),
            color=GRAY, stroke_opacity=0.4,
        )
        self.play(Create(sep2), run_time=0.3)

        # ── 3. Minimum clock rate ─────────────────────────────────────────────
        cursor_y -= 0.55
        h3 = _section_head("③ Minimum Clock Rate", GREEN_B, cursor_y)
        self.play(FadeIn(h3, shift=UP * 0.08))

        cursor_y -= 0.60
        eq_tc = _math(
            rf"T_{{c,\min}} \geq T_{{crit}} = {CRITICAL_PATH_PS}\text{{ ps}}",
            26, cursor_y,
        )
        self.play(Write(eq_tc))
        self.wait(0.4)

        cursor_y -= 0.60
        eq_f1 = _math(
            rf"f_{{max}} = \frac{{1}}{{{CRITICAL_PATH_PS} \times 10^{{-12}}\text{{ s}}}}",
            26, cursor_y,
        )
        self.play(Write(eq_f1))
        self.wait(0.5)

        cursor_y -= 0.78
        eq_result = _math(
            rf"f_{{max}} = {f_ghz}\text{{ GHz}}",
            42, cursor_y, color=YELLOW,
        )
        result_box = SurroundingRectangle(
            eq_result, color=YELLOW, stroke_width=2.5, buff=0.20, corner_radius=0.10,
        )
        self.play(Write(eq_result), Create(result_box))
        self.play(Indicate(eq_result, scale_factor=1.08, color=YELLOW), run_time=0.9)

        cursor_y -= 0.72
        note_clk = (
            Text(
                f"The clock period must be ≥ {CRITICAL_PATH_PS} ps\n"
                f"so lw has time to complete.",
                font_size=13, color=GRAY_A, line_spacing=1.3,
            )
            .move_to(np.array([right_x, cursor_y, 0]))
        )
        self.play(FadeIn(note_clk))
        self.wait(2)
