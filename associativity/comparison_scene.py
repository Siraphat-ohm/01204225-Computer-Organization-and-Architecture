from manim import *
from constants import *
from logic import (
    AssocCacheConfig, COMPARE_SEQ,
    DM_CFG, CMP_2WAY_CFG, CMP_4WAY_CFG,
    NWayLRUSimulator, split_assoc_address,
)


def _simulate_all(seq, configs):
    """Run sequence through each config; return list of (is_hit, ...) per config."""
    sims = [NWayLRUSimulator(c.num_sets, c.ways) for c in configs]
    results = []          # results[step] = [result_dm, result_2way, result_4way]
    for addr in seq:
        row = []
        for cfg, sim in zip(configs, sims):
            split   = split_assoc_address(addr, cfg)
            is_hit, *_ = sim.access(split["set_index"], split["tag"])
            row.append(is_hit)
        results.append(row)
    return results


class ComparisonScene(Scene):
    """Compares Direct Map, 2-Way, and 4-Way caches on the same access sequence.

    Layout
    ------
    Title + subtitle sequence
    Three columns: DM | 2-Way | 4-Way
      Each column: config info (small) + animated HIT/MISS squares
    Bottom: bar chart showing final hit rates
    """

    CONFIGS  = [DM_CFG, CMP_2WAY_CFG, CMP_4WAY_CFG]
    COL_X    = [-4.2, 0.0, 4.2]
    COL_NAMES = ["Direct Map\n(1-Way, 8 Sets)", "2-Way\n(4 Sets)", "4-Way\n(2 Sets)"]
    COL_COLORS = [RED_B, YELLOW_B, GREEN_B]

    def construct(self):
        title = Text(
            "Cache Associativity Comparison", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.18)
        self.add(title)

        seq_text = Text(
            "Sequence: " + "  ".join(str(a) for a in COMPARE_SEQ),
            font_size=FS_SMALL, color=GRAY_B,
        ).next_to(title, DOWN, buff=0.12)
        self.add(seq_text)
        note = Text(
            "Addresses 0, 32, 64 all conflict in Direct Map (same block index 0)",
            font_size=FS_SMALL - 2, color=ORANGE,
        ).next_to(seq_text, DOWN, buff=0.08)
        self.add(note)

        headers = []
        for name, cx, col_color in zip(self.COL_NAMES, self.COL_X, self.COL_COLORS):
            h = Text(name, font_size=FS_SMALL, color=col_color)
            h.move_to([cx, 2.2, 0])
            self.add(h)
            headers.append(h)

        infos = []
        for cfg, cx in zip(self.CONFIGS, self.COL_X):
            info = Text(
                f"Sets={cfg.num_sets}  Tag={cfg.tag_bits}b  Idx={cfg.index_bits}b",
                font_size=FS_SMALL - 2, color=GRAY_B,
            ).move_to([cx, 1.7, 0])
            self.add(info)
            infos.append(info)

        all_results = _simulate_all(COMPARE_SEQ, self.CONFIGS)

        SQUARE_SIZE = 0.42
        SQUARE_BUFF = 0.08
        START_Y     = 1.2

        grid_squares = []
        addr_labels  = []

        for step, (addr, row_hits) in enumerate(zip(COMPARE_SEQ, all_results)):
            y = START_Y - step * (SQUARE_SIZE + SQUARE_BUFF)
            # Address label on far left
            albl = Text(str(addr), font_size=FS_SMALL - 2, color=GRAY_B)
            albl.move_to([-6.2, y, 0])
            self.add(albl)
            addr_labels.append(albl)

            row_squares = []
            for is_hit, cx in zip(row_hits, self.COL_X):
                sq = Square(side_length=SQUARE_SIZE)
                sq.set_fill(GREEN if is_hit else RED_B, opacity=0.0)
                sq.set_stroke(GRAY_D, width=1)
                sq.move_to([cx, y, 0])
                row_squares.append(sq)
                self.add(sq)
            grid_squares.append(row_squares)

        hit_counts = [0] * 3
        rate_mobjs = []
        for col_idx, cx in enumerate(self.COL_X):
            rm = Text("0 / 0  (—%)", font_size=FS_SMALL, color=GRAY_B)
            rm.move_to([cx, START_Y - len(COMPARE_SEQ) * (SQUARE_SIZE + SQUARE_BUFF) - 0.4, 0])
            self.add(rm)
            rate_mobjs.append(rm)

        for step, (addr, row_hits) in enumerate(zip(COMPARE_SEQ, all_results)):
            anims = []
            for col_idx, (is_hit, sq) in enumerate(zip(row_hits, grid_squares[step])):
                anims.append(sq.animate.set_fill(
                    GREEN if is_hit else RED_B, opacity=0.75
                ))
                if is_hit:
                    hit_counts[col_idx] += 1

            new_rates = []
            for col_idx in range(3):
                total = step + 1
                h     = hit_counts[col_idx]
                pct   = h / total * 100
                color = GREEN if h > 0 else RED_B
                nr = Text(
                    f"{h} / {total}  ({pct:.0f}%)",
                    font_size=FS_SMALL, color=color,
                ).move_to(rate_mobjs[col_idx])
                new_rates.append(nr)

            anims += [Transform(rate_mobjs[ci], new_rates[ci]) for ci in range(3)]
            self.play(*anims, run_time=0.5)
            self.wait(0.3)

        self.wait(0.8)

        grid_all    = VGroup(*[sq for row in grid_squares for sq in row],
                              *addr_labels, *rate_mobjs)
        top_overlay = VGroup(*headers, *infos, seq_text, note)
        self.play(
            grid_all.animate.shift(UP * 8).set_opacity(0),
            FadeOut(top_overlay),
            run_time=0.8,
        )

        chart_title = Text("Final Hit Rates", font_size=FS_SECTION, color=YELLOW_B)
        chart_title.next_to(title, DOWN, buff=0.2)
        self.play(FadeIn(chart_title))
        final_rates = [hit_counts[i] / len(COMPARE_SEQ) for i in range(3)]
        MAX_H       = 3.5
        BAR_W       = 1.4
        BASE_Y      = -1.8
        BAR_X       = [-3.2, 0.0, 3.2]

        bars = []
        for i, (rate, cx, col_color) in enumerate(
            zip(final_rates, BAR_X, self.COL_COLORS)
        ):
            bar_h = max(rate * MAX_H, 0.05)
            bar   = Rectangle(width=BAR_W, height=bar_h, color=col_color, fill_opacity=0.7)
            bar.move_to([cx, BASE_Y + bar_h / 2, 0])

            pct_lbl = Text(f"{rate*100:.0f}%", font_size=FS_SECTION, color=col_color)
            pct_lbl.next_to(bar, UP, buff=0.12)

            name_lbl = Text(
                ["Direct Map", "2-Way", "4-Way"][i],
                font_size=FS_SMALL, color=col_color,
            )
            name_lbl.next_to(bar, DOWN, buff=0.12)

            bars.append(VGroup(bar, pct_lbl, name_lbl))

        # Baseline
        baseline = Line(
            [BAR_X[0] - BAR_W / 2 - 0.3, BASE_Y, 0],
            [BAR_X[-1] + BAR_W / 2 + 0.3, BASE_Y, 0],
            color=GRAY_D,
        )
        self.play(Create(baseline))
        for b in bars:
            self.play(FadeIn(b), run_time=0.5)

        winner_idx  = int(max(range(3), key=lambda i: final_rates[i]))
        winner_ring = SurroundingRectangle(
            bars[winner_idx], color=YELLOW, buff=0.15, corner_radius=0.08
        )
        winner_note = Text("Most hits with same cache size!", font_size=FS_SMALL, color=YELLOW)
        winner_note.next_to(winner_ring, UP, buff=0.2)
        self.play(Create(winner_ring), FadeIn(winner_note))
        self.wait(3)
