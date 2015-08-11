#!/usr/bin/python
import os
import sys
import shutil
from plumbum import local as local_cmd
from plumbum import ProcessExecutionError

class SevenZipArchiveProvider(object):
    TemporalFileName = ".temp_arch_file"
    """Provides a simple interface to add, and update files to an archive format."""
    def __init__(self, archivename):
        self.archivename = archivename
        self.sevenzip = local_cmd["7za"]

    def add(self, filename, content):
        """Writes a file inside the archive. Notes that filename is an list-compatible object."""
        #command = self.sevenzip["a"][self.archivename]["-si" + "/".join(filename)] << content
        command = self.sevenzip["a"][self.archivename]["-si" + "/".join(filename)]["-m0=lzma2"]["-mmt=8"] << content
        command()

    def remove(self, filename):
        """Removes a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["d"][self.archivename]["/".join(filename)]
        command()

    def read(self, filename):
        content = ""
        """Reads a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["x"][self.archivename]["-so"]["/".join(filename)]
        return command()


class ZipArchiveProvider(object):
    TemporalDirName = ".temp_arch_dir"
    """Provides a simple interface to add, and update files to an archive format."""
    def __init__(self, archivename):
        self.archivename = archivename
        self.zip = local_cmd["zip"]
        self.unzip = local_cmd["unzip"]

    def add(self, filename, content):
        """Writes a file inside the archive. Notes that filename is an list-compatible object."""
        tempfilename = "/".join([self.TemporalDirName] + filename)
        if not os.path.exists(os.path.dirname(tempfilename)):
            os.makedirs(os.path.dirname(tempfilename))
        with open(tempfilename, "w") as f:
            f.write(content)
        local_cmd.cwd.chdir("./" + self.TemporalDirName)
        #command = self.zip["-9"]["-Z"]["bzip2"]["../" + self.archivename]["-u"]["-m"]["-r"]["."]
        command = self.zip["../" + self.archivename]["-u"]["-m"]["-r"]["."]
        try:
            command()
        except ProcessExecutionError as e:
            if e.retcode != 12: #Nothing to do
                raise e
        local_cmd.cwd.chdir("./..")
        shutil.rmtree(self.TemporalDirName)

    def remove(self, filename):
        """Removes a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.zip["-d"][self.archivename]["/".join(filename)]
        command()

    def read(self, filename):
        content = ""
        """Reads a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.unzip["-p"][self.archivename]["/".join(filename)]
        return command()

ArchiveProvider = SevenZipArchiveProvider

class XArchiveProvider(object):
    TemporalFileName = ".temp_arch_file"
    TemporalDirName = ".temp_arch_dir"
    """Provides a simple interface to add, and update files to an archive format."""
    def __init__(self, archivename, filetype="zip"):
        self.archivename = archivename
        self.temporaldirname = self.TemporalDirName + "_" + os.path.basename(archivename)
        self.sevenzip = local_cmd["7za"]
        self.filetype = filetype

    def add(self, filename, content):
        """Writes a file inside the archive. Notes that filename is an list-compatible object."""
        tempfilename = "/".join([self.temporaldirname] + filename)
        if not os.path.exists(os.path.dirname(tempfilename)):
            os.makedirs(os.path.dirname(tempfilename))
        with open(tempfilename, "w") as f:
            f.write(content)
        if self.get_size(self.temporaldirname) > 1024*1024*200:
            self.force_write()

    def force_write(self):
        if not os.path.exists(self.temporaldirname):
            os.makedirs(self.temporaldirname)
        local_cmd.cwd.chdir("./" + self.temporaldirname)
        command = self.sevenzip["a"]["../" + self.archivename]["-r"]["-t"+self.filetype]
        command()
        local_cmd.cwd.chdir("./..")
        shutil.rmtree(self.temporaldirname)

    def remove(self, filename):
        """Removes a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["d"][self.archivename]["/".join(filename)]
        command()

    def read(self, filename):
        temp_name = os.path.join(self.temporaldirname, filename)
        if os.path.exists(temp_name):
            return open(temp_name, "r").read()
        content = ""
        """Reads a file inside the archive. Notes that filename is an list-compatible object."""
        command = self.sevenzip["x"][self.archivename]["-so"]["/".join(filename)]
        return command()

    @classmethod
    def get_size(cls, start_path = '.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
