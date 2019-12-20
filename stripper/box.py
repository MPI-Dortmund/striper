from stripper.helper import Roi, Lines_of_ROI
from PIL import Image,ImageDraw

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



class BoxPositionIterator:
    """ I barely translate the boxplacer-->BoxPositionIterator.java class """
    curr=0
    def __init__(self, p, boxsize, boxdista, topleft):
        self.p=p
        self.boxToBoxDistSq = boxdista * boxdista
        self.distToEndSq = (boxsize * boxsize) / 4.0
        self.topleft = topleft
        self.boxsize = boxsize

    def hasNext(self):
        """
        :return: the position of the next point, using the metric of  'nextPointPos'
        """
        return self.nextPointPos() > -1

    def nextPointPos(self):
        """
        :return: return the next point position. -1 if there is no next one
        """
        for i in range(self.curr+1, self.p.num-1):
            """ Point2D.distanceSq function call --> http://developer.classpath.org/doc/java/awt/geom/Point2D.html#distanceSq:double:double:double:double """
            distsq_to_start=(self.p.col[i]-self.p.col[0])*(self.p.col[i]-self.p.col[0]) + (self.p.row[i]-self.p.row[0])*(self.p.row[i]-self.p.row[0])
            distsq_to_prev=(self.p.col[i]-self.p.col[self.curr])*(self.p.col[i]-self.p.col[self.curr]) + (self.p.row[i]-self.p.row[self.curr])*(self.p.row[i]-self.p.row[self.curr])
            distsq_to_end=(self.p.col[i]-self.p.col[self.p.num-1])*(self.p.col[i]-self.p.col[self.p.num-1]) + (self.p.row[i]-self.p.row[self.p.num-1])*(self.p.row[i]-self.p.row[self.p.num-1])
            if distsq_to_start>self.distToEndSq and distsq_to_prev>=self.boxToBoxDistSq and distsq_to_end>self.distToEndSq:
                return i
        return -1

    def next(self):
        """return the next point of the polygon 'p'"""
        i=self.nextPointPos()
        if i> -1:
            self.curr =i
            col=self.p.col[i]
            row = self.p.row[i]
            if self.topleft is True:
                col = col - self.boxsize / 2
                row = row - self.boxsize / 2
            return [col,row]
        return None



def placeBoxesPainter(lines, target_img, placing_context):
    """
    I inverted col,row because at the beginning I have a np. array and convert it as PIL image to draw the box
    RED_PIXEL_LINE = (255, 0, 0)
    :param lines:           list of helper.Poligon
    :param target_img:      It is the original input image in grayscale as numpy array
    :param placing_context: dict with info about the box placing info filter. Should be crated via 'createBoxPlacingContext'
    :return: the target img with the painted boxes in RGB mode as PIL
    """
    #todo:  implement public ArrayList<Line> placeBoxes(ArrayList<Polygon> lines, ImagePlus targetImage, BoxPlacingContext placing_context)
    if isinstance(placing_context,dict ) is False or "slicePosition" not in placing_context.keys() or "box_size" not in placing_context.keys() or "box_distance" not in placing_context.keys() or "place_points" not in placing_context.keys():
        print("ERROR> invalid placing_context variable. Use 'createBoxPlacingContext(slicePosition =1,box_size = 2,box_distance = 4,place_points = False)' to create it")
        exit(-1)
    lines_in_roi=placeBoxes( lines=lines, placing_context=placing_context)
    pil_img=Image.fromarray(target_img).convert('RGB')
    draw = ImageDraw.Draw(pil_img)
    bs=placing_context["box_size"]
    for l in lines_in_roi.lines:
        for r in l:
            """ since the ROI's coordinates are calculated on np.array now I have to switch them"""
            draw.rectangle(xy=(int(r.y-bs/2),int(r.x-bs/2),int(r.y+bs/2),int(r.x+bs/2)),fill=None,outline=(255, 0, 0))
    return pil_img





def placeBoxes( lines, placing_context):
    """
    :param lines:           list of helper.Poligon
    :param placing_context: dict with info about the box placing info filter. Should be crated via 'createBoxPlacingContext'
    :return: the list of Roi to plot for each polygon in lines
    """
    if isinstance(placing_context,dict ) is False or "slicePosition" not in placing_context.keys() or "box_size" not in placing_context.keys() or "box_distance" not in placing_context.keys() or "place_points" not in placing_context.keys():
        print("ERROR> invalid placing_context variable. Use 'createBoxPlacingContext(slicePosition =1,box_size = 2,box_distance = 4,place_points = False)' to create it")
        exit(-1)

    box_size = placing_context["box_size"]

    lines_in_roi = Lines_of_ROI()   # it is the representation of the lines in box
    for l in lines:
        index=lines_in_roi.createLine()
        it = BoxPositionIterator(p=l, boxsize= box_size, boxdista=placing_context["box_distance"], topleft=True)
        while it.hasNext():
            point=it.next()
            if placing_context["place_points"] is True:
                box_size =1
            roi=Roi(x=point[0],y=point[1],w=box_size,h=box_size,line_id=index)
            lines_in_roi.add_ROI(roi=roi)
    return lines_in_roi


