"""Various helper functions."""

import json


def readFileContent(filePath):
    """Return the content of the file."""
    with open(filePath) as f:
        return f.read()


def toJson(serialized):
    """Return JSON string from given native Python datatypes."""
    return json.dumps(serialized)


def fromJson(jsonString):
    """Return native Python datatypes from JSON string."""
    return json.loads(jsonString, encoding="utf-8")
