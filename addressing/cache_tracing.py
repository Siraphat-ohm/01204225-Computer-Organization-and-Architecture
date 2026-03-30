from manim import *
from .constants import *
from .cache_logic import CacheTraceConfig, CacheSimulator, split_cache_address
from .ui_misc import AccessSequenceDisplay, HitRateCounter, MissTypeCounter
from .ui_table import CacheTraceTable
from .ui_address import CacheCalcDisplay

LEFT_X  = -3.5
RIGHT_X =  3.5


class CacheTracingScene(Scene):
    def construct(self):
        cfg = CacheTraceConfig()

        title = Text(
            "Direct Mapped Cache Tracing", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.15)
        self.add(title)

        cfg_info = VGroup(
            Text(f"Addr: {cfg.addr_bits}b",           font_size=FS_SMALL),
            Text("|",                                  font_size=FS_SMALL, color=GRAY_D),
            Text(f"Block: {cfg.block_size} B",         font_size=FS_SMALL),
            Text("|",                                  font_size=FS_SMALL, color=GRAY_D),
            Text(f"Blocks: {cfg.num_blocks}",          font_size=FS_SMALL),
            Text("|",                                  font_size=FS_SMALL, color=GRAY_D),
            Text(f"Offset: {cfg.offset_bits}b",        font_size=FS_SMALL, color=OFFSET_COLOR),
            Text("|",                                  font_size=FS_SMALL, color=GRAY_D),
            Text(f"Index: {cfg.index_bits}b",          font_size=FS_SMALL, color=INDEX_COLOR),
            Text("|",                                  font_size=FS_SMALL, color=GRAY_D),
            Text(f"Tag: {cfg.tag_bits}b",              font_size=FS_SMALL, color=TAG_COLOR),
        ).arrange(RIGHT, buff=0.2)
        cfg_info.next_to(title, DOWN, buff=0.12)
        self.add(cfg_info)

        divider = Line([0, 2.6, 0], [0, -2.8, 0], color=GRAY_D, stroke_width=1)
        self.add(divider)

        left_label = Text("Cache State", font_size=FS_SECTION, color=YELLOW_B)
        left_label.move_to([LEFT_X, 2.3, 0])
        self.add(left_label)

        cache_table = CacheTraceTable(cfg).scale(0.52).move_to([LEFT_X, -0.1, 0])
        self.add(cache_table)

        right_label = Text("Address Breakdown", font_size=FS_SECTION, color=YELLOW_B)
        right_label.move_to([RIGHT_X, 2.3, 0])
        self.add(right_label)

        miss_counter = MissTypeCounter().move_to([RIGHT_X, -1.55, 0])
        self.add(miss_counter)

        seq_label   = Text("Sequence:", font_size=FS_SMALL, color=YELLOW_B)
        seq_display = AccessSequenceDisplay(cfg.sequence, font_size=FS_SMALL, buff=0.22)
        seq_row     = VGroup(seq_label, seq_display).arrange(RIGHT, buff=0.2)
        seq_row.move_to([0, -3.15, 0])
        self.add(seq_row)

        hit_rate = HitRateCounter().move_to([LEFT_X, -3.6, 0])
        self.add(hit_rate)

        simulator    = CacheSimulator(cfg.num_blocks)
        current_calc = None

        for i, addr_val in enumerate(cfg.sequence):
            split = split_cache_address(addr_val, cfg)
            index = split["index"]
            tag   = split["tag"]

            indicator = seq_display.create_indicator(i)
            new_calc  = CacheCalcDisplay(cfg, addr_val, split).move_to([RIGHT_X, 0.7, 0])

            anims = [Create(indicator), seq_display.highlight_anim(i)]
            if current_calc is not None:
                anims.append(ReplacementTransform(current_calc, new_calc))
            else:
                anims.append(FadeIn(new_calc))
            self.play(*anims, run_time=0.6)
            current_calc = new_calc

            self.play(cache_table.indicate_row(index, color=YELLOW), run_time=0.5)

            is_hit, was_valid_before = simulator.access(index, tag)
            if is_hit:
                result_text, result_color = "HIT", GREEN
            elif not was_valid_before:
                result_text, result_color = "MISS: Compulsory", BLUE_B
            else:
                result_text, result_color = "MISS: Conflict", ORANGE

            hit_rate_anim = hit_rate.record(is_hit)
            miss_anims    = miss_counter.record(is_hit, was_valid_before)
            res_t         = cache_table.update_result(index, result_text, color=result_color)

            if not is_hit:
                v_t, tag_t = cache_table.update_row(index, tag)
                self.play(v_t, tag_t, res_t, hit_rate_anim, *miss_anims)
            else:
                self.play(res_t, hit_rate_anim, *miss_anims)

            self.wait(1.2)
            self.play(FadeOut(indicator), seq_display.reset_anim(i), run_time=0.4)

        self.wait(2)
