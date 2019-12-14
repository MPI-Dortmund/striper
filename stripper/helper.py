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
    """ row coordinates of the line/box points. """
    row = list()
    """ column coordinates of the line/box points. """
    col = list()
    """ number of points. """
    num = 0
    def __init__(self,col=None,row=None):
        self.row = row
        self.col = col
        self.num = 0 if col is None else len(col)

    def add_point(self,x,y):
        self.row.append(y)
        self.col.append(x)
        self.num+=1

def resize_img(img, resize=(1024, 1024)):
    """
    Resize the given image into the given size
    :param img: as numpy array
    :param resize: resize size
    :return: return the resized img as numpy array
    """
    im = Image.fromarray(img)
    return array(im.resize(resize, resample=Image.BILINEAR))

def normalizeImg(img,new_max=INTEGER_8BIT_MAX,new_min=INTEGER_8BIT_MIN):
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
    return new_img


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
    data["mandatory_parameters"] =[]
    data["mandatory_parameters"].append(
        {
            "Sigma": sigma,
            "Lower_Threshold": lower_th,
            "Upper_Threshold": upper_th,
            "Maximum_Line_Length": max_l_len,
            "Minimum_Line_Length": min_l_len,
            "Darkline": dl,
            "Overlap_resolution": ov
    })
    data["optional_parameters"] =[]
    data["optional_parameters"].append(
    {
            "Line_width":0,
            "High_contrast": 0,
            "Low_contrast": 0
    })
    data["further_options"] =[]
    data["further_options"].append(
    {
            "Correct_position": doCorrecPosition,
            "Estimate_width": doEstimateWidth,
            "doExtendLine": doExtendLine,
            "Show_junction_points":False,
            "Show_IDs": False,
            "Display_results":False,
            "Preview":False,
            "Make_Binary": False,
            "save_on_disk": False
    })
    return data

def convert_ridge_detectionLine_toPolygon(line):
    if not isinstance(line,list):
        return Polygon(col=line.col,row=line.row) if isValid_Line_obj(line) is True else line
    else:
        return [Polygon(col=l.col,row=l.row) if isValid_Line_obj(l) is True else l for l in line]