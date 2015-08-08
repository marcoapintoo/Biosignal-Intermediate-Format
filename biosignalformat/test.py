#!/usr/bin/python
import unittest
from biosignalformat import *

class TestBaseObjects(unittest.TestCase):
    def test_MinimalExperiment(self):
        provider = SevenZipArchiveProvider("experiment001.7z")
        #provider = ZipArchiveProvider("experiment001.zip")
        experiment = Experiment({
            "name": "Exp!",
            "description": "blah!"
        })
        experiment.setArchiver(provider)
        experiment.write()
        with self.assertRaises(Exception):
            experiment.remove(provider)
        metadata = experiment.readMetadata(provider)
        self.assertEqual(metadata["name"], "Exp!")
        self.assertEqual(metadata["description"], "blah!")

    def test_MinimalStructure7z(self):
        provider = SevenZipArchiveProvider("experiment002B.7z")
        experiment = Experiment({
            "name": "Exp!",
            "description": "blah!"
        })
        experiment.setArchiver(provider)
        subject = Subject({
            "name": "Subject001",
            "description": "description-subject!"
        })
        experiment.addSubject(subject)
        session = Session({
            "name": "Subject001-Session001",
            "description": "description-subject-session!"
        })
        subject.addSession(session)
        channel = Channel({
            "name": "AF8"
        })
        session.addChannel(channel)
        #channelDataset.rawData = [1e-1222, 2.344, 3.14159265358979323846264338327950288419716939937510582097494459230781640629]
        channel.setData([c/1e-12 for c in range(500000)])
        experiment.write()
        metadata = experiment.readMetadata()
        self.assertEqual(metadata["name"], "Exp!")
        self.assertEqual(metadata["description"], "blah!")

    def test_MinimalStructureZip(self):
        provider = ZipArchiveProvider("experiment002.zip")
        experiment = Experiment({
            "name": "Exp!",
            "description": "blah!"
        })
        experiment.setArchiver(provider)
        subject = Subject({
            "name": "Subject001",
            "description": "description-subject!"
        })
        experiment.addSubject(subject)
        session = Session({
            "name": "Subject001-Session001",
            "description": "description-subject-session!"
        })
        subject.addSession(session)
        channel = Channel({
            "name": "AF8"
        })
        session.addChannel(channel)
        #channelDataset.rawData = [1e-1222, 2.344, 3.14159265358979323846264338327950288419716939937510582097494459230781640629]
        channel.setData([c/1e-12 for c in range(500000)])
        experiment.write()
        metadata = experiment.readMetadata()
        self.assertEqual(metadata["name"], "Exp!")
        self.assertEqual(metadata["description"], "blah!")


class TestPlugins(unittest.TestCase):
    def test_plugins(self):
        from biosignalformat.plugins.cmd import sample
        #self.assertEqual(sample.ConstantVariable, 12)

def test_all():
    test_loader = unittest.TestLoader()
    unittest.TextTestRunner(verbosity=2).run(test_loader.loadTestsFromTestCase(TestBaseObjects))
    unittest.TextTestRunner(verbosity=2).run(test_loader.loadTestsFromTestCase(TestPlugins))
