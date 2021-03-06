#!/usr/bin/python
import os
import sys
import uuid
import ujson as json
import hashlib
from datatype import SegmentedData, StoredData
from base import BaseFile


class Experiment(BaseFile):
    """Represents a whole Biomedical experiment in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Experiment, self).__init__(metadata)
        self.subjects = []
        self.deletedSubjects = []

    def setArchiver(self, archiver):
        self._archiver = archiver

    def write(self):
        """Write the content inside the archive provide."""
        super(Experiment, self).write()
        for subject in self.subjects:
            subject.write()
        for subject in self.deletedSubjects:
            subject.remove()
        self.deletedSubjects = []
        self.writeMetadata()
        self.archiver.force_write()

    def remove(self):
        """Operation not allowed at Experiment-level."""
        raise Exception("Cannot delete an experiment! Are you sure it is what you want?")
        """"Removes the content inside the archive provide."""
        super(Experiment, self).remove()
        for subject in self.subjects + self.deletedSubjects:
            subject.remove()
        self.deletedSubjects = []
        self.writeMetadata()

    def addSubject(self, subject):
        """Adds a subject, recognizing it as a child XD."""
        self.subjects.append(subject)
        subject.experiment = self

    def removeSubject(self, subject):
        """Removes a subject."""
        self.subjects.remove(subject)
        self.deletedSubjects.append(subject)

    def updateHash(self):
        """Generates a hash code with the objects."""
        self.hash_me("-".join(child.objectHash for child in self.subjects))

    def defaultMetadataValues(self):
        """Fills the minimum neccesary metadata values."""
        super(Experiment, self).defaultMetadataValues()
        self.metadata.setdefault(".original_type", "")
        self.metadata.setdefault(".creator", "BiosignalFormat Tools")


class Subject(BaseFile):
    """Represents a subject experiment in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Subject, self).__init__(metadata)
        self.experiment = None
        self.sessions = []
        self.deletedSessions = []

    def write(self):
        """Write the content inside the archive provide."""
        super(Subject, self).write()
        for session in self.sessions:
            session.write()
        for session in self.deletedSessions:
            session.remove()
        self.deletedSession = []
        self.writeMetadata()

    def remove(self):
        """Removes the content inside the archive provide."""
        super(Subject, self).remove()
        for subject in self.session + self.deletedSessions:
            session.remove()
        self.deletedSession = []
        self.writeMetadata()

    def addSession(self, session):
        """Add a session, recognizing it as a child XD."""
        self.sessions.append(session)
        session.subject = self

    def removeSession(self, session):
        """Remove a session."""
        self.sessions.remove(session)
        self.deletedSessions.append(session)

    def updateHash(self):
        self.hash_me("-".join(child.objectHash for child in self.sessions))

    @property
    def pathname(self):
        return self.experiment.pathname + ["SUBJECT-" + self.uniqueID]

    @property
    def archiver(self):
        return self.experiment.archiver

    def defaultMetadataValues(self):
        """Fills the minimum neccesary metadata values."""
        super(Subject, self).defaultMetadataValues()
        self.metadata.setdefault("name", "")
        self.metadata.setdefault("gender", "")
        self.metadata.setdefault("age", -1)
        self.metadata.setdefault("description", "")


class Session(BaseFile):
    EventFileName = ".event"
    """Represents a session experiment of a subject in the sense of BIF."""
    def __init__(self, metadata={}):
        super(Session, self).__init__(metadata)
        self.subject = None
        self.channels = []
        self.deletedChannels = []
        self.events = []
        self.event_handler = None

    def write(self):
        """Write the content inside the archive provide."""
        super(Session, self).write()
        for channel in self.channels:
            channel.write()
        for channel in self.deletedChannels:
            channel.remove()
        self.deletedChannels = []
        if self.event_handler is None:
            self.event_handler = StoredData(self, self.pathname + [self.EventFileName])
        self.event_handler.set(SessionEvent.toJson(self.events), indent=4)

    def remove(self):
        """Removes the content inside the archive provide."""
        super(Session, self).remove()
        for channel in self.channels + self.deletedChannels:
            channel.remove()
        self.deletedChannels = []
        self.writeMetadata()
        self.events = {}
        self.event_handler.set([])

    def addChannel(self, channel):
        """Add a channel dataset, recognizing it as a child XD."""
        self.channels.append(channel)
        channel.session = self

    def removeChannel(self, channel):
        """Remove a session."""
        self.channels.remove(channel)
        self.deletedChannels.append(channel)

    def addEvent(self, event_data):
        self.events.append(event_data)

    def updateHash(self):
        self.hash_me("-".join(child.objectHash for child in self.channels))

    def defaultMetadataValues(self):
        """Fills the minimum neccesary metadata values."""
        super(Subject, self).defaultMetadataValues()
        self.metadata.setdefault("recording-start-time", [0,0,0,0,0])
        self.metadata.setdefault("sweep-number", 0)

    @property
    def pathname(self):
        return self.subject.pathname + ["SESSION-" + self.uniqueID]

    @property
    def archiver(self):
        return self.subject.archiver

class SessionEvent(object):
    """docstring for SessionEvent"""
    def __init__(self, time=0, event_name="Unknown", description=""):
        super(SessionEvent, self).__init__()
        self.time = time
        self.event_name = event_name
        self.description = description

    def asDict(self):
        return {"time": self.time, "event_name": self.event_name, "description": self.description}

    @classmethod
    def toJson(cls, event_list):
        return [o.asDict() for o in event_list]

    @classmethod
    def fromJson(cls, event_json_list):
        return [SessionEvent(*o) for o in event_json_list]




class Channel(BaseFile):
    DataFileName = "data"
    SegmentMaxLength = 512*60*3
    """Represents a session experiment of a subject in the sense of BIF.
    Why use uniqueID instead of channel name as a ID reference?
    Because in some experiments, the experimenter could have more than one data
    over the same channel in the same session. So, to avoid create a new channel,
    it would be better to assign a uniqueID reference. Obviously, this is an
    akward situation. But, the file format need to be standard
    """
    def __init__(self, metadata={}):
        super(Channel, self).__init__(metadata)
        self.session = None
        self.data = None

    def setData(self, data):
        if self.data is None:
            self.data = SegmentedData(self.SegmentMaxLength, self, self.pathname + [self.DataFileName])
        self.data.set(data)

    def getData(self, start = 0, end = None):
        if self.data is None:
            self.data = SegmentedData(self.SegmentMaxLength, self, self.pathname + [self.DataFileName])
        return self.data.get(start, end)

    def write(self):
        """Write the content inside the archive provide."""
        super(Channel, self).write()
        self.writeMetadata()

    def remove(self):
        """Removes the content inside the archive provide."""
        super(Channel, self).remove()
        self.writeMetadata()

    def updateHash(self):
        self.objectHash = self.data.objectHash

    def defaultMetadataValues(self):
        """Fills the minimum neccesary metadata values."""
        super(Subject, self).defaultMetadataValues()
        self.metadata.setdefault("manufacturer", "?")
        self.metadata.setdefault("label", "?")
        self.metadata.setdefault("unit", "?")
        self.metadata.setdefault("time-offset", 0)
        self.metadata.setdefault("impedance", 0)
        self.metadata.setdefault("sampling-rate", 0)
        self.metadata.setdefault("filters", [])

    @property
    def archiver(self):
        return self.session.archiver

    @property
    def pathname(self):
        return self.session.pathname + ["CHANNEL-" + self.uniqueID]
