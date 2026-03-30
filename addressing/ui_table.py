from manim import *
from constants import *
from cache_logic import CacheTraceConfig

class CacheTable(VGroup):
    """A visual representation of a cache table."""
    def __init__(self, num_rows=8, tag_bits=3, **kwargs):
        super().__init__(**kwargs)
        self.num_rows = num_rows
        self.tag_bits = tag_bits
        
        headers = ["Index", "V", "Tag", "Data"]
        header_group = VGroup(*[Text(h, font_size=FS_SECTION) for h in headers])
        header_group.arrange(RIGHT, buff=1.0)
        
        self.header_group = header_group
        self.rows = VGroup()
        self.rows.add(header_group)

        self.cells = []
        for i in range(num_rows):
            row_idx = Text(str(i), font_size=FS_BODY)
            row_v = Text("0", font_size=FS_BODY, color=VALID_COLOR)
            row_tag = Text("-" * tag_bits, font_size=FS_BODY, color=TAG_COLOR)
            row_data = Text("Block Data", font_size=FS_SMALL, color=DATA_COLOR)
            
            row = VGroup(row_idx, row_v, row_tag, row_data)
            for item, header in zip(row, header_group):
                item.move_to(header)
            
            row.shift(DOWN * (i + 1) * 0.5)
            self.rows.add(row)
            self.cells.append({"v": row_v, "tag": row_tag})
        
        self.add(self.rows)
        self.scale(TABLE_SCALE)

    def get_row(self, index):
        """Returns the specific row group (skipping header)."""
        return self.rows[index + 1]

    def highlight_row(self, index):
        """Creates a highlight rectangle for a specific row."""
        row = self.get_row(index)
        highlight = SurroundingRectangle(row, color=YELLOW, buff=0.1)
        return highlight

    def update_row(self, index, tag_val):
        """Updates the visual representation of a row's Valid bit and Tag."""
        v_cell = self.cells[index]['v']
        tag_cell = self.cells[index]['tag']
        
        # Convert tag_val to binary string
        tag_str = bin(tag_val)[2:].zfill(self.tag_bits)
        
        new_v = Text("1", font_size=FS_BODY, color=VALID_COLOR).move_to(v_cell)
        new_tag = Text(tag_str, font_size=FS_BODY, color=TAG_COLOR).move_to(tag_cell)
        
        return Transform(v_cell, new_v), Transform(tag_cell, new_tag)

class CacheTraceTable(VGroup):
    """Table component specialized for the cache tracing scene."""

    def __init__(self, config: CacheTraceConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.result_font_size = FS_SMALL

        table_data = [["Idx", "V", "Tag", "Data Range", "MISS: Compulsory"]]
        for i in range(config.num_blocks):
            table_data.append(
                [
                    str(i),
                    "0",
                    "---",
                    f"{i * config.block_size}-{(i + 1) * config.block_size - 1}",
                    "MISS: Compulsory",
                ]
            )

        self.table = Table(
            table_data,
            include_outer_lines=True,
            h_buff=1.1,
            v_buff=0.4,
            element_to_mobject_config={"font_size": FS_BODY},
        )

        header_row = self.table.get_rows()[0]
        for cell in header_row:
            cell.set_color(YELLOW_B)

        header_row[4].become(
            Text("MISS / HIT", font_size=FS_BODY, color=YELLOW_B).move_to(header_row[4])
        )

        for row in self.table.get_rows()[1:]:
            row[4].become(
                Text("\u2014", font_size=FS_SMALL, color=GRAY_B).move_to(row[4])
            )

        self.add(self.table)

    def get_row(self, cache_index: int):
        return self.table.get_rows()[cache_index + 1]

    def indicate_row(self, cache_index: int, color=YELLOW):
        return Indicate(self.get_row(cache_index), color=color)

    def update_row(self, cache_index: int, tag_val: int):
        row = self.get_row(cache_index)
        v_cell = row[1]
        tag_cell = row[2]

        new_v = Text("1", font_size=FS_BODY, color=WHITE).move_to(v_cell)
        new_tag = Text(
            bin(tag_val)[2:].zfill(self.config.tag_bits),
            font_size=FS_BODY,
            color=BLUE,
        ).move_to(tag_cell)

        return Transform(v_cell, new_v), Transform(tag_cell, new_tag)

    def update_result(self, cache_index: int, result_text: str, color=WHITE):
        row = self.get_row(cache_index)
        result_cell = row[4]

        new_result = Text(
            result_text,
            font_size=self.result_font_size,
            color=color,
        ).move_to(result_cell)

        return Transform(result_cell, new_result)
