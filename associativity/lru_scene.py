from manim import *
from constants import *


# ── Helper: single cache-way box ──────────────────────────────────────────────

def _way_box(label: str, content: str, content_color=WHITE):
    """Return a VGroup: titled rectangle showing content."""
    rect = Rectangle(width=2.2, height=1.1, color=GRAY_B, fill_opacity=0.15)
    title = Text(label, font_size=FS_SMALL, color=YELLOW_B).next_to(rect, UP, buff=0.08)
    text  = Text(content, font_size=FS_BODY, color=content_color)
    return VGroup(rect, title, text)


class LRUScene(Scene):
    """Scene: Explain the LRU (Least Recently Used) replacement policy.

    Walks through a 2-way cache set with 5 accesses, showing
    how the LRU pointer moves and which entry gets evicted.
    """

    # Symbolic names for the demo addresses
    ADDRS = [("A", 0, BLUE_B), ("B", 16, GREEN_B), ("C", 32, ORANGE)]

    def construct(self):
        title = Text(
            "LRU Replacement Policy", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.2)
        subtitle = Text(
            "When the cache set is full, evict the Least Recently Used entry.",
            font_size=FS_SMALL, color=GRAY_B,
        ).next_to(title, DOWN, buff=0.12)
        self.add(title, subtitle)

        set_label = Text("Cache Set  (2 ways)", font_size=FS_SECTION, color=YELLOW_B)
        set_label.move_to([0, 1.9, 0])
        self.add(set_label)

        way0 = self._make_way(0, "EMPTY", GRAY_B)
        way1 = self._make_way(1, "EMPTY", GRAY_B)
        ways = VGroup(way0, way1).arrange(RIGHT, buff=0.6).move_to([0, 0.5, 0])
        self.add(ways)

        lru_bar = self._make_lru_bar(["Way 0", "Way 1"])
        lru_bar.move_to([0, -0.9, 0])
        self.add(lru_bar)

        lru_l = Text("LRU ←", font_size=FS_SMALL, color=RED).next_to(lru_bar, LEFT, buff=0.2)
        mru_r = Text("→ MRU", font_size=FS_SMALL, color=GREEN).next_to(lru_bar, RIGHT, buff=0.2)
        self.add(lru_l, mru_r)

        log_title = Text("Access Log", font_size=FS_SMALL, color=YELLOW_B)
        log_title.move_to([4.5, 1.5, 0])
        self.add(log_title)
        self._log_mobjs = []
        self._log_y     = 1.0

        self._log_entry("Access A (addr 0)", color=BLUE_B)
        self.wait(0.3)

        new_way0 = self._make_way(0, "A  (tag=0)", BLUE_B).move_to(way0)
        self.play(
            ReplacementTransform(way0, new_way0),
            run_time=0.7,
        )
        way0 = new_way0
        miss_t = self._result_text("MISS (Compulsory)", RED).next_to(ways, DOWN, buff=0.35)
        self.play(FadeIn(miss_t))

        new_bar = self._make_lru_bar(["Way 1", "Way 0"]).move_to(lru_bar)
        self.play(Transform(lru_bar, new_bar))
        self.wait(0.8)
        self.play(FadeOut(miss_t))

        self._log_entry("Access B (addr 16)", color=GREEN_B)
        self.wait(0.3)

        new_way1 = self._make_way(1, "B  (tag=1)", GREEN_B).move_to(way1)
        self.play(ReplacementTransform(way1, new_way1), run_time=0.7)
        way1 = new_way1
        miss_t = self._result_text("MISS (Compulsory)", RED).next_to(ways, DOWN, buff=0.35)
        self.play(FadeIn(miss_t))

        new_bar = self._make_lru_bar(["Way 0", "Way 1"]).move_to(lru_bar)
        self.play(Transform(lru_bar, new_bar))
        full_note = Text("Set is now FULL", font_size=FS_SMALL, color=ORANGE)
        full_note.next_to(miss_t, DOWN, buff=0.15)
        self.play(FadeIn(full_note))
        self.wait(0.9)
        self.play(FadeOut(miss_t), FadeOut(full_note))

        self._log_entry("Access A again", color=BLUE_B)
        hit_flash = SurroundingRectangle(way0, color=GREEN, buff=0.1)
        hit_t = self._result_text("HIT!", GREEN).next_to(ways, DOWN, buff=0.35)
        self.play(Create(hit_flash), FadeIn(hit_t))

        new_bar = self._make_lru_bar(["Way 1", "Way 0"]).move_to(lru_bar)
        self.play(Transform(lru_bar, new_bar))
        self.wait(0.9)
        self.play(FadeOut(hit_flash), FadeOut(hit_t))

        self._log_entry("Access C (addr 32)", color=ORANGE)
        evict_arrow = Arrow(
            way1.get_top() + UP * 0.1, way1.get_top() + UP * 0.6,
            color=RED, stroke_width=4,
        )
        evict_lbl = Text("EVICT (LRU)", font_size=FS_SMALL, color=RED)
        evict_lbl.next_to(evict_arrow, RIGHT, buff=0.1)
        self.play(Create(evict_arrow), FadeIn(evict_lbl))
        self.wait(0.5)

        new_way1 = self._make_way(1, "C  (tag=2)", ORANGE).move_to(way1)
        miss_t = self._result_text("MISS (Conflict) — B evicted", RED).next_to(ways, DOWN, buff=0.35)
        self.play(
            ReplacementTransform(way1, new_way1),
            FadeOut(evict_arrow),
            FadeOut(evict_lbl),
            FadeIn(miss_t),
            run_time=0.7,
        )
        way1 = new_way1

        # Way 1 loaded → MRU; Way 0 is LRU
        new_bar = self._make_lru_bar(["Way 0", "Way 1"]).move_to(lru_bar)
        self.play(Transform(lru_bar, new_bar))
        self.wait(1.2)
        self.play(FadeOut(miss_t))

        summary = VGroup(
            Text("Key Idea:", font_size=FS_SMALL, color=YELLOW_B),
            Text("LRU tracks the last-use order of each way.", font_size=FS_SMALL),
            Text("On eviction, the way that was used LEAST recently is replaced.", font_size=FS_SMALL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        box = SurroundingRectangle(summary, color=YELLOW_B, buff=0.2, corner_radius=0.1)
        summary_grp = VGroup(box, summary).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(summary_grp))
        self.wait(3)

    def _make_way(self, way_idx: int, content: str, color=WHITE):
        rect  = Rectangle(width=2.4, height=1.1, color=GRAY_B, fill_opacity=0.18)
        title = Text(f"Way {way_idx}", font_size=FS_SMALL, color=YELLOW_B)
        title.next_to(rect, UP, buff=0.08)
        txt = Text(content, font_size=FS_SMALL, color=color)
        txt.move_to(rect)
        return VGroup(rect, title, txt)

    def _make_lru_bar(self, order: list):
        """Return a single VGroup (cells + labels) showing LRU-to-MRU order."""
        cells = VGroup(*[
            Rectangle(width=2.0, height=0.5, color=GRAY_B, fill_opacity=0.4)
            for _ in order
        ]).arrange(RIGHT, buff=0)
        labels = VGroup(*[
            Text(name, font_size=FS_SMALL, color=WHITE).move_to(cells[i])
            for i, name in enumerate(order)
        ])
        return VGroup(cells, labels)

    def _result_text(self, text: str, color=WHITE):
        return Text(text, font_size=FS_SMALL, color=color)

    def _log_entry(self, text: str, color=WHITE):
        entry = Text(f"• {text}", font_size=FS_SMALL - 2, color=color)
        entry.move_to([4.5, self._log_y, 0])
        self._log_y -= 0.35
        self.play(FadeIn(entry), run_time=0.3)
        self._log_mobjs.append(entry)
