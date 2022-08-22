import unreal

unreal.log(f'Python Asset Utilities nodes imported')
unreal.log(f'\tTools:')
unreal.log(f'\t\t Get Blueprint Factory node')
unreal.log(f'\t\t Create Blueprint From Static Mesh')


@unreal.uclass()
class MyPyFunctionLibrary(unreal.BlueprintFunctionLibrary):
    @unreal.ufunction(params=[str, ], ret=unreal.BlueprintFactory, static=True, meta=dict(Category="Python"))
    def get_blueprint_factory(in_object_path):
        factory = unreal.BlueprintFactory()
        if not in_object_path:
            factory.set_editor_property(name="parent_class", value=unreal.Actor)
        else:
            get_bp_class = unreal.EditorAssetLibrary.load_blueprint_class(in_object_path)
            factory.set_editor_property(name="parent_class", value=get_bp_class)
        return factory

    @unreal.ufunction(params=[unreal.StaticMesh, unreal.BlueprintFactory], ret=unreal.Blueprint, static=True, meta=dict(Category="Python"))
    def create_blueprint_from_static_mesh(mesh, factory):
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        in_prefix = "BP"
        in_directory_name = "BP"
        mesh_name = mesh.get_name()
        mesh_path = mesh.get_path_name()
        split_name = mesh_name.lower().split("_")
        if split_name[0] == "sm":
            split_name[0] = in_prefix
            out_name = "_".join(split_name)
        else:
            out_name = f'{in_prefix}_{mesh_name}'
        blueprint_name = out_name
        static_mesh_path = "/".join(mesh_path.split("/")[:-1])
        blueprint_path = f'{static_mesh_path}/{in_directory_name}'
        if not unreal.EditorAssetLibrary.does_directory_exist(blueprint_path):
            unreal.EditorAssetLibrary.make_directory(blueprint_path)
        new_blueprint = asset_tools.create_asset(blueprint_name, blueprint_path, None, factory)

        return new_blueprint




