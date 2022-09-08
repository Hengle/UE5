"""This script is part of python script node
Parse from JSON to Foliage
"""

import json
from unreal import Transform, Vector, Quat, load_asset, InstancedFoliageActor, get_editor_subsystem, \
    UnrealEditorSubsystem, GameplayStatics, EditorActorSubsystem, AssetRegistryHelpers, AssetToolsHelpers, \
    FoliageType_InstancedStaticMesh, FoliageType_InstancedStaticMeshFactory, EditorAssetLibrary, Name
from sys import argv
import os


class CreateInstancesFromJson:

    FOLIAGE_TYPE_PREFIX = "SMF"
    asset_registry = AssetRegistryHelpers.get_asset_registry()
    asset_tools = AssetToolsHelpers.get_asset_tools()
    potential_foliage_types = []

    def read_json(self, in_path: str):
        with open(in_path, "r") as f:
            return json.load(f)

    def create_name(self, in_name):
        """ Create correct name with prefix
            Args:
                in_name: str static mesh name
        """
        split_name = in_name.lower().split("_")
        if split_name[0] == "sm":
            split_name[0] = self.FOLIAGE_TYPE_PREFIX
            out_name = "_".join(split_name)
        else:
            out_name = f'{self.FOLIAGE_TYPE_PREFIX}_{in_name}'
        return out_name

    def create_foliage_types(self, in_json_data):
        """Search in folders provided with static meshes for Foliage Types if there isn't any method will create it
            Returns:
                dict: static_mesh_path: loaded_foliage_type
        """
        foliage_dict = {}
        used_static_meshes = []
        # Fill dict if we have foliage type for static mesh
        for static_mesh, instances in in_json_data.items():
            used_static_meshes.append(static_mesh)
            static_mesh_path = "/".join(static_mesh.split("/")[:-1])
            assets_in_folder = self.asset_registry.get_assets_by_path(Name(static_mesh_path))
            for index, asset_data in enumerate(assets_in_folder):
                if asset_data.asset_class == "FoliageType_InstancedStaticMesh":
                    loaded_asset = asset_data.get_asset()
                    if loaded_asset.mesh.get_path_name() == static_mesh and static_mesh not in foliage_dict:
                        foliage_dict[static_mesh] = loaded_asset
        # Check if used static meshes are in dictionary
        for static_mesh in used_static_meshes:
            if static_mesh not in foliage_dict:
                # Check if mesh have sm prefix
                loaded_static_mesh = load_asset(static_mesh)
                get_name = self.create_name(loaded_static_mesh.get_name())
                static_mesh_path = "/".join(static_mesh.split("/")[:-1])
                foliage_type = self.asset_tools.create_asset(get_name, static_mesh_path, FoliageType_InstancedStaticMesh,
                                                             FoliageType_InstancedStaticMeshFactory())
                foliage_type.mesh = loaded_static_mesh
                foliage_dict[static_mesh] = foliage_type
                EditorAssetLibrary.save_loaded_asset(foliage_type)
        return foliage_dict

    def replace_static_meshes(self, in_json_data: dict, in_foliage_type_dict: dict):
        """ First key of json data is static mesh path we use it look for foliage in folder

        """
        out_dict = in_json_data.copy()
        for static_mesh, foliage_type in in_foliage_type_dict.items():
            out_dict[foliage_type] = out_dict[static_mesh]
            del out_dict[static_mesh]
        return out_dict

    def create_list_of_instance(self, in_corrected_dict: dict):
        """ Index 0 - Foliage type
            Index 1 - List of transforms
        Args:
            in_corrected_dict: dict with corrected foliage types instead static meshes
        """
        main_instance_list = []
        for foliage_type, instances in in_corrected_dict.items():
            foliage_type_list = [foliage_type, ]
            for index, transform in instances.items():
                location_list = transform.get("location")
                orient_list = transform.get("orient")
                float_scale = transform.get("scale")
                # Create unreal data types
                location = Vector(location_list[0], location_list[1], location_list[2])
                rotation = Quat(orient_list[0], orient_list[1], orient_list[2], orient_list[3])
                # Scale is one value in json do not use float_scale[0]...
                scale = Vector(float_scale, float_scale, float_scale)
                # Create xform from generated data types
                xform = Transform()
                xform.rotation = rotation
                xform.scale3d = scale
                xform.translation = location
                foliage_type_list.append(xform)
            main_instance_list.append(foliage_type_list)
        return main_instance_list

    def add_instances_to_foliage_actor(self, in_instances: list, in_world, in_foliage_actor: InstancedFoliageActor):
        """ Index 0 - Foliage type
            Index 1 - List of transforms
        """
        for in_instances_data in in_instances:
            # Get Foliage Type as index 0
            foliage_type = in_instances_data.pop(0)
            in_foliage_actor.add_instances(in_world, foliage_type, in_instances_data)

    def execute(self):
        world = get_editor_subsystem(UnrealEditorSubsystem).get_editor_world()
        editor_subsystem = get_editor_subsystem(EditorActorSubsystem)
        foliage_actor = GameplayStatics.get_actor_of_class(world, InstancedFoliageActor)
        if not foliage_actor:
            foliage_actor = editor_subsystem.spawn_actor_from_class(InstancedFoliageActor, Vector(0, 0, 0))
        # Get input
        #json_path = argv[1]
        json_path = input
        data = self.read_json(json_path)
        foliage_type_list = self.create_foliage_types(data)
        corrected_dict = self.replace_static_meshes(data, foliage_type_list)
        sampled_transforms = self.create_list_of_instance(corrected_dict)
        self.add_instances_to_foliage_actor(sampled_transforms, world, foliage_actor)
        if os.path.isfile(json_path):
            os.remove(json_path)


if __name__ == "__main__":
    CreateInstancesFromJson().execute()


