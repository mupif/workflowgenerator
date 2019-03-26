import mupif
from . import tools
from . import Block
from . import DataSlot
from . import VisualMenu


class BlockConstPhysicalQuantity (Block.Block):
    """
    Implementation of sequential processing block
    """
    def __init__(self):
        Block.Block.__init__(self)
        self.addDataSlot(DataSlot.OutputDataSlot("value", 'mupif.PhysicalQuantity', False))
        self.value = 0.
        self.units = None

    def getDictForJSON(self):
        """
        :rtype: dict
        """
        answer = Block.Block.getDictForJSON(self)
        answer.update({'value': self.value})
        answer.update({'units': self.units})
        return answer

    def initializeFromJSONData(self, json_data):
        Block.Block.initializeFromJSONData(self, json_data)
        self.setValue(json_data['value'])
        self.setUnits(json_data['units'])

    def generateCodeName(self, base_name='constant_physical_quantity_'):
        Block.Block.generateCodeName(self, base_name)

    def getInitCode(self, indent=0):
        """
        Generates the initialization code of this block.
        :param int indent: number of indents to be added before each line
        :return: array of code lines
        :rtype: str[]
        """
        if self.getDataSlotWithName("value").connected():
            code = Block.Block.getInitCode(self)
            code.append("self.%s = mupif.Physics.PhysicalQuantities.PhysicalQuantity(%s, "
                        "mupif.Physics.PhysicalQuantities._unit_table['%s'])" % (
                            self.code_name, self.value, self.units))
            return tools.push_indents_before_each_line(code, indent)
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        return []

    def setValue(self, val):
        self.value = val

    def setUnits(self, val):
        self.units = val

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        """
        Returns code of get function for given dataslot.
        :param DataSlot.DataSlot slot:
        :param str time:
        :return: Python code representation
        :rtype: str
        """
        if slot in self.getSlots(DataSlot.OutputDataSlot):
            return "self.%s" % self.code_name
        return "None"

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def getLabels(self):
        """:rtype: list of str"""
        return ["value = %s\nunits = %s" % (self.value, self.units)]

    def modificationQuery(self, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        if keyword == 'set_units' and isinstance(value, str):
            items = []
            items.extend(list(map(str, mupif.Physics.PhysicalQuantities._unit_table)))
            items_real = []
            items_real.extend(list(mupif.Physics.PhysicalQuantities._unit_table))
            if value is not None:
                if value in items:
                    selected_id = items.index(value)
                    self.setUnits(items_real[selected_id])
        elif keyword == 'set_value' and isinstance(value, float):
            self.setValue(value)
        else:
            Block.Block.modificationQuery(self, keyword, value)

    def generateMenu(self):
        Block.Block.generateMenu(self)

        options = list(map(str, mupif.Physics.PhysicalQuantities._unit_table))
        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
            'set_units', None, "Set units", "select", "Set units", options), 'Modify')

        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
            'set_value', None, "Set value", "float", "Set value"), 'Modify')
