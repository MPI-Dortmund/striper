"""
MIT License

Copyright (c) 2020 Max Planck Institute of Molecular Physiology

Author: Luca Lusnig (luca.lusnig@mpi-dortmund.mpg.de)
Author: Thorsten Wagner (thorsten.wagner@mpi-dortmund.mpg.de)
Author: Markus Stabrin (markus.stabrin@mpi-dortmund.mpg.de)
Author: Fabian Schoenfeld (fabian.schoenfeld@mpi-dortmund.mpg.de)
Author: Tapu Shaikh (tapu.shaikh@mpi-dortmund.mpg.de)
Author: Adnan Ali (adnan.ali@mpi-dortmund.mpg.de)


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



"""
JAVA CLASS THAT I CONVERTED IN PYTHON DICTIONARY
"""
from numpy import array
from ridge_detection.basicGeometry import Line
from PIL import Image
from math import floor, ceil
from copy import deepcopy


""" to be compatible with java inplementation I listed the min and max value for the 'invert' """
JAVA_MAX_FLOAT32=3.4028234663852886E38
JAVA_MIN_FLOAT32=1.1754943508222875E-38
JAVA_MAX_DOUBLE= 1.7976931348623157E308
JAVA_MIN_DOUBLE= 2.2250738585072014E-308
INTEGER_8BIT_MAX = 255
INTEGER_8BIT_MIN = 0

class Polygon:
    """
    row =x
    col =y
    NB:
    PIL image (x,y)
    numpy array (y,x)   --> shape[0],shape[1]
    """
    """row coordinates of the line/box points."""
    row = list()
    """ column coordinates of the line/box points. """
    col = list()
    """ number of points. """
    num = 0
    """ used to count the number of boxes"""
    index =0

    def __init__(self,col=None,row=None):
        self.row = row
        self.col = col
        self.num = 0 if col is None else len(col)

    def add_point(self,x,y):
        self.row.append(y)
        self.col.append(x)
        self.num+=1

    def isInList(self,col,row):
        """
        Check if the given point is in the polygon
        :param col:
        :param row:
        :return:
        """
        for c,r in zip(self.col,self.row):
            if c==col and r==row:
                return True
        return False

    def smart_cast_row_and_col(self):
        """
        Cast the col and row to be an integer using ceil or flor in function of the rdecimal value
        """
        for i in range(self.num-1):
            if self.row[i]<0.5:
                self.row[i] = 0
            elif 1>self.row[i]>0.5:
                self.row[i] = 1
            else:
                self.row[i] = floor(self.row[i]) if self.row[i] % int(self.row[i]) < 0.5 else ceil(self.row[i])
            if self.col[i] < 0.5:
                self.col[i] = 0
            elif 1 > self.col[i] > 0.5:
                self.col[i] = 1
            else:
                self.col[i] = floor(self.col[i]) if self.col[i] % int(self.col[i]) < 0.5 else ceil(self.col[i])


def same_polygon(p1,p2):
    """
    Check if the 2 polygon have the same points. They do not have to be in the same order
    """
    if len(p1.col) ==0 or len(p1.col)!=len(p2.col):
        return False
    for c1,r1 in zip(p1.col,p1.row):
        if p2.isInList(c1,r1) is False:
            return False
    return True

def included_in(p1,p2):
    """
    It does not consider if they are the same polygon
    If p1 is included in p2 return p1
    If p2 is included in p1 return p2
    else None
    """
    if len(p1.col) == len(p2.col):
        return None
    big=p1
    small=p2
    if len(p1.col)<len(p2.col):
        big=p2
        small=p1
    for c1,r1 in zip(small.col,small.row):
        if big.isInList(c1,r1) is False:
            return None
    return small

class Roi:
    """
    It is boxplacer-->LRoi.java that is basically the native ROI.java
    """
    line_id= None
    serialVersionUID = -322247483958866642
    def __init__(self,x,y,w,h,line_id):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.line_id = line_id


class Lines_of_ROI:
    """
        it is a dict of boxplacer-->Line.java
        List of list
        1) index self.lines is the id of the lines
        2) elements in the index-list are the Roi obj representing the line
    """
    serialVersionUID = -8716351003343014469


    def __init__(self):
        self.lines = list()

    def add_ROI(self,roi):
        """add the given roi to the correct line"""
        if isinstance(roi,Roi) is False:
            print("ERROR: invalid Roi obj.")
            exit(-1)
        if roi.line_id > len(self.lines):
            self.lines.append([roi])
        else:
            self.lines[roi.line_id].append(roi)

    def get_totLine(self):
        """
        :return: the number of lines
        """
        return len(self.lines)

    def get_totRoi_inLine(self, index):
        """
        return the number of Roi obj representing the index line
        :param index: index of the line of interest
        :return:
        """
        if index>len(self.lines):
            print(f"ERROR: out of range. Line in Lines_of_ROI not found: number of line is '{len(self.lines)}. index in {index}")
            exit(-1)
        return len(self.lines[index])

    def createLine(self):
        """ Create nex line in the list and return its index"""
        self.lines.append(list())
        return self.get_totLine()-1

def saturation(img,minValue=None,max_value=None):
    """
    Set the value higher than max_value to max_value and value lower min_value to min_value
    :param img:
    :param minValue: saturation minimum value
    :param max_value: saturation maximum value
    :return:
    """
    im=deepcopy(img)
    if minValue is not None:
        im[im<minValue]=minValue
    if max_value is not None:
        im[im>max_value]=max_value
    return im

def resize_img(img, resize=(1024, 1024)):
    """
    Resize the given image into the given size
    :param img: as numpy array
    :param resize: resize size
    :return: return the resized img as numpy array
    """
    im = Image.fromarray(img)
    return array(im.resize(resize, resample=Image.BILINEAR))

def isValid_Line_obj(l,activate_error=False):
    risp= not (isinstance(l, list) and isinstance(l[0], Line)) and not isinstance(l, Line)
    if risp is False and activate_error is True:
        print("ERROR: Invalid variables. It has to be a [list of] instance[s] of the class 'Line'.")
        exit(-1)
    return risp



def createSliceRange(slice_from,slice_to):
    """
    It is used to create a dict instead of the helicalPicker->gui->SliceRange.java class
    :param slice_from: first slice
    :param slice_to: last slice
    :return: dict
    """
    return {"slice_from":int(slice_from),"slice_to":int(slice_to)}



def param_json_for_ridge_detection(sigma,lower_th,upper_th,max_l_len,min_l_len,darkLine =False, doCorrecPosition=True, doEstimateWidth=True, doExtendLine=True, overlap=False):
    dl = "LIGHT" if darkLine is False else "DARK"
    ov = "SLOPE" if overlap is True else "NONE"

    data=dict()
    data["path_to_file"] =""
    data["mandatory_parameters"] = {
            "Sigma": sigma,
            "Lower_Threshold": lower_th,
            "Upper_Threshold": upper_th,
            "Maximum_Line_Length": max_l_len,
            "Minimum_Line_Length": min_l_len,
            "Darkline": dl,
            "Overlap_resolution": ov
    }
    data["optional_parameters"] =    {
            "Line_width":0,
            "High_contrast": 0,
            "Low_contrast": 0
    }
    data["further_options"] =    {
            "Correct_position": doCorrecPosition,
            "Estimate_width": doEstimateWidth,
            "doExtendLine": doExtendLine,
            "Show_junction_points":False,
            "Show_IDs": False,
            "Display_results":False,
            "Preview":False,
            "Make_Binary": False,
            "save_on_disk": False
    }
    return data


