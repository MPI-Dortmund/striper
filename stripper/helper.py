"""
JAVA CLASS THAT I CONVERTED IN PYTHON DICTIONARY
"""
from numpy import zeros,add,repeat,arange,tile,reshape,multiply,divide,exp

from math import pi


# in invert floatProcess img i have to use min and max of float or double?? see in the code
# https://docs.oracle.com/javase/8/docs/api/constant-values.html#java.lang.Float.MAX_VALUE
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


def createFilamentEnhancerContext(	filament_width, mask_width,angle_step,equalize = False):
    """
    It is used to create a dict instead of the FilamentEnhancer->FilamentEnhancerContext.java class
    :param filament_width: The filament width defines the how broad a filament is (measured in pixel)
    :param mask_width: mask width
    :param angle_step: The angle step defines the degree how fine the directions will be enhanced (measured in degree)
    :param equalize: If equalization is turned on, large high contrast contamination don't have less effect on
                     the detection. For default is False
    :return: dict
    """
    if isinstance(equalize,bool) is False:
        print(f"WARNING: invalid 'FilamentEnhancerContext.equalize' values: {equalize}. It has to be a boolean value."
              f"\n The default value, False, will be used")

    return {"filament_width": int(filament_width), "mask_width": int(mask_width), "angle_step": int(angle_step), "equalize": equalize}


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




