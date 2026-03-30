from manim import *
from .constants import *
from .cache_logic import CacheTraceConfig


class CacheParamsScene(Scene):
    examples = [
        ("32-bit System",  CacheTraceConfig(addr_bits=32, cache_size=32768, block_size=64)),
        ("8-bit Embedded", CacheTraceConfig(addr_bits=8,  cache_size=32,    block_size=4)),
    ]

    def construct(self):
        self.title = Text(
            "Cache Parameter Calculation", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.25)
        self.add(self.title)

        for i, (name, cfg) in enumerate(self.examples):
            self._show_example(i + 1, name, cfg)

        self.wait(2)

    def _show_example(self, num: int, name: str, cfg: CacheTraceConfig):
        ob = cfg.offset_bits
        ib = cfg.index_bits
        tb = cfg.tag_bits

        header = Text(f"Example {num}:  {name}", font_size=FS_SECTION, color=BLUE_B)
        header.next_to(self.title, DOWN, buff=0.25)
        self.play(Write(header))

        given = VGroup(
            Text("Given",                              font_size=FS_BODY, color=YELLOW_B),
            Text(f"Address bits  :  {cfg.addr_bits}",  font_size=FS_BODY),
            Text(f"Block size    :  {cfg.block_size} B", font_size=FS_BODY),
            Text(f"Total sets    :  {cfg.num_blocks}", font_size=FS_BODY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        box = SurroundingRectangle(given, color=PARAM_COLOR, buff=0.3, corner_radius=0.1)
        given_grp = VGroup(box, given).to_edge(LEFT, buff=0.7).shift(UP * 0.5)
        self.play(Create(box), FadeIn(given))

        f_off = MathTex(
            r"\text{Offset} = \log_2(\text{block size}) = \log_2(",
            str(cfg.block_size), r") = ", str(ob), r"\ \text{bits}",
            font_size=28,
        )
        f_off.set_color_by_tex(str(ob), OFFSET_COLOR)

        f_idx = MathTex(
            r"\text{Index} = \log_2(\text{sets}) = \log_2(",
            str(cfg.num_blocks), r") = ", str(ib), r"\ \text{bits}",
            font_size=28,
        )
        f_idx.set_color_by_tex(str(ib), INDEX_COLOR)

        f_tag = MathTex(
            r"\text{Tag} = \text{addr} - \text{index} - \text{offset} = ",
            str(cfg.addr_bits), r" - ", str(ib), r" - ", str(ob),
            r" = ", str(tb), r"\ \text{bits}",
            font_size=28,
        )
        f_tag.set_color_by_tex(str(tb), TAG_COLOR)

        cache_b  = cfg.cache_size
        size_kb  = cache_b // 1024
        size_str = (f"{size_kb}\\ \\text{{KB}}" if size_kb >= 1 else f"{cache_b}\\ \\text{{B}}")
        f_size = MathTex(
            r"\text{Cache size} = \text{sets} \times \text{block size} = ",
            str(cfg.num_blocks), r" \times ", str(cfg.block_size),
            r" = ", str(cache_b), r"\ \text{B} = " + size_str,
            font_size=28,
        )

        formulas = VGroup(f_off, f_idx, f_tag, f_size).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        formulas.next_to(given_grp, RIGHT, buff=0.7).align_to(given_grp, UP)

        for f in (f_off, f_idx, f_tag, f_size):
            self.play(Write(f), run_time=0.7)
            self.wait(0.2)

        W, H = 9.0, 0.65
        tag_box = Rectangle(width=tb / cfg.addr_bits * W, height=H,
                            color=TAG_COLOR,    fill_opacity=0.6)
        idx_box = Rectangle(width=ib / cfg.addr_bits * W, height=H,
                            color=INDEX_COLOR,  fill_opacity=0.6)
        off_box = Rectangle(width=ob / cfg.addr_bits * W, height=H,
                            color=OFFSET_COLOR, fill_opacity=0.6)
        VGroup(tag_box, idx_box, off_box).arrange(RIGHT, buff=0)

        tag_lbl = Text(f"Tag ({tb}b)",    font_size=FS_SMALL).move_to(tag_box)
        idx_lbl = Text(f"Index ({ib}b)",  font_size=FS_SMALL).move_to(idx_box)
        off_lbl = Text(f"Offset ({ob}b)", font_size=FS_SMALL).move_to(off_box)
        bar = VGroup(tag_box, idx_box, off_box, tag_lbl, idx_lbl, off_lbl)
        bar.to_edge(DOWN, buff=0.7)

        self.play(FadeIn(bar))
        self.wait(0.5)

        self.play(
            Indicate(f_off, color=OFFSET_COLOR), Indicate(off_box, color=OFFSET_COLOR),
            Indicate(f_idx, color=INDEX_COLOR),  Indicate(idx_box, color=INDEX_COLOR),
            Indicate(f_tag, color=TAG_COLOR),    Indicate(tag_box, color=TAG_COLOR),
        )
        self.wait(2)

        self.play(FadeOut(VGroup(header, given_grp, formulas, bar)))
        self.wait(0.3)
