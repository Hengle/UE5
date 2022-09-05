"""This script is part of python script node"""
import json
from unreal import Transform, Vector, Quat, InstancedFoliageActor, get_editor_subsystem, UnrealEditorSubsystem, \
    GameplayStatics, EditorActorSubsystem, AssetRegistryHelpers, Name
from os import path

actor_subsystem = get_editor_subsystem(EditorActorSubsystem)
unreal_subsystem = get_editor_subsystem(UnrealEditorSubsystem)
asset_registry = AssetRegistryHelpers.get_asset_registry()
foliage_types_asset_data = asset_registry.get_assets_by_class(Name("FoliageType_InstancedStaticMesh"))


def read_json(in_path: str):
    with open(in_path, "r") as f:
        return json.load(f)


def data_conversion(in_json_data: dict):
    """ Find foliage type with static mesh, and create correct data types
    """
    out_dict = {}
    for instance_actor, complex_dictionary in in_json_data.items():
        foliage_type_dict = {}
        for static_mesh, instance_info in complex_dictionary.items():
            loaded_asset = None
            # Replace static mesh with foliage type
            for asset_data in foliage_types_asset_data:
                loaded_asset = asset_data.get_asset()
                if static_mesh == loaded_asset.mesh.get_path_name():
                    break
                else:
                    continue
            if loaded_asset:
                # Replace transform with unreal Transform type
                transforms_list = []
                for instance_index, transform in instance_info.items():
                    location_list = transform.get("translation")
                    orient_list = transform.get("rotation")
                    float_scale = transform.get("scale3d")
                    # Create unreal data types
                    location = Vector(location_list[0], location_list[1], location_list[2])
                    rotation = Quat(orient_list[0], orient_list[1], orient_list[2], orient_list[3])
                    scale = Vector(float_scale[0], float_scale[1], float_scale[2])
                    # Create xform from generated data types
                    xform = Transform()
                    xform.rotation = rotation
                    xform.scale3d = scale
                    xform.translation = location
                    transforms_list.append(xform)
                foliage_type_dict[loaded_asset] = transforms_list
        out_dict[instance_actor] = foliage_type_dict
    return out_dict


def add_instances_to_foliage_actor(in_instances: dict):
    """ Add instance to foliage actor from correct dictionary
    """
    editor_world = unreal_subsystem.get_editor_world()
    main_foliage_actor = GameplayStatics.get_actor_of_class(editor_world, InstancedFoliageActor)
    for foliage_actor, instances_info in in_instances.items():
        foliage_actor_reference = actor_subsystem.get_actor_reference(foliage_actor)
        if not foliage_actor_reference:
            foliage_actor_reference = main_foliage_actor
        for foliage_type, transforms in instances_info.items():
            foliage_actor_reference.add_instances(editor_world, foliage_type, transforms)


def execute():
    json_path = input
    valid_path = path.exists(json_path)
    if valid_path:
        data = read_json(json_path)
        corrected_dict = data_conversion(data)
        add_instances_to_foliage_actor(corrected_dict)


if __name__ == "__main__":
    execute()
