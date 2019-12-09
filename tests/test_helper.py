import stripper.helper as helper
import unittest
from numpy import array,array_equal,allclose,zeros
from copy import deepcopy

class Test_javaClass_in_pythonDict(unittest.TestCase):
    def test_createSliceRange(self):
        sliceRange=helper.createSliceRange(slice_from=0,slice_to=5)
        self.assertEqual(sliceRange["slice_from"],0)
        self.assertEqual(sliceRange["slice_to"], 5)

    def test_createDetectionThresholdRange(self):
        DetectionThresholdRange=helper.createDetectionThresholdRange(lower_threshold=0.2,upper_threshold=0.5)
        self.assertEqual(DetectionThresholdRange["lower_threshold"],0.2)
        self.assertEqual(DetectionThresholdRange["upper_threshold"], 0.5)

    def test_createFilamentEnhancerContext(self):
        FilamentEnhancerContext=helper.createFilamentEnhancerContext(	filament_width=0, mask_width=5,angle_step=3,equalize = True)
        self.assertEqual(FilamentEnhancerContext["filament_width"],0)
        self.assertEqual(FilamentEnhancerContext["mask_width"], 5)
        self.assertEqual(FilamentEnhancerContext["angle_step"], 3)
        self.assertTrue(FilamentEnhancerContext["equalize"])



class Test_invert(unittest.TestCase):
    def test_invert(self):
        x = array([[1, 2.0], [0, 0], [2, 3.]])
        expected_array = array([[-0.7 ,-1.7], [0.3, 0.3], [-1.7, -2.7]])
        self.assertTrue(allclose(helper.invert(img=deepcopy(x),m=0.1,M=0.2),expected_array, atol=0.0000001))


#for now only test_invalid_type it is running
class Test_createMask(unittest.TestCase):
    img= array([[1, 2.0], [0, 0]])
    mask_size=2

    def test_invalid_type(self):
        self.assertTrue(array_equal(zeros((self.mask_size, self.mask_size), dtype=float),helper.createMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=5)))

    def test_type0(self):
        expected_array= array([[1, 2.0], [0, 0]])
        out_array=helper.createMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=0)
        self.assertTrue(allclose(out_array, expected_array, atol=0.0000001))

    def test_type1(self):
        expected_array= array([[1, 2.0], [0, 0]])
        out_array=helper.createMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=1)
        self.assertTrue(allclose(out_array, expected_array, atol=0.0000001))