from manim import *
from .constants import *
from .logic import AssocCacheConfig, split_assoc_address


class AssocCalcDisplay(VGroup):
    """Right-panel widget: proportional bit bar + formula lines for N-way cache."""

    def __init__(self, config: AssocCacheConfig, addr_val: int, split: dict, **kwargs):
        super().__init__(**kwargs)

        tag, set_index, offset = split["tag"], split["set_index"], split["offset"]
        b_tag, b_idx, b_off    = split["b_tag"], split["b_idx"], split["b_off"]

        addr_label = Text(f"Address:  {addr_val}", font_size=FS_SECTION, color=BLUE_B)

        BOX_W, BOX_H = 4.5, 0.5
        total = config.addr_bits
        tag_w = (config.tag_bits    / total) * BOX_W
        idx_w = max((config.index_bits / total) * BOX_W, 0.3)
        off_w = (config.offset_bits / total) * BOX_W

        tag_box = Rectangle(width=tag_w, height=BOX_H, color=TAG_COLOR,    fill_opacity=0.6)
        idx_box = Rectangle(width=idx_w, height=BOX_H, color=INDEX_COLOR,  fill_opacity=0.6)
        off_box = Rectangle(width=off_w, height=BOX_H, color=OFFSET_COLOR, fill_opacity=0.6)
        VGroup(tag_box, idx_box, off_box).arrange(RIGHT, buff=0)

        tag_txt = Text(b_tag,                  font_size=FS_SMALL, color=WHITE).move_to(tag_box)
        idx_txt = Text(b_idx if b_idx else "-", font_size=FS_SMALL, color=WHITE).move_to(idx_box)
        off_txt = Text(b_off,                  font_size=FS_SMALL, color=WHITE).move_to(off_box)
        boxes   = VGroup(tag_box, idx_box, off_box, tag_txt, idx_txt, off_txt)

        stride   = config.block_size * config.num_sets
        calc_off = Text(
            f"Offset  =  {addr_val} mod {config.block_size}  =  {offset}",
            font_size=FS_SMALL, color=OFFSET_COLOR,
        )
        calc_idx = Text(
            f"Set     =  ({addr_val} \u00f7 {config.block_size}) mod {config.num_sets}  =  {set_index}",
            font_size=FS_SMALL, color=INDEX_COLOR,
        )
        calc_tag = Text(
            f"Tag     =  {addr_val} \u00f7 {stride}  =  {tag}",
            font_size=FS_SMALL, color=TAG_COLOR,
        )
        calcs = VGroup(calc_off, calc_idx, calc_tag).arrange(DOWN, aligned_edge=LEFT, buff=0.22)

        content = VGroup(addr_label, boxes, calcs).arrange(DOWN, buff=0.3, center=True)
        self.add(content)


class _AssocTraceTableBase(VGroup):
    """
    Base class for set-associative cache trace tables.

    Subclasses call _build_table(header, rows) from __init__ and implement
    update_way().  All other methods (indicate_set, update_lru, update_result)
    are provided here; they assume LRU is the second-to-last column and
    MISS/HIT is the last column.
    """

    _H_BUFF             = 0.55
    _V_BUFF             = 0.28
    _RESULT_PLACEHOLDER = "Compulsory"   # longest label — sizes the column

    def _build_table(self, header: list, rows: list):
        self.table = Table(
            [header] + rows,
            include_outer_lines=True,
            h_buff=self._H_BUFF,
            v_buff=self._V_BUFF,
            element_to_mobject_config={"font_size": FS_SMALL},
        )

        n_cols           = len(header)
        self._result_col = n_cols - 1
        self._lru_col    = n_cols - 2

        header_row = self.table.get_rows()[0]
        for cell in header_row:
            cell.set_color(YELLOW_B)
        header_row[self._result_col].become(
            Text("Result", font_size=FS_SMALL, color=YELLOW_B)
            .move_to(header_row[self._result_col])
        )
        for row in self.table.get_rows()[1:]:
            row[self._result_col].become(
                Text("\u2014", font_size=FS_SMALL, color=GRAY_B)
                .move_to(row[self._result_col])
            )

        self.add(self.table)

    def _data_row(self, set_idx: int):
        return self.table.get_rows()[set_idx + 1]

    def indicate_set(self, set_idx: int, color=YELLOW):
        return Indicate(self._data_row(set_idx), color=color)

    def update_lru(self, set_idx: int, lru_order: list):
        """lru_order[0] = least recently used way."""
        row      = self._data_row(set_idx)
        lru_cell = row[self._lru_col]
        new_lru  = Text(f"W{lru_order[0]}", font_size=FS_SMALL, color=ORANGE).move_to(lru_cell)
        return Transform(lru_cell, new_lru)

    def update_result(self, set_idx: int, result_text: str, color=WHITE):
        row     = self._data_row(set_idx)
        cell    = row[self._result_col]
        new_res = Text(result_text, font_size=FS_SMALL, color=color).move_to(cell)
        return Transform(cell, new_res)


class TwoWayTraceTable(_AssocTraceTableBase):
    """
    Cache-state table for a 2-way set-associative cache.

    Columns: Set | Way 0 | Way 1 | LRU | Result
    Each way cell shows the binary tag (or '-' when empty).
    """

    def __init__(self, config: AssocCacheConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        _R     = self._RESULT_PLACEHOLDER
        header = ["Set", "Way 0", "Way 1", "LRU", _R]
        rows   = [[str(i), "-", "-", "W0", _R] for i in range(config.num_sets)]
        self._build_table(header, rows)

    def update_way(self, set_idx: int, way: int, tag_val: int):
        """Animate tag update for one way. Returns a Transform."""
        row      = self._data_row(set_idx)
        cell     = row[1 + way]              # Way 0 → col 1, Way 1 → col 2
        tag_str  = bin(tag_val)[2:].zfill(self.config.tag_bits)
        new_cell = Text(tag_str, font_size=FS_SMALL, color=TAG_COLOR).move_to(cell)
        return Transform(cell, new_cell)


class FourWayTraceTable(_AssocTraceTableBase):
    """
    Cache-state table for a 4-way set-associative cache.

    Columns: Set | Way 0 | Way 1 | Way 2 | Way 3 | LRU | MISS/HIT
    Each way cell shows the binary tag string, or '-' when empty.
    """

    def __init__(self, config: AssocCacheConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        _R     = self._RESULT_PLACEHOLDER
        header = ["Set", "W0", "W1", "W2", "W3", "LRU", _R]
        rows   = [[str(i), "-", "-", "-", "-", "W0", _R] for i in range(config.num_sets)]
        self._build_table(header, rows)

    def update_way(self, set_idx: int, way: int, tag_val: int):
        """Animate tag update for one way. Returns a Transform."""
        row      = self._data_row(set_idx)
        cell     = row[1 + way]              # Way 0 → col 1, Way 1 → col 2, …
        tag_str  = bin(tag_val)[2:].zfill(self.config.tag_bits)
        new_cell = Text(tag_str, font_size=FS_SMALL, color=TAG_COLOR).move_to(cell)
        return Transform(cell, new_cell)
