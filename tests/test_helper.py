import stripper.helper as helper
import unittest
from numpy import array,array_equal,allclose,zeros
import sys
from io import StringIO

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



class Test_invert(unittest.TestCase):
    def test_invert(self):
        x = array([[1, 2.0], [0, 0], [2, 3.]])
        expected_array = array([[1,2], [0, 0], [2, 3]])
        helper.invert(img=x, m=0.1, M=0.2)
        self.assertTrue(array_equal(x,expected_array))


class Test_generateMask(unittest.TestCase):
    img= array([[1, 2.0], [0, 0]])
    mask_size=2

    def test_invalid_type(self):
        self.assertTrue(array_equal(zeros((self.mask_size, self.mask_size), dtype=float),helper.generateMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=5)))

    def test_type0(self):
        expected_array= array([[0, -5.23543306e+00], [1.31984404e-11 ,-1.04719755e+01]])
        out_array=helper.generateMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=0)
        self.assertTrue(allclose(out_array, expected_array, atol=0.0000001))

    def test_type1(self):
        expected_array= array([[0.00000000e+00, -1.42357804e-04], [-8.20949204e-32 ,-1.89850628e-04]])
        out_array=helper.generateMask(mask_size=self.mask_size, filamentwidth=0.3, maskwidth=2, t=1)
        self.assertTrue(allclose(out_array, expected_array, atol=0.0000001))


class Test_getTransformedMasks(unittest.TestCase):
    mask_size=8

    def test_error_case(self):
        with self.assertRaises(SystemExit):
            old_stdout = sys.stdout
            print_out = StringIO()
            sys.stdout = print_out
            helper.getTransformedMasks(30, 1, 1, 4, 0)
        sys.stdout = old_stdout
        self.assertEqual("ERROR: Mask size is not a power of 2. (maskSize=30)\n",print_out.getvalue())
