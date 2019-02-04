import mupif
from . import tools
from . import Block
from . import DataSlot
import uuid
from .exceptions import DuplicateKnobNameError, KnobConnectionError


class DataLink:
    """
    Represents a connection between source and receiver DataSlots
    """
    def __init__(self, slot_1=None, slot_2=None):
        self.uuid = str(uuid.uuid4())

        self.source = slot_1
        self.target = slot_2

    def __str__(self):
        return "Datalink (%s -> %s)" % (self.source, self.target)

    def __repr__(self):
        return self.__str__()

    def destroy(self):
        """Remove this DataLink and its reference in other objects."""
        if self.source:
            self.source.removeDataConnection(self)
        if self.target:
            self.target.removeDataConnection(self)
        del self

    def giveTheOtherSlot(self, first_slot):
        if self.source == first_slot:
            return self.target
        if self.target == first_slot:
            return self.source
        return None

    def getDictForJSON(self):
        answer = {'classname': self.__class__.__name__, 'uuid': self.uuid}
        answer.update({'ds1_uuid': self.source.uuid, 'ds2_uuid': self.target.uuid})
        return answer
