from PIL import Image
from math import sqrt as math_sqrt
from numpy import zeros,multiply,sqrt as np_sqrt, sum as np_sum
from stripper.helper import convert_ridge_detectionLine_toPolygon,invert,JAVA_MIN_DOUBLE,JAVA_MAX_DOUBLE,Polygon

"""
class Polygon seems to be used by thorsten just as a list of coordinate x,y.
Hence If i will need to translate Line obj from ridge detector I use helper.convert_ridge_detectionLine_toPolygon(Line)  
"""

def createFilamentFilterContext(	min_number_boxes = 0,
                                    min_line_straightness = 0,
                                    window_width_straightness = 5,
                                    removement_radius = 0,
                                    fit_distribution = False,
                                    sigma_min_response = 0,
                                    sigma_max_response = 0,
                                    min_filament_distance = 0,
                                    border_diameter = 0,
                                    double_filament_insensitivity = 1,
                                    userFilters = None,
                                    box_size = 1,
                                    box_distance = 1,
                                    mask = None):
    """
    It is used to create a dict instead of the helicalPicker-->FilamentFilter->FilamentFilterContext.java class
    :param min_number_boxes:
    :param min_line_straightness:
    :param window_width_straightness:
    :param removement_radius:
    :param fit_distribution:
    :param sigma_min_response:
    :param sigma_max_response:
    :param min_filament_distance:
    :param border_diameter:
    :param double_filament_insensitivity:
    :param userFilters:
    :param box_size:
    :param box_distance:
    :param mask:
    :return: dict
    """
    return {"min_number_boxes" : min_number_boxes,
            "min_line_straightness":min_line_straightness,
            "window_width_straightness":window_width_straightness,
            "removement_radius":removement_radius,
            "fit_distribution":fit_distribution,
            "sigma_min_response":sigma_min_response,
            "sigma_max_response":sigma_max_response,
            "min_filament_distance":min_filament_distance,
            "border_diameter":border_diameter,
            "double_filament_insensitivity": double_filament_insensitivity,
            "userFilters":userFilters,
            "box_size":box_size,
            "box_distance":box_distance,
            "mask":mask
            }



def isValid_FilamentFilterContext(ffc):
    """
    Check if the variable has all the info in the correct format. The correct one should be generated via 'createFilamentFilterContext'
    :param ffc:
    :return: True if everything is ok
    """
    if isinstance(ffc,dict) is False:
        return False
    k=ffc.keys()
    for v in ["min_number_boxes","min_line_straightness","window_width_straightness","removement_radius",
            "fit_distribution","sigma_min_response","sigma_max_response","min_filament_distance",
            "border_diameter","double_filament_insensitivity","userFilters","box_size","box_distance","mask"]:
        if v not in k:
            return False
    return True



def filterLines(lines,filamenFilter_context,input_images,response_maps):
    """
    :param lines:  list of  object Line from 'ridge_detection.basicGeometry'       [HashMap<Integer, ArrayList<Polygon>>]
    :param filamenFilter_context: dict with info about the filament filter. Should be crated via 'createFilamentFilterContext'
    :param input_images: list of images (the stack)     [ImageStack]
    :param response_maps:                               [ImageStack]
    :return:    list of filtered images                 [HashMap<Integer, ArrayList<Polygon>>]
    """
    lines=convert_ridge_detectionLine_toPolygon(lines)
    if isValid_FilamentFilterContext(filamenFilter_context) is False:
        print("ERROR> invalid filamenFilter_context variable. Use 'createFilamentFilterContext(	min_number_boxes = 0,min_line_straightness = 0,window_width_straightness = 5,removement_radius = 0,fit_distribution = False,sigma_min_response = 0,sigma_max_response = 0,min_filament_distance = 0,border_diameter = 0,double_filament_insensitivity = 1,userFilters = None,box_size = 1,box_distance = 1,mask = None)' to create it")
        exit(-1)

    filtered_lines = list()
    masks = filamenFilter_context["mask"]

    for pos,l in enumerate(lines):
        line_image = Image.new(mode="I", size=input_images[0].shape, color=0)
        drawLines(detected_lines=l, im=input_images[0].shape, fg=255)
        #todo: what about invert an skeleton
        #line_image=invert(line_image)
        #line_image.skeletonize();
		#line_image.invert();
        maskImage = masks[pos] if isinstance(masks,list) else None
        filtered_lines+=filterLineImage(line_image=line_image,input_image=input_images[pos],response_image =response_maps[pos], filamenFilter_context=filamenFilter_context,mask = maskImage)
        #filtered_lines.put(slice_position, filteredLines); because it has an hashmap
    return filtered_lines



def filterLineImage(line_image,input_image,response_image,filamenFilter_context,mask=None):
    """
     1. Set border to zero      it was "private void setBorderToZero(ImageProcessor ip, int bordersize)" I hard coded into this function
	 2. Remove junctions
	 3. (Apply mask)            it was "private void applyMask(ImageProcessor lineImage, ImageProcessor mask)" I hard coded into this function
	 4. Straightness
	 5. User filter
	 6. length filter
	 7. Filter by response
	 8. Remove parallel lines
	 9. Length filter 2
    :param line_image:                                      [ImageProcessor]
    :param input_image:                                     [ImageProcessor]
    :param response_image:                                  [ImageProcessor]
    :param mask:                                            [ImageProcessor]
    :param filamenFilter_context: dict with info about the filament filter. Should be crated via 'createFilamentFilterContext'
    :return:
    """
    if isValid_FilamentFilterContext(filamenFilter_context) is False:
        print("ERROR> invalid filamenFilter_context variable. Use 'createFilamentFilterContext(	min_number_boxes = 0,min_line_straightness = 0,window_width_straightness = 5,removement_radius = 0,fit_distribution = False,sigma_min_response = 0,sigma_max_response = 0,min_filament_distance = 0,border_diameter = 0,double_filament_insensitivity = 1,userFilters = None,box_size = 1,box_distance = 1,mask = None)' to create it")
        exit(-1)
    setBorderToZero(line_image=line_image,bordersize=filamenFilter_context["border_diameter"])
    removeJunctions(line_image=line_image, removement_radius=filamenFilter_context["removement_radius"])
    if mask is not  None:
        applyMask(line_image=line_image, mask=mask)

    lines = list() #=tracer.extractLines((ByteProcessor) line_image);   it is a list of Polygon
    lines = splitByStraightness(lines=lines,line_image=line_image, min_straightness=filamenFilter_context["min_line_straightness"], window_length=filamenFilter_context["window_width_straightness"], radius=filamenFilter_context["removement_radius"])

    #todo: translate this part of the code
    """
    		ArrayList<IUserFilter> userFilters = context.getUserFilters();
		if(userFilters!=null){
			for (IUserFilter filter : userFilters) {
				lines = filter.apply(input_image, response_image, line_image);

				drawLines(lines, line_image);
			}
		}
    """
    lines=filterByLength(lines=lines, minimum_number_boxes=filamenFilter_context["min_number_boxes"])
    drawLines(detected_lines=lines,im=line_image,fg=255)
    lines=filterByResponseMeanStd(lines=lines, response_map=response_image, sigmafactor_max=filamenFilter_context["sigma_max_response"], sigmafactor_min=filamenFilter_context["sigma_min_response"],  double_filament_insensitivity=filamenFilter_context["double_filament_insensitivity"], fitDistr=filamenFilter_context["fit_distribution"])
    drawLines(detected_lines=lines, im=line_image, fg=255)
    lines=removeParallelLines(line_image=line_image, lines=lines, radius=filamenFilter_context["min_filament_distance"])
    return filterByLength(lines=lines, minimum_number_boxes=filamenFilter_context["min_number_boxes"])



def applyMask(line_image, mask):
    """

    :param line_image:
    :param mask:
    :return:
    """
    for x in mask.shape[0]:
        for y in mask.shape[1]:
            if mask[x,y] ==0:
                line_image[x,y]=0



def filterByResponseMeanStd(lines, response_map, sigmafactor_max, sigmafactor_min,  double_filament_insensitivity, fitDistr=False):
    """

    :param lines:
    :param response_map:
    :param sigmafactor_max:
    :param sigmafactor_min:
    :param double_filament_insensitivity:
    :param fitDistr:
    :return:
    """
    filtered=list()     # it will be a list of polygon
    lines = convert_ridge_detectionLine_toPolygon(lines)
    ''' Calculate mean response over all lines '''
    sum_mean_line_response = 0
    for l in lines:
        sum_mean_line_response += meanResponse(l=l, response_map=response_map)
    mean_response = sum_mean_line_response / len(lines)

    ''' Calculate standard deviation of the response '''
    sd=0
    n=0
    for l in lines:
        n+=l.num
        for i, j in zip(l.col, l.row):
            value= response_map[i, j]-mean_response
            sd += (value*value)
    sd=math_sqrt(sd/n)

    ''' Fit a distribution to get better estimates for mean response and the standard deviation '''
    if fitDistr is True:
        fitted=fitNormalDistributionToHist(hist=getResponseHistogram(lines=lines, response_map=response_map),initMean=mean_response,initSD=sd)
        mean_response=fitted[2]
        sd = fitted[3]

    ''' Calculate the thresholds '''
    th_power=pow(10,-6)
    threshold_min = JAVA_MIN_DOUBLE if sigmafactor_min<th_power else mean_response-(sd*sigmafactor_min)
    threshold_max = mean_response + (sd * sigmafactor_max)
    if sigmafactor_max<th_power:
        '''no max threshold'''
        threshold_max=JAVA_MAX_DOUBLE
    elif threshold_max>255:
        threshold_max=254.9

    '''
    For each line: Count the number of positions (pixel) which has a response below threshold_min or above threshold_max.
    If the number if higher then a the number of positions times some factor (0-1) the filament will be excluded.
    '''
    for l in lines:
        nOver = 0
        nUnder = 0
        for x, y in zip(l.col, l.row):
            if response_map[x, y] > threshold_max:
                nOver += 1
            if response_map[x, y] < threshold_min:
                nUnder += 1
            numberOfPointsToBeExcluded = int(l.num * double_filament_insensitivity)
            if nUnder < numberOfPointsToBeExcluded and nOver < numberOfPointsToBeExcluded:
                filtered += l
    return filtered



def getResponseHistogram(lines, response_map):
    """

    :param lines:
    :param response_map:
    :return: an histogram
    """
    lines = convert_ridge_detectionLine_toPolygon(lines)
    hist = [ 0 for i in range(256)]
    for l in lines:
        for x, y in zip(l.col, l.row):
            index = response_map[x, y]
            hist[index] += 1


def fitNormalDistributionToHist( hist, initMean, initSD):
    """

    :param hist:
    :param initMean:
    :param initSD:
    :return:
    """
    #todo: implement fitNormalDistributionToHist
    return list()


def meanResponse(l, response_map):
    """
    :param l:
    :param response_map:
    :return:
    """
    l = convert_ridge_detectionLine_toPolygon(l)
    s=0
    for i, j in zip(l.col, l.row):
        s+=response_map[i, j]
    return s/l.num


def setBorderToZero(line_image, bordersize):
    """
    :param line_image:
    :param bordersize:
    :return:
    """
    # todo: implement setBorderToZero
    pass



def removeJunctions(line_image,removement_radius):
    """
    :param line_image:
    :param removement_radius:
    :return:
    """
    juncPos = Polygon(col=[],row=[])
    for x in line_image[0]:
        for y in line_image[1]:
            if isJunction(x=x,y=y,line_image=line_image,connected=True):
                juncPos.add_point(x,y)

    for x,y in zip(juncPos.col,juncPos.row):
        setRegionToBlack(x,y,img=line_image,radius=removement_radius)



def isJunction(x,y,line_image,connected=True):
    """
    :param x:
    :param y:
    :param line_image:
    :param connected:
    :return:
    """
    return countNeighbors(x=x,y=y,line_image=line_image,connected=connected) > 2



def countNeighbors(x,y,line_image,connected=True):
    """
    :param x:
    :param y:
    :param line_image:
    :param connected:
    :return:
    """
    n=0
    if line_image[x,y]>0:
        if connected is True:
            for i in [-1,0,1]:
                for j in [-1, 0, 1]:
                    if j==0 and i==0:
                        continue
                    if line_image[x+1,y+1]>0:
                        n+=1
        else:
            n+= (line_image[x+1,y]>0) + (line_image[x-1,y]>0) + (line_image[x,y+1]>0) + (line_image[x,y-1]>0)
    return n

def removeParallelLines(line_image, lines, radius):
    """

    :param ip:                                                                    [ByteProcessor]
    :param lines: list of  object Line from 'ridge_detection.basicGeometry'       [ArrayList<Polygon>]
    :param radius:
    :return:
    """
    #todo: it depends filamentFilter->LineTracer.java
    lines =convert_ridge_detectionLine_toPolygon(lines)
    for l in lines:
        for r,c in zip(l.col, l.row):
            for x in range(r-radius,r+radius):
                for y in range(c - radius, c + radius):
                    if x<0 or y<0 or x>=line_image[0] or y>=line_image[1]:
                        continue
                    if line_image[x,y]>0 and isOnLine(x=x,y=y,line=l) is False:
                        line_image[x,y]=0
                        line_image[r,c] = 0

    filtered_lines = list()
    # filtered_lines = tracer.extractLines(line_image) #tracer.extractLines((ByteProcessor) ip);
    return filtered_lines

def isOnLine(x,y,line):
    """
    Check if the point (x,y) is on the line
    :param x:
    :param y:
    :param line: object Line from 'ridge_detection.basicGeometry' or helper.Poligon
    :return:
    """
    line=convert_ridge_detectionLine_toPolygon(line)
    for c,r in zip(line.col,line.row):
        if x==c and y==r:
            return True
    return False

def drawLines(detected_lines,im,fg=255):
    """
    plot the lines, in detected_lines' on a new image of the given size.
    For default the bacground colour is black and the lines are white
    :param detected_lines: list of  object Line from 'ridge_detection.basicGeometry'
    :param im: PIL image
    :param fg: lines color
    :return:
    """
    """ plot the lines"""
    for line in convert_ridge_detectionLine_toPolygon(detected_lines):
        for i,j in zip(line.col,line.row):
            im[int(i), int(j)] = fg

def splitByStraightness(lines,line_image, min_straightness, window_length, radius):
    """

    :param lines: list of  object Line from 'ridge_detection.basicGeometry'
    :param line_image:                                  [ByteProcessor]
    :param min_straightness:
    :param window_length:
    :param radius:
    :return:
    """
    lines=convert_ridge_detectionLine_toPolygon(lines)
    filtered=list()
    for l in lines:
        for i in range(l.num-window_length):
            s=getStraightness(l,i,i+window_length)
            if s<min_straightness:
                index = int(i + window_length / 2 + 1)
                setRegionToBlack(l.col[index],l.row[index],line_image,radius)
    #ArrayList<Polygon> filtered = tracer.extractLines((ByteProcessor) line_image);
    return filtered


def setRegionToBlack(x,y,img,radius):
    """
    set as black a circle of radius on the input image
    :param x:
    :param y:
    :param img:
    :param radius:
    :return:
    """
    for i in range(-radius,radius+1):
        for j in range(-radius,radius+1):
            img[x+i,y+j]=0



def getStraightness(line, start,end):
    """
    :param line: object Line from 'ridge_detection.basicGeometry' or helper.Poligon
    :param start: index of the starting point
    :param end: index of the ending point
    :return:
    """
    line=convert_ridge_detectionLine_toPolygon(line)

    xend = line.col[end][:-1]
    xstart = line.col[start][1:]
    yend = line.row[end][:-1]
    ystart = line.row[start][1:]
    sx = xstart - xend
    sy = ystart - yend

    out_shape=sx.shape[0]
    pow_sx = zeros(out_shape)
    pow_sy = zeros(out_shape)
    sqrt_sum_pows = zeros(out_shape)

    multiply(sx, sx, out=pow_sx)
    multiply(sy, sy, out=pow_sy)
    sum_pows = pow_sx + pow_sy
    np_sqrt(sum_pows, out=sqrt_sum_pows)
    s =np_sum(sqrt_sum_pows)

    distance = math_sqrt( (line.col[start]-line.col[end])*(line.col[start]-line.col[end]) + (line.row[start]-line.row[end])*(line.row[start]-line.row[end]) )
    return distance/s



def filterByLength(lines,minimum_number_boxes):
    """
    :param lines: list of  object Line from 'ridge_detection.basicGeometry'
    :param minimum_number_boxes:
    :return: list of polygon obj (should i create them??)
    """
    lines = convert_ridge_detectionLine_toPolygon(lines)
    filtered=list()
    for l in lines:
        if calcNumberOfBoxes(l)>=minimum_number_boxes:
            filtered.append(l)
    return filtered



def calcNumberOfBoxes(l):
    """

    :param l:
    :return:
    """
    # todo: implement calcNumberOfBoxes ... it depends from 'BoxPositionIterator.java'
    l = convert_ridge_detectionLine_toPolygon(l)
    """
    BoxPositionIterator it = new BoxPositionIterator(p, context.getBoxSize(), context.getBoxDistance(), false);
		int N = 0;
		
		while(it.hasNext()){
			N++;
			it.next();
		}
		
		return N;
    """
    return 0