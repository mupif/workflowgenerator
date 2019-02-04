from . import tools
from . import Block
from . import DataSlot
from . import BlockModel


class BlockTimeloop (Block.Block):
    """
    Implementation of sequential processing block
    """
    def __init__(self):
        Block.Block.__init__(self)
        self.addDataSlot(DataSlot.InputDataSlot("start_time", DataSlot.DataSlotType.PhysicalQuantity, False))
        self.addDataSlot(DataSlot.InputDataSlot("target_time", DataSlot.DataSlotType.PhysicalQuantity, False))
        self.addDataSlot(DataSlot.InputDataSlot("max_dt", DataSlot.DataSlotType.PhysicalQuantity, True))

    def getStartTime(self):
        connected_slot = self.getDataSlotWithName("start_time").getLinkedDataSlot()
        if connected_slot:
            return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot)
        return None

    def getTargetTime(self):
        connected_slot = self.getDataSlotWithName("target_time").getLinkedDataSlot()
        if connected_slot:
            return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot)
        return None

    def getMaxDt(self):
        connected_slot = self.getDataSlotWithName("max_dt").getLinkedDataSlot()
        if connected_slot:
            return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot)
        return None

    def getInitCode(self, indent=0):
        return []

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)
        var_time = "%s_time" % self.code_name
        var_target_time = "%s_target_time" % self.code_name
        var_dt = "%s_dt" % self.code_name
        var_compute = "%s_compute" % self.code_name
        var_time_step = "%s_time_step" % self.code_name
        var_time_step_number = "%s_time_step_number" % self.code_name

        code.append("time_units = mupif.Physics.PhysicalQuantities.PhysicalUnit('s', 1., [0, 0, 1, 0, 0, 0, 0, 0, 0])")

        code.append("%s = %s" % (var_time, self.getStartTime()))
        code.append("%s = %s" % (var_target_time, self.getTargetTime()))

        code.append("%s = True" % var_compute)
        code.append("%s = 0" % var_time_step_number)

        code.append("while %s:" % var_compute)
        while_code = []

        code.append("\t%s += 1" % var_time_step_number)

        dt_code = "\t%s = min([" % var_dt
        first = True

        if self.getMaxDt():
            dt_code += self.getMaxDt()
            first = False

        for model in self.getBlocks(BlockModel.BlockModel):
            if not first:
                dt_code += ", "
            dt_code += "self.%s.getCriticalTimeStep()" % model.code_name
            first = False
        dt_code += "])"

        while_code.append("")
        while_code.append(dt_code)
        while_code.append("\t%s = min(%s+%s, %s)" % (var_time, var_time, var_dt, var_target_time))
        while_code.append("")

        while_code.append("\tif %s.inUnitsOf(time_units).getValue() + 1.e-6 > %s.inUnitsOf(time_units).getValue():" % (
            var_time, var_target_time))
        while_code.append("\t\t%s = False" % var_compute)

        while_code.append("\t")
        while_code.append("\t%s = mupif.TimeStep.TimeStep(%s, %s, %s, n=%s)" % (
            var_time_step, var_time, var_dt, var_target_time, var_time_step_number))
        # while_code.append("\t")

        for block in self.getBlocks(BlockModel.BlockModel):
            while_code.extend(block.getExecutionCode(1, "%s.getTime()" % var_time_step, var_time_step))

        code.extend(while_code)
        code.append("")

        return tools.push_indents_before_each_line(code, indent)

    def generateCodeName(self, base_name='timeloop_'):
        Block.Block.generateCodeName(self, base_name)
