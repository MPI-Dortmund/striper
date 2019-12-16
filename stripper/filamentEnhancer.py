from numpy import expand_dims,multiply,fft,empty,amax,argmax
from multiprocessing import Pool

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



"""
I copied the following functions from https://github.com/MPI-Dortmund/LineEnhancer/blob/master/lineenhancer/line_enhancer.py
Thorsten.wagner committed 10 Dec              1 parent 88cd94c commit 3c679acf6d6b0717de1bc5a105c19279e2e287c1 
"""
def enhance_images(input_images, maskcreator, num_cpus = -1):

    fft_masks = maskcreator.get_mask_fft_stack()
    #global all_kernels
    #all_kernels = fft_masks
    input_img_and_kernel = [(img, fft_masks) for img in input_images]
    if num_cpus > -1:
        pool = Pool(processes=num_cpus)
    else:
        pool = Pool()

    enhanced_images = pool.map(wrapper_fourier_stack, input_img_and_kernel)
    pool.close()
    pool.join()
    for img in enhanced_images:
        img["max_angle"] = img["max_angle"]*maskcreator.get_angle_step()

    return enhanced_images



def convolve(fft_image, fft_mask):

   # fft_mask = np.array(fft_mask)
    if len(fft_mask.shape) > 2:
        fft_image = expand_dims(fft_image, 2)
    result_fft = multiply(fft_mask, fft_image)
    result = fft.irfft2(result_fft, axes=(0, 1))
    result = fft.fftshift(result, axes=(0, 1))

    return result

def wrapper_fourier_stack(input_img_and_kernel):
    img_paths, kernels = input_img_and_kernel
    return enhance_image(fourier_kernel_stack=kernels, input_image=img_paths)

def enhance_image(fourier_kernel_stack, input_image):
    input_image_fft = fft.rfft2(input_image)
    number_kernels = fourier_kernel_stack.shape[2]
    result = convolve(input_image_fft, fourier_kernel_stack[:, :, 0])
    enhanced_images = empty((result.shape[0], result.shape[1], number_kernels))
    enhanced_images[:, :, 0] = result
    for i in range(1,number_kernels):
        result = convolve(input_image_fft, fourier_kernel_stack[:, :, i])
        enhanced_images[:, :, i] = result

    m = amax(enhanced_images, axis=2)
    maxID = argmax(enhanced_images, axis=2)
    return {"max_value": m, "max_angle": maxID}