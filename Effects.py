import json

class Effects:
    effect_dictionary: dict

    def __init__(self, effect_path):
        with open(effect_path, 'r') as fd:
            effects = json.load(fd)
        self.effect_dictionary = {0: 'NULL'}
        for effect in effects:
            self.effect_dictionary[int(effect['id'])] = effect['name']
    
    def translate(self, effect_id):
        return self.effect_dictionary[effect_id]