from math import sqrt
from stripper.helper import param_json_for_ridge_detection
from ridge_detection import lineDetector
from PIL import Image

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

#todo: test if it is ok.  ---> it invert it, skeletonize it and invert it again before returning the img
def binaryImage(shape_img,detected_lines):
    """
    :param shape_img:
    :param detected_lines:
    :return: plot the detectedLines as black on white background
    """
    im=Image.new(mode="I",size=shape_img,color=255)
    """ plot the lines"""
    for line in detected_lines:
        for i,j in zip(line.col,line.row):
            im[int(i), int(j)] = 0
    return im



def filamentDetectorWorker(stack_imgs, slice_range, filamentDetectContext):
    """

    :param stack_imgs: list of images
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
    lines=[]
    for i in range(slice_range["slice_from"],slice_range["slice_to"]+1):
        input_image = stack_imgs[i]
        p = param_json_for_ridge_detection(sigma=filamentDetectContext["sigma"],
                                           lower_th=filamentDetectContext["thresholdRange"]["lower_threshold"],
                                           upper_th=filamentDetectContext["thresholdRange"]["upper_threshold"],
                                           max_l_len=0, min_l_len=0,
                                           darkLine =False, doCorrecPosition=True, doEstimateWidth=False, doExtendLine=True, overlap=False)
        ld = lineDetector.LineDetector(params=p)
        detected_lines=ld.get_lines(in_img=input_image)
        binary_img = binaryImage(shape_img=input_image.shape,detected_lines=detected_lines)

        #todo:
        #ArrayList<Polygon> lines_current_image = tracer.extractLines((ByteProcessor) line_image);
        #l+=lines_current_image
    return lines
