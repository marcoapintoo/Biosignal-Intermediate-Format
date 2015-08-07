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

    def write(self, provider, dirpath=None):
        """Write the metadata inside the archive provider, with a like-list directory path. """
        if dirpath is None:
            dirpath = self.pathname
        provider.add(dirpath + [self.MetadataFileName], json.dumps(self.metadata, indent=4))

    def remove(self, provider, dirpath=None):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        if dirpath is None:
            dirpath = self.pathname
        provider.remove(dirpath + [self.MetadataFileName])

    def readMetadata(self, provider, dirpath=[]):
        """Removes the metadata inside the archive provider, with a like-list directory path. """
        self.metadata = json.loads(provider.read(dirpath + [self.MetadataFileName]))
        return self.metadata

    @property
    def pathname(self):
        return []


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

class Subject(BaseFile):
    """Represents a subject experiment in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Subject, self).__init__(metadata)
        self.experiment = None
        self.sessions = []
        self.deletedSessions = []

    def write(self, provider):
        """Write the content inside the archive provide."""
        super(Subject, self).write(provider)
        for session in self.sessions:
            session.write(provider)
        for session in self.deletedSessions:
            session.remove(provider)
        self.deletedSession = []

    def remove(self, provider):
        """Removes the content inside the archive provide."""
        super(Subject, self).remove(provider)
        for subject in self.session + self.deletedSessions:
            session.remove(provider)
        self.deletedSession = []

    def addSession(self, session):
        """Add a session, recognizing it as a child XD."""
        self.sessions.append(session)
        session.subject = self

    def removeSession(self, session):
        """Remove a session."""
        self.sessions.remove(session)
        self.deletedSessions.append(session)

    @property
    def pathname(self):
        return self.experiment.pathname + ["SUBJECT-" + self.uniqueID]

class Session(BaseFile):
    """Represents a session experiment of a subject in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Session, self).__init__(metadata)
        self.subject = None
        self.channelDatasets = []
        self.deletedChannelDatasets = []

    def write(self, provider):
        """Write the content inside the archive provide."""
        super(Session, self).write(provider)
        for channelDataset in self.channelDatasets:
            channelDataset.write(provider)
        for channelDataset in self.deletedChannelDatasets:
            channelDataset.remove(provider)
        self.deletedChannelDatasets = []

    def remove(self, provider):
        """Removes the content inside the archive provide."""
        super(Session, self).remove(provider)
        for channelDataset in self.channelDatasets + self.deletedChannelDatasets:
            channelDataset.remove(provider)
        self.deletedChannelDatasets = []

    def addChannelDataset(self, channelDataset):
        """Add a channel dataset, recognizing it as a child XD."""
        self.channelDatasets.append(channelDataset)
        channelDataset.session = self

    def removeChannelDataset(self, channelDataset):
        """Remove a session."""
        self.channelDatasets.remove(channelDataset)
        self.deletedChannelDatasets.append(channelDataset)

    @property
    def pathname(self):
        return self.subject.pathname + ["SESSION-" + self.uniqueID]


class ChannelDataset(BaseFile):
    RawDataFileName = "raw_data"
    """Represents a session experiment of a subject in the sense of BIF.
    Why use uniqueID instead of channel name as a ID reference?
    Because in some experiments, the experimenter could have more than one data
    over the same channel in the same session. So, to avoid create a new channel,
    it would be better to assign a uniqueID reference. Obviously, this is an
    akward situation. But, the file format need to be standard
    """
    def __init__(self, metadata={}):
        super(ChannelDataset, self).__init__(metadata)
        self.session = None
        self.rawData = []

    def write(self, provider):
        """Write the content inside the archive provide."""
        super(ChannelDataset, self).write(provider)
        provider.add(self.pathname + [self.RawDataFileName], json.dumps(self.rawData))

    def remove(self, provider):
        """Removes the content inside the archive provide."""
        super(ChannelDataset, self).remove(provider)
        provider.remove(self.pathname + [self.RawDataFileName])

    def loadData(self, provider):
        """Read the content from the archive provide."""
        self.rawData = json.loads(provider.read(self.pathname + [self.RawDataFileName]))
        return self.rawData

    @property
    def pathname(self):
        return self.session.pathname + ["CHANNEL-" + self.uniqueID]
