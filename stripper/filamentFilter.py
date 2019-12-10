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