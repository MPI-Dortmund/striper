"""
JAVA CLASS THAT I CONVERTED IN PYTHON DICTIONARY
"""

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