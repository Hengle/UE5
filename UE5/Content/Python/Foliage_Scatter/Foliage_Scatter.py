from unreal import , EditorActorSubsystem, get_editor_subsystem, log_warning, HoudiniPublicAPIWorldInput, \
    load_asset, Vector, uclass, Object
from Foliage_Scatter.library import hou_utils
from sys import argv


@uclass()
class FoliageScatter(Object):
    """Defaults"""
    HDA_ASSET_PATH = "/Game/Common/HDA/Foliage_Scatter_1_0"
    SPLITTER = ";;;;"
    SCATTERING_ACTOR_TAG = "scatter"
    scatter_surface_actors = []
    scattering_actors = []
    static_meshes_path = []
    wrapper = None

    actor_sub_system = get_editor_subsystem(EditorActorSubsystem)

    def __init__(self, in_paths):
        super().__init__()
        self.assets_string = in_paths[1]
        self.actors_string = in_paths[2]
        self.execute()

    def get_loaded_actors(self):
        """ Load actors via path
        """
        create_actors_path = self.actors_string.split(self.SPLITTER)
        for full_actor_path in create_actors_path:
            level_actor_path = full_actor_path.split(":")[-1].replace("\"", "")
            loaded_actor = self.actor_sub_system.get_actor_reference(level_actor_path)
            self.scatter_surface_actors.append(loaded_actor)

    def set_actor_tag(self):
        tags = self.static_meshes_path
        for actor in self.scatter_surface_actors:
            actor.tags = tags

    def spawn_scattering_objects(self):
        """ Load static meshes via path
        """
        create_assets_path = self.assets_string.split(self.SPLITTER)
        tags = [self.SCATTERING_ACTOR_TAG, ]
        for asset_path in create_assets_path:
            loaded_asset = load_asset(asset_path)
            self.static_meshes_path.append(asset_path)
            spawned_actor = self.actor_sub_system.spawn_actor_from_object(loaded_asset, Vector(0, 0, 0))
            spawned_actor.tags = tags
            self.scattering_actors.append(spawned_actor)

    def instantiate_hou_asset(self):
        hda_asset = hou_utils.load_houdini_asset(self.HDA_ASSET_PATH)
        self.wrapper = hou_utils.instantiate_asset(hda_asset)
        self.wrapper.on_post_instantiation_delegate.add_callable(self.wrapper_post_instantiation)
        # wrapper.on_post_cook_delegate.add_callable(self.wrapper_post_cook)

    def wrapper_post_instantiation(self, in_wrapper):
        log_warning(f'post inst')
        # houdini_utils.start_session()
        # Set input 0
        world_input_0 = in_wrapper.create_empty_input(HoudiniPublicAPIWorldInput)
        world_input_0.set_input_objects(self.scatter_surface_actors)
        in_wrapper.set_input_at_index(0, world_input_0)
        # Set input 1
        world_input_1 = in_wrapper.create_empty_input(HoudiniPublicAPIWorldInput)
        world_input_1.set_input_objects(self.scattering_actors)
        in_wrapper.set_input_at_index(1, world_input_1)

        # in_wrapper.set_string_parameter_value("json_path", f'D:/reports/{self.validating_asset.get_name()}.json')
        # set tag to actor
        # houdini_actor = in_wrapper.get_houdini_asset_actor()
        # houdini_actor.tags = self.hda_actor_tag
        in_wrapper.recook()

    def wrapper_post_cook(self, in_wrapper):
        pass

    def execute(self):
        self.get_loaded_actors()
        self.spawn_scattering_objects()
        self.set_actor_tag()
        self.instantiate_hou_asset()
        self.wrapper.get_path_name()
        log_warning(f'Retrieve wrapper::::{self.wrapper.get_path_name()}')


print(argv)
#FoliageScatter(argv)



