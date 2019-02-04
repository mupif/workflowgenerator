import mupif
from . import tools
from . import DataSlot
import uuid

from termcolor import colored


class Block:

    def __init__(self):
        self.blocks = []
        self.slots = []
        self.name = ""
        self.code_name = ""
        self.parent_block = None
        self.allow_child_blocks = False
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return "Block (%s, %s)" % (self.name, self.__class__.__name__)

    def getUUID(self):
        return self.uuid

    def getBlocks(self, cls=None):
        """
        Returns list of child blocks.
        :param cls: Filtering parameter to obtain only blocks of such class.
        :return: List of child blocks.
        :rtype: list of Block.Block
        """
        if cls is None:
            return self.blocks
        return list(filter(lambda k: k.__class__ is cls, self.blocks))

    def getSlots(self, cls=None):
        """
        Returns list of the block's data slots.
        :param cls: Filtering parameter to obtain only slots of such class.
        :return: List of the block's data slots.
        :rtype: list of DataSlot.DataSlot
        """
        if cls is None:
            return self.slots
        return list(filter(lambda k: k.__class__ is cls, self.slots))

    def getBlocksRecursive(self, cls=None):
        """
        Returns list of blocks with recursive search.
        :param cls: Filtering parameter to obtain only blocks of such class.
        :return: List of blocks.
        :rtype: list of Block.Block
        """
        return_list = self.getBlocks(cls)[:]
        for block in self.getBlocks():
            return_list.extend(block.getBlocksRecursive(cls)[:])
        return return_list

    def getSlotsRecursive(self, cls=None):
        """
        Returns list of the data slots with recursive search.
        :param cls: Filtering parameter to obtain only slots of such class.
        :return: List of data slots.
        :rtype: list of DataSlot.DataSlot
        """
        return_list = self.getSlots(cls)
        for block in self.getBlocksRecursive():
            return_list.extend(block.getSlots(cls))
        return return_list

    def getParentBlock(self):
        """
        :return:
        :rtype: Block.Block or None
        """
        return self.parent_block

    def setParentBlock(self, parent_block):
        self.parent_block = parent_block

    def getWorkflowBlock(self):
        """
        :return:
        :rtype: BlockWorkflow.BlockWorkflow
        """
        return self.getParentBlock().getWorkflowBlock()

    def getInitCode(self, indent=0):
        """
        Returns list of strings with __init__ code lines.
        :param int indent:
        :return: Lines of code.
        :rtype: str[]
        """
        code = ["", "# __init__ code of %s (%s)" % (self.code_name, self.name)]
        return tools.push_indents_before_each_line(code, indent)

    def getInitializationCode(self, indent=0):
        """
        Returns list of strings with initialization code lines.
        :param int indent:
        :return: Lines of code.
        :rtype: str[]
        """
        code = ["", "# initialization code of %s (%s)" % (self.code_name, self.name)]
        return tools.push_indents_before_each_line(code, indent)

    def getExecutionCode(self, indent=0, time='', timestep='tstep'):
        """
        Returns list of strings with execution code lines.
        :param int indent:
        :param str time:
        :param str timestep:
        :return: Lines of code.
        :rtype: str[]
        """
        code = ["", "# execution code of %s (%s)" % (self.code_name, self.name)]
        return tools.push_indents_before_each_line(code, indent)

    def generateOutputDataSlotGetFunction(self, slot, time=''):
        """
        Returns code of get function for given dataslot.
        :param DataSlot.DataSlot slot:
        :param str time:
        :return:
        :rtype: str
        """
        return "ToBeImplemented"

    # def getAllDataSlots(self, recursive=False):
    #     array = self.getDataSlots()
    #     if recursive:
    #         for block in self.getChildExecutionBlocks():
    #             array.extend(block.getAllDataSlots(True))
    #     return array

    # def getDataSlotWithUUID(self, uuid, recursive_search=False):
    #     for slot in self.getAllDataSlots(recursive_search):
    #         if slot.uuid == uuid:
    #             return slot
    #     return None

    def getDataSlotWithName(self, name):
        """Return matching data slot by its name, None otherwise.
        :rtype: DataSlot.DataSlot or None
        """
        for slot in self.getSlots():
            if slot.name == name:
                return slot
        return None

    # def getDataSlot(self, name=None, uuid=None, parent_uuid=None, recursive_search=False):
    #     if name or uuid or parent_uuid:
    #         for slot in self.getAllDataSlots(recursive_search):
    #             if (not name or (slot.name == name and slot.name)) and (
    #                     not uuid or (slot.uuid == uuid and slot.uuid)) and (
    #                     not parent_uuid or (slot.getParentUUID() == parent_uuid and slot.getParentUUID())):
    #                 return slot
    #     return None

    def addDataSlot(self, slot):
        """
        :param DataSlot.DataSlot slot:
        """
        slot.setParentBlock(self)
        self.slots.append(slot)

    def removeDataSlot(self, slot):
        self.slots.remove(slot)

    def addBlock(self, block):
        block.setParentBlock(self)
        self.blocks.append(block)

    def getConnectedDataLinks(self):
        answer = []
        for slot in self.getSlots():
            answer.extend(slot.getDataLinks())
        return answer

    def moveBlockInList(self, block, direction):
        block_id = -5
        if block in self.blocks:
            block_id = self.blocks.index(block)

        if direction == "up" and block_id > 0:
            temp = self.blocks[block_id]
            self.blocks[block_id] = self.blocks[block_id - 1]
            self.blocks[block_id - 1] = temp
        elif direction == "down" and block_id < len(self.blocks) - 1:
            temp = self.blocks[block_id]
            self.blocks[block_id] = self.blocks[block_id+1]
            self.blocks[block_id+1] = temp

    def getParentUUID(self):
        if self.parent_block:
            return self.parent_block.uuid
        return ""

    def getDictForJSON(self):
        answer = {'classname': self.__class__.__name__, 'uuid': self.uuid, 'parent_uuid': self.getParentUUID()}
        return answer

    def convertToJSON(self):
        return_json_array = [self.getDictForJSON()]
        return_json_array.extend([k.getDictForJSON() for k in self.getSlots()])
        return_json_array.extend([k.getDictForJSON() for k in self.getBlocks()])
        return return_json_array

    # @staticmethod
    # def getListOfModelClassnames():
    #     array = [m.__name__ for m in ExecutionBlock.list_of_models]
    #     return array

    # @staticmethod
    # def getListOfModelDependencies():
    #     return ExecutionBlock.list_of_model_dependencies

    # @staticmethod
    # def getListOfStandardBlockClassnames():
    #     array = [m.__name__ for m in ExecutionBlock.list_of_block_classes]
    #     return array

    def initializeFromJSONData(self, json_data):
        self.uuid = json_data['uuid']
        e_parent_e = self.getWorkflowBlock().getNodeById(json_data['parent_uuid'])
        self.parent = e_parent_e
        self.setParentItem(e_parent_e)

    def generateNewDataSlotName(self, base="data_slot_"):
        names = [n.name for n in self.getSlots()]
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base, i)
            if not new_name in names:
                return new_name

    def generateCodeName(self, base_name='block_'):
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base_name, i)
            if new_name not in self.getWorkflowBlock().getAllElementCodeNames():
                self.code_name = new_name
                return

    def printStructure(self, indent=0):
        print("")
        print("%s%s" % ("\t" * indent, colored(self, "green")))
        if len(self.getSlots()):
            print("")
            for slot in self.getSlots():
                print("%s%s" % ("\t" * (indent+1), slot))
        if len(self.getBlocks()):
            for block in self.getBlocks():
                block.printStructure(indent + 1)

