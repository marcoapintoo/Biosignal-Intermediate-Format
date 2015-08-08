#!/usr/bin/python
import os
import sys
import uuid
import ujson as json
import hashlib
from base import BaseFile


class AdditionalData(BaseFile):
    Preffix = "AdditionalData"
    """Represents data which was calculated and stored."""
    def __init__(self, parent, metadata={}):
        super(AdditionalData, self).__init__(metadata)
        self.parent = None
        self.data = []
        self.targetHash = None
        if parent is not None:
            self.setParent(parent)

    def setParent(self, parent):
        self.parent = parent
        self.removeHash = parent.objectHash

    def calculate(self):
        return []

    def getData(self):
        if self.targetHash != self.parent.objectHash:
            self.setData(self.calculate())
        return self.data

    def setData(self, data):
        self.data = data

    def updateHash(self):
        self.hash_me(json.dumps(self.whole_data))

    def addMetadataInfo(self, metadata):
        """Adds additional information to metadata before writing in the file."""
        super(AdditionalData, self).addMetadataInfo(metadata)
        metadata.pop(".dataHash")
        metadata[".targetHash"] = self.targetHash

    @property
    def archiver(self):
        return self.parent.archiver

    @property
    def pathname(self):
        return self.parent.pathname + [self.Preffix + "-" + self.uniqueID]

    @property
    def whole_data(self):
        return self.data


class GenericAdditionalData(AdditionalData):
    Preffix = "AdditionalData"
    """Represents data which was calculated and stored."""
    def __init__(self, parent, file_name, metadata={}):
        super(GenericAdditionalData, self).__init__(parent, metadata)
        self.file_name = file_name

    def getData(self, *args):
        if self.data is None:
            self.data = self.createDataHandler()
        if self.targetHash != self.parent.objectHash:
            self.setData(self.calculate())
        return self.data.get(*args)

    def setData(self, data):
        if self.data is None:
            self.data = self.createDataHandler()
        self.data.set(data)

    def createDataHandler(self):
        raise Exception("Not implemented!")

    def updateHash(self):
        self.objectHash = self.data.objectHash


class SegmentedAdditionalData(GenericAdditionalData):
    Preffix = "AdditionalData"
    """Represents data which was calculated and stored."""
    def __init__(self, parent, file_name, segment_length, metadata={}):
        super(SegmentedAdditionalData, self).__init__(parent, file_name, metadata)
        self.segment_length = segment_length

    def createDataHandler(self):
        return SegmentedData(self.segment_length, self, self.pathname + [self.file_name])


class StoredAdditionalData(GenericAdditionalData):
    Preffix = "AdditionalData"
    """Represents data which was calculated and stored."""
    def __init__(self, parent, file_name, metadata={}):
        super(StoredAdditionalData, self).__init__(parent, file_name, metadata)

    def createDataHandler(self):
        return GenericData(self, self.pathname + [self.file_name])
