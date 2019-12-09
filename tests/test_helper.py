import stripper.helper as helper
import unittest

class Test_createSliceRange(unittest.TestCase):
    def test_createSliceRange(self):
        sliceRange=helper.createSliceRange(slice_from=0,slice_to=5)
        self.assertEqual(sliceRange["slice_from"],0)
        self.assertEqual(sliceRange["slice_to"], 5)