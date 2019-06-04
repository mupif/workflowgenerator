import mupif
from . import tools
from . import Block
from . import BlockSequentional
from . import DataSlot
from . import DataLink
from . import BlockModel
from . import VisualMenu
from . import BlockConstPhysicalQuantity
from . import BlockConstProperty
from . import BlockTimeloop
from . import BlockBoolCompareValue
from . import BlockIfElse

import os
import sys
import inspect
import importlib.util


class BlockWorkflow (BlockSequentional.BlockSequentional):

    list_of_block_classes = []

    list_of_model_metadata = []

    def __init__(self):
        BlockSequentional.BlockSequentional.__init__(self)
        self.datalinks = []
        self.loadListOfBlockClasses()

    def loadListOfBlockClasses(self):
        BlockWorkflow.list_of_block_classes = []
        BlockWorkflow.list_of_block_classes.append(BlockConstPhysicalQuantity.BlockConstPhysicalQuantity)
        BlockWorkflow.list_of_block_classes.append(BlockConstProperty.BlockConstProperty)
        BlockWorkflow.list_of_block_classes.append(BlockTimeloop.BlockTimeloop)
        BlockWorkflow.list_of_block_classes.append(BlockBoolCompareValue.BlockBoolCompareValue)
        BlockWorkflow.list_of_block_classes.append(BlockIfElse.BlockIfElse)
        BlockWorkflow.list_of_block_classes.append(BlockSequentional.BlockSequentional)

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
        code.append("\tdef __init__(self, metaData={}):")

        code.append("\t\tMD = {")
        code.append("\t\t\t'Inputs': [")

        code.append("\t\t\t],")
        code.append("\t\t\t'Outputs': [")

        code.append("\t\t\t],")
        code.append("\t\t}")

        code.append("\t\tmupif.Workflow.Workflow.__init__(self, metaData=MD)")

        # metadata
        code.append("\t\tself.setMetadata('Name', '%s')" % workflow_classname)
        code.append("\t\tself.setMetadata('ID', '%s')" % workflow_classname)
        code.append("\t\tself.setMetadata('Description', '%s')" % "")

        code.append("\t\tself.updateMetadata(metaData)")

        if class_code:

            code_add = ""
            for s in self.getAllExternalDataSlots("out"):
                if s.connected():
                    num_of_external_input_dataslots += 1
                    params = "'Name': '%s', 'Type': '%s', 'required': %s, 'description': '%s', 'Type_ID': '%s', " \
                             "'Obj_ID': ['%s'], 'ID': 0, 'Units': '', 'Required': True" % (
                                s.name, s.type, True, "",
                                s.getLinkedDataSlot().getObjType(), s.getObjID())

                    if code_add != "":
                        code_add = "%s, " % code_add
                    code_add = "%s{%s}" % (code_add, params)

            code.append("\t\tself.updateMetadata({'Inputs': [%s]})" % code_add)

            code_add = ""
            for s in self.getAllExternalDataSlots("in"):
                if s.connected():
                    params = "'Name': '%s', 'Type': '%s', 'required': %s, 'description': '%s', 'Type_ID': '%s', " \
                             "'Obj_ID': ['%s'], 'ID': 0, 'Units': '', 'Required': False" % (
                                s.name, s.type, False, "",
                                s.getLinkedDataSlot().getObjType(), s.getObjID())

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

        code.append("")

        for model in all_model_blocks:
            code.append("\t\tself.registerModel(self.%s)" % model.getCodeName())

        # initialize function

        code.append("\t")
        code.append(
            "\tdef initialize(self, file='', workdir='', "
            "targetTime=mupif.Physics.PhysicalQuantities.PhysicalQuantity(0., 's'), "
            "metaData={}, validateMetaData=True, **kwargs):"
        )

        code.append("\t\t")

        code.append("\t\tself.updateMetadata(dictionary=metaData)")

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

        code.append("\t\t")

        code.append(
            "\t\tmupif.Workflow.Workflow.initialize(self, file=file, workdir=workdir, targetTime=targetTime, "
            "metaData={}, validateMetaData=validateMetaData, **kwargs)"
        )

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
            code.append("\tproblem.printMetadata()")
            code.append("\tproblem.terminate()")
            code.append("\t")
            code.append("\tprint('Simulation has finished.')")
            code.append("")

        return tools.replace_tabs_with_spaces_for_each_line(code)

    @staticmethod
    def getListOfModelClassnames():
        # array = [m.__name__ for m in BlockWorkflow.list_of_models]
        array = [m['workflowgenerator_classname'] for m in BlockWorkflow.list_of_model_metadata]
        return array

    @staticmethod
    def getListOfBlockClassnames():
        array = [m.__name__ for m in BlockWorkflow.getListOfBlockClasses()]
        return array

    @staticmethod
    def loadModelsFromGivenFile(full_path):
        mod_name, file_ext = os.path.splitext(os.path.split(full_path)[-1])
        directory = os.path.split(full_path)[0]
        # print(directory)
        if directory is not '':
            sys.path.append(directory)
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        py_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_mod)
        for mod in dir(py_mod):
            if not mod[0] == "_":
                my_class = getattr(py_mod, mod)
                if hasattr(my_class, '__name__'):
                    if my_class.__name__ not in BlockWorkflow.getListOfModelClassnames() and inspect.isclass(my_class):
                        is_sub_model = issubclass(my_class, mupif.Model.Model)
                        is_sub_workflow = issubclass(my_class, mupif.Workflow.Workflow)

                        if is_sub_model or is_sub_workflow:
                            instance = my_class()
                            md = instance.getAllMetadata()
                            md.update({'workflowgenerator_classname': my_class.__name__})
                            md.update({'workflowgenerator_module': my_class.__module__})
                            BlockWorkflow.list_of_model_metadata.append(md)

    @staticmethod
    def loadCustomStandardBlocksFromGivenFile(full_path):
        mod_name, file_ext = os.path.splitext(os.path.split(full_path)[-1])
        directory = os.path.split(full_path)[0]
        # print(directory)
        if directory is not '':
            sys.path.append(directory)
        spec = importlib.util.spec_from_file_location(mod_name, full_path)
        py_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_mod)
        for mod in dir(py_mod):
            if not mod[0] == "_":
                my_class = getattr(py_mod, mod)
                if hasattr(my_class, '__name__'):
                    if my_class.__name__ not in BlockWorkflow.getListOfModelClassnames() and inspect.isclass(my_class):
                        is_sub_model = issubclass(my_class, mupif.Model.Model)
                        is_sub_workflow = issubclass(my_class, mupif.Workflow.Workflow)
                        is_sub_block = issubclass(my_class, Block.Block)

                        if is_sub_block and not is_sub_model and not is_sub_workflow:
                            BlockWorkflow.list_of_block_classes.append(my_class)

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
    def getListOfModelMetadata():
        """:rtype: list of class"""
        return BlockWorkflow.list_of_model_metadata

    @staticmethod
    def getListOfBlockClasses():
        """:rtype: list of class"""
        return BlockWorkflow.list_of_block_classes

    def getBlockWithUID(self, uid):
        """
        :param str uid:
        :rtype: Block.Block
        """
        if self.getUID() == uid:
            return self
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

    def convertToJSON(self):
        return_json_array = [self.getDictForJSON()]
        return_json_array.extend([k.getDictForJSON() for k in self.getSlots()])
        return_json_array.extend([k.getDictForJSON() for k in self.getBlocksRecursive()])
        return_json_array.extend([k.getDictForJSON() for k in self.getDataLinks()])
        return return_json_array

    def initializeFromJSONData(self, json_data):
        self.uuid = json_data['uuid']

    def constructFromJSON(self, json_data):
        self.deleteAllItems()
        block_classes = self.getListOfBlockClasses()
        block_classes.append(BlockModel.BlockModel)
        for item in json_data:
            try:
                if item['classname'] == 'BlockWorkflow':
                    self.initializeFromJSONData(item)
                    print("setting BlockWorkflow")

                elif item['classname'] == 'DataLink':
                    s1 = self.getSlotWithUID(item['ds1_uid'])
                    s2 = self.getSlotWithUID(item['ds2_uid'])
                    if isinstance(s1, DataSlot.DataSlot) and isinstance(s2, DataSlot.DataSlot):
                        new_dl = DataLink.DataLink(s1, s2)
                        self.addDataLink(new_dl)
                    else:
                        print("Some slots were not found.")

                elif item['classname'] == 'ExternalInputDataSlot':
                    new_ds = DataSlot.ExternalInputDataSlot(
                        item['name'],
                        item['type'],
                        True,
                        item['obj_type'],
                        item['obj_id']
                    )
                    new_ds.setUUID(item['uuid'])
                    self.addDataSlot(new_ds)

                elif item['classname'] == 'ExternalOutputDataSlot':
                    new_ds = DataSlot.ExternalOutputDataSlot(
                        item['name'],
                        item['type'],
                        False,
                        item['obj_type'],
                        item['obj_id']
                    )
                    new_ds.setUUID(item['uuid'])
                    self.addDataSlot(new_ds)

                else:
                    for block_class in block_classes:

                        if item['classname'] == block_class.__name__:
                            print("setting %s" % block_class.__name__)
                            new_block = None

                            if block_class.__name__ == 'BlockModel' and False:
                                if item['model_classname'] in self.getListOfModelClassnames():
                                    model_index = self.getListOfModelClassnames().index(item['model_classname'])
                                    new_model_md = self.getListOfModelMetadata()[model_index]
                                    # new_block = block_class(self.getListOfModels()[model_index]())
                                    new_block = BlockModel.BlockModel(model_md=new_model_md)
                                    new_block.constructFromModelMetaData()
                                else:
                                    print("Model is not in list of known models.")
                            else:
                                new_block = block_class()

                            parent_block = self.getBlockWithUID(item['parent_uuid'])
                            if parent_block is not None:
                                parent_block.addBlock(new_block)
                                new_block.setParentBlock(parent_block)
                                new_block.initializeFromJSONData(item)

                            else:
                                print("Parent block was not found.")
                            break

            except KeyError:
                print("Something could not have been loaded.")

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def modificationQueryForItemWithUID(self, uid, keyword, value=None):
        """
        :param str uid:
        :param str keyword:
        :param value:
        """
        if self.getUID() == uid:
            self.modificationQuery(keyword, value)
        else:
            elem = self.getBlockWithUID(uid)
            if elem is not None:
                elem.modificationQuery(keyword, value)

    def generateMenu(self):
        self.menu = VisualMenu.VisualMenu()
        self.generateAddBlockMenuItems()
