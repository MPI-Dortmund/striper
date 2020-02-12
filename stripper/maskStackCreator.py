"""
MIT License

Copyright (c) 2020 Max Planck Institute of Molecular Physiology

Author: Luca Lusnig (luca.lusnig@mpi-dortmund.mpg.de)
Author: Thorsten Wagner (thorsten.wagner@mpi-dortmund.mpg.de)
Author: Markus Stabrin (markus.stabrin@mpi-dortmund.mpg.de)
Author: Fabian Schoenfeld (fabian.schoenfeld@mpi-dortmund.mpg.de)
Author: Tapu Shaikh (tapu.shaikh@mpi-dortmund.mpg.de)
Author: Adnan Ali (adnan.ali@mpi-dortmund.mpg.de)


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from math import pi
import functools
import scipy.ndimage
from numpy import zeros,add,repeat,arange,tile,reshape,multiply,divide,exp,fft,moveaxis,asarray

"""
I copied the following functions from https://github.com/MPI-Dortmund/LineEnhancer/blob/master/lineenhancer/line_enhancer.py
Thorsten.wagner committed 7 Sep 2018              1 parent 7f54d3d commit d8adf43b63568598c6df34b0fa6e4e67e0083733 
"""

""" order of the spline interpolation in scipy.ndimage for BICUBIC interpolation """
BICUBIC=3       #https://stackoverflow.com/questions/13242382/resampling-a-numpy-array-representing-an-image

class MaskStackCreator:

    def __init__(self, filament_width, mask_size, mask_width, angle_step, interpolation_order = BICUBIC, bright_background=False):
        self._filament_width = filament_width
        self._mask_size = mask_size
        self._mask_width = mask_width
        self._mask_stack = None
        self._mask_fft_stack = None
        self._angle_step = angle_step
        self._interpolation_order = interpolation_order
        self._bright_background = bright_background     #in the java code it used 't' in 'generateMask'

    def get_mask_stack(self):
        return self._mask_stack

    def get_mask_fft_stack(self):

        # Only calculate it once!
        if self._mask_fft_stack is not None:
            return self._mask_fft_stack

        self.init()

        return self._mask_fft_stack

    def init(self):
        mask = self.calculate_mask(self._mask_size, self._filament_width, self._mask_width)
        self._mask_fft_stack = self.calculate_fourier_mask_stack_vectorized(mask, self._angle_step)

    def set_interpolation_order(self, order):
        self._interpolation_order = order

    def get_angle_step(self):
        return self._angle_step

    def get_mask_size(self):
        return self._mask_size

    ''' this is the original function
    def calculate_mask(self, mask_size, filament_width, mask_width):
        mask = np.zeros(shape=(mask_size, mask_size))

        x0 = mask_size / 2.0 + 0.5
        y0 = mask_size / 2.0 + 0.5

        sigmax = mask_width / 2.355  # full width at half maximum
        varx = sigmax * sigmax
        sigmay = filament_width / 2.355
        vary = sigmay * sigmay

        background_factor = 1.0
        if self._bright_background:
            background_factor = -1.0
        for i in range(0, mask_size):
            for j in range(0, mask_size):
                y = j + 0.5
                x = i + 0.5
                value = background_factor * np.pi * sigmax * (vary - np.power(y - y0, 2)) / (2 * vary * sigmay) * np.exp(
                    -1.0 * (np.power(x - x0, 2) / (2 * varx) + np.power(y - y0, 2) / (2 * vary)))
                if np.sqrt((y - y0) ** 2 + (x - x0) ** 2) > 300:
                    value = 0
                mask[j, i] = value
        return mask
    '''

    ''' I adapted this function to match with the 'FilamentEnhancer->MaskCreator_.java' class '''
    def calculate_mask(self,mask_size, filamentwidth, maskwidth ):
        """
        It is used to return a maskinstead of the FilamentEnhancer->MaskCreator_.java class
        the parameter 't' is now the 'self._bright_background
        :param mask_size:
        :param filamentwidth:
        :param maskwidth:
        :return:
        """
        mask = zeros((mask_size, mask_size), dtype=float)

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

        if self._bright_background is False:
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
        else:
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

    def rotate_and_fft(self, mask, angle):
        rot_mask = scipy.ndimage.interpolation.rotate(mask, angle, reshape=False, order=self._interpolation_order)
        return rot_mask


    def calculate_fourier_mask_stack_vectorized(self, mask, angle_step):

        # calculate the fft for each rotation of the  mask
        # return a list of complex arrays

        angle_steps = range(0, 180, angle_step)
        # pool = multiprocessing.Pool()
        result = list(map(functools.partial(self.rotate_and_fft, mask), angle_steps))
        self._mask_stack = asarray(result)
        result_fft = fft.rfft2(self._mask_stack,axes=(-2,-1))

        result_fft = moveaxis(result_fft, 0, 2)

        return result_fft





