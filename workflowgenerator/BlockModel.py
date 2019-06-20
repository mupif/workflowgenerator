import mupif
from . import tools
from . import Block
from . import DataSlot
from . import BlockWorkflow
from . import VisualMenu


class BlockModel (Block.Block):
    """
    Implementation of a block representing model
    """
    def __init__(self, model=None, model_md=None):  # TODO
        """
        :param mupif.Model.Model or mupif.Model.RemoteModel or mupif.Workflow.Workflow model:
        """
        Block.Block.__init__(self)

        self.model_module = 'undefined'
        self.name = 'undefined'
        self.model_metadata_inputs = {}
        self.model_metadata_outputs = {}

        if model is not None:
            self.model_module = model.__module__
            self.name = model.__class__.__name__
            md = model.getAllMetadata()
            if model.hasMetadata('Inputs'):
                self.model_metadata_inputs = md['Inputs']
            if model.hasMetadata('Outputs'):
                self.model_metadata_outputs = md['Outputs']
        elif model_md is not None:
            self.model_module = model_md['workflowgenerator_module']
            self.name = model_md['workflowgenerator_classname']
            self.model_metadata_inputs = model_md['Inputs']
            self.model_metadata_outputs = model_md['Outputs']

        self.input_file_name = ""
        self.input_file_directory = ""

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

    def getInitCode(self, indent=0):
        """
        Generates the __init__ code of this block.
        :param int indent: number of indents to be added before each line
        :return: list of code lines
        :rtype: str[]
        """
        code = Block.Block.getInitCode(self)
        if self.model_module == "":
            code.append("self.%s = %s()" % (self.code_name, self.name))
        else:
            code.append("self.%s = %s.%s()" % (self.code_name, self.model_module, self.name))
        return tools.push_indents_before_each_line(code, indent)

    def getInitializationCode(self, indent=0, metaDataStr="{}"):
        """
        Generates the initialization code of this block.
        :param int indent: number of indents to be added before each line
        :param str metaDataStr:
        :return: list of code lines
        :rtype: str[]
        """
        code = Block.Block.getInitializationCode(self)
        input_file_add = ""
        if self.input_file_name != "":
            input_file_add = "file='%s', workdir='%s', " % (self.input_file_name, self.input_file_directory)
        code.append("self.%s.initialize(%smetaData=%s)" % (self.code_name, input_file_add, metaDataStr))
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
        """
        :rtype: dict
        """
        answer = Block.Block.getDictForJSON(self)
        answer.update({'model_classname': self.name})
        answer.update({'model_module': self.model_module})
        answer.update({'model_classname': self.name})
        answer.update({'model_input_file_name': self.input_file_name})
        answer.update({'model_input_file_directory': self.input_file_directory})
        answer.update({'model_metadata_inputs': self.model_metadata_inputs})
        answer.update({'model_metadata_outputs': self.model_metadata_outputs})
        list_slots = []
        for slot in self.getSlots():
            list_slots.append(slot.getDictForJSON())

        answer.update({'data_slots': list_slots})
        return answer

    def initializeFromJSONData(self, json_data):
        self.name = json_data['model_classname']
        self.model_module = json_data['model_module']
        self.input_file_name = json_data['model_input_file_name']
        self.input_file_directory = json_data['model_input_file_directory']
        self.model_metadata_inputs = json_data['model_metadata_inputs']
        self.model_metadata_outputs = json_data['model_metadata_outputs']
        self.constructFromModelMetaData()
        Block.Block.initializeFromJSONData(self, json_data)

    def constructFromModelMetaData(self):
        try:
            for slot in self.model_metadata_inputs:
                if 'Obj_ID' in slot:
                    if isinstance(slot['Obj_ID'], (list, tuple)):
                        for obj_id in slot['Obj_ID']:
                            obj_id_str = obj_id if isinstance(obj_id, str) else str(obj_id)
                            self.addDataSlot(
                                DataSlot.InputDataSlot(
                                    slot['Name'] + " " + obj_id_str,
                                    slot['Type'],
                                    slot['Required'],
                                    slot['Type_ID'],
                                    obj_id
                                )
                            )
                    else:
                        print("Some slot was not added. (Slot with name '%s')" % slot['Name'])
                else:
                    self.addDataSlot(
                        DataSlot.InputDataSlot(
                            slot['Name'],
                            slot['Type'],
                            slot['Required'],
                            slot['Type_ID'],
                            0
                        )
                    )
        except KeyError:
            print("Some model inputs could not have been loaded due to KeyError.")

        try:
            for slot in self.model_metadata_outputs:
                if 'Obj_ID' in slot:
                    if isinstance(slot['Obj_ID'], (list, tuple)):
                        for obj_id in slot['Obj_ID']:
                            obj_id_str = obj_id if isinstance(obj_id, str) else str(obj_id)
                            self.addDataSlot(
                                DataSlot.OutputDataSlot(
                                    slot['Name'] + " " + obj_id_str,
                                    slot['Type'],
                                    False,
                                    slot['Type_ID'],
                                    obj_id
                                )
                            )
                    else:
                        print("Some slot was not added. (Slot with name '%s')" % slot['Name'])
                else:
                    self.addDataSlot(
                        DataSlot.OutputDataSlot(
                            slot['Name'],
                            slot['Type'],
                            False,
                            slot['Type_ID'],
                            0
                        )
                    )
        except KeyError:
            print("Some model outputs could not have been loaded due to KeyError.")

    def generateCodeName(self, base_name='model_'):
        Block.Block.generateCodeName(self, base_name)

    def getIDOfModelNameInList(self, model_name):
        if model_name in BlockWorkflow.BlockWorkflow.getListOfModelClassnames():
            return BlockWorkflow.BlockWorkflow.getListOfModelClassnames().index(model_name)
        return -1

    def getModelDependency(self):
        if self.model_module != "":
            return "import %s" % self.model_module
        return ""

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
            return "self.%s.get(%s, %s, %s)" % (self.code_name, slot.getObjType(), time, obj_id)
        return "None"

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def getLabels(self):
        """:rtype: list of str"""
        if self.input_file_name == "":
            return []
        else:
            return ["input_file = '%s'\npath = '%s'" % (self.input_file_name, self.input_file_directory)]

    def getHeaderText(self):
        """:rtype: str"""
        return "%s - %s" % (self.__class__.__name__, self.name)

    def modificationQuery(self, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        if keyword == 'set_input_file' and isinstance(value, str):
            self.setInputFile(value)
        elif keyword == 'set_input_file_path' and isinstance(value, str):
            self.setInputFilePath(value)
        else:
            Block.Block.modificationQuery(self, keyword, value)

    def generateMenu(self):
        Block.Block.generateMenu(self)

        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
            'set_input_file', None, "Set input file", "str", "Set input file"), 'Modify')

        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem(
            'set_input_file_path', None, "Set path", "str", "Set path"), 'Modify')

