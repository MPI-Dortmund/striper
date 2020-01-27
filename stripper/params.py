
from json import load as json_load
from json import JSONDecodeError
from os import path
from PIL import Image
from stripper.helper import createSliceRange
from stripper.filamentDetector import createFilamentDetectorContext,filamentWidthToSigma
from stripper.filamentEnhancer import createFilamentEnhancerContext
from stripper.filamentFilter import createFilamentFilterContext
from stripper.box import createBoxPlacingContext
from math import sqrt



def load_json(config_path):
    """
    Check if the config file exist and has a valid json format
    :param config_path: path to the json config file
    :return: loaded json file
    """
    if path.isfile(config_path) is False:
        print("ERROR: file '"+config_path+"' not found!")
        exit(-1)
    try:
        with open(config_path) as json_file:
            return  json_load(json_file)
    except JSONDecodeError:
        print("Your configuration file seems to be corruped. Please check if it is valid.")

class Params:
    def __init__(self, cfg):
        self.cfg=load_json(cfg)
        self.config_path_to_file = self.cfg["path_to_file"]
        self.slice_range=createSliceRange(slice_from=0,slice_to=0)          #todo we will change these values when I'll open the stack, if it is a stack

        self.detectorContext=createFilamentDetectorContext(sigma=filamentWidthToSigma(self.cfg["Detection"]["Filament_width"]),
                                                           lower_threshold=self.cfg["Detection"]["Lower_Threshold"],
                                                           upper_threshold=self.cfg["Detection"]["Upper_Threshold"])

        self.enhancerContext=createFilamentEnhancerContext(filament_width=self.cfg["Detection"]["Filament_width"],
                                                           mask_width=self.cfg["Detection"]["Mask_width"],
                                                           angle_step=2,
                                                           equalize=self.cfg["Detection"]["Equalize"])

        m=self.cfg["Filtering"]["Custom_mask"]
        min_filament_distance= sqrt( 2*(self.cfg["Filtering"]["Allowed_box_overlapping"]*self.cfg["General"]["Box_size"])*(self.cfg["Filtering"]["Allowed_box_overlapping"]*self.cfg["General"]["Box_size"])  ) /2

        self.filterContext=createFilamentFilterContext(min_number_boxes = self.cfg["Filtering"]["Min_number_of_boxes"],
                                    min_line_straightness = self.cfg["Filtering"]["Min_straightness"],
                                    window_width_straightness = self.cfg["Filtering"]["Window_size"],
                                    removement_radius = int(self.cfg["General"]["Box_size"]/2),
                                    fit_distribution = False,
                                    sigma_min_response = self.cfg["Filtering"]["Sigma_min_response"],
                                    sigma_max_response = self.cfg["Filtering"]["Sigma_max_response"],
                                    min_filament_distance = min_filament_distance,
                                    border_diameter = int(self.cfg["General"]["Box_size"]/2),
                                    double_filament_insensitivity = 1-self.cfg["Filtering"]["Sensitivity"],
                                    userFilters = None,
                                    box_size = self.cfg["General"]["Box_size"],
                                    box_distance = self.cfg["General"]["Box_distance"],
                                    mask = None if m is False else Image.open(m))

        #todo: the slicePosition has to be changed in the stack position ... of course if I'll decide to use a stack
        self.placing_context=createBoxPlacingContext(slicePosition =1,box_size = self.cfg["General"]["Box_size"],
                                                     box_distance = self.cfg["General"]["Box_distance"],
                                                     place_points = self.cfg["General"]["place_points"])

        self.convert8bit=self.cfg["General"]["Convert_to_8bit"] if "Convert_to_8bit" in self.cfg["General"] else False
        self.resize = (self.cfg["General"]["Resize"],self.cfg["General"]["Resize"]) if "Resize" in self.cfg["General"] else None



