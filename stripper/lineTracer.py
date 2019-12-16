from stripper.helper import Polygon
from  numpy import zeros

def extractLines(img):
    """
    return a list of polygon
    :param img:
    :return:
    """
    lines=list()
    img_map=zeros(img.shape)
    rangeX=range(img.shape[0])
    rangeY = range(img.shape[1])
    for x in rangeX:
        for y in rangeY:
            if isStartPoint(x=x,y=y,img=img,connected=True) and img_map[x,y] == 0:
                img_map[x, y] =1
                lines.append(traceLine(x=x,y=y,img=img,img_map=img_map))

    for x in rangeX:
        for y in rangeY:
            if img[x,y] and img_map[x,y] == 0:
                img_map[x, y] =1
                lines.append(traceLine(x=x,y=y,img=img,img_map=img_map))

    return lines



def traceLine(x, y, img, img_map):
    """
    Returns a Polygon obj
    :param x:
    :param y:
    :param img:
    :param img_map:
    :return:
    """
    p=Polygon(col=[x],row=[y])
    img_map[x,y]=1
    while True:
        point=getNext(x=x, y=y, img=img, img_map=img_map)
        if point is None:
            break
        img_map[point[0],point[1]] = 1
        p.add_point(point[0],point[1])
    return p


def getNext(x, y, img, img_map):
    """
    Returns the coordinate of the next point if exists. otherwise None
    :param x:
    :param y:
    :param img:
    :param img_map:
    :return:
    """
    for i in [-1,0,1]:
        for j in [-1, 0, 1]:
            if (j==0 and i== 0) or isInside(x=x+1,y=y+1,img=img):
                continue
            if  x+i<img.shape[0] and y+j<img.shape[0] and img[x+i,y+j]>0 and x+i<img_map.shape[0] and y+j<img_map.shape[0]  and img_map[x+i,y+j]==0:
                return [x+i,y+j]
    return None


def countNeighbors(x, y, img, connected=True):
    """
    :param x:
    :param y:
    :param img:
    :param connected:
    :return:
    """
    n=0
    if img[x, y] >0 and x+1<img.shape[0] and y+1<img.shape[1]:
        if connected is True :
            for i in [-1,0,1]:
                for j in [-1, 0, 1]:
                    if j==0 and i==0:
                        continue
                    if img[x + 1, y + 1]>0:
                        n+=1
        else:
            n+= (img[x + 1, y] > 0) + (img[x - 1, y] > 0) + (img[x, y + 1] > 0) + (img[x, y - 1] > 0)
    return n



def isStartPoint(x, y, img, connected=True):
    """
    :param x:
    :param y:
    :param img:
    :param connected:
    :return:
    """
    return countNeighbors(x=x, y=y, img=img, connected=connected) ==1



def isInside(x, y, img):
    """
    :param x:
    :param y:
    :param img:
    :return:
    """
    if x<0 or y<0 or x>=img.shape[0] or y>=img.shape[1]:
        return False
    return True