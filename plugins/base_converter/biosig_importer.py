#!/usr/bin/python
import os
import sys
import re
import datetime
import uuid
import ujson as json
from plumbum import local as local_cmd
from biosignalformat import *
import biosig_constant

class BiosigCaller(object):
    """docstring for BiosigCaller"""
    def __init__(self, origin_file, archiver):
        super(BiosigCaller, self).__init__()
        self.origin_file = origin_file
        self.archiver = archiver
        self.json_data = {}
        self.__dest_dirname = str(uuid.uuid4())
        self.__ascii_filename = str(uuid.uuid4()) + ".ascii"
        self.__json_filename = str(uuid.uuid4()) + ".json"

    def process_datetime(self, date):
        """Returns a string-date as a tuple."""
        match = re.match("(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)", date)
        if match:
            return list(match.groups())
        return list(datetime.datetime.now().timetuple())[:6]

    def recognize_scale(self, unit):
        """Recognize a scale, and the unit from a scaled-unit. For example, for uV returns [1e-6, 'V']."""
        if unit[0] in biosig_constant.unit_scales.keys():
            return 10**biosig_constant.unit_scales[unit[0]], unit[1:]
        return 1, unit

    def recognize_event(self, event):
        event_type = biosig_constant.event_codes.get(event["TYP"], "User-defined event")
        event_time = self.get_number(event, "POS", -1)
        return event_time, event_type

    def get_number(self, data, key, default_value):
        """Simple, but common operation for obtaining a number from a dict."""
        try:
            return float(data[key])
        except:
            return default_value

    def execute_command(self):
        """Defines the command to execute with save2gdf."""
        if not os.path.exists(self.__dest_dirname):
            os.makedirs(self.__dest_dirname)
        ascii_name = os.path.join(self.__dest_dirname, self.__ascii_filename)
        json_name = self.json_data_path
        command = local_cmd["save2gdf"]["-JSON"]["-f=ASCII"][self.origin_file][ascii_name]  > json_name
        command()
        #Fixing an invalid JSON file generated when a warning is found...
        json_text = open(json_name, "r").read()
        debug_index = json_text.rfind("Debugging Information:")
        if debug_index > 0:
            json_text = json_text[:debug_index]
        #Fix Nan-value problem
        json_text = json_text.replace(": nan", ": -1")
        #Fix Noth-key problem. Missing a comma before
        json_text = json_text.replace('"Notch"', ',"Notch"')
        self.json_data = json.loads(json_text)
        del json_text
        json_text = None

    def convert(self):
        """Handles the generic logic to conver a file. Normally, it must not be changed."""
        self.execute_command()
        self.create_file()

    def create_file(self):
        pass

    @property
    def json_data_path(self):
        """Path of the JSON-file with the metadata of the original file (created by save2gdf)."""
        return os.path.join(self.__dest_dirname, self.__json_filename)

    @property
    def channel_data_basename(self):
        """Basename of the channel files."""
        return os.path.join(self.__dest_dirname, self.__ascii_filename.replace(".ascii", ""))

    @property
    def data_dir_path(self):
        """Where is the temporal files?."""
        return os.path.realpath(self.__dest_dirname)


class XDFImporter(BiosigCaller):
    """docstring for XDFImporter"""
    def __init__(self, origin_file, archiver=None, experiment=None, subject=None):
        super(XDFImporter, self).__init__(origin_file, archiver)
        if archiver is None and experiment is None and subject is None:
            raise Exception("Must be indicate a destination file name for XDFImporter!")
        self.experiment = experiment
        self.subject = subject

    def create_file(self):
        if self.experiment is None and self.subject is not None:
            self.experiment = self.subject.experiment
        if self.experiment is None:
            self.experiment = self._create_experiment(self.archiver)
        if self.subject is None:
            self.subject = self._create_subject(self.experiment, self.json_data)
        session = self._create_session(self.subject, self.json_data)
        self._create_event(session, self.json_data)
        self._create_channel(session, self.json_data)
        self.experiment.write()

    def _create_experiment(self, archiver):
        experiment = Experiment()
        experiment.metadata[".original_type"] = "EDF"
        experiment.metadata[".creator"] = "BiosignalFormat Tools - EDF Importer"
        experiment.setArchiver(archiver)
        return experiment

    def _create_subject(self, experiment, json_data):
        subject = Subject()
        subject.metadata["name"] = json_data["Patient"].get("Name", "")
        subject.metadata["gender"] = json_data["Patient"].get("Gender", "")
        subject.metadata["age"] = json_data["Patient"].get("Age", -1)
        subject.metadata["description"] = ""
        experiment.addSubject(subject)
        return subject

    def _create_session(self, subject, json_data):
        session = Session()
        session.metadata["recording-start-time"] = self.process_datetime(json_data["StartOfRecording"])
        session.metadata["sweep-number"] = json_data["NumberOfSweeps"]
        subject.addSession(session)
        return session

    def _create_event(self, session, json_data):
        for event in json_data["EVENT"]:
            event_data = self.recognize_event(event)
            session_event = SessionEvent(time=event_data[0], event_name=event_data[1])
            session.addEvent(session_event)

    def _create_channel(self, session, json_data):
        for channel_info in json_data["CHANNEL"]:
            if "annotations" in channel_info["Label"].lower():
                continue
            channel_id = "{0:02}".format(channel_info["ChannelNumber"])
            channel_name = self.channel_data_basename + ".a" + channel_id
            channel_label = channel_info["Label"].upper().replace(".", "")
            scale, unit = self.recognize_scale(channel_info["PhysicalUnit"])
            #Unnecesary: #offset = self.get_number(channel_info, "offset", 0)
            scale *= self.get_number(channel_info, "scaling", 1)
            if not os.path.exists(channel_name):
                print "Warning:", channel_name, "(", channel_label, ") cannot be processed!"
                continue
            channel = Channel()
            session.addChannel(channel)
            channel.metadata["manufacturer"] = json_data["Manufacturer"].get("Name", "unknown")
            channel.metadata["label"] = channel_label
            channel.metadata["unit"] = unit
            channel.metadata["time-offset"] = self.get_number(channel_info, "TimeDelay", 0)
            channel.metadata["impedance"] = self.get_number(channel_info, "Impedance", 0)
            channel.metadata["sampling-rate"] = self.get_number(channel_info, "Samplingrate", 0)
            channel_data = [float(val.strip())*scale for val in open(channel_name, "r").readlines()]
            channel.setData(channel_data)
            del channel_data
            channel_data = None

# Creating aliases:
EDFImporter = XDFImporter
EDFPlusImporter = XDFImporter
BDFImporter = XDFImporter
