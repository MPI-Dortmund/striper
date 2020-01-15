from scipy.optimize import curve_fit
from math import sqrt as math_sqrt
from numpy import where,arange,exp,pi, asarray,ones, sqrt as np_sqrt
from skimage.morphology import skeletonize
from skimage.util import invert

from stripper.helper import JAVA_MIN_DOUBLE,JAVA_MAX_DOUBLE,Polygon
from stripper.lineTracer import countNeighbors,extractLines
from stripper.box import BoxPositionIterator

#todo: numpy array instead of PIL img. Should I swap the loop operation over col,row??
"""
more info hier https://stackoverflow.com/questions/384759/how-to-convert-a-pil-image-into-a-numpy-array
needs noticing is that Pillow-style im is column-major while numpy-style im2arr is row-major. 
    However, the function Image.fromarray already takes this into consideration. 
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
    :param lines:  list of  object helper.polygon       [HashMap<Integer, ArrayList<Polygon>>]
    :param filamenFilter_context: dict with info about the filament filter. Should be crated via 'createFilamentFilterContext'
    :param input_images: list of images (the stack)     [ImageStack]
    :param response_maps:                               [ImageStack]
    :return:    list of filtered images                 [HashMap<Integer, ArrayList<Polygon>>]
    """
    if isValid_FilamentFilterContext(filamenFilter_context) is False:
        print("ERROR> invalid filamenFilter_context variable. Use 'createFilamentFilterContext(	min_number_boxes = 0,min_line_straightness = 0,window_width_straightness = 5,removement_radius = 0,fit_distribution = False,sigma_min_response = 0,sigma_max_response = 0,min_filament_distance = 0,border_diameter = 0,double_filament_insensitivity = 1,userFilters = None,box_size = 1,box_distance = 1,mask = None)' to create it")
        exit(-1)

    filtered_lines = list()
    masks = filamenFilter_context["mask"]

    #todo: when I'll be able to debug I have to see into it. I canno understand how could work input_images[pos]
    for pos in range(len(input_images)):
        line_image = ones(input_images[0].shape,dtype=bool)
        drawLines(detected_lines=lines[pos], im=line_image, fg=False)  #error
        #line_image=invert(line_image)         # --> because my init i do not need that
        # todo: more test. Since I already skeletonized in a previous functions and now i do not invert the image because my init. the following 2 operations are wrong.
            # Since a test the code step by step and not the wntire workflow could be that I'll have to restore these operation
        #line_image=skeletonize(line_image)       #https://scikit-image.org/docs/dev/auto_examples/edges/plot_skeleton.html
        #line_image = invert(line_image)
        maskImage = masks[pos] if isinstance(masks,list) else None
        filtered_lines+=filterLineImage(line_image=line_image,response_image =response_maps[pos], filamenFilter_context=filamenFilter_context,mask = maskImage)
        #filtered_lines.put(slice_position, filteredLines); because it has an hashmap
    return filtered_lines



def filterLineImage(line_image,response_image,filamenFilter_context,mask=None):
    """
     1. Set border to zero      it was "private void setBorderToZero(ImageProcessor ip, int bordersize)"
	 2. Remove junctions
	 3. (Apply mask)            it was "private void applyMask(ImageProcessor lineImage, ImageProcessor mask)" I hard coded into this function
	 4. Straightness
	 5. User filter
	 6. length filter
	 7. Filter by response
	 8. Remove parallel lines
	 9. Length filter 2
    :param line_image:                                      [ImageProcessor]
    :param response_image:                                  [ImageProcessor]
    :param mask:                                            [ImageProcessor]
    :param filamenFilter_context: dict with info about the filament filter. Should be crated via 'createFilamentFilterContext'
    :return:
    """
    if isValid_FilamentFilterContext(filamenFilter_context) is False:
        print("ERROR> invalid filamenFilter_context variable. Use 'createFilamentFilterContext(	min_number_boxes = 0,min_line_straightness = 0,window_width_straightness = 5,removement_radius = 0,fit_distribution = False,sigma_min_response = 0,sigma_max_response = 0,min_filament_distance = 0,border_diameter = 0,double_filament_insensitivity = 1,userFilters = None,box_size = 1,box_distance = 1,mask = None)' to create it")
        exit(-1)

    setBorderToZero(line_image=line_image, bordersize=filamenFilter_context["border_diameter"])
    removeJunctions(line_image=line_image, removement_radius=filamenFilter_context["removement_radius"])

    #todo:check with a mask in order to adapt it to the python logic. I think you have just to replace 0 with True for cleaning code purpouse
    if mask is not  None:
        line_image[mask==0]=0

    lines = splitByStraightness(lines=extractLines(line_image),line_image=line_image, min_straightness=filamenFilter_context["min_line_straightness"], window_length=filamenFilter_context["window_width_straightness"], radius=filamenFilter_context["removement_radius"])

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



    lines=filterByLength(lines=lines, filamenFilter_context=filamenFilter_context)
    drawLines(detected_lines=lines,im=line_image,fg=False)
    lines=filterByResponseMeanStd(lines=lines, response_map=response_image, sigmafactor_max=filamenFilter_context["sigma_max_response"], sigmafactor_min=filamenFilter_context["sigma_min_response"],  double_filament_insensitivity=filamenFilter_context["double_filament_insensitivity"], fitDistr=filamenFilter_context["fit_distribution"])
    drawLines(detected_lines=lines, im=line_image, fg=False)
    lines=removeParallelLines(line_image=line_image, lines=lines, radius=filamenFilter_context["min_filament_distance"])
    return filterByLength(lines=lines, filamenFilter_context=filamenFilter_context)



def filterByResponseMeanStd(lines, response_map, sigmafactor_max, sigmafactor_min,  double_filament_insensitivity, fitDistr=False):
    """

    :param lines: list of  object helper.polygon
    :param response_map:
    :param sigmafactor_max:
    :param sigmafactor_min:
    :param double_filament_insensitivity:
    :param fitDistr:
    :return:
    """
    filtered=list()     # it will be a list of polygon
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
        fitted=fitNormalDistributionToHist(hist=getResponseHistogram(lines=lines, response_map=response_map))
        mean_response=fitted[0]
        sd = fitted[1]

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
                filtered.append(l)
    return filtered



def getResponseHistogram(lines, response_map):
    """

    :param lines: list of  object helper.polygon
    :param response_map:
    :return: an histogram
    """
    hist = [ 0 for i in range(256)]
    for l in lines:
        for x, y in zip(l.col, l.row):
            index = response_map[x, y]
            hist[index] += 1


def fitNormalDistributionToHist( hist):
    """
    https://riptutorial.com/it/scipy/example/31081/adatta-una-funzione-ai-dati-da-un-istogramma
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    :param hist: it is a list
    :return: [mean,sd] fitted curve
    """
    def gauss(x):
        """
        :param x: has to be a numpy array
        :return:
        """
        return exp(-0.5 * x ** 2 / np_sqrt(2 * pi))

    y = asarray(hist)
    fitResult, cov = curve_fit(gauss, xdata=arange(y.shape[0]),ydata=y)
    return fitResult


def meanResponse(l, response_map):
    """
    :param l: object helper.polygon
    :param response_map:
    :return:
    """
    s=0
    for i, j in zip(l.col, l.row):
        s+=response_map[i, j]
    return s/l.num



def removeJunctions(line_image,removement_radius):
    """
    :param line_image:
    :param removement_radius:
    :return:
    """
    juncPos = Polygon(col=[],row=[])
    index_r, index_c = where(line_image == False)  # coordinate pixel black
    for col, row in zip(index_r, index_c ):
            if isJunction(col=col, row=row, line_image=line_image, connected=True):
                juncPos.add_point(col,row)

    for col,row in zip(juncPos.col,juncPos.row):
        setRegionToWhite(col,row,img=line_image,radius=removement_radius)



def isJunction(col, row, line_image, connected=True):
    """
    :param col:
    :param row:
    :param line_image:
    :param connected:
    :return:
    """
    return countNeighbors(col=col, row=row, img=line_image, connected=connected) > 2



#todo: check in a real case scenario
def removeParallelLines(line_image, lines, radius):
    radius = int(radius)
    max_r=line_image.shape[0]
    max_c = line_image.shape[1]
    for l in lines:
        for r, c in zip(l.col, l.row):
            range_c = range(max(0, c - radius), min(max_c, c + radius))
            for x in range(max(0, r - radius), min(max_r, r + radius)):
                for y in range_c:
                    if line_image[x, y] is False and isOnLine(x=x, y=y, line=l) is False:
                        line_image[int(x), int(y)] = True
                        line_image[int(r), int(c)] = True
    return extractLines(line_image)

def isOnLine(x,y,line):
    """
    Check if the point (x,y) is on the line
    :param x:
    :param y:
    :param line: object helper.polygon
    :return:
    """
    for c,r in zip(line.col,line.row):
        if x==c and y==r:
            return True
    return False


def drawLines(detected_lines,im,fg=False):
    """
    The im for default is considered binary hence fg=False means Black) ... it works for L type too
    plot the lines, in detected_lines' on a new image of the given size.
    For default the bacground colour is white and the lines are black
    :param detected_lines: list of  object Line from 'ridge_detection.basicGeometry'
    :param im:  numpy array (it should be binary hence fg=False means Black) ... it works
    :param fg: lines color
    :return:
    """
    #todo: I created it to get as input a PIL image. In order to speed up the code now it gets a numpy array. Is it still ok? or so I have to swap 'line.col,line.row' ?
    """ plot the lines"""
    if isinstance(detected_lines, list) is False:
        detected_lines=[detected_lines]
    for line in detected_lines:
        for i,j in zip(line.col,line.row):
            im[int(i),int(j)] = fg

def splitByStraightness(lines,line_image, min_straightness, window_length, radius):
    """

    :param lines: list of  object helper.polygon
    :param line_image:                                  [ByteProcessor]
    :param min_straightness:
    :param window_length:
    :param radius:
    :return:
    """
    for l in lines:
        for i in range(l.num-window_length):
            s=getStraightness(l,i,i+window_length)
            if s<min_straightness:
                index = int(i + window_length / 2 + 1)
                setRegionToWhite(l.col[index],l.row[index],line_image,radius)
    return extractLines(line_image)


def setRegionToWhite(col, row, img, radius):
    """
    set as white a circle of radius on the input image
    :param col:
    :param row:
    :param img:     as binary numpy array
    :param radius:
    :return:
    """
    for i in range(-radius,radius+1):
        for j in range(-radius,radius+1):
            if img.shape[0] > col + i > -1 and img.shape[1] > row + j > -1:
                img[int(col + i), int(row + j)] = True



def getStraightness(line, start,end):
    """
    :param line: object helper.polygon
    :param start: index of the starting point
    :param end: index of the ending point
    :return:
    """

    s=0
    for i in range(start,end):
        s=+ math_sqrt( (line.col[i]-line.col[i+1]) * (line.col[i]-line.col[i+1])    +   (line.row[i]-line.row[i+1]) * (line.row[i]-line.row[i+1]) )
    distance =  math_sqrt( (line.col[start]-line.col[end]) * (line.col[start]-line.col[end])    +   (line.row[start]-line.row[end]) * (line.row[start]-line.row[end]) )
    #todo: vectorize it. Since I changed the structure of the input value it does not work
    """
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
    """
    return distance / s



def filterByLength(lines,filamenFilter_context):
    """
    :param lines: list of  object helper.polygon
    :param filamenFilter_context:
    :return: list of polygon obj (should i create them??)
    """
    filtered=list()
    for l in lines:
        if calcNumberOfBoxes(l,filamenFilter_context["box_size"],filamenFilter_context["box_distance"]) >= filamenFilter_context["min_number_boxes"]:
            filtered.append(l)
    return filtered



def calcNumberOfBoxes(l,boxSize,boxDistance):
    """

    :param l: helper.polygon obj
    :param boxSize:
    :param boxDistance:
    :return: the number of boxes in the polygon
    """
    n = 0
    it = BoxPositionIterator(p=l, boxsize=boxSize, boxdista=boxDistance, topleft=False)
    while it.hasNext():
        n+=1
        it.next()
    return n


def setBorderToZero(line_image, bordersize):
    """
    :param line_image:
    :param bordersize:
    """
    line_image[0:bordersize, :] = True
    line_image[line_image.shape[0]-bordersize:, :] = True
    line_image[:,0:bordersize] = True
    line_image[:,line_image.shape[1]-bordersize:] = True