from manim import *
from .constants import *

class Comparator(VGroup):
    """Hardware comparator logic block."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circle = Circle(radius=0.4, color=COMPARATOR_COLOR)
        self.symbol = Text("==", font_size=FS_SECTION)
        self.add(self.circle, self.symbol)

class AccessSequenceDisplay(VGroup):
    """Bottom-row display for the memory access sequence."""

    def __init__(self, sequence, font_size=FS_BODY, buff=0.5, **kwargs):
        super().__init__(**kwargs)
        self.numbers = VGroup(*[Text(str(n), font_size=font_size) for n in sequence])
        self.numbers.arrange(RIGHT, buff=buff)
        self.add(self.numbers)

    def create_indicator(self, index, color=YELLOW, buff=0.1):
        return Underline(self.numbers[index], color=color, buff=buff)

    def highlight_anim(self, index, color=YELLOW):
        return self.numbers[index].animate.set_color(color)

    def reset_anim(self, index, color=WHITE):
        return self.numbers[index].animate.set_color(color)

class HitRateCounter(VGroup):
    """Live hit rate counter. Call record(is_hit) to get a Transform animation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hits  = 0
        self.total = 0
        label           = Text("Hit Rate", font_size=FS_SECTION, color=YELLOW_B)
        self.value_mobj = Text("— / —  (—%)", font_size=FS_BODY, color=GRAY_B)
        VGroup(label, self.value_mobj).arrange(DOWN, buff=0.15, center=True)
        self.add(label, self.value_mobj)

    def record(self, is_hit: bool):
        self.total += 1
        if is_hit:
            self.hits += 1
        pct     = self.hits / self.total * 100
        color   = GREEN if is_hit else ORANGE
        new_val = Text(
            f"{self.hits} / {self.total}  ({pct:.1f}%)", font_size=FS_BODY, color=color,
        ).move_to(self.value_mobj)
        return Transform(self.value_mobj, new_val)


class MissTypeCounter(VGroup):
    """Live miss-type breakdown + miss rate. Call record(is_hit, was_valid_before)
    each access to get a list of Transform animations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.compulsory = 0
        self.conflict   = 0
        self.total      = 0

        header          = Text("Miss Breakdown", font_size=FS_SECTION, color=YELLOW_B)
        self.comp_mobj  = Text("Compulsory :  0", font_size=FS_SMALL,  color=BLUE_B)
        self.conf_mobj  = Text("Conflict   :  0", font_size=FS_SMALL,  color=ORANGE)
        self.rate_mobj  = Text("Miss Rate  :  — / —  (—%)", font_size=FS_SMALL, color=GRAY_B)

        stack = VGroup(header, self.comp_mobj, self.conf_mobj, self.rate_mobj)
        stack.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        self.add(stack)

    def record(self, is_hit: bool, was_valid_before: bool) -> list:
        """Update state and return a list of Transform animations."""
        self.total += 1
        if not is_hit:
            if not was_valid_before:
                self.compulsory += 1
            else:
                self.conflict += 1

        misses     = self.compulsory + self.conflict
        miss_pct   = misses / self.total * 100
        rate_color = RED if misses > 0 else GREEN

        new_comp = Text(
            f"Compulsory :  {self.compulsory}", font_size=FS_SMALL, color=BLUE_B,
        ).move_to(self.comp_mobj)
        new_conf = Text(
            f"Conflict   :  {self.conflict}", font_size=FS_SMALL, color=ORANGE,
        ).move_to(self.conf_mobj)
        new_rate = Text(
            f"Miss Rate  :  {misses} / {self.total}  ({miss_pct:.1f}%)",
            font_size=FS_SMALL, color=rate_color,
        ).move_to(self.rate_mobj)

        return [
            Transform(self.comp_mobj, new_comp),
            Transform(self.conf_mobj, new_conf),
            Transform(self.rate_mobj, new_rate),
        ]
