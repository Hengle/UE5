from unreal import EditorActorSubsystem, get_editor_subsystem, EditorUtilityLibrary, EditorAssetLibrary, Object, \
    GameplayStatics, UnrealEditorSubsystem


def get_selected_actors():
    """ Get selected actors via Actor subsystem
    """
    actor_subsystem = get_editor_subsystem(EditorActorSubsystem)
    return actor_subsystem.get_selected_level_actors()


def cast_to_class(in_class_to_check, in_object):
    """Cast to class
    Args:
        in_class_to_check: unreal class
        in_object: input object
    """
    try:
        in_class_to_check.cast(in_object)
        return True
    except:
        return False


def get_selected_assets():
    """Get all selected assets"""
    return EditorUtilityLibrary.get_selected_assets()


def save_loaded_asset(in_asset: Object):
    EditorAssetLibrary.save_loaded_asset(in_asset)


def get_actor_by_class(in_class):
    world = get_editor_subsystem(UnrealEditorSubsystem).get_editor_world()
    return GameplayStatics.get_actor_of_class(in_class, world)
