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

from datetime import datetime
from argparse import ArgumentParser
import mrcfile
from multiprocessing import cpu_count

from stripper.params import Params
from ridge_detection.helper import normalizeImg,INTEGER_8BIT_MIN,INTEGER_8BIT_MAX
from stripper.helper import resize_img, createSliceRange,saturation
from stripper.maskStackCreator import MaskStackCreator
from stripper.filamentEnhancer import enhance_images
from stripper.filamentFilter import filterLines,asarray
from stripper.filamentDetector import filamentDetectorWorker
from stripper.box import placeBoxesPainter
from numpy import mean,std,flipud
from PIL import Image

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
        isMrc=True
    except ValueError:
        img=asarray(Image.open(params.config_path_to_file))
        isMrc=False

    if params.resize is not None:
        img=resize_img(img=img,resize=params.resize)
    if params.convert8bit is True:
        img=normalizeImg(img=img,new_max=INTEGER_8BIT_MAX,new_min=INTEGER_8BIT_MIN,return_Aslist=False)

    """ START helicalPicker->gui->PipelineRunner.java --> run() """
    """ STEP 1: enhance images"""
    print(str(datetime.now())+" STEP 1: enhance images ")
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

    """ If the "Detection.Equalize" flag is True, the enhanced images have to:
        1) normalize via mean and std 
        2) saturate max to 5
    """
    if params.enhancerContext["equalize"] is True:
        enhanced_imgs = [(img-mean(img))/std(img) for img in enhanced_imgs]
        enhanced_imgs = [saturation(img=img,max_value=5) for img in enhanced_imgs]

    '''
     If the params.slice_range for a single input image case will be init via createSliceRange(slice_from=1,slice_to=1)
     I have to change it with  createSliceRange(slice_from=1,slice_to=params.slice_range["slice_from"]-params.slice_range["slice_from"]+1)
     '''
    enhanced_substack_slice_range = createSliceRange(slice_from=0,slice_to=params.slice_range["slice_from"]-params.slice_range["slice_from"])

    """ STEP 2: detect filaments"""
    print(str(datetime.now())+" STEP 2: detect filaments")
    lines_in_enhanced_substack,junctions_in_enhanced_substack = filamentDetectorWorker(stack_imgs=enhanced_imgs,
                                                        slice_range=enhanced_substack_slice_range,
                                                        filamentDetectContext=params.detectorContext)
    """ STEP 3: filament filaments"""
    print(str(datetime.now())+" STEP 3: filament filaments")
    input_imgs=[img] if isinstance(img,list) is False else img[params.slice_range["slice_from"]-params.slice_range["slice_from"]]
    if isinstance(input_imgs,list) is False:
        input_imgs=[input_imgs]

    filtered_lines= filterLines(lines=lines_in_enhanced_substack,
                                filamenFilter_context=params.filterContext,
                                input_images=input_imgs,
                                response_maps=enhanced_imgs,
                                junctions=junctions_in_enhanced_substack)

    img = placeBoxesPainter(lines=filtered_lines, target_img=img[0], placing_context=params.placing_context,box_top_left=False)
    if isMrc is True:
        img = Image.fromarray(flipud(asarray(img)))
    img.save("stripper_output.jpg")
    img.show()

    """ Correct slice positions for originak stack if only a substack was processed """
    #todo: is there somethings to do?

    """ END helicalPicker->gui->PipelineRunner.java --> run() """

    """  START helicalPicker->gui->PreviewActionListener.java or ApplyActionListener.java  after runner.getFilteredLines() """


    print("END:", datetime.now())
if __name__ == "__main__":
    run()


