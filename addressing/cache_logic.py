import math
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class CacheTraceConfig:
    """Configuration and derived bit-widths for direct-mapped cache tracing."""
    addr_bits: int = 8
    cache_size: int = 32
    block_size: int = 4
    sequence: tuple[int, ...] = (0, 4, 8, 16, 0, 32, 0, 128, 129, 4)

    @property
    def num_blocks(self) -> int:
        return self.cache_size // self.block_size

    @property
    def offset_bits(self) -> int:
        return int(math.log2(self.block_size))

    @property
    def index_bits(self) -> int:
        return int(math.log2(self.num_blocks))

    @property
    def tag_bits(self) -> int:
        return self.addr_bits - self.index_bits - self.offset_bits

def calculate_index(addr_val: int, config: CacheTraceConfig) -> int:
    """Calculate direct-mapped cache index for an address."""
    return (addr_val // config.block_size) % config.num_blocks

def split_cache_address(addr_val: int, config: CacheTraceConfig) -> dict:
    """Split an address into tag/index/offset (numeric + binary forms)."""
    offset = addr_val % config.block_size
    index = calculate_index(addr_val, config)
    tag = addr_val // (config.block_size * config.num_blocks)

    bin_full = bin(addr_val)[2:].zfill(config.addr_bits)
    b_tag = bin_full[: config.tag_bits]
    b_idx = bin_full[config.tag_bits : config.tag_bits + config.index_bits]
    b_off = bin_full[config.tag_bits + config.index_bits :]

    return {
        "offset": offset,
        "index": index,
        "tag": tag,
        "b_tag": b_tag,
        "b_idx": b_idx,
        "b_off": b_off,
    }

class CacheSimulator:
    """Handles the state of a direct-mapped cache."""
    def __init__(self, num_blocks: int):
        self.num_blocks = num_blocks
        self.state = [{"valid": False, "tag": None} for _ in range(num_blocks)]

    def access(self, index: int, tag: int) -> tuple[bool, bool]:
        """
        Accesses the cache and updates state.
        Returns (is_hit, was_valid_before)
        """
        entry = self.state[index]
        is_hit = entry["valid"] and entry["tag"] == tag
        was_valid_before = entry["valid"]
        
        if not is_hit:
            entry["valid"] = True
            entry["tag"] = tag
            
        return is_hit, was_valid_before

    def get_entry(self, index: int) -> Dict[str, Any]:
        return self.state[index]
