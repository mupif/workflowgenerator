import mupif
from . import tools
from . import Block
from . import BlockSequentional
from . import DataSlot
from . import DataLink
from . import BlockModel
from . import VisualMenu

import os
import inspect
import importlib.util


class BlockWorkflow (BlockSequentional.BlockSequentional):

    list_of_models = []
    list_of_model_dependencies = []
    list_of_block_classes = []

    def __init__(self):
        BlockSequentional.BlockSequentional.__init__(self)
        self.datalinks = []
        self.loadListOfBlockClasses()

    def loadListOfBlockClasses(self):
        BlockWorkflow.list_of_block_classes = []
        BlockWorkflow.list_of_block_classes.append(BlockWorkflow)
        BlockWorkflow.list_of_block_classes.append(BlockModel.BlockModel)

    def getWorkflowBlock(self):
        """
        :rtype: BlockWorkflow.BlockWorkflow
        """
        return self

    def getParentBlock(self):
        """
        :rtype: None
        """
        return None

    def saveClassCodeToFile(self, filename):
        if self.checkConsistency():
            code = self.generateClassCode()
            print("Saving code to '%s'" % filename)
            f = open(filename, "w")
            f.write(tools.formatCodeToText(code))
            f.close()

    def saveExecutionCodeToFile(self, filename):
        if self.checkConsistency():
            code = self.generateExecutionCode()
            print("Saving code to '%s'" % filename)
            f = open(filename, "w")
            f.write(tools.formatCodeToText(code))
            f.close()

    def generateExecutionCode(self):
        return self.generateWorkflowCode(class_code=False)

    def generateClassCode(self):
        return self.generateWorkflowCode(class_code=True)

    def getAllElementCodeNames(self):
        code_names = [block.code_name for block in self.getBlocksRecursive()]
        code_names.extend([slot.code_name for slot in self.getSlotsRecursive()])
        return code_names

    def checkConsistency(self, execution=False):
        for ds in self.getSlotsRecursive():
            if not ds.getOptional() and not ds.connected():
                print("Some compulsory DataSlots are not connected.")
                return False
            if execution and (isinstance(ds, DataSlot.ExternalInputDataSlot)
                              or isinstance(ds, DataSlot.ExternalOutputDataSlot)):
                if ds.connected():
                    print("Usage of External DataSlots is not allowed in execution Workflow.")
                    return False
        return True

    def getAllExternalDataSlots(self, only=""):
        """
        :param string only: "in" or "out"
        :rtype: list of DataSlot.ExternalOutputDataSlot, DataSlot.ExternalInputDataSlot
        """
        eds = []  #: :type: list of (DataSlot.ExternalOutputDataSlot, DataSlot.ExternalInputDataSlot)
        for slot in self.getSlots():
            if isinstance(slot, DataSlot.ExternalInputDataSlot) and (only == "" or only == "in"):
                eds.append(slot)
            if isinstance(slot, DataSlot.ExternalOutputDataSlot) and (only == "" or only == "out"):
                eds.append(slot)
        return eds

    def generateAllElementCodeNames(self):
        for block in self.getBlocksRecursive():
            block.generateCodeName()
        for slot in self.getAllExternalDataSlots():
            slot.generateCodeName()

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        """
        :param DataSlot.DataSlot slot:
        :param str time:
        :rtype: str
        """
        return slot.getCodeRepresentation()

    def generateWorkflowCode(self, class_code):
        if class_code:
            workflow_classname = "MyProblemClassWorkflow"
        else:
            workflow_classname = "MyProblemExecutionWorkflow"

        #

        num_of_external_input_dataslots = 0

        self.generateAllElementCodeNames()

        all_model_blocks = self.getBlocksRecursive(BlockModel.BlockModel)
        child_blocks = self.getBlocks()

        code = ["import mupif"]

        printed_dependencies = []
        for model in all_model_blocks:
            if model.getModelDependency() not in printed_dependencies:
                code.append(model.getModelDependency())
                printed_dependencies.append(model.getModelDependency())

        code.append("")
        code.append("")
        code.append("class %s(mupif.Workflow.Workflow):" % workflow_classname)

        # __init__ function

        code.append("\t")
        code.append("\tdef __init__(self):")

        code.append("\t\tmetaData = {")
        code.append("\t\t\t'Inputs': [")

        code.append("\t\t\t],")
        code.append("\t\t\t'Outputs': [")

        code.append("\t\t\t],")
        code.append("\t\t}")

        code.append("\t\tmupif.Workflow.Workflow.__init__(self, metaData=metaData)")

        # metadata
        code.append("\t\tself.setMetadata('Name', '%s')" % workflow_classname)
        code.append("\t\tself.setMetadata('ID', '%s')" % workflow_classname)
        code.append("\t\tself.setMetadata('Description', '%s')" % "")
        code.append("\t\tself.setMetadata('Model_refs_ID', [])")

        if class_code:

            code_add = ""
            for s in self.getAllExternalDataSlots("out"):
                if s.connected():
                    num_of_external_input_dataslots += 1
                    params = "'Name': '%s', 'Type': '%s', 'required': %s, 'description': '%s', 'Type_ID': '%s', " \
                             "'Object_ID': '%s', 'ID': 0, 'Units': '', 'Required': True" % (
                                s.name, s.type, True, "",
                                s.getLinkedDataSlot().getObjType(), s.obj_id)

                    if code_add != "":
                        code_add = "%s, " % code_add
                    code_add = "%s{%s}" % (code_add, params)

            code.append("\t\tself.updateMetadata({'Inputs': [%s]})" % code_add)

            code_add = ""
            for s in self.getAllExternalDataSlots("in"):
                if s.connected():
                    params = "'Name': '%s', 'Type': '%s', 'required': %s, 'description': '%s', 'Type_ID': '%s', " \
                             "'Object_ID': '%s', 'ID': 0, 'Units': '', 'Required': False" % (
                                s.name, s.type, False, "",
                                s.getLinkedDataSlot().getObjType(), s.obj_id)

                    if code_add != "":
                        code_add = "%s, " % code_add
                    code_add = "%s{%s}" % (code_add, params)

            code.append("\t\tself.updateMetadata({'Outputs': [%s]})" % code_add)

            # initialization of workflow inputs
            for s in self.getAllExternalDataSlots("out"):
                if s.connected():
                    code.append("\t")
                    code.append("\t\t# initialization code of external input")
                    code.append("\t\tself.%s = None" % s.code_name)
                    code.append("\t\t# It should be defined from outside using set() method.")

        # init codes of child blocks

        for model in self.getBlocksRecursive():
            code.extend(model.getInitCode(2))

        # initialize function

        code.append("\t")
        code.append("\tdef initialize(self, file='', workdir='', targetTime=mupif.Physics.PhysicalQuantities.PhysicalQuantity(0., 's'), metaData={}, validateMetaData=True, **kwargs):")
        # code.append("\t\tself.updateMetadata(metaData)")

        code.append("\t\t")

        code.append("\t\tmupif.Workflow.Workflow.initialize(self, file=file, workdir=workdir, targetTime=targetTime, metaData=metaData, validateMetaData=validateMetaData, **kwargs)")

        code.append("\t\t")
        code.append("\t\texecMD = {")
        code.append("\t\t\t'Execution': {")
        code.append("\t\t\t\t'ID': self.getMetadata('Execution.ID'),")
        code.append("\t\t\t\t'Use_case_ID': self.getMetadata('Execution.Use_case_ID'),")
        code.append("\t\t\t\t'Task_ID': self.getMetadata('Execution.Task_ID')")
        code.append("\t\t\t}")
        code.append("\t\t}")

        for model in all_model_blocks:
            code.extend(model.getInitializationCode(2, "execMD"))

        # get critical time step

        if class_code:
            code.append("\t")
            code.append("\tdef getCriticalTimeStep(self):")
            code_add = ""
            i = 0
            for model in child_blocks:
                if isinstance(model, BlockModel.BlockModel):
                    if i:
                        code_add += ", "
                    code_add += "self.%s.getCriticalTimeStep()" % model.code_name
                    i += 1
            code.append("\t\treturn min([%s])" % code_add)

        if class_code:
            #
            #
            # set method

            code.append("\t")
            code.append("\t# set method for all external inputs")
            code.append("\tdef set(self, obj, objectID=0):")
            code.append("\t\t\t")
            code.append("\t\t# in case of Property")
            code.append("\t\tif isinstance(obj, mupif.Property.Property):")
            code.append("\t\t\tpass")
            for s in self.getAllExternalDataSlots("out"):
                if s.connected():
                    if s.type == 'mupif.Property':
                        code.append("\t\t\tif objectID == '%s':" % s.name)
                        code.append("\t\t\t\tself.%s = obj" % s.code_name)

            code.append("\t\t\t")
            code.append("\t\t# in case of Field")
            code.append("\t\tif isinstance(obj, mupif.Field.Field):")
            code.append("\t\t\tpass")
            for s in self.getAllExternalDataSlots("out"):
                if s.connected():
                    if s.type == 'mupif.Field':
                        code.append("\t\t\tif objectID == '%s':" % s.name)
                        code.append("\t\t\t\tself.%s = obj" % s.code_name)

            #
            #
            # get method

            code.append("\t")
            code.append("\t# get method for all external outputs")
            code.append("\tdef get(self, objectType, time=None, objectID=0):")
            code.append("\t\t\t")
            code.append("\t\t# in case of Property")
            code.append("\t\tif isinstance(objectType, mupif.PropertyID):")
            code.append("\t\t\tpass")
            for s in self.getAllExternalDataSlots("in"):
                if s.connected():
                    if s.type == 'mupif.Property':
                        code.append("\t\t\tif objectID == '%s':" % s.name)
                        code.append("\t\t\t\treturn self.%s" %
                                    s.getLinkedDataSlot().getParentBlock().generateOutputDataSlotGetFunction(
                                        s.getLinkedDataSlot(), 'time'))

            code.append("\t\t\t")
            code.append("\t\t# in case of Field")
            code.append("\t\tif isinstance(objectType, mupif.FieldID):")
            code.append("\t\t\tpass")
            for s in self.getAllExternalDataSlots("in"):
                if s.connected():
                    if s.type == 'mupif.Field':
                        code.append("\t\t\tif objectID == '%s':" % s.name)
                        code.append("\t\t\t\treturn %s" %
                                    s.getLinkedDataSlot().getParentBlock().generateOutputDataSlotGetFunction(
                                        s.getLinkedDataSlot(), 'time'))

            code.append("\t\t")
            code.append("\t\treturn None")

        # terminate

        code.append("\t")
        code.append("\tdef terminate(self):")
        for model in all_model_blocks:
            code.append("\t\tself.%s.terminate()" % model.code_name)
        code.append("\t")

        # solve or solveStep

        if class_code:
            code.append("\tdef solveStep(self, tstep, stageID=0, runInBackground=False):")
        else:
            code.append("\tdef solve(self, runInBackground=False):")

        for model in child_blocks:
            code.extend(model.getExecutionCode(2, "tstep.getTime()"))

        if not class_code:
            code.append("\t\t# terminate all models")
            code.append("\t\tself.terminate()")
            code.append("")

        code.append("")

        # execution

        if not class_code or num_of_external_input_dataslots == 0:
            code.append("if __name__ == '__main__':")
            code.append("\tproblem = %s()" % workflow_classname)
            code.append("\t")
            code.append("\tmd = {")
            code.append("\t\t'Execution': {")
            code.append("\t\t\t'ID': 'N/A',")
            code.append("\t\t\t'Use_case_ID': 'N/A',")
            code.append("\t\t\t'Task_ID': 'N/A'")
            code.append("\t\t}")
            code.append("\t}")
            code.append("\tproblem.initialize(metaData=md)")
            code.append("\tproblem.solve()")
            code.append("\tproblem.terminate()")
            code.append("\t")
            code.append("\tprint('Simulation has finished.')")
            code.append("")

        return tools.replace_tabs_with_spaces_for_each_line(code)

    @staticmethod
    def getListOfModelClassnames():
        array = [m.__name__ for m in BlockWorkflow.list_of_models]
        return array

    @staticmethod
    def loadModelsFromGivenFile(full_path):
        mod_name, file_ext = os.path.splitext(os.path.split(full_path)[-1])
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        py_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_mod)
        for mod in dir(py_mod):
            if not mod[0] == "_":
                my_class = getattr(py_mod, mod)
                if hasattr(my_class, '__name__'):
                    if my_class.__name__ not in BlockWorkflow.getListOfModelClassnames() and inspect.isclass(my_class):
                        if issubclass(my_class, mupif.Application.Application) or issubclass(my_class,
                                                                                            mupif.Workflow.Workflow):
                            BlockWorkflow.list_of_models.append(my_class)
                            BlockWorkflow.list_of_model_dependencies.append("from %s import %s" % (
                                py_mod.__name__, my_class.__name__))

    def getDataLinks(self):
        """
        :rtype: list of DataLink.DataLink
        """
        return self.datalinks

    def getDataLinksOfSlot(self, slot):
        dls = []
        for dl in self.getDataLinks():
            if dl.containsSlot(slot):
                dls.append(dl)
        return dls

    def addDataLink(self, datalink):
        self.datalinks.append(datalink)

    def removeDataLink(self, datalink):
        idx = self.datalinks.index(datalink)
        if idx is not None:
            del self.datalinks[idx]

    @staticmethod
    def getListOfModels():
        """:rtype: list of class"""
        return BlockWorkflow.list_of_models

    @staticmethod
    def getListOfBlockClasses():
        """:rtype: list of class"""
        return BlockWorkflow.list_of_block_classes

    def getBlockWithUID(self, uid):
        """
        :param str uid:
        :rtype: Block.Block
        """
        for block in self. getBlocksRecursive():
            if block.getUID() == uid:
                return block
        return None

    def getSlotWithUID(self, uid):
        for slot in self. getSlotsRecursive():
            if slot.getUID() == uid:
                return slot
        return None

    def connectSlotsWithUID(self, uid_1, uid_2):
        slot_1 = self.getSlotWithUID(uid_1)
        slot_2 = self.getSlotWithUID(uid_2)
        if isinstance(slot_1, DataSlot.DataSlot) and isinstance(slot_2, DataSlot.DataSlot):
            slot_1.connectTo(slot_2)

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------
    
    def modificationQueryForItemWithUID(self, uid, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        elem = self.getBlockWithUID(uid)
        if elem is not None:
            elem.modificationQuery(keyword, value)

    def generateMenu(self):
        self.menu = VisualMenu.VisualMenu()
        self.generateAddBlockMenuItems()
