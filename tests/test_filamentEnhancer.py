import stripper.filamentEnhancer as filamentEnhancer
import unittest


class Test_javaClass_in_pythonDict(unittest.TestCase):

    def test_createFilamentEnhancerContext(self):
        FilamentEnhancerContext=filamentEnhancer.createFilamentEnhancerContext(	filament_width=0, mask_width=5,angle_step=3,equalize = True)
        self.assertEqual(FilamentEnhancerContext["filament_width"],0)
        self.assertEqual(FilamentEnhancerContext["mask_width"], 5)
        self.assertEqual(FilamentEnhancerContext["angle_step"], 3)
        self.assertTrue(FilamentEnhancerContext["equalize"])

