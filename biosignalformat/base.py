#!/usr/bin/python
import os
import sys
import uuid
import json

class BaseFile(object):
    MetadataFileName = ".metadata"
    """Represents an abstract structure."""
    def __init__(self, metadata={}):
        super(BaseFile, self).__init__()
        self.metadata = metadata
        self.uniqueID = str(uuid.uuid1())
        self.metadata["uniqueID"] = self.uniqueID

    def write(self, provider, dirpath=[]):
        """Write the metadata inside the archive provider, with a like-list directory path. """
        provider.add(dirpath + [self.MetadataFileName], json.dumps(self.metadata, indent=4))

    def remove(self, provider, dirpath=[]):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        provider.remove(dirpath + [self.MetadataFileName])

    def readMetadata(self, provider, dirpath=[]):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        return json.loads(provider.read(dirpath + [self.MetadataFileName]))


class Experiment(BaseFile):
    """Represents a whole Biomedical experiment in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Experiment, self).__init__(metadata)
        self.subjects = []
        self.deletedSubjects = []

    def write(self, provider):
        """Write the content inside the archive provide."""
        super(Experiment, self).write(provider)
        for subject in self.subjects:
            subject.write(provider)
        for subject in self.deletedSubjects:
            subject.remove(provider)
        self.deletedSubjects = []

    def remove(self, provider):
        """Operation not allowed at Experiment-level."""
        raise Exception("Cannot delete an experiment! Are you sure it is what you want?")
        #"""Removes the content inside the archive provide."""
        #super(Experiment, self).remove(provider)
        #for subject in self.subjects + self.deletedSubjects:
        #    subject.remove(provider)
        #self.deletedSubjects = []

    def addSubject(self, subject):
        """Add a subject, recognizing it as a child XD."""
        self.subjects.append(subject)
        subject.experiment = self

    def removeSubject(self, subject):
        """Remove a subject."""
        self.subjects.remove(subject)
        self.deletedSubjects.append(subject)
