from . import tools
from . import Block


class BlockSequentional (Block.Block):
    """
    Implementation of sequential processing block
    """
    def __init__(self):
        Block.Block.__init__(self)

    def getInitCode(self, indent=0):
        return []

    def getInitializationCode(self, indent=0):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)

        for block in self.getBlocks():
            code.extend(block.getExecutionCode(0, timestep))

        return tools.push_indents_before_each_line(code, indent)
