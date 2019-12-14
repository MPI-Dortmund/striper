from stripper.helper import Roi, Lines_of_ROI

def createBoxPlacingContext(slicePosition =1,box_size = 2,box_distance = 4,place_points = False):
    """
    It is used to create a dict instead of the boxplacer-->BoxPlacingContext.java class
    :param slicePosition: Position where the boxes will be placed
    :param box_size:      side length of the boxes to be placed.
    :param box_distance:  The distance between two boxes
    :param place_points:  place_points True, if points instead of boxes should be placed
    :return: dict
    """
    return {"slicePosition": slicePosition,"box_size": box_size,"box_distance": box_distance,"place_points": place_points}


def placeBoxesPainter(lines, target_img, placing_context):
    """

    :param lines:           list of helper.Poligon
    :param target_img:      output img          #todo: should be PIL or numpy array?
    :param placing_context: dict with info about the box placing info filter. Should be crated via 'createBoxPlacingContext'
    :return:
    """
    #todo:  implement public ArrayList<Line> placeBoxes(ArrayList<Polygon> lines, ImagePlus targetImage, BoxPlacingContext placing_context)
    if isinstance(placing_context,dict ) is False or "slicePosition" not in placing_context.keys() or "boxsize" not in placing_context.keys() or "box_distance" not in placing_context.keys() or "place_points" not in placing_context.keys():
        print("ERROR> invalid placing_context variable. Use 'createBoxPlacingContext(slicePosition =1,box_size = 2,box_distance = 4,place_points = False)' to create it")
        exit(-1)
    allLines=Lines_of_ROI()
    for p in lines:
        pass
    pass


def placeBoxes( lines, target_img, placing_context):
    """

    :param lines:           list of helper.Poligon
    :param target_img:      output img          #todo: should be PIL or numpy array?
    :param placing_context: dict with info about the box placing info filter. Should be crated via 'createBoxPlacingContext'
    :return:
    """
    if isinstance(placing_context,dict ) is False or "slicePosition" not in placing_context.keys() or "boxsize" not in placing_context.keys() or "box_distance" not in placing_context.keys() or "place_points" not in placing_context.keys():
        print("ERROR> invalid placing_context variable. Use 'createBoxPlacingContext(slicePosition =1,box_size = 2,box_distance = 4,place_points = False)' to create it")
        exit(-1)

    #todo: what???
    for pos,img in enumerate(list(set(lines))):
        placing_context["slicePosition"]=pos
        lines_in_img = lines # todo: what???
        if len(lines_in_img):
            placeBoxesPainter(lines=lines_in_img, target_img=target_img, placing_context=placing_context)