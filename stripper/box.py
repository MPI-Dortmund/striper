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
