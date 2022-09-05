"""This script is part of python script node"""

from unreal import get_editor_subsystem, UnrealEditorSubsystem, Paths, GameplayStatics, InstancedFoliageActor, \
    FoliageInstancedStaticMeshComponent
from os import path, mkdir
import datetime
import json

# Argument from node input
foliage_folder = directory
unreal_editor = get_editor_subsystem(UnrealEditorSubsystem)
editor_world = unreal_editor.get_editor_world()


def create_folders():
    """Check if folders exists in Saved, if not create new"""
    # Check if main folder exists
    saved_directory = Paths.project_saved_dir()
    main_path = f'{saved_directory}{foliage_folder}'
    main_path_exists = path.exists(main_path)
    if not main_path_exists:
        mkdir(main_path)
    # Create folder for working levels
    level_directory_path = f'{main_path}/{editor_world.get_name()}'
    path_exists = path.exists(level_directory_path)
    if not path_exists:
        mkdir(level_directory_path)
    # Create date folder
    current_date = datetime.date.today()
    format_date = f'{current_date.day}_{current_date.month}_{current_date.year}'
    date_folder_path = f'{level_directory_path}/{format_date}/'
    date_folder_exists = path.exists(date_folder_path)
    if not date_folder_exists:
        mkdir(date_folder_path)
    return date_folder_path


def create_json_file(in_path: str):
    """Pack instance information in json file format:
    foliage_actor:{
        static_mesh:{
            instance_index:{
                [
                    rotation:{},
                    translation:{},
                    scale3d:{}
                ]
            }
        }
    }"""
    main_dictionary = {}
    time = datetime.datetime.now()
    short_time = f'{time.hour}_{time.minute}_{time.second}'
    json_path = f'{in_path}{short_time}.json'
    foliage_actors = GameplayStatics.get_all_actors_of_class(editor_world, InstancedFoliageActor)
    # loop over multiple actors <WorldPartition>
    for foliage_actor in foliage_actors:
        foliage_components = foliage_actor.get_components_by_class(FoliageInstancedStaticMeshComponent)
        if foliage_components:
            foliage_dictionary = {}
            # Loop over foliage components
            for foliage_component in foliage_components:
                static_mesh = foliage_component.static_mesh
                instance_count = foliage_component.get_instance_count()
                instances_xforms = {}
                # Get instances for component
                for instance_id in range(instance_count):
                    xform_struct = foliage_component.get_instance_transform(instance_id, world_space=True)
                    instance_xforms = {
                        "rotation": [xform_struct.rotation.x,
                                     xform_struct.rotation.y,
                                     xform_struct.rotation.z,
                                     xform_struct.rotation.w],
                        "translation": [xform_struct.translation.x,
                                        xform_struct.translation.y,
                                        xform_struct.translation.z],
                        "scale3d": [xform_struct.scale3d.x,
                                    xform_struct.scale3d.y,
                                    xform_struct.scale3d.z]
                    }
                    instances_xforms[instance_id] = instance_xforms
                foliage_dictionary[static_mesh.get_path_name()] = instances_xforms
            main_dictionary[foliage_actor.get_path_name()] = foliage_dictionary
    #print(main_dictionary)
    if main_dictionary:
        with open(json_path, 'w') as output:
            json.dump(main_dictionary, output, indent=2)


def execute():
    json_folder = create_folders()
    create_json_file(json_folder)


if __name__ == "__main__":
    execute()

