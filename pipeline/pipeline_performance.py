import numpy as np
from manim import *

config.frame_width  = 28.0
config.frame_height = 15.75

STAGE_NAMES  = ["IF", "ID", "EX", "MEM", "WB"]
STAGE_COLORS = [BLUE_C, PURPLE_C, GREEN_C, ORANGE, TEAL_C]

# Textbook-style stage latencies in nanoseconds
STAGE_NS = [250, 350, 150, 300, 200]
TOTAL_NS = sum(STAGE_NS)        # 1250 ns single-cycle clock period
MAX_NS   = max(STAGE_NS)        # 350 ns  bottleneck stage
PIPE_REG_OVERHEAD = 20          # pipeline register overhead in ns
PIPE_CLK = MAX_NS + PIPE_REG_OVERHEAD   # 370 ns effective pipelined clock

BG_DARK  = "#111111"

class PipelinePerformanceScene(Scene):
    """Full performance analysis of a 5-stage RISC-V pipeline."""

    def construct(self):
        self.camera.background_color = BG_DARK
        self._section_title()
        self._section_stage_latencies()
        self._section_single_cycle_clock()
        self._section_pipelined_clock()
        self._section_timing_diagram()
        self._section_throughput()
        self._section_speedup()
        self._section_min_clock_rate()
        self._section_hazards()
        self._section_summary()
        self.wait(2)

    def _clear(self, *mobs, fade=True):
        """Fade-out & remove a list of mobjects."""
        if fade and mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=0.4)
        for m in mobs:
            self.remove(m)

    def _header(self, text, color=WHITE):
        h = Text(text, font_size=36, color=color, weight=BOLD)
        h.to_edge(UP, buff=0.55)
        return h

    def _subheader(self, text, ref, color=GRAY_A):
        s = Text(text, font_size=22, color=color)
        s.next_to(ref, DOWN, buff=0.15)
        return s

    def _section_title(self):
        title = Text(
            "Pipeline Performance Analysis",
            font_size=48, color=WHITE, weight=BOLD,
        ).move_to(UP * 0.6)
        sub = Text(
            "RISC-V 5-Stage Pipeline  —  Quantifying the Speed-Up",
            font_size=26, color=GRAY_A,
        ).next_to(title, DOWN, buff=0.25)

        self.play(Write(title), run_time=0.6)
        self.play(FadeIn(sub), run_time=0.4)
        self.wait(1.2)
        self._clear(title, sub)

    def _section_stage_latencies(self):
        hdr = self._header("① Stage Latencies")
        shdr = self._subheader(
            "Each stage takes a different amount of time (nanoseconds)",
            hdr,
        )
        self.play(Write(hdr), FadeIn(shdr), run_time=0.5)

        max_w = 4.5
        bar_h = 0.75
        start_y = 2.0
        gap = 1.15
        x_left = -4.0

        bars = VGroup()
        labels = VGroup()
        ns_labels = VGroup()

        for i, (name, ns, col) in enumerate(zip(STAGE_NAMES, STAGE_NS, STAGE_COLORS)):
            w = max_w * ns / MAX_NS
            y = start_y - i * gap

            bar = Rectangle(
                width=w, height=bar_h,
                fill_color=col, fill_opacity=0.65,
                stroke_color=col, stroke_width=1.5,
            )
            bar.move_to([x_left + w / 2, y, 0])

            name_lbl = Text(name, font_size=26, color=col, weight=BOLD)
            name_lbl.next_to(bar, LEFT, buff=0.35)

            ns_lbl = Text(f"{ns} ns", font_size=24, color=WHITE)
            ns_lbl.next_to(bar, RIGHT, buff=0.30)

            bars.add(bar)
            labels.add(name_lbl)
            ns_labels.add(ns_lbl)

        self.play(
            LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.15),
            LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.15),
            run_time=1.0,
        )
        self.play(
            LaggedStart(*[FadeIn(n) for n in ns_labels], lag_ratio=0.1),
            run_time=0.6,
        )

        slowest_idx = STAGE_NS.index(MAX_NS)
        star = Text(
            f"★ Slowest stage: {STAGE_NAMES[slowest_idx]} = {MAX_NS} ns  →  determines pipelined clock",
            font_size=22, color=YELLOW, weight=BOLD,
        ).next_to(bars, DOWN, buff=0.70)

        self.play(
            bars[slowest_idx].animate.set(stroke_width=4, stroke_color=YELLOW),
            FadeIn(star),
            run_time=0.5,
        )

        total_txt = Text(
            f"Total (all stages) = {TOTAL_NS} ns  →  single-cycle clock period",
            font_size=22, color=RED_B,
        ).next_to(star, DOWN, buff=0.25)
        self.play(FadeIn(total_txt), run_time=0.4)

        self.wait(2.0)
        self._clear(hdr, shdr, bars, labels, ns_labels, star, total_txt)

    # 2.  SINGLE-CYCLE CLOCK PERIOD

    def _section_single_cycle_clock(self):
        hdr = self._header("② Single-Cycle Clock Period", color=RED_B)
        self.play(Write(hdr), run_time=0.4)

        bar_h = 1.0
        total_w = 18.0
        x_start = -total_w / 2
        y_bar = 1.8

        blocks = VGroup()
        for i, (name, ns, col) in enumerate(zip(STAGE_NAMES, STAGE_NS, STAGE_COLORS)):
            w = total_w * ns / TOTAL_NS
            prev_w = sum(STAGE_NS[:i]) / TOTAL_NS * total_w
            bx = x_start + prev_w + w / 2

            block = Rectangle(
                width=w, height=bar_h,
                fill_color=col, fill_opacity=0.55,
                stroke_color=col, stroke_width=1.5,
            ).move_to([bx, y_bar, 0])

            lbl = VGroup(
                Text(name, font_size=20, color=WHITE, weight=BOLD),
                Text(f"{ns} ns", font_size=17, color=GRAY_A),
            ).arrange(DOWN, buff=0.05).move_to(block)

            blocks.add(VGroup(block, lbl))

        self.play(
            LaggedStart(*[FadeIn(b) for b in blocks], lag_ratio=0.12),
            run_time=0.8,
        )

        full_bar = VGroup(*[b[0] for b in blocks])
        brace = Brace(full_bar, DOWN, color=RED_B)
        brace_lbl = brace.get_tex(
            r"T_{\text{clk,single}} = " + f"{TOTAL_NS}" + r"\text{{ ns}}"
        ).set_color(RED_B).scale(0.9)

        self.play(GrowFromCenter(brace), Write(brace_lbl), run_time=0.6)

        formula = MathTex(
            r"T_{\text{clk,single}}",
            r"=",
            r"\sum_{i=1}^{5} t_i",
            r"=",
            " + ".join(str(n) for n in STAGE_NS),
            r"=",
            f"{TOTAL_NS}" + r"\text{ ns}",
            font_size=34,
        ).next_to(brace_lbl, DOWN, buff=0.65)
        formula[0].set_color(RED_B)
        formula[-1].set_color(RED_B)

        self.play(Write(formula), run_time=0.8)

        exec_eq = MathTex(
            r"T_{\text{exec}}",
            r"= N \times T_{\text{clk}}",
            r"= N \times",
            f"{TOTAL_NS}" + r"\text{ ns}",
            font_size=32, color=GRAY_A,
        ).next_to(formula, DOWN, buff=0.50)
        exec_eq[0].set_color(WHITE)

        note = Text(
            "Every instruction must wait for ALL stages — even if some finish early.",
            font_size=20, color=GRAY_B,
        ).next_to(exec_eq, DOWN, buff=0.40)

        self.play(Write(exec_eq), run_time=0.6)
        self.play(FadeIn(note), run_time=0.3)

        self.wait(2.0)
        self._clear(hdr, blocks, brace, brace_lbl, formula, exec_eq, note)

    # 3.  PIPELINED CLOCK PERIOD

    def _section_pipelined_clock(self):
        hdr = self._header("③ Pipelined Clock Period", color=GREEN_B)
        self.play(Write(hdr), run_time=0.4)

        bar_h = 1.0
        block_w = 3.2
        gap = 0.20
        total_w = 5 * block_w + 4 * gap
        x_start = -total_w / 2
        y_bar = 2.0

        blocks = VGroup()
        for i, (name, ns, col) in enumerate(zip(STAGE_NAMES, STAGE_NS, STAGE_COLORS)):
            bx = x_start + i * (block_w + gap) + block_w / 2
            block = Rectangle(
                width=block_w, height=bar_h,
                fill_color=col, fill_opacity=0.55,
                stroke_color=col, stroke_width=1.5,
            ).move_to([bx, y_bar, 0])

            lbl = VGroup(
                Text(name, font_size=22, color=WHITE, weight=BOLD),
                Text(f"{ns} ns", font_size=18, color=GRAY_A),
            ).arrange(DOWN, buff=0.05).move_to(block)

            blocks.add(VGroup(block, lbl))

        self.play(FadeIn(blocks), run_time=0.5)

        slowest_idx = STAGE_NS.index(MAX_NS)
        self.play(
            blocks[slowest_idx][0].animate.set(stroke_width=4, stroke_color=YELLOW),
            run_time=0.4,
        )

        f1 = MathTex(
            r"T_{\text{clk,pipe}}",
            r"= \max(t_i)",
            r"+ t_{\text{reg}}",
            font_size=36,
        ).move_to([0, 0.15, 0])
        f1[0].set_color(GREEN_B)

        f2 = MathTex(
            r"=",
            f"{MAX_NS}",
            r"+",
            f"{PIPE_REG_OVERHEAD}",
            r"=",
            f"{PIPE_CLK}" + r"\text{ ns}",
            font_size=36,
        ).next_to(f1, DOWN, buff=0.30)
        f2[1].set_color(YELLOW)
        f2[3].set_color(GRAY_A)
        f2[-1].set_color(GREEN_B)

        self.play(Write(f1), run_time=0.6)
        self.play(Write(f2), run_time=0.6)

        overhead_note = Text(
            f"Pipeline register overhead:  {PIPE_REG_OVERHEAD} ns  (setup + propagation delay of flip-flops)",
            font_size=20, color=GRAY_B,
        ).next_to(f2, DOWN, buff=0.50)
        self.play(FadeIn(overhead_note), run_time=0.3)

        insight = VGroup(
            Text("Key insight:", font_size=24, color=YELLOW, weight=BOLD),
            Text(
                f"Clock is {TOTAL_NS / PIPE_CLK:.1f}x shorter than single-cycle"
                f"  ({PIPE_CLK} ns vs {TOTAL_NS} ns)",
                font_size=22, color=WHITE,
            ),
        ).arrange(RIGHT, buff=0.3).next_to(overhead_note, DOWN, buff=0.40)

        self.play(FadeIn(insight), run_time=0.4)
        self.wait(2.0)
        self._clear(hdr, blocks, f1, f2, overhead_note, insight)

    # 4.  PIPELINE TIMING DIAGRAM  (Gantt chart)

    def _section_timing_diagram(self):
        hdr = self._header("④ Pipeline Timing Diagram")
        shdr = self._subheader("5 instructions flowing through 5 stages", hdr)
        self.play(Write(hdr), FadeIn(shdr), run_time=0.5)

        n_instr = 5
        n_stages = 5
        cell_w = 1.70
        cell_h = 0.65
        x_origin = -8.5
        y_origin = 2.2

        row_labels = VGroup()
        for i in range(n_instr):
            lbl = Text(f"Instr {i+1}", font_size=18, color=WHITE)
            lbl.move_to([x_origin - 1.2, y_origin - i * cell_h, 0])
            row_labels.add(lbl)

        total_cols = n_instr + n_stages - 1   # 9 cycles
        col_headers = VGroup()
        for c in range(total_cols):
            lbl = Text(f"CC{c+1}", font_size=16, color=GRAY_B)
            lbl.move_to([x_origin + c * cell_w + cell_w / 2,
                         y_origin + cell_h * 0.75, 0])
            col_headers.add(lbl)

        self.play(FadeIn(row_labels), FadeIn(col_headers), run_time=0.4)

        all_cells = VGroup()
        for i in range(n_instr):
            for s in range(n_stages):
                col = i + s
                cx = x_origin + col * cell_w + cell_w / 2
                cy = y_origin - i * cell_h

                rect = Rectangle(
                    width=cell_w * 0.92, height=cell_h * 0.85,
                    fill_color=STAGE_COLORS[s], fill_opacity=0.6,
                    stroke_color=STAGE_COLORS[s], stroke_width=1.2,
                ).move_to([cx, cy, 0])

                txt = Text(STAGE_NAMES[s], font_size=16, color=WHITE, weight=BOLD)
                txt.move_to(rect)

                all_cells.add(VGroup(rect, txt))

        # Animate row by row (each instruction enters one cycle later)
        for i in range(n_instr):
            row_cells = VGroup(*all_cells[i * n_stages : (i + 1) * n_stages])
            self.play(
                LaggedStart(*[FadeIn(c) for c in row_cells], lag_ratio=0.18),
                run_time=0.55,
            )

        last_row_y = y_origin - (n_instr - 1) * cell_h
        ss_start_col = n_stages - 1   # column 4 (CC5)
        ax_start = x_origin + ss_start_col * cell_w + cell_w / 2
        ax_end   = x_origin + (total_cols - 1) * cell_w + cell_w / 2
        arr_y    = last_row_y - cell_h * 0.7

        arr = Arrow(
            [ax_start, arr_y, 0],
            [ax_end, arr_y, 0],
            color=GREEN_B, stroke_width=2, tip_length=0.15, buff=0,
        )
        arr_lbl = Text(
            "Steady state: 1 result per cycle",
            font_size=20, color=GREEN_B, weight=BOLD,
        ).next_to(arr, DOWN, buff=0.15)

        self.play(GrowArrow(arr), FadeIn(arr_lbl), run_time=0.5)

        # Fill / drain note
        fill_note = Text(
            f"Fill: {n_stages-1} cycles  |  Drain: {n_stages-1} cycles  |  "
            f"Total for {n_instr} instr: {n_instr + n_stages - 1} cycles",
            font_size=19, color=GRAY_A,
        ).next_to(arr_lbl, DOWN, buff=0.30)
        self.play(FadeIn(fill_note), run_time=0.3)

        self.wait(2.5)
        self._clear(hdr, shdr, row_labels, col_headers, all_cells, arr, arr_lbl, fill_note)

    # 5.  THROUGHPUT & EXECUTION TIME

    def _section_throughput(self):
        hdr = self._header("⑤ Throughput & Execution Time")
        self.play(Write(hdr), run_time=0.4)

        sc_eq = MathTex(
            r"T_{\text{single}}",
            r"= N \times",
            f"{TOTAL_NS}" + r"\text{ ns}",
            font_size=34, color=RED_B,
        ).move_to([0, 2.2, 0])

        pipe_eq = MathTex(
            r"T_{\text{pipe}}",
            r"= \bigl(",
            r"N + (k-1)",
            r"\bigr) \times",
            f"{PIPE_CLK}" + r"\text{ ns}",
            font_size=34, color=GREEN_B,
        ).next_to(sc_eq, DOWN, buff=0.50)

        k_note = Text(
            "k = number of pipeline stages = 5",
            font_size=20, color=GRAY_B,
        ).next_to(pipe_eq, DOWN, buff=0.20)

        self.play(Write(sc_eq), run_time=0.5)
        self.play(Write(pipe_eq), run_time=0.5)
        self.play(FadeIn(k_note), run_time=0.3)

        N = 1000
        t_sc  = N * TOTAL_NS
        t_pip = (N + 4) * PIPE_CLK

        example_hdr = Text(
            f"Example:  N = {N} instructions",
            font_size=24, color=YELLOW, weight=BOLD,
        ).next_to(k_note, DOWN, buff=0.55)

        sc_val = Text(
            f"Single-cycle:  {N} x {TOTAL_NS} = {t_sc:,} ns  =  {t_sc/1e6:.2f} ms",
            font_size=22, color=RED_B,
        ).next_to(example_hdr, DOWN, buff=0.25)

        pip_val = Text(
            f"Pipelined:  ({N} + 4) x {PIPE_CLK} = {t_pip:,} ns  =  {t_pip/1e6:.3f} ms",
            font_size=22, color=GREEN_B,
        ).next_to(sc_val, DOWN, buff=0.18)

        ratio = t_sc / t_pip
        speedup_txt = Text(
            f"->  {ratio:.2f}x faster",
            font_size=26, color=YELLOW, weight=BOLD,
        ).next_to(pip_val, DOWN, buff=0.35)

        self.play(FadeIn(example_hdr), run_time=0.3)
        self.play(Write(sc_val), run_time=0.4)
        self.play(Write(pip_val), run_time=0.4)
        self.play(FadeIn(speedup_txt), run_time=0.4)

        self.wait(2.0)
        self._clear(hdr, sc_eq, pipe_eq, k_note,
                    example_hdr, sc_val, pip_val, speedup_txt)

    # 6.  SPEEDUP FORMULA

    def _section_speedup(self):
        hdr = self._header("⑥ Speedup", color=YELLOW)
        self.play(Write(hdr), run_time=0.4)

        gen = MathTex(
            r"\text{Speedup}",
            r"= \frac{T_{\text{single}}}{T_{\text{pipe}}}",
            r"= \frac{N \cdot T_{\text{clk,single}}}"
            r"{(N + k - 1) \cdot T_{\text{clk,pipe}}}",
            font_size=36,
        ).move_to([0, 2.0, 0])
        gen[0].set_color(YELLOW)

        self.play(Write(gen), run_time=0.8)

        limit = MathTex(
            r"\lim_{N \to \infty} \text{Speedup}",
            r"= \frac{T_{\text{clk,single}}}{T_{\text{clk,pipe}}}",
            r"= \frac{" + f"{TOTAL_NS}" + r"}{" + f"{PIPE_CLK}" + r"}",
            r"\approx",
            f"{TOTAL_NS / PIPE_CLK:.2f}",
            font_size=34,
        ).next_to(gen, DOWN, buff=0.60)
        limit[0].set_color(GRAY_A)
        limit[-1].set_color(GREEN_B)

        self.play(Write(limit), run_time=0.7)

        ideal = MathTex(
            r"\text{Ideal (balanced stages, no overhead): Speedup} = k = 5",
            font_size=28, color=TEAL_C,
        ).next_to(limit, DOWN, buff=0.55)

        actual = Text(
            f"Actual < ideal because stages are unbalanced and register overhead adds {PIPE_REG_OVERHEAD} ns",
            font_size=20, color=GRAY_A,
        ).next_to(ideal, DOWN, buff=0.25)

        self.play(Write(ideal), run_time=0.5)
        self.play(FadeIn(actual), run_time=0.3)

        self.wait(2.0)
        self._clear(hdr, gen, limit, ideal, actual)

    # 7.  MINIMUM CLOCK RATE / FREQUENCY

    def _section_min_clock_rate(self):
        hdr = self._header("⑦ Minimum Clock Rate", color=BLUE_B)
        self.play(Write(hdr), run_time=0.4)

        sc_title = Text("Single-Cycle", font_size=26, color=RED_B, weight=BOLD)
        sc_title.move_to([-6, 2.3, 0])

        sc_f = MathTex(
            r"f_{\text{single}}",
            r"= \frac{1}{T_{\text{clk}}}",
            r"= \frac{1}{" + f"{TOTAL_NS}" + r" \times 10^{-9}}",
            font_size=30,
        ).next_to(sc_title, DOWN, buff=0.30, aligned_edge=LEFT)
        sc_f[0].set_color(RED_B)

        sc_mhz = 1e3 / TOTAL_NS
        sc_result = MathTex(
            r"= " + f"{sc_mhz:.0f}" + r"\text{{ MHz}}",
            font_size=30, color=RED_B,
        ).next_to(sc_f, DOWN, buff=0.20, aligned_edge=LEFT)

        pipe_title = Text("Pipelined", font_size=26, color=GREEN_B, weight=BOLD)
        pipe_title.move_to([4, 2.3, 0])

        pipe_f = MathTex(
            r"f_{\text{pipe}}",
            r"= \frac{1}{T_{\text{clk}}}",
            r"= \frac{1}{" + f"{PIPE_CLK}" + r" \times 10^{-9}}",
            font_size=30,
        ).next_to(pipe_title, DOWN, buff=0.30, aligned_edge=LEFT)
        pipe_f[0].set_color(GREEN_B)

        pipe_mhz = 1e3 / PIPE_CLK
        pipe_result = MathTex(
            r"\approx " + f"{pipe_mhz:.0f}" + r"\text{{ MHz}}",
            font_size=30, color=GREEN_B,
        ).next_to(pipe_f, DOWN, buff=0.20, aligned_edge=LEFT)

        self.play(
            FadeIn(sc_title), Write(sc_f), run_time=0.5,
        )
        self.play(Write(sc_result), run_time=0.4)
        self.play(
            FadeIn(pipe_title), Write(pipe_f), run_time=0.5,
        )
        self.play(Write(pipe_result), run_time=0.4)

        comp = Text(
            f"Pipeline runs at {pipe_mhz:.0f} MHz vs {sc_mhz:.0f} MHz  "
            f"->  {pipe_mhz / sc_mhz:.1f}x higher clock rate",
            font_size=24, color=YELLOW, weight=BOLD,
        ).move_to([0, -1.6, 0])
        self.play(FadeIn(comp), run_time=0.4)

        meaning = Text(
            "\"Minimum clock rate\" = the slowest you can clock the processor\n"
            "and still execute one instruction per cycle (pipelined) or per period (single-cycle).",
            font_size=18, color=GRAY_B, line_spacing=1.4,
        ).next_to(comp, DOWN, buff=0.40)
        self.play(FadeIn(meaning), run_time=0.3)

        self.wait(2.5)
        self._clear(hdr, sc_title, sc_f, sc_result,
                    pipe_title, pipe_f, pipe_result, comp, meaning)

    # 8.  HAZARDS & STALLS  (real-world penalty)

    def _section_hazards(self):
        hdr = self._header("⑧ Real-World: Hazards & Stalls", color=ORANGE)
        self.play(Write(hdr), run_time=0.4)

        hazards = [
            ("Data hazard",
             "Instruction needs a result not yet\n"
             "written back -> forwarding resolves\n"
             "most; load-use needs 1-cycle stall",
             BLUE_C),
            ("Control hazard",
             "Branch outcome unknown until EX\n"
             "stage -> branch prediction or\n"
             "1-2 cycle flush penalty",
             GREEN_C),
            ("Structural hazard",
             "Two instructions need the same\n"
             "hardware unit -> rare in RISC-V\n"
             "(separate I-mem / D-mem)",
             PURPLE_C),
        ]

        cards = VGroup()
        for i, (title, desc, col) in enumerate(hazards):
            card = VGroup()
            bg = RoundedRectangle(
                width=7.5, height=2.6,
                fill_color=col, fill_opacity=0.10,
                stroke_color=col, stroke_width=1.5,
                corner_radius=0.15,
            )
            t = Text(title, font_size=24, color=col, weight=BOLD)
            t.next_to(bg.get_top(), DOWN, buff=0.25)
            d = Text(desc, font_size=18, color=GRAY_A, line_spacing=1.3)
            d.next_to(t, DOWN, buff=0.15)
            card.add(bg, t, d)
            cards.add(card)

        cards.arrange(RIGHT, buff=0.50).move_to([0, 1.2, 0])

        self.play(
            LaggedStart(*[FadeIn(c) for c in cards], lag_ratio=0.25),
            run_time=1.0,
        )

        cpi_eq = MathTex(
            r"\text{CPI}_{\text{eff}}",
            r"= 1 + \text{stall cycles per instruction}",
            font_size=30,
        ).move_to([0, -1.2, 0])
        cpi_eq[0].set_color(ORANGE)

        example = Text(
            "Example:  20% loads (1-cycle stall) + 15% branches (1-cycle penalty)\n"
            "CPI = 1 + 0.20 x 1 + 0.15 x 1 = 1.35",
            font_size=20, color=GRAY_A, line_spacing=1.4,
        ).next_to(cpi_eq, DOWN, buff=0.35)

        real_speedup = TOTAL_NS / (PIPE_CLK * 1.35)
        real_txt = Text(
            f"Real speedup = {TOTAL_NS}/{PIPE_CLK} / 1.35 = {real_speedup:.2f}x  (down from {TOTAL_NS/PIPE_CLK:.2f}x)",
            font_size=22, color=YELLOW,
        ).next_to(example, DOWN, buff=0.30)

        self.play(Write(cpi_eq), run_time=0.5)
        self.play(FadeIn(example), run_time=0.4)
        self.play(FadeIn(real_txt), run_time=0.4)

        self.wait(2.5)
        self._clear(hdr, cards, cpi_eq, example, real_txt)

    # 9.  SUMMARY TABLE

    def _section_summary(self):
        hdr = self._header("⑨ Summary Comparison")
        self.play(Write(hdr), run_time=0.4)

        sc_mhz  = 1e3 / TOTAL_NS
        pip_mhz = 1e3 / PIPE_CLK

        rows_data = [
            ("Metric",          "Single-Cycle",           "Pipelined (5-stage)"),
            ("Clock period",    f"{TOTAL_NS} ns",         f"{PIPE_CLK} ns"),
            ("Clock rate",      f"{sc_mhz:.0f} MHz",      f"{pip_mhz:.0f} MHz"),
            ("CPI",             "1",                       "1  (ideal)"),
            ("Throughput",      f"{sc_mhz:.0f} MIPS",     f"{pip_mhz:.0f} MIPS"),
            ("Speedup",         "1x",                     f"~{TOTAL_NS/PIPE_CLK:.2f}x"),
            ("Latency / instr", f"{TOTAL_NS} ns",         f"{5 * PIPE_CLK} ns"),
        ]

        n_rows = len(rows_data)
        col_w  = [4.5, 5.0, 5.0]
        row_h  = 0.70
        x0     = -sum(col_w) / 2
        y0     = 2.2

        table_grp = VGroup()

        for r, row in enumerate(rows_data):
            cx = x0
            for c, cell in enumerate(row):
                w = col_w[c]
                y = y0 - r * row_h

                bg_col = DARK_GRAY if r == 0 else (
                    "#1a1a1a" if r % 2 == 0 else "#222222"
                )
                rect = Rectangle(
                    width=w, height=row_h,
                    fill_color=bg_col, fill_opacity=0.8,
                    stroke_color=GRAY, stroke_width=0.6,
                ).move_to([cx + w / 2, y, 0])

                if r == 0:
                    txt = Text(cell, font_size=20, color=WHITE, weight=BOLD)
                elif c == 1:
                    txt = Text(cell, font_size=19, color=RED_B)
                elif c == 2:
                    txt = Text(cell, font_size=19, color=GREEN_B)
                else:
                    txt = Text(cell, font_size=19, color=WHITE)

                txt.move_to(rect)
                table_grp.add(VGroup(rect, txt))
                cx += w

        self.play(
            LaggedStart(*[FadeIn(c) for c in table_grp], lag_ratio=0.02),
            run_time=1.2,
        )

        takeaway = VGroup(
            Text("Takeaway:", font_size=24, color=YELLOW, weight=BOLD),
            Text(
                "Pipelining doesn't reduce latency — it increases throughput by overlapping instructions.",
                font_size=22, color=WHITE,
            ),
        ).arrange(RIGHT, buff=0.3).next_to(table_grp, DOWN, buff=0.60)

        self.play(FadeIn(takeaway), run_time=0.5)
        self.wait(3.0)
        self._clear(hdr, table_grp, takeaway)