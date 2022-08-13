from unreal import ScopedEditorTransaction, EditorUtilityLibrary, uclass, log
from LightUtils.library import Common_Functions
from sys import argv


@uclass()
class RenameActors(EditorUtilityLibrary):
    """ Renames actors hierarchy
    """

    def __init__(self, in_name):
        super().__init__()
        self.new_name = in_name
        self.actors_list = Common_Functions.get_selected_actors()
        self.renamed_actors = []
        self.execute()

    def split_attached_actors(self):
        """ Create list without children only top level actors
            Returns:
                top level actors list
        """
        all_child_actors = []
        top_level_actors = []
        for actor in self.actors_list:
            attached_actors = actor.get_attached_actors(reset_array=True)
            if attached_actors:
                for attached_actor in attached_actors:
                    all_child_actors.append(attached_actor)
        for actor in self.actors_list:
            if actor not in all_child_actors:
                top_level_actors.append(actor)
        return top_level_actors

    def rename_actors(self, in_list: list):
        """ rename method
        """
        for index, actor in enumerate(in_list):
            actor_formed_name = f'{self.new_name}_{str(index + 1)}'
            actor.set_actor_label(actor_formed_name, mark_dirty=False)
            self.renamed_actors.append(actor)
            attached_actors = actor.get_attached_actors(reset_array=True)
            if attached_actors:
                for child_index, attached_actor in enumerate(attached_actors):
                    child_formed_name = f'{actor_formed_name}_{str(child_index + 1)}'
                    attached_actor.set_actor_label(child_formed_name, mark_dirty=False)
                    self.renamed_actors.append(attached_actor)

    def execute(self):
        if not self.actors_list:
            log("Nothing selected")
            return
        top_level_actors = self.split_attached_actors()
        with ScopedEditorTransaction("Rename selected actors") as trans:
            self.rename_actors(top_level_actors)
            renamed_count = len(self.renamed_actors)
            if renamed_count == 1:
                log(f'{len(self.renamed_actors)} actor were renamed')
            else:
                log(f'{len(self.renamed_actors)} actors was renamed')


RenameActors(argv[1])

