from unreal import load_object, log_error, HoudiniPublicAPIBlueprintLib, log, Transform, HoudiniAsset

houdini_api = HoudiniPublicAPIBlueprintLib.get_api()


def start_session():
    """Try to start a houdini session provided number of times
    """
    attemption_count = 10
    create_houdini_session(attemption_count)


def create_houdini_session(attemption_count):
    """Attempt to create a houdini session recursively provided amount of times

    Args:
        attemption_count(int):

    """
    if not houdini_api.is_session_valid():
        if attemption_count > 0:
            log('Creating new Houdini session...')
            houdini_api.create_session()
            create_houdini_session(attemption_count - 1)
        else:
            log_error("Can't start houdini session.")
    else:
        log('Houdini session created successfully')


def load_houdini_asset(hda_path):
    """load houdini digital asset

    Args:
        hda_path(str):

    """
    return load_object(None, hda_path)


def instantiate_asset(hda, auto_bake=False, remove_output_after_bake=True): # ToDo check auto bake
    """Create an instance of provided houdini digital asset

    Args:
        hda(HoudiniAsset):
        auto_bake:
        remove_output_after_bake:
    """
    return houdini_api.instantiate_asset(hda, Transform(), enable_auto_cook=True, enable_auto_bake=auto_bake, remove_output_after_bake=remove_output_after_bake, replace_previous_bake=True)

