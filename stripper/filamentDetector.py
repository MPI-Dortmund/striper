from math import sqrt
from stripper.helper import param_json_for_ridge_detection
from ridge_detection import lineDetector
from numpy import zeros
from skimage.morphology import skeletonize
from skimage.util import invert
from stripper.lineTracer import extractLines

def filamentWidthToSigma(filament_width):
    """
    :param filament_width:
    :return:
    """
    return filament_width / (2*sqrt(3)) +0.5

def createDetectionThresholdRange(lower_threshold,upper_threshold):
    """
    It is used to create a dict instead of the helicalPicker->FilamentDetector->DetectionThresholdRange.java class
    :param lower_threshold:
    :param upper_threshold:
    :return:
    """
    return {"lower_threshold": lower_threshold, "upper_threshold": upper_threshold}

def createFilamentDetectorContext(sigma, lower_threshold, upper_threshold):
    """
    It is used to create a dict instead of the helicalPicker->FilamentDetector->FilamentDetectorContext.java class
    :param sigma:
    :param lower_threshold:
    :param upper_threshold:
    :return:
    """
    return {"sigma":sigma,"thresholdRange":createDetectionThresholdRange(lower_threshold=lower_threshold,upper_threshold=upper_threshold)}



def binaryImage(shape_img,detected_lines):
    """
    plot the detectedLines as black on white background
    :param shape_img:
    :param detected_lines:
    :return: numpy array
    """
    arr_im=zeros(shape_img,dtype=bool)
    """ plot the lines"""
    for line in detected_lines:
        #todo:If you change ridgeDetection out, you have to change that ...  I swap row and col of the lines because I get them from ridgeDetection prj. There I use PILImage. Since here I use numpy array (that have x,y swapped) I adapted that.
        for i,j in zip(line.row,line.col):
            arr_im[int(i),int(j)]=True

    #arr_im = invert(arr_im)        --> because my init i do not need that
    arr_im = skeletonize(arr_im)  # https://scikit-image.org/docs/dev/auto_examples/edges/plot_skeleton.html
    return invert(arr_im)



def filamentDetectorWorker(stack_imgs, slice_range, filamentDetectContext):
    """
    it is public HashMap<Integer, ArrayList<Polygon>> getFilaments(SliceRange slice_range) of
        helicalPicker->FilamentDetector->FilamentDetectorWorker.java
    :param stack_imgs: list of images. Each image is a numpy array
    :param slice_range: dict. shold generate via helper.createSliceRange
    :param filamentDetectContext:  dict. shold generate via createFilamentDetectorContext
    :return:
    """

    if isinstance(slice_range,dict ) is False or "slice_from" not in slice_range.keys() or "slice_from" not in slice_range.keys():
        print("ERROR> invalid slice_range variable. Use 'helper.createSliceRange(slice_from,slice_to)' to create it")
        exit(-1)
    if isinstance(filamentDetectContext,dict ) is False or "sigma" not in filamentDetectContext.keys() or "thresholdRange" not in filamentDetectContext.keys():
        print("ERROR> invalid filamentDetectorContext variable. Use 'createFilamentDetectorContext(slice_from,slice_to)' to create it")
        exit(-1)

    p = param_json_for_ridge_detection(sigma=filamentDetectContext["sigma"],
                                       lower_th=filamentDetectContext["thresholdRange"]["lower_threshold"],
                                       upper_th=filamentDetectContext["thresholdRange"]["upper_threshold"],
                                       max_l_len=0, min_l_len=0,
                                       darkLine=False, doCorrecPosition=True, doEstimateWidth=False, doExtendLine=True,
                                       overlap=False)
    stack_range = stack_imgs[0] if isinstance(stack_imgs,list) is False else stack_imgs[slice_range["slice_from"]:slice_range["slice_to"]+1]

    lines = []

    for input_image in stack_range:
        ld = lineDetector.LineDetector(params=p)
        detected_lines=ld.get_lines(in_img=input_image)
        binary_img = binaryImage(shape_img=input_image.shape,detected_lines=detected_lines)
        lines.append(extractLines(binary_img))
        del ld
    return lines
