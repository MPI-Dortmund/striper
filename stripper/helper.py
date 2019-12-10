"""
JAVA CLASS THAT I CONVERTED IN PYTHON DICTIONARY
"""
from numpy import zeros,add,repeat,arange,tile,reshape,multiply,divide,exp,fft,moveaxis
from math import pi
from scipy import ndimage
import functools


""" order of the spline interpolation in scipy.ndimage for BICUBIC interpolation """
BICUBIC=3       #https://stackoverflow.com/questions/13242382/resampling-a-numpy-array-representing-an-image


""" to be compatible with java inplementation I listed the min and max value for the 'invert' """
JAVA_MAX_FLOAT32=3.4028234663852886E38
JAVA_MIN_FLOAT32=1.1754943508222875E-38
JAVA_MAX_DOUBLE= 1.7976931348623157E308
JAVA_MIN_DOUBLE= 2.2250738585072014E-308
INTEGER_8BIT_MAX = 255
INTEGER_8BIT_MIN = 0


def createSliceRange(slice_from,slice_to):
    """
    It is used to create a dict instead of the helicalPicker->gui->SliceRange.java class
    :param slice_from: first slice
    :param slice_to: last slice
    :return: dict
    """
    return {"slice_from":int(slice_from),"slice_to":int(slice_to)}


def invert(img,m=INTEGER_8BIT_MIN,M=INTEGER_8BIT_MAX):
    """
    This function simulate the FloatProcessor.invert function. For more info see:
                        ij.process.FloatProcesor.invert() ln(493)
    Each pixel in the image is inverted using p=max-(p-min), where 'min' and 'max' are the display range limits
    :param img:
    :param m: min value
    :param M: max value
    :return: inverted image as in java
    """
    img = M-(img-m)
    return img

def generateMask(mask_size, filamentwidth, maskwidth, t):
    """
    It is used to return a maskinstead of the FilamentEnhancer->MaskCreator_.java class
    :param mask_size:
    :param filamentwidth:
    :param maskwidth:
    :param t: type
    :return:
    """
    mask = zeros((mask_size, mask_size), dtype=float)
    if t not in [0, 1]:
        return mask

    x0 = mask_size / 2 + 0.5
    y0 = mask_size / 2 + 0.5
    sigmax = maskwidth / 2.355  # Full width at half maximum
    varx = sigmax * sigmax
    sigmay = filamentwidth / 2.355
    vary = sigmay * sigmay

    index_x = repeat(arange(mask_size), mask_size)
    index_y = tile(arange(mask_size), mask_size)
    pow_index_x0 = zeros((mask_size, mask_size), dtype=float)
    pow_indey_y0 = zeros((mask_size, mask_size), dtype=float)
    res_exp = zeros((mask_size, mask_size), dtype=float)

    if t == 0:
        index_y = reshape(index_y, (mask_size, mask_size)) + 0.5
        index_x = reshape(index_x, (mask_size, mask_size)) + 0.5
        indey_y0 = reshape(index_y, (mask_size, mask_size)) - y0
        index_x0 = reshape(index_x, (mask_size, mask_size)) - x0
        multiply(index_x0, index_x0, out=pow_index_x0)
        multiply(indey_y0, indey_y0, out=pow_indey_y0)

        val = zeros((mask_size, mask_size), dtype=float)
        divide(multiply(-1.0 * pi * sigmax, vary - pow_indey_y0), 2 * vary * sigmay, out=val)
        val_exp = (divide(pow_index_x0, 2 * varx) + divide(pow_indey_y0, 2 * vary)) * -1
        exp(val_exp, out=res_exp)
        multiply(val, res_exp, out=mask)
    elif t == 1:
        indey_y0 = reshape(index_y, (mask_size, mask_size)) - y0
        index_x0 = reshape(index_x, (mask_size, mask_size)) - x0

        multiply(index_x0, index_x0, out=pow_index_x0)
        multiply(indey_y0, indey_y0, out=pow_indey_y0)

        val_exp = (divide(pow_index_x0, 2 * varx) + divide(pow_indey_y0, 2 * vary)) * -1

        exp(val_exp, out=res_exp)
        multiply(index_x0, res_exp, out=mask)

    value_to_add = -mask[0, 0]
    add(mask, value_to_add, out=mask)

    """
    the 'fp' is the 'mask' var in the java code
    The following code is useless because it comments the multiply step
    // Normalize
		double sum = 0;
		for(int x = 0; x < fp.getWidth(); x++){
			for(int y = 0; y < fp.getHeight(); y++){
				sum += fp.getf(x, y);
			}
		}
		double scale = 1.0/sum;
		//fp.multiply(scale);
    """
    return mask



""" 
I adapted the following 2 functions 
 from https://github.com/MPI-Dortmund/LineEnhancer/blob/master/lineenhancer/image_reader.py
 
 https://github.com/MPI-Dortmund/LineEnhancer/blob/master/lineenhancer/line_enhancer.py
Thorsten.wagner committed on Sep 7, 2018              1 parent 7f54d3d commit d8adf43b63568598c6df34b0fa6e4e67e0083733 
"""
def rotate_and_fft(mask, angle):
    return ndimage.interpolation.rotate(mask, angle, reshape=False, order=BICUBIC)


def getTransformedMasks( mask_size, filament_width, mask_width, angle_step,t):
    """
    calculate the fft for each rotation of the  mask return a list of complex arrays
    I adapted the 'calculate_fourier_mask_stack_vectorized' from https://github.com/MPI-Dortmund/LineEnhancer/blob/master/lineenhancer/maskstackcreator.py
    In java it was SYNCHRONIZED ... I'm not going to implement multithread but multiprocess. !!!
    https://stackoverflow.com/questions/7848471/what-does-synchronized-mean-in-java
    It replace the whole 'FilamentEnhancer->TransformedMaskProvider.java' class

    :param mask_size:
    :param filament_width:
    :param mask_width:
    :param angle_step:
    :param t:
    :return: fft for each rotation of the  mask return a list of complex arrays
    """
    if (mask_size & (mask_size - 1)) != 0:
        print(f"ERROR: Mask size is not a power of 2. (maskSize={mask_size})")
        exit(-1)

    mask = generateMask(mask_size, filament_width, mask_width, t)
    angle_steps = range(0, 180, angle_step)
    mask_stack = list(map(functools.partial(rotate_and_fft, mask), angle_steps))
    result_fft = fft.rfft2(mask_stack,axes=(-2,-1))
    result_fft = moveaxis(result_fft, 0, 2)
    return result_fft



"""
My old code. I translated it directly from java
def getTransformedMasks( mask_size, filament_width, mask_width, angle_step,t):
    if (mask_size & (mask_size - 1)) != 0:
        print(f"ERROR: Mask size is not a power of 2. (maskSize={mask_size})")
        exit(-1)

    fp = generateMask(mask_size, filament_width, mask_width, t)
    fftOfFilters = [fft.fft2(fp)]

    for i in range(1,int(180/angle_step)):
        fftOfFilters.append(fft.fft2(ndimage.rotate(input=fp, angle=i*angle_step,order=BICUBIC)))

    return fftOfFilters
"""