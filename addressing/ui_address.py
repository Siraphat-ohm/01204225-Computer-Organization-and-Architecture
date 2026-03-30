from manim import *
from constants import *
from cache_logic import CacheTraceConfig


class AddressBlock(VGroup):
    """A proportionally-split memory address bar (tag / index / offset)."""

    def __init__(self, address_bits=10, tag_bits=3, index_bits=4, offset_bits=3, **kwargs):
        super().__init__(**kwargs)
        self.address_bits = address_bits
        self.tag_bits     = tag_bits
        self.index_bits   = index_bits
        self.offset_bits  = offset_bits

        self.full_rect = Rectangle(
            height=ADDRESS_HEIGHT, width=ADDRESS_WIDTH, color=WHITE, fill_opacity=0.1
        )
        self.add(self.full_rect)

    def create_split_sections(self):
        tag_w = (self.tag_bits    / self.address_bits) * ADDRESS_WIDTH
        idx_w = (self.index_bits  / self.address_bits) * ADDRESS_WIDTH
        off_w = (self.offset_bits / self.address_bits) * ADDRESS_WIDTH

        self.tag_rect = Rectangle(width=tag_w, height=ADDRESS_HEIGHT,
                                  color=TAG_COLOR,    fill_opacity=0.5)
        self.idx_rect = Rectangle(width=idx_w, height=ADDRESS_HEIGHT,
                                  color=INDEX_COLOR,  fill_opacity=0.5)
        self.off_rect = Rectangle(width=off_w, height=ADDRESS_HEIGHT,
                                  color=OFFSET_COLOR, fill_opacity=0.5)

        self.tag_rect.move_to(self.full_rect.get_left(), aligned_edge=LEFT)
        self.idx_rect.next_to(self.tag_rect, RIGHT, buff=0)
        self.off_rect.next_to(self.idx_rect, RIGHT, buff=0)

        self.tag_label = Text(f"Tag ({self.tag_bits})",      font_size=FS_SMALL, color=TAG_COLOR   ).next_to(self.tag_rect, DOWN)
        self.idx_label = Text(f"Index ({self.index_bits})",  font_size=FS_SMALL, color=INDEX_COLOR ).next_to(self.idx_rect, DOWN)
        self.off_label = Text(f"Offset ({self.offset_bits})",font_size=FS_SMALL, color=OFFSET_COLOR).next_to(self.off_rect, DOWN)

        return VGroup(self.tag_rect, self.idx_rect, self.off_rect,
                      self.tag_label, self.idx_label, self.off_label)


class CacheCalcDisplay(VGroup):
    def __init__(self, config: CacheTraceConfig, addr_val: int, split: dict, **kwargs):
        super().__init__(**kwargs)

        b_tag  = split["b_tag"]
        b_idx  = split["b_idx"]
        b_off  = split["b_off"]
        tag    = split["tag"]
        index  = split["index"]
        offset = split["offset"]

        addr_label = Text(f"Address:  {addr_val}", font_size=FS_SECTION, color=BLUE_B)

        total  = config.addr_bits
        BOX_W, BOX_H = 4.5, 0.5
        tag_w  = (config.tag_bits    / total) * BOX_W
        idx_w  = (config.index_bits  / total) * BOX_W
        off_w  = (config.offset_bits / total) * BOX_W

        tag_box = Rectangle(width=tag_w, height=BOX_H, color=TAG_COLOR,    fill_opacity=0.6)
        idx_box = Rectangle(width=idx_w, height=BOX_H, color=INDEX_COLOR,  fill_opacity=0.6)
        off_box = Rectangle(width=off_w, height=BOX_H, color=OFFSET_COLOR, fill_opacity=0.6)
        VGroup(tag_box, idx_box, off_box).arrange(RIGHT, buff=0)

        tag_txt = Text(b_tag, font_size=FS_SMALL, color=WHITE).move_to(tag_box)
        idx_txt = Text(b_idx, font_size=FS_SMALL, color=WHITE).move_to(idx_box)
        off_txt = Text(b_off, font_size=FS_SMALL, color=WHITE).move_to(off_box)
        boxes = VGroup(tag_box, idx_box, off_box, tag_txt, idx_txt, off_txt)

        stride = config.block_size * config.num_blocks
        calc_off = Text(
            f"Offset  =  {addr_val} mod {config.block_size}  =  {offset}",
            font_size=FS_SMALL, color=OFFSET_COLOR,
        )
        calc_idx = Text(
            f"Index   =  ({addr_val} \u00f7 {config.block_size}) mod {config.num_blocks}  =  {index}",
            font_size=FS_SMALL, color=INDEX_COLOR,
        )
        calc_tag = Text(
            f"Tag     =  {addr_val} \u00f7 {stride}  =  {tag}",
            font_size=FS_SMALL, color=TAG_COLOR,
        )
        calcs = VGroup(calc_off, calc_idx, calc_tag).arrange(DOWN, aligned_edge=LEFT, buff=0.22)

        content = VGroup(addr_label, boxes, calcs).arrange(DOWN, buff=0.3, center=True)
        self.add(content)
