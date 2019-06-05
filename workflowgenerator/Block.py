import mupif
from . import tools
from . import DataSlot
from . import VisualMenu
import uuid

from termcolor import colored


class Block:

    def __init__(self):
        self.blocks = []
        self.slots = []
        self.name = ""
        self.code_name = ""
        self.parent_block = None
        self.uuid = str(uuid.uuid4())

        self.allow_child_blocks = False

        self.menu = None

    def __repr__(self):
        return "Block (%s, %s)" % (self.name, self.__class__.__name__)

    def getUID(self):
        return self.uuid

    def getCodeName(self):
        """:rtype: str"""
        return self.code_name

    def getBlocks(self, cls=None):
        """
        Returns list of child blocks.
        :param cls: Filtering parameter to obtain only blocks of such class.
        :return: List of child blocks.
        :rtype: list of Block
        """
        if cls is None:
            return self.blocks[:]
        return list(filter(lambda k: k.__class__ is cls, self.blocks))[:]

    def getSlots(self, cls=None):
        """
        Returns list of the block's data slots.
        :param cls: Filtering parameter to obtain only slots of such class.
        :return: List of the block's data slots.
        :rtype: list of DataSlot.DataSlot
        """
        if cls is None:
            return self.slots[:]
        return list(filter(lambda k: k.__class__ is cls, self.slots))[:]

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
        :rtype: Block or None
        """
        return self.parent_block

    def setParentBlock(self, parent_block):
        self.parent_block = parent_block

    def getWorkflowBlock(self):
        """
        :rtype: workflowgenerator.BlockWorkflow.BlockWorkflow
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

    def getInitializationCode(self, indent=0, metaDataStr="{}"):
        """
        Returns list of strings with initialization code lines.
        :param int indent:
        :param str metaDataStr:
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
        :rtype: str
        """
        return "ToBeImplemented"

    def getOutputDataSlotGetFunctionOfLinkedDataSlot(self, slot, time=''):
        """
        :param DataSlot.DataSlot slot:
        :param str time:
        :return: str
        """
        connected_slot = self.getDataSlotWithName(slot.getName()).getLinkedDataSlot()
        return connected_slot.getParentBlock().generateOutputDataSlotGetFunction(connected_slot, time)

    def getDataSlotWithName(self, name):
        """Return matching data slot by its name, None otherwise.
        :param str name:
        :rtype: DataSlot.DataSlot or None
        """
        for slot in self.getSlots():
            if slot.name == name:
                return slot
        return None

    def getDataSlotWithUID(self, uid):
        """Return matching data slot by its UID, None otherwise.
        :param str uid:
        :rtype: DataSlot.DataSlot or None
        """
        for slot in self.getSlotsRecursive():
            if slot.getUID() == uid:
                return slot
        return None

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
        """
        :rtype: dict
        """
        slot_dict = {}
        for slot in self.getSlots():
            slot_dict.update({slot.getName(): slot.getUID()})

        answer = {
            'classname': self.__class__.__name__,
            'uuid': self.uuid,
            'parent_uuid': self.getParentUUID(),
            'slot_uids': slot_dict
        }
        return answer

    # def convertToJSON(self):
    #     return_json_array = [self.getDictForJSON()]
    #     return_json_array.extend([k.getDictForJSON() for k in self.getSlots()])
    #     return_json_array.extend([k.getDictForJSON() for k in self.getBlocks()])
    #     return return_json_array

    def initializeFromJSONData(self, json_data):
        self.uuid = json_data['uuid']
        if json_data['parent_uuid'] != '':
            e_parent_e = self.getWorkflowBlock().getBlockWithUID(json_data['parent_uuid'])
            self.parent_block = e_parent_e
        for key, value in json_data['slot_uids'].items():
            for slot in self.getSlots():
                if slot.getName() == key:
                    slot.setUUID(value)

    def generateNewDataSlotName(self, base="data_slot_"):
        names = [n.name for n in self.getSlots()]
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base, i)
            if new_name not in names:
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

    def deleteAllItems(self):
        for block in self.getBlocks()[:]:
            self.deleteBlock(block)
        for slot in self.getSlots()[:]:
            self.deleteSlot(slot)

    def deleteSlot(self, slot):
        if slot in self.slots:
            idx = self.slots.index(slot)
            if idx is not None:
                slot.deleteAllConnections()
                del self.slots[idx]

    def deleteBlock(self, block):
        if block in self.blocks:
            idx = self.blocks.index(block)
            if idx is not None:
                block.deleteAllItems()
                del self.blocks[idx]

    def delete(self):
        self.getParentBlock().deleteBlock(self)

    # ------------------------------------------------------------------------------------------
    # support functions for visualisation
    # ------------------------------------------------------------------------------------------

    def getHeaderText(self):
        """:rtype: str"""
        return self.__class__.__name__

    def getLabels(self):
        """:rtype: list of str"""
        return []

    def getVisualStructureItems(self):
        """
        Defines structure of the visual representation.
        Available keywords:
        label, slot, slots, block, blocks
        Supposes that all slots and blocks have to be printed.
        The default printing of these elements comes after the defined structure.
        :rtype: list of str
        """
        return []

    def modificationQuery(self, keyword, value=None):
        """
        :param str keyword:
        :param value:
        """
        if keyword == 'add_block' and isinstance(value, Block):
            self.addBlock(value)
        elif keyword == 'delete_block' and isinstance(value, Block):
            self.deleteBlock(value)
        elif keyword == 'delete':
            self.delete()
        elif keyword == 'move_me':
            self.getParentBlock().moveBlockInList(self, value)

    def generateMenu(self):
        self.menu = VisualMenu.VisualMenu()
        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem('move_me', 'up', 'Up'), 'Move')
        self.getMenuProperty().addItemIntoSubMenu(VisualMenu.VisualMenuItem('move_me', 'down', 'Down'), 'Move')
        self.getMenuProperty().addItem(VisualMenu.VisualMenuItem('delete', self.getUID(), 'Delete'))

    def getMenuProperty(self):
        """:rtype: VisualMenu.VisualMenu"""
        return self.menu

    def getMenu(self):
        """:rtype: VisualMenu.VisualMenu"""
        if self.menu is None:
            self.generateMenu()
        return self.menu
