from unreal import LightComponent, log
from Lighting_Project.library import Common_Functions
import sys


LIGHT_PROPERTIES = {
    "max_draw_distance",
    "volumetric_scattering_intensity",
    "indirect_lighting_intensity"
}


def parse_unreal_output(in_list: list):
    """Find name and value from unreal output format:
    property_name = value
    """
    light_properties_to_set = {}
    value_list = in_list[1].split(":")
    if len(value_list) > 1:
        property_name = value_list[0]
        value = value_list[1]
        if value.replace('.', '', 1).isdigit():
            float_value = float(value)
        else:
            return
        if property_name in LIGHT_PROPERTIES:
            light_properties_to_set[property_name] = float_value
    return light_properties_to_set


def set_light_properties(in_unreal_output):
    """ Set light parameters from widget
    """
    valid_light_component = False
    selected = Common_Functions.get_selected_actors()
    property_dict = parse_unreal_output(in_unreal_output)
    if not selected:
        log("Nothing selected")
        return
    if property_dict:
        pass
    else:
        log("No parameters to set")
        return
    for actor in selected:
        get_root = actor.get_editor_property("root_component")
        all_components = get_root.get_children_components(False)
        all_components.append(get_root)
        for component in all_components:
            # Cast to light component
            is_light = Common_Functions.cast_to_class(LightComponent, component)
            if is_light:
                valid_light_component = True
                for name, value in property_dict.items():
                    if name == "max_draw_distance":
                        if value < 8000:
                            fade_value = value / 2
                        else:
                            fade_value = 5000
                        property_dict = {name: value, "max_distance_fade_range": fade_value}
                        component.set_editor_properties(property_dict)
                    else:
                        component.set_editor_property(name, value)

    if not valid_light_component:
        log("There is any LightComponent present")
    else:
        log("Success!")


if __name__ == "__main__":
    argument_list = sys.argv
    set_light_properties(argument_list)

