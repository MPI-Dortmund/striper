from datetime import datetime
from argparse import ArgumentParser
import mrcfile
from multiprocessing import cpu_count

from stripper.params import Params,Image
from stripper.helper import normalizeImg,INTEGER_8BIT_MIN,INTEGER_8BIT_MAX,resize_img, createSliceRange
from stripper.maskStackCreator import MaskStackCreator
from stripper.filamentEnhancer import enhance_images
from stripper.filamentFilter import filterLines,asarray
from stripper.filamentDetector import filamentDetectorWorker
from stripper.box import placeBoxesPainter,createBoxPlacingContext
from numpy import mean,std,amin



# it is basically the run in the PipelineRunner.java
def run():
    parser = ArgumentParser("stripper parser tool")
    parser.add_argument(dest="config_filename",type=str, nargs='?',help="name of the config_file to use. Default value is 'example_config.json'")
    args=parser.parse_args()
    config_filename = args.config_filename if args.config_filename is not None else "example_config.json"
    print("START:",datetime.now())
    params=Params(config_filename)
    try:
        img=mrcfile.open(params.config_path_to_file).data
    except ValueError:
        img=asarray(Image.open(params.config_path_to_file))

    if params.resize is not None:
        img=resize_img(img=img,resize=params.resize)
    if params.convert8bit is True:
        img=normalizeImg(img=img,new_max=INTEGER_8BIT_MAX,new_min=INTEGER_8BIT_MIN)


    """ START helicalPicker->gui->PipelineRunner.java --> run() """
    """ STEP 1: enhance images"""
    maskcreator=MaskStackCreator(filament_width=params.enhancerContext['filament_width'],
                                 mask_size=img.shape[0],
                                 mask_width=params.enhancerContext['mask_width'],
                                 angle_step=params.enhancerContext['angle_step'],
                                 interpolation_order = 3,
                                 bright_background=False)

    """ the input images has to be always a list"""
    if isinstance(img,list) is False:
        img=[img]
    enhanced_imgs = enhance_images(input_images=img, maskcreator=maskcreator, num_cpus=cpu_count())

    """ for the stripper I need the 'max_value' images"""
    enhanced_imgs=[img["max_value"] for img in enhanced_imgs]

    """ If the "Detection.Equalize" flag is True, the enhanced images have to be normalize:
        1) via mean and std 
        2) between min img and 5
        3) between 0 255
    """
    if params.enhancerContext["equalize"] is True:
        enhanced_imgs = [(img-mean(img))/std(img) for img in enhanced_imgs]
        enhanced_imgs = [normalizeImg(img=img,new_max=5, new_min=amin(img)) for img in enhanced_imgs]
        enhanced_imgs = [normalizeImg(img=img, new_max=INTEGER_8BIT_MAX, new_min=INTEGER_8BIT_MIN) for img in enhanced_imgs]

    '''
     If the params.slice_range for a single input image case will be init via createSliceRange(slice_from=1,slice_to=1)
     I have to change it with  createSliceRange(slice_from=1,slice_to=params.slice_range["slice_from"]-params.slice_range["slice_from"]+1)
     '''
    enhanced_substack_slice_range = createSliceRange(slice_from=0,slice_to=params.slice_range["slice_from"]-params.slice_range["slice_from"])


    """ STEP 2: detect filaments"""
    lines_in_enhanced_substack = filamentDetectorWorker(stack_imgs=enhanced_imgs,
                                                        slice_range=enhanced_substack_slice_range,
                                                        filamentDetectContext=params.detectorContext)

    """ STEP 3: filament filaments"""
    input_imgs=[img] if isinstance(img,list) is False else img[params.slice_range["slice_from"]-params.slice_range["slice_from"]]
    if isinstance(input_imgs,list) is False:
        input_imgs=[input_imgs]

    filtered_lines= filterLines(lines=lines_in_enhanced_substack,
                                filamenFilter_context=params.filterContext,
                                input_images=input_imgs,
                                response_maps=enhanced_imgs)

    #todo: how create placing_context via params?
    placing_context = createBoxPlacingContext(slicePosition=1, box_size=64, box_distance=10, place_points=False)
    img = placeBoxesPainter(lines=filtered_lines, target_img=img[0], placing_context=placing_context,box_top_left=False)
    img.save("real_case.jpg")
    img.show()

    """ Correct slice positions for originak stack if only a substack was processed """
    #todo: is there somethings to do?

    """ END helicalPicker->gui->PipelineRunner.java --> run() """

    """  START helicalPicker->gui->PreviewActionListener.java or ApplyActionListener.java  after runner.getFilteredLines() """


    """ """
    print("END:", datetime.now())



if __name__ == "__main__":
    run()