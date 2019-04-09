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

    def modificationQuery(self, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        if keyword == 'add_standard_block' and isinstance(value, str):
            if value in self.getWorkflowBlock().getListOfBlockClassnames():
                index = self.getWorkflowBlock().getListOfBlockClassnames().index(value)
                new_block = self.getWorkflowBlock().getListOfBlockClasses()[index]()
                self.addBlock(new_block)
        elif keyword == 'add_model_block' and isinstance(value, str):
            from . import BlockModel
            if value in self.getWorkflowBlock().getListOfModelClassnames():
                index = self.getWorkflowBlock().getListOfModelClassnames().index(value)
                new_model = self.getWorkflowBlock().getListOfModels()[index]()
                new_block = BlockModel.BlockModel(new_model)
                new_block.constructFromModelMetaData()
                self.addBlock(new_block)
        else:
            Block.Block.modificationQuery(self, keyword, value)

    def generateMenu(self):
        Block.Block.generateMenu(self)
        self.generateAddBlockMenuItems()

    def generateAddBlockMenuItems(self):
        for block_class in self.getWorkflowBlock().getListOfBlockClasses():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'add_standard_block', block_class.__name__, block_class.__name__), 'Add Block.Standard')

        for block_class in self.getWorkflowBlock().getListOfModels():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'add_model_block', block_class.__name__, block_class.__name__), 'Add Block.Model')
