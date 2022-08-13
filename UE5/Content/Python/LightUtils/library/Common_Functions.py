from unreal import EditorActorSubsystem, get_editor_subsystem


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
