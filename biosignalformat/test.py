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
        from biosignalformat.external import sample
        self.assertEqual(sample.ConstantVariable, 12)

class TestConverters(unittest.TestCase):
    def test_single_edf(self):
        from biosignalformat.external import base_converter
        #importer = base_converter.EDFImporter("ExampleEDF.edf", SevenZipArchiveProvider("ExampleEDFAscii.bif.7z"))
        importer = base_converter.EDFImporter("ExampleEDF.edf", XArchiveProvider("ExampleEDFAscii.bif.zip"))
        importer.convert()

    def atest_multiple_edf(self):
        from biosignalformat.external import base_converter
        importer = base_converter.EDFImporter("ExampleEDF.edf", SevenZipArchiveProvider("ExampleMultipleEDFAscii.bif.7z"))
        #importer = base_converter.EDFImporter("ExampleEDF.edf", ZipArchiveProvider("ExampleMultipleEDFAscii.bif.zip"))
        importer.convert()
        importer2 = base_converter.EDFImporter("ExampleEDF2.edf", experiment=importer.experiment, subject=importer.subject)
        importer2.convert()
        importer3 = base_converter.EDFImporter("ExampleEDF2.edf", experiment=importer.experiment)
        importer3.convert()

    def test_single_bdf(self):
        from biosignalformat.external import base_converter
        #importer = base_converter.BDFImporter("ExampleBDF.bdf", SevenZipArchiveProvider("ExampleBDFAscii.bif.7z"))
        importer = base_converter.BDFImporter("ExampleBDF.bdf", ZipArchiveProvider("ExampleBDFAscii.bif.zip"))
        importer.convert()

    def test_multiple_bdf(self):
        from biosignalformat.external import base_converter
        #importer = base_converter.EDFImporter("ExampleBDF.bdf", SevenZipArchiveProvider("ExampleMultipleBDFAscii.bif.7z"))
        importer = base_converter.EDFImporter("ExampleBDF.bdf", XArchiveProvider("ExampleMultipleBDFAscii-3.bif.zip"))
        importer.convert()
        importer2 = base_converter.EDFImporter("ExampleBDF.bdf", experiment=importer.experiment, subject=importer.subject)
        importer2.convert()
        importer3 = base_converter.EDFImporter("ExampleBDF.bdf", experiment=importer.experiment)
        importer3.convert()

def test_all():
    test_loader = unittest.TestLoader()
    #unittest.TextTestRunner(verbosity=2).run(test_loader.loadTestsFromTestCase(TestBaseObjects))
    #unittest.TextTestRunner(verbosity=2).run(test_loader.loadTestsFromTestCase(TestPlugins))
    unittest.TextTestRunner(verbosity=2).run(test_loader.loadTestsFromTestCase(TestConverters))
