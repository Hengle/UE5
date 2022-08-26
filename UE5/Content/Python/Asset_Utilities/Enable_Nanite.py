from unreal import StaticMesh, Material, MaterialInstanceConstant, BlendMode, MeshNaniteSettings, log, EditorDialog, \
    AppMsgType, Text
from Asset_Utilities.library import Common_Functions


class EnableNanite:
    """First argument is force set nanite to valid static meshes, second argument
    to set False nanite for transparent materials
    """

    SUPPORTED_BLEND_MODES = [
        BlendMode.BLEND_OPAQUE
    ]
    MATERIAL_CLASSES = [
        Material,
        MaterialInstanceConstant
    ]
    MESSAGE_SUCCESS_SET_ENABLE = "static meshes were converted to nanite"
    MESSAGE_SUCCESS_SET_DISABLED = "static meshes were disabled nanite"
    MESSAGE_NOTHING_TO_CONVERT = "Nothing to convert"
    MESSAGE_TURNED_OFF = "static meshes with inappropriate " \
                         "\n materials nanite was turned off"

    def __init__(self, nanite_enabled, turn_off_on_transparent):
        self.nanite_state_to_set = nanite_enabled
        self.turn_off_on_transparent = turn_off_on_transparent
        self.execute()

    @staticmethod
    def find_all_static_meshes(in_assets: list):
        static_meshes_list = []
        for asset in in_assets:
            is_static_mesh = Common_Functions.cast_to_class(StaticMesh, asset)
            if is_static_mesh:
                static_meshes_list.append(asset)
        return static_meshes_list

    def check_static_meshes_materials(self, in_static_meshes: list):
        """Loop over static meshes, if static mesh has not all opaque materials it won't be valid for nanit
            Args:
                in_static_meshes: list of static meshes
        """
        valid_static_mesh = []
        invalid_static_meshes = []
        for static_mesh in in_static_meshes:
            valid_materials = []
            static_materials = static_mesh.static_materials
            # Loop over each static mesh material
            for static_material in static_materials:
                current_material_class = None
                material_interface = static_material.material_interface
                # Check if material has valid class
                for material_class in self.MATERIAL_CLASSES:
                    if Common_Functions.cast_to_class(material_class, material_interface):
                        current_material_class = material_class
                        break
                if current_material_class:
                    # unreal.Material
                    if current_material_class == self.MATERIAL_CLASSES[0]:
                        if material_interface.blend_mode in self.SUPPORTED_BLEND_MODES:
                            valid_materials.append(material_interface)
                    # unreal.MaterialInstanceConstant
                    elif current_material_class == self.MATERIAL_CLASSES[1]:
                        get_blend_mode = material_interface.get_editor_property("base_property_overrides").\
                            get_editor_property("blend_mode")
                        if get_blend_mode in self.SUPPORTED_BLEND_MODES:
                            valid_materials.append(material_interface)
            # If length of validated materials not equal sm is not valid
            if len(static_materials) == len(valid_materials):
                valid_static_mesh.append(static_mesh)
            else:
                invalid_static_meshes.append(static_mesh)
        return valid_static_mesh, invalid_static_meshes

    def validate_static_mesh_polycount(self):
        pass

    def enable_nanite(self, in_valid_static_meshes: list, state_to_set: bool):
        """Set nanite state accordingly to input from widget"""
        list_of_changed_meshes = []
        for static_mesh in in_valid_static_meshes:
            # Check static mesh nanite state
            nanite_state = static_mesh.get_editor_property("nanite_settings").enabled
            if nanite_state != state_to_set:
                custom_nanite_settings = MeshNaniteSettings()
                custom_nanite_settings.enabled = state_to_set
                # set needed state
                static_mesh.set_editor_property("nanite_settings", custom_nanite_settings)
                Common_Functions.save_loaded_asset(static_mesh)
                list_of_changed_meshes.append(static_mesh)
        return list_of_changed_meshes

    def execute(self):
        selected_assets = Common_Functions.get_selected_assets()
        static_meshes_list = EnableNanite.find_all_static_meshes(selected_assets)
        valid_static_mesh, invalid_static_meshes = self.check_static_meshes_materials(static_meshes_list)
        changed_static_meshes = self.enable_nanite(valid_static_mesh, self.nanite_state_to_set)
        if changed_static_meshes:
            if self.nanite_state_to_set:
                EditorDialog.show_message(Text("Success"),
                                          Text(f'{len(changed_static_meshes)} {self.MESSAGE_SUCCESS_SET_ENABLE}'),
                                          AppMsgType.OK)
            else:
                EditorDialog.show_message(Text("Success"),
                                          Text(f'For {len(changed_static_meshes)} {self.MESSAGE_SUCCESS_SET_DISABLED}'),
                                          AppMsgType.OK)
        else:
            EditorDialog.show_message(Text("Fail"),
                                      Text(self.MESSAGE_NOTHING_TO_CONVERT),
                                      AppMsgType.OK)
        if self.turn_off_on_transparent:
            if invalid_static_meshes:
                print("Turn off")
                turned_off_nanite = self.enable_nanite(invalid_static_meshes, False)
                EditorDialog.show_message(Text("Success"),
                                          Text(f'For {len(turned_off_nanite)}{self.MESSAGE_TURNED_OFF}'),
                                          AppMsgType.OK)


if __name__ == "__main__":
    EnableNanite(True, True)


