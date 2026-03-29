import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scenes.datapath_base import DatapathBase


class SingleDatapath(DatapathBase):
    """Static render of the full RISC-V single-cycle datapath."""

    def construct(self):
        self.setup_datapath()
        self.wait(1)
