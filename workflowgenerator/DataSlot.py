import mupif
from . import tools
from . import Block
from . import DataLink
import uuid
from .exceptions import DuplicateKnobNameError, KnobConnectionError
import os
from enum import Enum

from termcolor import colored


class DataSlotType(Enum):
    Unknown = 0

    Property = 1
    Field = 2
    Function = 3

    PhysicalQuantity = 5

    Int = 11
    Double = 12
    String = 13

    Scalar = 111

    @staticmethod
    def getTypeFromName(val):
        for t in DataSlotType:
            if t.name == val:
                return t
        return None

    @staticmethod
    def getNameFromType(val):
        for t in DataSlotType:
            if t == val:
                return t.name
        return None


class DataSlot:
    def __init__(self, name, type, optional=False, obj_type=None, obj_id=0):
        self.name = name
        self.parent_block = None
        self.type = type
        self.optional = optional
        self.external = False
        self.obj_type = obj_type
        self.obj_id = obj_id

        self.code_name = ""

        if isinstance(self, OutputDataSlot):
            self.optional = True
        if isinstance(self, ExternalInputDataSlot) or isinstance(self, ExternalOutputDataSlot):
            self.optional = True
            self.external = True

        self.uuid = str(uuid.uuid4())

        self.datalinks = []  # data

        self.maxConnections = -1  # A negative value means 'unlimited'.
        if isinstance(self, InputDataSlot):
            self.maxConnections = 1

    def connectedInfo(self):
        if self.connected():
            connect_info = colored("connected", "green")
        elif self.optional:
            connect_info = "not-connected"
        else:
            connect_info = colored("not-connected", "red")
        return connect_info

    def __repr__(self):
        return "%s %s" % (colored("%s (%s.%s %s)" % (
            self.__class__.__name__, self.getParentBlock().name, self.name, self.type), "blue"),
                          self.connectedInfo())

    def getUUID(self):
        return self.uuid

    def getDataLinks(self):
        """

        :return:
        :rtype: list of DataLink.DataLink
        """
        return self.datalinks

    def setType(self, val):
        self.type = val

    def getParentBlock(self):
        """
        :return:
        :rtype: Block.Block or None
        """
        return self.parent_block

    def setParentBlock(self, parent_block):
        self.parent_block = parent_block

    @staticmethod
    def connectDataSlots(slot_a, slot_b):
        """

        :param DataSlot slot_a:
        :param DataSlot slot_b:
        :return:
        """
        dl = DataLink.DataLink(slot_a, slot_b)
        slot_a.addDataConnection(dl)
        slot_b.addDataConnection(dl)

    def connectTo(self, target):
        """

        :param DataSlot target:
        :return:
        """

        if not isinstance(target, DataSlot):
            print("(%s x %s)" % (self, target))
            raise KnobConnectionError("Ignoring connection to all element types except DataSlot and derived classes.")

        if self.reachedMaxConnections() or target.reachedMaxConnections():
            raise KnobConnectionError("One of the slots can accept no more connections.")

        if target is self:
            raise KnobConnectionError("Can't connect DataSlot to itself.")

        if not ((isinstance(self, InputDataSlot) and isinstance(target, OutputDataSlot)) or (
                    isinstance(self, OutputDataSlot) and isinstance(target, InputDataSlot))):
            raise KnobConnectionError("Only InputDataSlot and OutputDataSlot can be connected.")

        if self.external:
            self.setType(target.type)
        elif target.external:
            target.setType(self.type)

        if not self.type == target.type:
            raise KnobConnectionError("Two slots of different value types cannot be connected.")

        if self.isConnectedToSlot(target):
            raise KnobConnectionError("Connection already exists.")

        self.connectDataSlots(self, target)

    def connected(self):
        if len(self.datalinks):
            return True
        return False

    def isConnectedToSlot(self, slot):
        """
        :param slot:
        :return:
        :rtype: bool
        """
        for dl in self.getDataLinks():
            if dl.giveTheOtherSlot(self) == slot:
                return True
        return False

    def addDataConnection(self, data_link):
        """
        :param DataLink.DataLink data_link:
        :return:
        """
        self.datalinks.append(data_link)

    def removeDataConnection(self, data_link):
        """
        :param DataLink.DataLink data_link:
        :return:
        """
        self.datalinks.remove(data_link)

    def setUUID(self, uuid):
        self.uuid = uuid

    def reachedMaxConnections(self):
        if self.maxConnections < 0:
            return False
        if len(self.datalinks) < self.maxConnections:
            return False
        return True

    def deleteAllConnections(self):
        datalink_to_be_deleted = self.datalinks[::]  # Avoid shrinking during deletion.
        for data_link in datalink_to_be_deleted:
            data_link.destroy()

    def rename(self, val):
        self.name = val

    def getParentUUID(self):
        if self.getParentBlock():
            return self.getParentBlock().getUUID()

    def getDictForJSON(self):
        answer = {'classname': self.__class__.__name__, 'uuid': self.uuid, 'parent_uuid': self.getParentUUID()}
        answer.update({'name': self.name, 'type': "%s" % DataSlotType.getNameFromType(self.type)})
        answer.update({'obj_id': self.obj_id, 'obj_type': "%s" % self.obj_type})
        return answer

    def getLinkedDataSlot(self):
        """
        :return:
        :rtype: DataSlot
        """
        if len(self.datalinks) == 1:
            return self.datalinks[0].giveTheOtherSlot(self)
        return None

    def generateCodeName(self, base_name='dataslot_'):
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base_name, i)
            if new_name not in self.getParentBlock().getWorkflowBlock().getAllElementCodeNames():
                self.code_name = new_name
                return

    def getCodeRepresentation(self):
        return "self.%s" % self.code_name


class InputDataSlot (DataSlot):
    """
    Class describing input parameter of block
    """
    def __init__(self, name, type, optional=False, obj_type=None, obj_id=0):
        DataSlot.__init__(self, name, type, optional, obj_type, obj_id)


class OutputDataSlot (DataSlot):
    """
    Class describing output parameter of block
    """
    def __init__(self, name, type, optional=False, obj_type=None, obj_id=0):
        DataSlot.__init__(self, name, type, optional, obj_type, obj_id)


class ExternalInputDataSlot(InputDataSlot):
    def __init__(self, name, type, optional=True, obj_type=None, obj_id=0):
        InputDataSlot.__init__(self, name, type, optional, obj_type, obj_id)
        self.obj_id = self.name

    def generateCodeName(self, base_name='external_output_'):
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base_name, i)
            if new_name not in self.getParentBlock().getWorkflowBlock().getAllElementCodeNames():
                self.code_name = new_name
                return

    def rename(self, val):
        DataSlot.rename(self, val)
        self.obj_id = self.name


class ExternalOutputDataSlot(OutputDataSlot):
    def __init__(self, name, type, optional=True, obj_type=None, obj_id=0):
        OutputDataSlot.__init__(self, name, type, optional, obj_type, obj_id)
        self.obj_id = self.name

    def generateCodeName(self, base_name='external_input_'):
        i = 0
        while True:
            i += 1
            new_name = "%s%d" % (base_name, i)
            if new_name not in self.getParentBlock().getWorkflowBlock().getAllElementCodeNames():
                self.code_name = new_name
                return

    def rename(self, val):
        DataSlot.rename(self, val)
        self.obj_id = self.name