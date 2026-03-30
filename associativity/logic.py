import math
from dataclasses import dataclass


@dataclass(frozen=True)
class AssocCacheConfig:
    """Configuration for an N-way set-associative cache."""
    addr_bits:  int   = 8
    cache_size: int   = 32
    block_size: int   = 4
    ways:       int   = 2
    # Sequence chosen to demo: compulsory, temporal hit, LRU eviction, conflict miss
    #   0,16 → compulsory (fill set 0 both ways)
    #   4    → compulsory (set 1)
    #   0    → HIT (temporal locality)
    #   32   → conflict miss (evicts LRU in set 0)
    #   16   → conflict miss (was evicted)
    #   4    → HIT
    #   48   → conflict miss (set 0 again)
    sequence: tuple = (0, 16, 4, 0, 32, 16, 4, 48)

    @property
    def num_sets(self) -> int:
        return (self.cache_size // self.block_size) // self.ways

    @property
    def offset_bits(self) -> int:
        return int(math.log2(self.block_size))

    @property
    def index_bits(self) -> int:
        return int(math.log2(self.num_sets)) if self.num_sets > 1 else 0

    @property
    def tag_bits(self) -> int:
        return self.addr_bits - self.index_bits - self.offset_bits


TWO_WAY_CFG  = AssocCacheConfig(ways=2)
FOUR_WAY_CFG = AssocCacheConfig(
    ways=4,
    sequence=(0, 8, 16, 24, 0, 32, 8, 4),
)
COMPARE_SEQ  = (0, 32, 0, 32, 64, 0, 32, 64, 0)
DM_CFG       = AssocCacheConfig(ways=1, sequence=COMPARE_SEQ)
CMP_2WAY_CFG = AssocCacheConfig(ways=2, sequence=COMPARE_SEQ)
CMP_4WAY_CFG = AssocCacheConfig(ways=4, sequence=COMPARE_SEQ)


def split_assoc_address(addr_val: int, config: AssocCacheConfig) -> dict:
    """Split an address into tag / set-index / offset for a set-associative cache."""
    offset    = addr_val % config.block_size
    set_index = (addr_val // config.block_size) % config.num_sets
    tag       = addr_val // (config.block_size * config.num_sets)

    bin_full = bin(addr_val)[2:].zfill(config.addr_bits)
    b_tag    = bin_full[: config.tag_bits]
    b_idx    = bin_full[config.tag_bits : config.tag_bits + config.index_bits]
    b_off    = bin_full[config.tag_bits + config.index_bits :]

    return {
        "offset":    offset,
        "set_index": set_index,
        "tag":       tag,
        "b_tag":     b_tag,
        "b_idx":     b_idx,
        "b_off":     b_off,
    }


class NWayLRUSimulator:
    """N-way set-associative cache with LRU replacement policy."""

    def __init__(self, num_sets: int, ways: int):
        self.num_sets  = num_sets
        self.ways      = ways
        self.state     = [
            [{"valid": False, "tag": None} for _ in range(ways)]
            for _ in range(num_sets)
        ]
        # lru_order[set]: index 0 = LRU, index -1 = MRU
        self.lru_order = [list(range(ways)) for _ in range(num_sets)]

    def access(self, set_idx: int, tag: int):
        ways_state = self.state[set_idx]
        order      = self.lru_order[set_idx]

        for w in range(self.ways):
            if ways_state[w]["valid"] and ways_state[w]["tag"] == tag:
                order.remove(w)
                order.append(w)          # promote to MRU
                return True, False, -1, -1

        was_full  = all(ways_state[w]["valid"] for w in range(self.ways))
        empty_way = next(
            (w for w in range(self.ways) if not ways_state[w]["valid"]), None
        )

        if empty_way is not None:
            ways_state[empty_way]["valid"] = True
            ways_state[empty_way]["tag"]   = tag
            order.remove(empty_way)
            order.append(empty_way)
            return False, was_full, -1, empty_way
        else:
            evict = order[0]             # LRU way
            ways_state[evict]["valid"] = True
            ways_state[evict]["tag"]   = tag
            order.pop(0)
            order.append(evict)
            return False, was_full, evict, evict

    def get_set_state(self, set_idx: int):
        """Return (ways_state_list, lru_order_copy) for the given set."""
        return self.state[set_idx], list(self.lru_order[set_idx])
