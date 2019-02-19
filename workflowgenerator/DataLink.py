import mupif
from . import DataSlot
import uuid


class DataLink:
    """
    Represents a connection between source and receiver DataSlots
    """
    def __init__(self, slot_1=None, slot_2=None):
        self.uid = str(uuid.uuid4())

        self.source = slot_1  # type: DataSlot.DataSlot
        self.target = slot_2  # type: DataSlot.DataSlot

    def __str__(self):
        return "Datalink (%s -> %s)" % (self.source, self.target)

    def __repr__(self):
        return self.__str__()

    def destroy(self):
        """Remove this DataLink and its reference in workflow."""
        self.source.getParentBlock().getWorkflowBlock().removeDataLink(self)
        # del self

    def giveTheOtherSlot(self, first_slot):
        if self.source == first_slot:
            return self.target
        if self.target == first_slot:
            return self.source
        return None

    def getDictForJSON(self):
        answer = {'classname': self.__class__.__name__, 'uuid': self.uid}
        answer.update({'ds1_uid': self.source.uid, 'ds2_uid': self.target.uid})
        return answer

    @staticmethod
    def addNew(slot1, slot2):
        """
        :param DataSlot.DataSlot slot1:
        :param DataSlot.DataSlot slot2:
        :return:
        :rtype: bool
        """
        workflow = slot1.getParentBlock().getWorkflowBlock()
        workflow.addDataLink(DataLink(slot1, slot2))

    def containsSlot(self, slot):
        if self.source is slot or self.target is slot:
            return True
        return False

    def getSlotsUID(self):
        return [self.source.getUID(), self.target.getUID()]
