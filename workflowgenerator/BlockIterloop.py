from . import tools
from . import Block
from . import DataSlot
from . import BlockModel
from . import BlockSequentional


class BlockIterloop (BlockSequentional.BlockSequentional):
    """
    Implementation of while timeloop block
    """
    def __init__(self):
        BlockSequentional.BlockSequentional.__init__(self)
        self.addDataSlot(DataSlot.InputDataSlot("tolerance", 'mupif.PhysicalQuantity', False))
        self.addDataSlot(DataSlot.InputDataSlot("field", 'mupif.Field', False))

    def getTolerance(self):
        connected_slot = self.getDataSlotWithName("tolerance").getLinkedDataSlot()
        if connected_slot:
            return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot)
        return None

    def getField(self, time=''):
        connected_slot = self.getDataSlotWithName("field").getLinkedDataSlot()
        if connected_slot:
            return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot, time)
        return None

    def getInitCode(self, indent=0):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)
        var_field = "%s_field" % self.code_name
        var_field_prev = "%s_field_prev" % self.code_name
        var_compute = "%s_compute" % self.code_name
        var_tolerance = "%s_tolerance" % self.code_name
        var_norm = "%s_norm" % self.code_name
        var_iter_number = "%s_iter_number" % self.code_name

        code.append("%s = %s" % (var_field, None))
        code.append("%s = %s" % (var_field_prev, None))
        code.append("%s = True" % var_compute)
        code.append("%s = %s" % (var_tolerance, self.getTolerance()))
        code.append("%s = 2.*%s" % (var_norm, self.getTolerance()))
        code.append("%s = 0" % var_iter_number)

        code.append("while %s:" % var_compute)

        code.append("\t%s += 1" % var_iter_number)
        code.append("\tprint('Iteration number %%d' %% %s)" % var_iter_number)

        code.append("")
        for block in self.getBlocks(BlockModel.BlockModel):
            code.extend(block.getExecutionCode(1, "%s.getTime()" % timestep, timestep))
        code.append("")

        code.append("\t%s = copy.deepcopy(%s)" % (var_field, self.getField(time)))  # "%s.getTime()" % timestep

        code.append("\tif %s > 1:" % var_iter_number)
        code.append("\t\t%s = copy.deepcopy(%s)" % (var_field_prev, var_field))

        code.append("\tif %s is not None and %s is not None:" % (var_field_prev, var_field))
        code.append("\t\t%s = mupif.Field.Field.subtractValuesAndNorm(%s, %s)" % (var_norm, var_field_prev, var_field))
        code.append("\t\tif %s < %s.getValue():" % (var_norm, var_tolerance))
        code.append("\t\t\t%s = False" % var_compute)

        code.append("")

        return tools.push_indents_before_each_line(code, indent)

    def generateCodeName(self, base_name='iterloop_'):
        Block.Block.generateCodeName(self, base_name)
