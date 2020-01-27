from math import sqrt
from stripper.helper import param_json_for_ridge_detection,Polygon
from ridge_detection import lineDetector
from datetime import datetime

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


def filamentDetectorWorker(stack_imgs, slice_range, filamentDetectContext):
    """
    it is public HashMap<Integer, ArrayList<Polygon>> getFilaments(SliceRange slice_range) of
        helicalPicker->FilamentDetector->FilamentDetectorWorker.java
    :param stack_imgs: list of images. Each image is a numpy array
    :param slice_range: dict. shold generate via helper.createSliceRange
    :param filamentDetectContext:  dict. shold generate via createFilamentDetectorContext
    :return: lines and junction got via the ridge detection script
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
                                       darkLine=False, doCorrecPosition=True, doEstimateWidth=True, doExtendLine=True,
                                       overlap=False)
    stack_range = stack_imgs[0] if isinstance(stack_imgs,list) is False else stack_imgs[slice_range["slice_from"]:slice_range["slice_to"]+1]
    lines = []
    junctions =[]

    #todo: I'll change the stack analysys. ... Let the junctions,lines list as list and not as list of lists as should be ... I'll always have a single img in stack_range in this point of the code
    # I have still to think how cahnge the structure of the code
    for input_image in stack_range:
        converted_pol=list()
        ld = lineDetector.LineDetector(params=p)
        print(str(datetime.now()) + " STEP 2: IN detect filaments->ld.detectLines")
        detected_lines=ld.detectLines(img=input_image)
        print(str(datetime.now()) + " STEP 2: OUT detect filaments->ld.detectLines")

        # convert the lines obj from RidgeDetection to Polygon object
        for v in detected_lines:
            converted_pol.append(Polygon(col=v.col, row=v.row))
        lines.append(converted_pol)
        junctions.append(ld.junctions)
    return lines,junctions


