#!/usr/bin/python
import os
import sys
import uuid
import ujson as json
import hashlib

class StoredData(object):
    def __init__(self, parent, file_name):
        self.parent = parent
        self.file_name = file_name
        self.objectHash = None

    def set(self, data, indent=None):
        if indent is not None:
            strdata = json.dumps(data, indent=indent)
        else:
            strdata = json.dumps(data)
        self.archiver.add(self.file_name, strdata)
        strdata = None

    def get(self):
        return self.archiver.read(self.file_name)

    @property
    def archiver(self):
        return self.parent.archiver

    def hash(self, strdata):
        hasher = hashlib.sha224('ripemd160')
        hasher.update(strdata)
        self.objectHash = hasher.hexdigest()


class SegmentedData(StoredData):
    def __init__(self, segment_size, parent, file_name):
        super(SegmentedData, self).__init__(parent, file_name)
        self.segment_size = segment_size
        self.data_length = 0

    def set(self, data):
        hasher = hashlib.sha224('ripemd160')
        maxlen = self.segment_size
        self.data_length = len(data)
        segment_number = int(round(len(data)*1.0/maxlen))+1
        #segments = [data[maxlen*i:maxlen*(i+1)] for i in range(segment_number)]
        for i in range(segment_number):
            strdata = json.dumps(data[maxlen*i:maxlen*(i+1)])
            self.archiver.add(self.file_name + ["SEGMENT-" + str(i)], strdata)
            hasher.update(strdata)
            strdata = None
        self.objectHash = hasher.hexdigest()

    def get(self, start = 0, end = None):
        maxlen = self.segment_size
        end = end or self.data_length - 1
        startSegment = int(start/maxlen)
        startOffset = int(start%maxlen)
        endSegment = int(end/maxlen)
        data = [None] * (end-start+1)
        return [ v for i in range(startSegment, endSegment)
            for v in json.loads(self.archiver.read(self.file_name + ["SEGMENT-" + str(i)]))
                [(startOffset if i == startSegment else 0):]
        ]
