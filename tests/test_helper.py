import stripper.helper as helper
import unittest

class Test_javaClass_in_pythonDict(unittest.TestCase):
    def test_createSliceRange(self):
        sliceRange=helper.createSliceRange(slice_from=0,slice_to=5)
        self.assertEqual(sliceRange["slice_from"],0)
        self.assertEqual(sliceRange["slice_to"], 5)

    def test_createFilamentEnhancerContext(self):
        FilamentEnhancerContext=helper.createFilamentEnhancerContext(	filament_width=0, mask_width=5,angle_step=3,equalize = True)
        self.assertEqual(FilamentEnhancerContext["filament_width"],0)
        self.assertEqual(FilamentEnhancerContext["mask_width"], 5)
        self.assertEqual(FilamentEnhancerContext["angle_step"], 3)
        self.assertTrue(FilamentEnhancerContext["equalize"])