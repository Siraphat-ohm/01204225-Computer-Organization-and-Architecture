from manim import *
from constants import *
from logic import (
    TWO_WAY_CFG, FOUR_WAY_CFG,
    NWayLRUSimulator, split_assoc_address,
)
from ui_assoc import AssocCalcDisplay, TwoWayTraceTable, FourWayTraceTable

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "addressing"))
from ui_misc import AccessSequenceDisplay, HitRateCounter, MissTypeCounter

LEFT_X  = -3.2
RIGHT_X =  3.3

# Result label constants (text, color)
_HIT        = ("HIT",         GREEN )
_COMPULSORY = ("Compulsory",  BLUE_B)
_CONFLICT   = ("Conflict",    ORANGE)


def _cfg_info_bar(cfg) -> VGroup:
    """Horizontal config summary bar shown below the title."""
    def sep():
        return Text("|", font_size=FS_SMALL, color=GRAY_D)
    return VGroup(
        Text(f"Addr: {cfg.addr_bits}b",     font_size=FS_SMALL),               sep(),
        Text(f"Block: {cfg.block_size} B",  font_size=FS_SMALL),               sep(),
        Text(f"Ways: {cfg.ways}",           font_size=FS_SMALL),               sep(),
        Text(f"Sets: {cfg.num_sets}",       font_size=FS_SMALL),               sep(),
        Text(f"Offset: {cfg.offset_bits}b", font_size=FS_SMALL, color=OFFSET_COLOR), sep(),
        Text(f"Index: {cfg.index_bits}b",   font_size=FS_SMALL, color=INDEX_COLOR),  sep(),
        Text(f"Tag: {cfg.tag_bits}b",       font_size=FS_SMALL, color=TAG_COLOR),
    ).arrange(RIGHT, buff=0.18)


def _seq_row(cfg) -> tuple:
    """Return (row_VGroup, AccessSequenceDisplay) for the bottom strip."""
    label   = Text("Sequence:", font_size=FS_SMALL, color=YELLOW_B)
    display = AccessSequenceDisplay(cfg.sequence, font_size=FS_SMALL, buff=0.28)
    row     = VGroup(label, display).arrange(RIGHT, buff=0.2)
    return row, display


def _result_label(is_hit: bool, was_full: bool) -> tuple:
    """Return (text, color) for the current access result."""
    if is_hit:
        return _HIT
    return _CONFLICT if was_full else _COMPULSORY


class TwoWayTracingScene(Scene):
    """
    Full tracing scene for a 2-way set-associative cache.

    Left   : cache-state table  (Set | W0 V | W0 Tag | W1 V | W1 Tag | LRU | Result)
    Right  : address breakdown widget + miss-type counter
    Bottom : access sequence strip + live hit-rate counter
    """

    def construct(self):
        cfg = TWO_WAY_CFG

        title = Text(
            "2-Way Set-Associative Cache Tracing", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.15)
        self.add(title)

        cfg_info = _cfg_info_bar(cfg).next_to(title, DOWN, buff=0.12)
        self.add(cfg_info)

        divider = Line([0, 2.6, 0], [0, -2.8, 0], color=GRAY_D, stroke_width=1)
        self.add(divider)

        left_label = Text("Cache State", font_size=FS_SECTION, color=YELLOW_B)
        left_label.move_to([LEFT_X, 2.3, 0])
        self.add(left_label)

        right_label = Text("Address Breakdown", font_size=FS_SECTION, color=YELLOW_B)
        right_label.move_to([RIGHT_X, 2.3, 0])
        self.add(right_label)

        cache_table = TwoWayTraceTable(cfg).scale(0.72).move_to([LEFT_X, -0.1, 0])
        self.add(cache_table)

        miss_counter = MissTypeCounter().move_to([RIGHT_X, -1.55, 0])
        self.add(miss_counter)

        seq_row, seq_display = _seq_row(cfg)
        seq_row.move_to([0, -3.15, 0])
        self.add(seq_row)

        hit_rate = HitRateCounter().move_to([LEFT_X, -3.6, 0])
        self.add(hit_rate)

        simulator    = NWayLRUSimulator(cfg.num_sets, cfg.ways)
        current_calc = None

        for i, addr_val in enumerate(cfg.sequence):
            split   = split_assoc_address(addr_val, cfg)
            set_idx = split["set_index"]
            tag     = split["tag"]

            indicator = seq_display.create_indicator(i)
            new_calc  = AssocCalcDisplay(cfg, addr_val, split).move_to([RIGHT_X, 0.7, 0])

            entry_anims = [Create(indicator), seq_display.highlight_anim(i)]
            entry_anims.append(
                ReplacementTransform(current_calc, new_calc) if current_calc else FadeIn(new_calc)
            )
            self.play(*entry_anims, run_time=0.6)
            current_calc = new_calc

            self.play(cache_table.indicate_set(set_idx, color=YELLOW), run_time=0.5)

            is_hit, was_full, _, loaded_way = simulator.access(set_idx, tag)
            _, lru_order = simulator.get_set_state(set_idx)
            result_text, result_color = _result_label(is_hit, was_full)

            lru_anim      = cache_table.update_lru(set_idx, lru_order)
            res_anim      = cache_table.update_result(set_idx, result_text, color=result_color)
            hit_rate_anim = hit_rate.record(is_hit)
            miss_anims    = miss_counter.record(is_hit, was_full)

            if not is_hit:
                self.play(
                    cache_table.update_way(set_idx, loaded_way, tag),
                    res_anim, lru_anim, hit_rate_anim, *miss_anims,
                )
            else:
                self.play(res_anim, lru_anim, hit_rate_anim, *miss_anims)

            self.wait(1.2)
            self.play(FadeOut(indicator), seq_display.reset_anim(i), run_time=0.4)

        self.wait(2)


class FourWayTracingScene(Scene):
    """
    Tracing scene for a 4-way set-associative cache.

    Left   : compact cache-state table  (Set | Way 0–3 | LRU | Result)
    Right  : address breakdown widget + live hit-rate counter
    Bottom : access sequence strip
    """

    def construct(self):
        cfg = FOUR_WAY_CFG

        title = Text(
            "4-Way Set-Associative Cache Tracing", font_size=FS_TITLE, color=YELLOW
        ).to_edge(UP, buff=0.15)
        self.add(title)

        cfg_info = _cfg_info_bar(cfg).next_to(title, DOWN, buff=0.12)
        self.add(cfg_info)

        divider = Line([0, 2.6, 0], [0, -2.8, 0], color=GRAY_D, stroke_width=1)
        self.add(divider)

        left_label = Text("Cache State", font_size=FS_SECTION, color=YELLOW_B)
        left_label.move_to([LEFT_X, 2.3, 0])
        self.add(left_label)

        right_label = Text("Address Breakdown", font_size=FS_SECTION, color=YELLOW_B)
        right_label.move_to([RIGHT_X, 2.3, 0])
        self.add(right_label)

        cache_table = FourWayTraceTable(cfg).scale(0.58).move_to([LEFT_X, 0.2, 0])
        self.add(cache_table)

        hit_rate = HitRateCounter().move_to([RIGHT_X, -1.0, 0])
        self.add(hit_rate)

        seq_row, seq_display = _seq_row(cfg)
        seq_row.move_to([0, -3.2, 0])
        self.add(seq_row)

        simulator    = NWayLRUSimulator(cfg.num_sets, cfg.ways)
        current_calc = None

        for i, addr_val in enumerate(cfg.sequence):
            split   = split_assoc_address(addr_val, cfg)
            set_idx = split["set_index"]
            tag     = split["tag"]

            indicator = seq_display.create_indicator(i)
            new_calc  = AssocCalcDisplay(cfg, addr_val, split).move_to([RIGHT_X, 0.9, 0])

            entry_anims = [Create(indicator), seq_display.highlight_anim(i)]
            entry_anims.append(
                ReplacementTransform(current_calc, new_calc) if current_calc else FadeIn(new_calc)
            )
            self.play(*entry_anims, run_time=0.5)
            current_calc = new_calc

            self.play(cache_table.indicate_set(set_idx, color=YELLOW), run_time=0.4)

            is_hit, was_full, _, loaded_way = simulator.access(set_idx, tag)
            _, lru_order = simulator.get_set_state(set_idx)
            result_text, result_color = _result_label(is_hit, was_full)

            lru_anim      = cache_table.update_lru(set_idx, lru_order)
            res_anim      = cache_table.update_result(set_idx, result_text, color=result_color)
            hit_rate_anim = hit_rate.record(is_hit)

            if not is_hit:
                self.play(
                    cache_table.update_way(set_idx, loaded_way, tag),
                    res_anim, lru_anim, hit_rate_anim,
                )
            else:
                self.play(res_anim, lru_anim, hit_rate_anim)

            self.wait(1.0)
            self.play(FadeOut(indicator), seq_display.reset_anim(i), run_time=0.3)

        self.wait(2)
