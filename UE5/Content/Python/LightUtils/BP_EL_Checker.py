from unreal import BlueprintGeneratedClass, StaticMeshActor, EditorUtilityLibrary, uclass, log
from LightUtils.library import Common_Functions
import re


@uclass()
class BpElChecker(EditorUtilityLibrary):
    VALID_MESSAGE = "passed"

    LIGHT_COMPONENT_CLASSES = [
        "RectLightComponent",
        "SpotLightComponent",
        "PointLightComponent"
    ]

    PREFIX_LIST = [
        "BP",
        "EL",
        "LGT"
    ]

    EXCLUDE_NAMES = [
        "BillboardComponent",
        "SceneComponent"
    ]

    # Init variables
    invalid_bp = []
    static_meshes_list = []
    valid_bp = []
    invalid_actors_class = []


    def check_actor_prefix(self, in_parsed_name):
        prefixes = ""
        for prefix in self.PREFIX_LIST:
            if prefix not in in_parsed_name:
                prefixes += f'{prefix} '
        if prefixes:
            # log(f'No {prefixes}in name')
            return f'No {prefixes}in name'
        if not prefixes:
            return "passed"

    def name_has_valid_light_type(self, in_actor, in_parsed_name):
        light_type = None
        light_components = 0
        message = "passed"
        if "Spot" in in_parsed_name or "Point" in in_parsed_name or "Rect" in in_parsed_name:
            # Check if label corresponds to light type in blueprint
            if "Spot" in in_parsed_name:
                light_type = "Spot"
            elif "Rect" in in_parsed_name:
                light_type = "Rect"
            elif "Point" in in_parsed_name:
                light_type = "Point"
        if light_type:
            # Get BP scene components
            get_component = in_actor.get_editor_property("root_component")
            get_component_children = get_component.get_children_components(False)
            # Append root component if actual light is scene root
            get_component_children.append(get_component)
            for scene_component in get_component_children:
                get_component_name = scene_component.get_class().get_name()
                if get_component_name in self.EXCLUDE_NAMES:
                    continue
                elif get_component_name in self.LIGHT_COMPONENT_CLASSES:
                    light_components += 1
                    component_parsed_name = re.findall("[A-Z][^A-Z]*", get_component_name)
                    # Check if name corresponds light component class
                    if component_parsed_name[0] != light_type:
                        message = "Name and light type mismatch"
            if not light_components:
                message = "Any light component found"
        else:
            message = "Missing light type in name"
        return message

    def check_cast_shadow_suffix(self, in_actor, in_parsed_name):
        message = "passed"
        cast_shadow_property = False
        try:
            cast_shadow_property = in_actor.get_editor_property("Cast_Shadows")
            cast_shadow_property_exists = True
        except:
            message = "Actor doesn't have Cast Shadow property"
            cast_shadow_property_exists = False
        if cast_shadow_property_exists:
            if "S" in in_parsed_name and not cast_shadow_property:
                message = "Light doesn't cast shadows"
            elif "S" not in in_parsed_name and cast_shadow_property:
                message = "Add suffix S"
        return message

    def create_log(self):
        """logging result"""
        # Logging bad BPs first
        if self.invalid_bp:
            for per_actor_message_list in self.invalid_bp:
                log(f'Actor name: {per_actor_message_list[0]}')
                for index, message in enumerate(per_actor_message_list):
                    if index != 0:
                        log(message)
                log("****************************")
        log(f'*****Summary*****')
        log(f'Bad BPs count {len(self.invalid_bp)}')
        log(f'Static meshes count {len(self.static_meshes_list)}')
        log(f'Valid BPs count {len(self.valid_bp)}')

    def create_messages_list(self, in_all_messages):
        # Create list with invalid message
        for actor_message in in_all_messages:
            only_invalid_message = []
            actor_label = actor_message[0]
            for index, message in enumerate(actor_message):
                if index != 0:
                    if message != self.VALID_MESSAGE:
                        only_invalid_message.append(message)
                        if len(only_invalid_message) > 0:
                            only_invalid_message.insert(0, actor_label)
                            self.invalid_bp.append(only_invalid_message)
            if actor_label not in only_invalid_message:
                self.valid_bp.append(actor_label)

    def checker(self):
        """Checker features:
        Prefix check, Type in name, Name corresponds component class
        """
        all_messages_list = []
        selected = Common_Functions.get_selected_actors()
        if not selected:
            log("Nothing to check")
            return
        for actor in selected:
            per_actor_message = []
            get_class = actor.get_class()
            cast_bp = Common_Functions.cast_to_class(BlueprintGeneratedClass, get_class)
            cast_static = Common_Functions.cast_to_class(StaticMeshActor, actor)
            if cast_bp:
                actor_label = actor.get_actor_label()
                parsed_name = actor_label.split("_")
                # Prefix check
                prefix_message = self.check_actor_prefix(parsed_name)
                # Light type in name check
                light_type_message = self.name_has_valid_light_type(actor, parsed_name)
                # Check Cast Shadow suffix
                shadow_suffix = self.check_cast_shadow_suffix(actor, parsed_name)
                # List with all messages
                per_actor_message.extend([actor_label, prefix_message, light_type_message, shadow_suffix])
                all_messages_list.append(per_actor_message)
            elif cast_static:
                self.static_meshes_list.append(actor)
            else:
                self.invalid_actors_class.append(actor)
        return all_messages_list

    def execute(self):
        all_messages = self.checker()
        self.create_messages_list(all_messages)
        self.create_log()


BpElChecker().execute()

    
    