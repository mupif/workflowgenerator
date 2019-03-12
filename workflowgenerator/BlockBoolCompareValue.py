from . import tools
from . import Block
from . import DataSlot
from . import VisualMenu


class BlockBoolCompareValue (Block.Block):

    def __init__(self):
        Block.Block.__init__(self)
        self.addDataSlot(DataSlot.InputDataSlot("A", DataSlot.DataSlotType.PhysicalQuantity, False))
        self.addDataSlot(DataSlot.InputDataSlot("B", DataSlot.DataSlotType.PhysicalQuantity, False))
        self.addDataSlot(DataSlot.OutputDataSlot("result", DataSlot.DataSlotType.Bool, False))
        self.compare_operator = ">"

    def getInitCode(self, indent=0):
        return []

    def getInitializationCode(self, indent=0):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        return []

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        A_connected_slot = self.getDataSlotWithName("A").getLinkedDataSlot()
        B_connected_slot = self.getDataSlotWithName("B").getLinkedDataSlot()
        A_val = None
        B_val = None
        if A_connected_slot is not None:
            A_val = A_connected_slot.getParentBlock().generateOutputDataSlotGetFunction(A_connected_slot)
        if B_connected_slot is not None:
            B_val = B_connected_slot.getParentBlock().generateOutputDataSlotGetFunction(B_connected_slot)
        return "True if %s %s %s else False" % (A_val, self.compare_operator, B_val)

    def getBlocks(self, cls=None):
        return []

    def addBlock(self, block):
        pass

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def getVisualStructureItems(self):
        """:rtype: list of str"""
        return ['slot', 'slot', 'label', 'slot']

    def getLabels(self):
        """:rtype: list of str"""
        return ['True if A %s B else False' % self.compare_operator]

    def modificationQuery(self, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        if keyword == 'set_sign' and isinstance(value, str):
            self.compare_operator = value

    def generateMenu(self):
        Block.Block.generateMenu(self)
        available_signs = [">", ">=", "==", "===", "<=", "<", "!=", "!==", "is", "is not"]
        for sign in available_signs:
            self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem('set_sign', sign, sign), 'Set operator')
