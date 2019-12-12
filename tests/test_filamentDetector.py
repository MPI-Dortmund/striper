import stripper.filamentDetector as fD
import unittest

class Test_javaClass_in_pythonDict(unittest.TestCase):
    def test_createDetectionThresholdRange(self):
        DetectionThresholdRange=fD.createDetectionThresholdRange(lower_threshold=0.2,upper_threshold=0.5)
        self.assertEqual(DetectionThresholdRange["lower_threshold"],0.2)
        self.assertEqual(DetectionThresholdRange["upper_threshold"], 0.5)

    def test_createFilamentDetectorContext(self):
        fDc=fD.createFilamentDetectorContext(sigma=0.2, lower_threshold=0.13, upper_threshold=0.3)
        self.assertEqual(fDc["sigma"],0.2)
        self.assertEqual(fDc["thresholdRange"]["lower_threshold"], 0.13)
        self.assertEqual(fDc["thresholdRange"]["upper_threshold"], 0.3)

class Test_filamentWidthToSigma(unittest.TestCase):
    def test_filamentWidthToSigma(self):
        self.assertEqual(1.3660254037844388,fD.filamentWidthToSigma(3))