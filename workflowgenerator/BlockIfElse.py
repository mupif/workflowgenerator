from . import tools
from . import Block
from . import DataSlot
from . import VisualMenu


class BlockIfElse (Block.Block):

    def __init__(self):
        Block.Block.__init__(self)
        self.addDataSlot(DataSlot.InputDataSlot("condition", DataSlot.DataSlotType.Bool, False))
        self.block_if = None
        self.block_else = None

    def getInitCode(self, indent=0):
        return []

    def getInitializationCode(self, indent=0):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)
        code.append("")
        code.append("if %s:" % self.getCondition())
        code.extend(self.block_if.getExecutionCode(1, timestep))
        code.append("")
        code.append("else:")
        code.extend(self.block_else.getExecutionCode(1, timestep))

        return tools.push_indents_before_each_line(code, indent)

    def getCondition(self):
        """:rtype: str"""
        return "True"  # temporary until a condition block exists

    def getBlocks(self, cls=None):
        blocks = []
        if self.block_if is not None:
            blocks.append(self.block_if)
        if self.block_else is not None:
            blocks.append(self.block_else)
        return blocks

    def setBlockIf(self, block):
        block.setParentBlock(self)
        self.block_if = block

    def setBlockElse(self, block):
        block.setParentBlock(self)
        self.block_else = block

    def addBlock(self, block):
        pass

    def deleteBlock(self, block):
        if self.block_if == block:
            block.deleteAllItems()
            self.block_if = None
        elif self.block_else == block:
            block.deleteAllItems()
            self.block_else = None

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def getVisualStructureItems(self):
        """:rtype: list of str"""
        vs_list = ['slot', 'label']
        if self.block_if is not None:
            vs_list.append('block')
        else:
            vs_list.append('label')
        vs_list.append('label')
        if self.block_else is not None:
            vs_list.append('block')
        else:
            vs_list.append('label')
        return vs_list

    def getLabels(self):
        """:rtype: list of str"""
        l_list = ['If (condition):']
        if self.block_if is None:
            l_list.append('   No block defined')
        l_list.append('Else:')
        if self.block_else is None:
            l_list.append('   No block defined')
        return l_list

    def generateMenu(self):
        Block.Block.generateMenu(self)
        for block_class in self.getWorkflowBlock().getListOfBlockClasses():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'set_standard_block_if', block_class.__name__, block_class.__name__), 'Set Block If.Standard')
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'set_standard_block_else', block_class.__name__, block_class.__name__), 'Set Block Else.Standard')

        for block_class in self.getWorkflowBlock().getListOfModels():
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'set_standard_block_if', block_class.__name__, block_class.__name__), 'Set Block If.Model')
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
                'set_standard_block_else', block_class.__name__, block_class.__name__), 'Set Block Else.Model')
