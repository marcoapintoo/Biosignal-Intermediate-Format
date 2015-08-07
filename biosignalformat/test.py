#!/usr/bin/python
import unittest
from biosignalformat import *

class TestBaseObjects(unittest.TestCase):
    def test_MinimalExperiment(self):
        provider = ArchiveProvider("experiment001.7z")
        experiment = Experiment({
            "name": "Exp!",
            "description": "blah!"
        })
        experiment.write(provider)
        with self.assertRaises(Exception):
            experiment.remove(provider)
        metadata = experiment.readMetadata(provider)
        self.assertEqual(metadata["name"], "Exp!")
        self.assertEqual(metadata["description"], "blah!")

    def test_MinimalStructure(self):
        provider = ArchiveProvider("experiment002.7z")
        experiment = Experiment({
            "name": "Exp!",
            "description": "blah!"
        })
        subject = Subject({
            "name": "Subject001",
            "description": "description-subject!"
        })
        session = Session({
            "name": "Subject001-Session001",
            "description": "description-subject-session!"
        })
        channelDataset = ChannelDataset({
            "name": "AF8"
        })
        channelDataset.rawData = [1e-1222, 2.344, 3.14159265358979323846264338327950288419716939937510582097494459230781640629]
        experiment.write(provider)
        with self.assertRaises(Exception):
            experiment.remove(provider)
        metadata = experiment.readMetadata(provider)
        self.assertEqual(metadata["name"], "Exp!")
        self.assertEqual(metadata["description"], "blah!")

def test_all():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBaseObjects)
    unittest.TextTestRunner(verbosity=2).run(suite)
