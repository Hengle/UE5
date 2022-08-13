from unreal import AttachmentRule, ComponentMobility, ScopedEditorTransaction, Actor, EditorLevelLibrary, \
    Vector, Rotator, log_warning, log
import sys
from LightUtils.library import Common_Functions


def find_clones(in_distance_threshold):
    selected = Common_Functions.get_selected_actors()
    
    mobility = ComponentMobility.STATIC
    rule = AttachmentRule.KEEP_WORLD

    clone_array = []
    clone_names = []  # For debug only
    
    with ScopedEditorTransaction("Find clones and attach") as trans:
        # Remove clones from SELECTED array and put them into Clone_array
        for index, actor in enumerate(selected):
            # Empty actor spawn bool
            clones_present = False
            clone_array_local = []  # ToDo check usage
            counter = 0
            actors_count = len(selected)
            actor_name = actor.get_name()
            clean_array = []
            clean_array_ind = []
            
            if actor_name in clone_names:
                continue
            else:                                  
                for i in range(actors_count):
                    i = (i+1) % actors_count
                    if index != i:
                        exception_selected = selected[i]
                        clean_array.append(exception_selected) 
                        clean_array_ind.append(i)
                
                for k in clean_array[:]:
                    second_selected = clean_array[counter]
                    second_name = second_selected.get_name()
                    
                    # Get distance
                    dist = actor.get_distance_to(second_selected)
                    
                    if dist <= in_distance_threshold:
                        clones_present = True
                        selected.remove(second_selected)
                        clean_array.remove(second_selected)
                        clone_names.append(second_name)
                        clone_array.append(second_selected)
                        clone_array_local.append(second_selected)
                    else:
                        counter = (counter+1) % actors_count

            # Create empty actor and attach clones
            if clones_present:
                main_actor_name = actor.get_actor_label()
                empty_actor_name = "CLONE_"+main_actor_name
                empty_actor = EditorLevelLibrary.spawn_actor_from_class(Actor, Vector(), Rotator())
                empty_actor.set_actor_label(empty_actor_name)
                root = empty_actor.get_editor_property("root_component")
                root.set_mobility(mobility)
                for clone in clone_array_local:               
                    clone.attach_to_actor(empty_actor, "None", rule, rule, rule, False)
    # Log result
    if clone_array:
        if len(clone_array) == 1:
            log_warning(f'{len(clone_array)} clone present in scene')
        else:
            log_warning(f'{len(clone_array)} clones present in scene')
    else:
        log("Everything is fine")
                

distance_threshold = int(sys.argv[1])
find_clones(distance_threshold)
    
