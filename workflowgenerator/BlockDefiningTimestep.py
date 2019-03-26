from . import BlockSequentional


class BlockDefiningTimestep (BlockSequentional.BlockSequentional):
    """
    Base class of a block, which defines a timestep in its code.
    """
    def __init__(self):
        BlockSequentional.BlockSequentional.__init__(self)
