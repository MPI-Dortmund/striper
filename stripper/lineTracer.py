from stripper.helper import Polygon,same_polygon
from  numpy import where

#todo: more test because i rewrote it
"""
Since my first translation was buggy and really slow because the use of an "img_map" to track the lines in order to find them.
I rewrote the functions without image_map as following.
"""
def extractLines(img):
    """
    return a list of polygon
    :param img: as binary numpy array
    :return: list of line as list of obj polygon
    """
    index_r, index_c = where(img == False)  # coordinate pixel black
    lines=list()
    for col, row in zip(index_r, index_c ):
        if isStartPoint(col=col, row=row, img=img, connected=True) is True:
            l=traceLine(col=col, row=row, img=img)

            """ Avoid to insert twice the same line """
            isinLines=False
            for p in lines:
                isinLines=same_polygon(p,l)
                if isinLines is True:
                    break
            if isinLines is False:
                lines.append(l)
    return lines


def traceLine(col, row, img):
    """
    It track the line starting from the given point. Returns as Polygon obj
    :param col:
    :param row:
    :param img: as binary numpy array
    :return: line as polygon obj
    """
    p=Polygon(col=[col], row=[row])
    while True:
        point=getNext(col=col, row=row, img=img,p=p)
        # To avoid to rewrite a map image to find the lines I need this workaround over the list of point for avoiding inifinite loop
        #todo: rewriting getNext using mask and .sum when you vectorize the code in order to clean and speed up the code ... pay attention top the border
        if point is None or p.isInList(col=point[0],row=point[1]) is True:
            break
        p.add_point(point[0],point[1])
        col=point[0]
        row = point[1]
    return p


def getNext(col, row, img,p):
    """
    Returns the coordinate of the next point if exists. otherwise None
    :param col:
    :param row:
    :param img: as numpy array
    :param p: list of polygon already processed in order to avoid to analyze the same pixel more than once
    :return: Returns the coordinate of the next point if exists. otherwise None
    """
    for i in [-1,0,1]:
        for j in [-1, 0, 1]:
            if (j==0 and i== 0) or 0<col+i>=img.shape[0] or 0<row+j>=img.shape[1]:
                continue
            if  0<=col+i<img.shape[0] and 0<=row+j<img.shape[0] and img[col + i, row + j] ==False and p.isInList(col=col+i,row=row+j) is False:
                return [col + i, row + j]
    return None


def countNeighbors(col, row, img, connected=True):
    """
    Return the number of pixel around the pixel.
    If connected is False evaluates pixels in the positions of the cardinal points
    :param col:
    :param row:
    :param img: as numpy array
    :param connected:
    :return: number of neighbors points
    """
    n=0
    if img[col, row] == False and col+1<img.shape[0] and row+1<img.shape[1]:
        if connected is True :
            for i in [-1,0,1]:
                for j in [-1, 0, 1]:
                    if j==0 and i==0:
                        continue
                    if img[col + i, row + j] == False:
                        n+=1
        else:
            n+= (img[col + 1, row] ==False ) + (img[col - 1, row] ==False) + (img[col, row + 1] ==False) + (img[col, row - 1] ==False)
    return n



def isStartPoint(col, row, img, connected=True):
    """
    Return True if the given point is the first (or last) in a line.
    In case of single point it returns False
    :param col:
    :param row:
    :param img: as numpy array
    :param connected:
    :return: True f the point is at the ends of the line
    """
    return countNeighbors(col=col, row=row, img=img, connected=connected) == 1