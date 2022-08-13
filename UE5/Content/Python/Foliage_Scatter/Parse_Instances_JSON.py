import json
from unreal import Transform, Vector, Quat, load_asset, InstancedFoliageActor, get_editor_subsystem, \
    UnrealEditorSubsystem, GameplayStatics, EditorActorSubsystem
from sys import argv
import os


def read_json(in_path: str):
    with open(in_path, "r") as f:
        return json.load(f)


def parse_json(in_json_data: dict):
    main_instance_list = []
    for foliage_type, instances in in_json_data.items():
        foliage_type_list = [foliage_type, ]
        for index, transform in instances.items():
            location_list = transform.get("location")
            orient_list = transform.get("orient")
            float_scale = transform.get("scale")
            # Create unreal data types
            location = Vector(location_list[0], location_list[1], location_list[2])
            rotation = Quat(orient_list[0], orient_list[1], orient_list[2], orient_list[3])
            scale = Vector(float_scale, float_scale, float_scale)
            # Create xform from generated data types
            xform = Transform()
            xform.rotation = rotation
            xform.scale3d = scale
            xform.translation = location

            foliage_type_list.append(xform)
        main_instance_list.append(foliage_type_list)
    return main_instance_list


def add_instances_to_foliage_actor(in_instances, in_world, in_foliage_actor):
    for foliage_type in in_instances:
        foliage_type_path = foliage_type.pop(0)
        loaded_foliage_type = load_asset(foliage_type_path)
        in_foliage_actor.add_instances(in_world, loaded_foliage_type, foliage_type)


def execute():
    world = get_editor_subsystem(UnrealEditorSubsystem).get_editor_world()
    editor_subsystem = get_editor_subsystem(EditorActorSubsystem)
    foliage_actor = GameplayStatics.get_actor_of_class(world, InstancedFoliageActor)
    if not foliage_actor:
        foliage_actor = editor_subsystem.spawn_actor_from_class(InstancedFoliageActor, Vector(0, 0, 0))
    # Get input
    #json_path = argv[1]
    json_path = input
    data = read_json(json_path)
    sampled_transforms = parse_json(data)
    add_instances_to_foliage_actor(sampled_transforms, world, foliage_actor)
    if os.path.isfile(json_path):
        os.remove(json_path)


if __name__ == "__main__":
    execute()


