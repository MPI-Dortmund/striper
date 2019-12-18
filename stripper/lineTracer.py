from stripper.helper import Polygon
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
    :return:
    """
    index_r, index_c = where(img == False)  # coordinate pixel black
    lines=list()
    for col, row in zip(index_r, index_c ):
        if isStartPoint(col=col, row=row, img=img, connected=True) is True:
            lines.append(traceLine(col=col, row=row, img=img))
    return lines


def traceLine(col, row, img):
    """
    Returns a Polygon obj
    :param col:
    :param row:
    :param img: as binary numpy array
    :param img_map: as binary numpy array
    :return:
    """
    p=Polygon(col=[], row=[])
    while True:
        point=getNext(col=col, row=row, img=img)
        # To avoid to rewrite a map image to find the lines I need this workaround over the list of point for avoiding inifinite loop
        #todo: rewriting getNext in a properly way I could avoid this workaround .... Do that if we will have performance problems or if you'd like to vectorize the code
        if point is None or p.isInList(col=point[0],row=point[1]) is True:
            break
        p.add_point(point[0],point[1])
        col=point[0]
        row = point[1]
    return p


def getNext(col, row, img):
    """
    Returns the coordinate of the next point if exists. otherwise None
    :param col:
    :param row:
    :param img: as numpy array
    :return:
    """
    for i in [-1,0,1]:
        for j in [-1, 0, 1]:
            if (j==0 and i== 0) or 0<col+i>=img.shape[0] or 0<row+j>=img.shape[1]:
                continue
            if  0<=col+i<img.shape[0] and 0<=row+j<img.shape[0] and img[col + i, row + j] ==False :
                return [col + i, row + j]
    return None


def countNeighbors(col, row, img, connected=True):
    """
    :param col:
    :param row:
    :param img: as numpy array
    :param connected:
    :return:
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
    :param col:
    :param row:
    :param img: as numpy array
    :param connected:
    :return:
    """
    return countNeighbors(col=col, row=row, img=img, connected=connected) == 1