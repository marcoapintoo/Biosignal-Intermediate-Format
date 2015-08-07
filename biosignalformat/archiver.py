#!/usr/bin/python
import os
import sys
from plumbum import local as local_cmd

class ArchiveProvider(object):
    """Provides a simple interface to add, and update files to an archive format."""
    def __init__(self, archivename):
        self.archivename = archivename
        self.sevenzip = local_cmd["7z"]

    def add(self, filename, content):
        """Writes a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["a"][self.archivename]["-si" + "/".join(filename)] << content
        command()

    def remove(self, filename):
        """Removes a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["d"][self.archivename]["/".join(filename)]
        command()

    def read(self, filename):
        content = ""
        """Reads a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["x"][self.archivename]["-so"]
        return command()
