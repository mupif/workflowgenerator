from . import tools
from . import Block
from . import VisualMenu


class BlockSequentional (Block.Block):
    """
    Implementation of sequential processing block
    """
    def __init__(self):
        Block.Block.__init__(self)

    def getInitCode(self, indent=0):
        return []

    def getInitializationCode(self, indent=0, metaDataStr="{}"):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)

        for block in self.getBlocks():
            code.extend(block.getExecutionCode(0, timestep))

        return tools.push_indents_before_each_line(code, indent)

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def generateMenu(self):
        Block.Block.generateMenu(self)
        self.generateAddBlockMenuItems()

    def generateAddBlockMenuItems(self):
        for block_class in self.getWorkflowBlock().getListOfBlockClasses():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'add_standard_block', block_class.__name__, block_class.__name__), 'Add Block.Standard')

        for block_class in self.getWorkflowBlock().getListOfModels():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'add_standard_block', block_class.__name__, block_class.__name__), 'Add Block.Model')
