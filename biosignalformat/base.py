#!/usr/bin/python
import os
import sys
import uuid
import collections
import ujson as json
import hashlib

class BaseFile(object):
    MetadataFileName = ".metadata"
    """Represents an abstract structure."""
    def __init__(self, metadata={}):
        super(BaseFile, self).__init__()
        self.metadata = metadata or {}
        self.uniqueID = str(uuid.uuid1())
        self.objectHash = ""
        self.calculatedInformation = {}
        self._archiver = None

    def write(self, dirpath=None):
        """Writes the information the metadata file, using a like-list directory path. """
        self.writeMetadata(dirpath)

    def remove(self, dirpath=None):
        """Removes the information inside the archive provider, with a like-list directory path. """
        self.removeMetadata(dirpath)

    def defaultMetadataValues(self):
        """Fills the minimum neccesary metadata values."""
        self.metadata.setdefault(".uniqueID", None)
        self.metadata.setdefault(".dataHash", None)
        self.metadata.setdefault(".calculatedInformation", None)

    def readMetadata(self, dirpath=[]):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        self.metadata = json.loads(self.archiver.read(dirpath + [self.MetadataFileName]))
        self.objectHash = self.metadata.pop(".dataHash")
        self.objectHash = self.metadata.pop(".uniqueID")
        self.calculatedInformation = {key: [] for key in self.metadata.pop(".calculatedInformation")}
        return self.metadata

    def writeMetadata(self, dirpath=None):
        """Write the metadata inside the archive provider, with a like-list directory path. """
        self.updateHash()
        if dirpath is None:
            dirpath = self.pathname
        metadata = self.metadata.copy()
        self.addMetadataInfo(metadata)
        self.archiver.add(dirpath + [self.MetadataFileName], json.dumps(metadata, indent=4))

    def removeMetadata(self, dirpath=None):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        if dirpath is None:
            dirpath = self.pathname
        self.archiver.remove(dirpath + [self.MetadataFileName])

    def addMetadataInfo(self, metadata):
        """Adds additional information to metadata before writing in the file."""
        metadata[".dataHash"] = self.objectHash
        metadata[".uniqueID"] = self.uniqueID
        metadata[".calculatedInformation"] = list(self.calculatedInformation.keys())

    def writeCalculatedInformation(self, dirpath=[]):
        for key, values in self.calculatedInformation.values():
            self.archiver.add(dirpath + [key], json.dumps(values, indent=4))

    def readCalculatedInformation(self, dirpath=[]):
        keys = self.calculatedInformation.keys()
        for key in keys:
            self.calculatedInformation[key] = json.loads(provider.read(dirpath + [key]))

    def updateHash(self):
        return ""

    def hash_me(self, data):
        hasher = hashlib.sha224('ripemd160')
        hasher.update(self.uniqueID)
        hasher.update(data)
        self.objectHash = hasher.hexdigest()
        return self.objectHash

    @property
    def pathname(self):
        return []

    @property
    def archiver(self):
        return self._archiver
