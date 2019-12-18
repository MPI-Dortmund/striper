"""
JAVA CLASS THAT I CONVERTED IN PYTHON DICTIONARY
"""
from numpy import zeros,multiply,divide,array,amin,amax
from ridge_detection.basicGeometry import Line
from PIL import Image





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

    def hasNext(self,boxToBoxDistSq,distToEndSq):
        return self.nextPointPos(boxToBoxDistSq=boxToBoxDistSq,distToEndSq=distToEndSq)

    def nextPointPos(self,boxToBoxDistSq,distToEndSq):
        pass

    def next(self):
        pass


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





def resize_img(img, resize=(1024, 1024)):
    """
    Resize the given image into the given size
    :param img: as numpy array
    :param resize: resize size
    :return: return the resized img as numpy array
    """
    im = Image.fromarray(img)
    return array(im.resize(resize, resample=Image.BILINEAR))

def normalizeImg(img,new_min=INTEGER_8BIT_MIN,new_max=INTEGER_8BIT_MAX):
    """
    Normalize the image. For default it is converted to an 8bit img
    :param img:
    :param new_max:
    :param new_min:
    :return:
    """
    new_img = zeros(img.shape)
    m = amin(img)
    divide(img - m, amax(img) - m, out=new_img)
    multiply(new_img, new_max - new_min, out=new_img)
    return new_img+new_min


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
