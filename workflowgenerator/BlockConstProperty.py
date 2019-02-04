from . import tools
from . import Block
from . import DataSlot


class BlockConstProperty (Block.Block):
    """
    Implementation of sequential processing block
    """
    def __init__(self):
        Block.Block.__init__(self)
        self.addDataSlot(DataSlot.OutputDataSlot("value", DataSlot.DataSlotType.Property, False))
        self.value = ()
        self.propID = None
        self.valueType = None
        self.units = None
        self.objectID = 0

    def getDictForJSON(self):
        answer = Block.Block.getDictForJSON(self)
        answer.update({'value': self.value})
        answer.update({'propID': str(self.propID)})
        answer.update({'valueType': str(self.valueType)})
        answer.update({'units': self.units})
        answer.update({'objectID': str(self.objectID)})
        return answer

    def initializeFromJSONData(self, json_data):
        Block.Block.initializeFromJSONData(self, json_data)
        t = ()
        for e in json_data['value']:
            t = t + (float(e),)
        self.setValue(t)
        self.setPropertyID(json_data['propID'])
        self.setValueType(json_data['valueType'])
        self.setUnits(json_data['units'])
        self.setObjectID(json_data['objectID'])

    def generateCodeName(self, base_name='constant_property_'):
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
            code.append(
                "self.%s = mupif.Property.ConstantProperty("
                "%s, mupif.%s, mupif.%s, mupif.Physics.PhysicalQuantities._unit_table['%s'], "
                "None, %s)" % (
                            self.code_name, self.value, self.propID, self.valueType, self.units, self.objectID))
            return tools.push_indents_before_each_line(code, indent)
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        return []

    def setValue(self, val):
        self.value = val

    def setPropertyID(self, val):
        self.propID = val

    def setValueType(self, val):
        self.valueType = val

    def setObjectID(self, val):
        self.objectID = val

    def setUnits(self, val):
        self.units = val

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        """
        Returns code of get function for given dataslot.
        :param DataSlot.DataSlot slot:
        :param str time:
        :return:
        :rtype: str
        """
        if slot in self.getSlots(DataSlot.OutputDataSlot):
            return "self.%s" % self.code_name
        return "None"