import mupif
from . import tools
from . import Block
from . import DataSlot
from . import BlockWorkflow

import os
import inspect
import importlib.util


class BlockModel (Block.Block):
    """
    Implementation of a block representing model
    """
    def __init__(self, model):
        """
        :param object model:
        """
        Block.Block.__init__(self)

        self.model = model
        self.model_module = model.__module__
        self.name = model.__class__.__name__
        self.input_file_name = ""
        self.input_file_directory = "."

    def setInputFile(self, val):
        """
        Sets the input file name.
        :param str val: Input file name
        """
        self.input_file_name = val

    def setInputFilePath(self, val):
        """
        Sets the input file directory.
        :param str val: Input file directory.
        """
        self.input_file_directory = val

    # def getInputSlots(self):
    #     return self.model.getInputSlots()
    #
    # def getOutputSlots(self):
    #     return self.model.getOutputSlots()

    def getInitCode(self, indent=0):
        """
        Generates the initialization code of this block.
        :param int indent: number of indents to be added before each line
        :return: list of code lines
        :rtype: str[]
        """
        code = Block.Block.getInitCode(self)
        input_file_add = ""
        if self.input_file_name != "":
            input_file_add = "file='%s', workdir='%s'" % (self.input_file_name, self.input_file_directory)
        # code.append("self.%s = %s(%s)" % (self.code_name, self.name, input_file_add))
        code.append("self.%s = %s.%s(%s)" % (self.code_name, self.model_module, self.name, input_file_add))
        return tools.push_indents_before_each_line(code, indent)

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        code = Block.Block.getExecutionCode(self)

        for slot in self.getSlots(DataSlot.InputDataSlot):
            linked_slot = slot.getLinkedDataSlot()
            if linked_slot:
                code.append("self.%s.set(%s, %s)" % (
                    self.code_name, linked_slot.getParentBlock().generateOutputDataSlotGetFunction(linked_slot, time),
                    "'%s'" % slot.obj_id if isinstance(slot.obj_id, str) else str(slot.obj_id)))

        code.append("self.%s.solveStep(%s)" % (self.code_name, timestep))

        return tools.push_indents_before_each_line(code, indent)

    def getDictForJSON(self):
        answer = Block.Block.getDictForJSON(self)
        answer.update({'model_classname': self.name})
        answer.update({'model_input_file_name': self.input_file_name})
        answer.update({'model_input_file_directory': self.input_file_directory})
        return answer

    def initializeFromJSONData(self, json_data):
        Block.Block.initializeFromJSONData(self, json_data)
        self.input_file_name = json_data['model_input_file_name']
        self.input_file_directory = json_data['model_input_file_directory']

    def constructFromModelMetaData(self):
        model = self.model
        if model.hasMetadata('name') and model.hasMetadata('inputs') and model.hasMetadata('outputs'):
            self.name = self.model = model.getMetadata('name')
            for slot in model.getMetadata('inputs'):
                obj_id = 0
                if 'obj_id' in slot:
                    obj_id = slot['obj_id']
                self.addDataSlot(
                    DataSlot.InputDataSlot(
                        slot['name'], DataSlot.DataSlotType.getTypeFromName(slot['type']), slot['optional'],
                        slot['obj_type'], obj_id))
            for slot in model.getMetadata('outputs'):
                obj_id = 0
                if 'obj_id' in slot:
                    obj_id = slot['obj_id']
                self.addDataSlot(
                    DataSlot.OutputDataSlot(
                        slot['name'], DataSlot.DataSlotType.getTypeFromName(slot['type']), slot['optional'],
                        slot['obj_type'], obj_id))

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
                    if my_class.__name__ not in BlockWorkflow.BlockWorkflow.getListOfModelClassnames() and inspect.isclass(my_class):
                        if issubclass(my_class, mupif.Application.Application) or issubclass(my_class,
                                                                                            mupif.Workflow.Workflow):
                            BlockWorkflow.BlockWorkflow.list_of_models.append(my_class)
                            BlockWorkflow.BlockWorkflow.list_of_model_dependencies.append("from %s import %s" % (
                                py_mod.__name__, my_class.__name__))

    def generateCodeName(self, base_name='model_'):
        Block.Block.generateCodeName(self, base_name)

    def getIDOfModelNameInList(self, model_name):
        if model_name in BlockWorkflow.BlockWorkflow.getListOfModelClassnames():
            return BlockWorkflow.BlockWorkflow.getListOfModelClassnames().index(model_name)
        return -1

    def getModelDependency(self):
        return "import %s" % self.model_module
        # model_id = self.getIDOfModelNameInList(self.name)
        # if model_id > -1:
        #     return BlockWorkflow.BlockWorkflow.list_of_model_dependencies[model_id]
        # return "# dependency of %s not found" % self.code_name

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        """
        Returns code of get function for given dataslot.
        :param DataSlot.DataSlot slot:
        :param str time:
        :return:
        :rtype: str
        """
        if slot in self.getSlots(DataSlot.OutputDataSlot):
            if isinstance(slot.obj_id, str):
                obj_id = "'%s'" % slot.obj_id
            else:
                obj_id = str(slot.obj_id)
            return "self.%s.get(%s, %s, %s)" % (self.code_name, slot.obj_type, time, obj_id)
        return "None"

    def getHeaderText(self):
        """:rtype: str"""
        return "%s - %s" % (self.__class__.__name__, self.name)

