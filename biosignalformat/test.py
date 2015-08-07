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

def test_all():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBaseObjects)
    unittest.TextTestRunner(verbosity=2).run(suite)
