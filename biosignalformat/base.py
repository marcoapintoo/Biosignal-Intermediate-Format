#!/usr/bin/python
import os
import sys
import pprint
import uuid
import json
from plumbum import local as local_cmd


class ArchiveProvider(object):
	"""docstring for FileProvider"""
	def __init__(self, archivename):
		self.archivename = archivename
		self.sevenzip = local_cmd["7z"]

	def add(self, filename, content):
		command = self.sevenzip["a"][self.archivename]["-si" + "/".join(filename)] << content
		command()


class BaseFile(object):
	MetadataFileName = ".metadata"
	"""docstring for BaseFile"""
	def __init__(self, metadata={}):
		super(BaseFile, self).__init__()
		self.metadata = metadata
		self.uniqueID = str(uuid.uuid1())
		self.metadata["uniqueID"] = self.uniqueID

	def write(self, provider, dirpath=[]):
		provider.add(dirpath + [self.MetadataFileName], json.dumps(self.metadata, indent=4))


class Experiment(BaseFile):
	"""docstring for Experiment"""
	def __init__(self, metadata={}):
		super(Experiment, self).__init__(metadata)

	def write(self, provider):
		super(Experiment, self).write(provider)


#if __name__ == '__main__':
def test():
	provider = ArchiveProvider("experiment001.7z")
	experiment = Experiment({
		"name": "Exp!",
		"description": "blah!"
	})
	experiment.write(provider)
