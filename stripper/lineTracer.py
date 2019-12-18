from stripper.helper import Polygon
from  numpy import zeros

def extractLines(img):
    """
    return a list of polygon
    :param img: as numpy array
    :return:
    """
    lines=list()
    img_map=zeros(img.shape)
    rangeCol=range(img.shape[0])
    rangeRow = range(img.shape[1])
    for col in rangeCol:
        for row in rangeRow:
            if isStartPoint(col=col, row=row, img=img, connected=True) and img_map[col, row] == 0:
                img_map[col, row] =1
                lines.append(traceLine(col=col, row=row, img=img, img_map=img_map))

    for col in rangeCol:
        for row in rangeRow:
            if img[col,row] and img_map[col,row] == 0:
                img_map[col, row] =1
                lines.append(traceLine(col=col, row=row, img=img, img_map=img_map))

    return lines



def traceLine(col, row, img, img_map):
    """
    Returns a Polygon obj
    :param col:
    :param row:
    :param img: as numpy array
    :param img_map: as numpy array
    :return:
    """
    p=Polygon(col=[col], row=[row])
    img_map[col, row]=1
    while True:
        point=getNext(col=col, row=row, img=img, img_map=img_map)
        if point is None:
            break
        img_map[point[0],point[1]] = 1
        p.add_point(point[0],point[1])
    return p


def getNext(col, row, img, img_map):
    """
    Returns the coordinate of the next point if exists. otherwise None
    :param col:
    :param row:
    :param img: as numpy array
    :param img_map: as numpy array
    :return:
    """
    for i in [-1,0,1]:
        for j in [-1, 0, 1]:
            if (j==0 and i== 0) or isInside(col=col + 1, row=row + 1, img=img) is False:
                continue
            if  0<=col+i<img.shape[0] and 0<=row+j<img.shape[0] and img[col + i, row + j]>0 and 0<=col+i<img_map.shape[0] and 0<=row+j<img_map.shape[0]  and img_map[col + i, row + j]==0:
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
    if img[col, row] >0 and col+1<img.shape[0] and row+1<img.shape[1]:
        if connected is True :
            for i in [-1,0,1]:
                for j in [-1, 0, 1]:
                    if j==0 and i==0:
                        continue
                    if img[col + 1, row + 1]>0:
                        n+=1
        else:
            n+= (img[col + 1, row] > 0) + (img[col - 1, row] > 0) + (img[col, row + 1] > 0) + (img[col, row - 1] > 0)
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



def isInside(col, row, img):
    """
    :param col:
    :param row:
    :param img: as numpy array
    :return:
    """
    if col<0 or row<0 or col>=img.shape[0] or row>=img.shape[1]:
        return False
    return True