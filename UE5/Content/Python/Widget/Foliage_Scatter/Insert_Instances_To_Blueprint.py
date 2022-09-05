"""These scripts are part of python script node"""
import unreal


def check_if_is_blueprint():
    """
        Unreal Args:
            blueprint: unreal.Blueprint
        Unreal Return:
            bool:
    """
    potential_blueprint = blueprint
    asset_path = potential_blueprint.get_class().get_outer().get_path_name()
    loaded_asset = unreal.load_asset(asset_path)
    if loaded_asset.get_class().get_name() == "Blueprint":
        return 1, asset_path
    return 0, None


is_blueprint, blueprint_path = check_if_is_blueprint()
######################################
# END
######################################


import unreal
import json


def read_json(in_path: str):
    with open(in_path, "r") as f:
        return json.load(f)


def create_list_of_transforms(json_data: dict,
                              in_static_mesh: unreal.StaticMesh,
                              in_blueprint_transform: unreal.Transform):
    """ Index 0 - Static Mesh Path
        Index 1 - List of Transforms
    Args:
        json_data: dict with static meshes and transforms
        in_static_mesh: SM object
        in_blueprint_transform: Actor level Transform
    """
    transforms_list = []
    # loop over static meshes
    for static_mesh_path, instances in json_data.items():
        if static_mesh_path != in_static_mesh.get_path_name():
            continue
        # loop over transforms
        for index, transform in instances.items():
            location_list = transform.get("location")
            orient_list = transform.get("orient")
            float_scale = transform.get("scale")
            # Create unreal data types
            location = unreal.Vector(location_list[0], location_list[1], location_list[2])
            rotation = unreal.Quat(orient_list[0], orient_list[1], orient_list[2], orient_list[3])
            scale = unreal.Vector(float_scale, float_scale, float_scale)
            # Create xform from generated data types
            xform = unreal.Transform()
            xform.rotation = rotation
            xform.scale3d = scale
            xform.translation = location
            # Create relative transform to actor xform in level because they are different
            # We spawn our instances in original BP without transforms, so we need to apply relative transform
            relative_transform = unreal.MathLibrary.make_relative_transform(xform, in_blueprint_transform)
            # Skip instances with zero scale3d
            if unreal.MathLibrary.equal_equal_vector_vector(relative_transform.scale3d, unreal.Vector(0, 0, 0)):
                continue
                # relative_transform.scale3d += unreal.Vector(0.02, 0.02,  )
            transforms_list.append(relative_transform)
    return transforms_list


def execute():
    static_mesh = in_static_mesh
    json_path = in_json
    blueprint_actor_transform = in_blueprint_transform
    data = read_json(json_path)
    return create_list_of_transforms(data, static_mesh, blueprint_actor_transform)


transforms = execute()


