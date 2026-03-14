from numpy.typing import NDArray
from RelicColor import Color
from RelicType import Type

RELIC_SIZE = 80
ID_OFFSET = 4
PRIMARY_EFFECT_OFFSET = 16
SECONDARY_EFFECT_OFFSET = 56

class Relic:
    raw: NDArray

    def __init__(self, savegame, offset):
        self.savegame = savegame
        self.offset = offset
    
    def get_effects(self):
        effects = [0] * 6
        primary_effects = self.savegame.read(self.offset + PRIMARY_EFFECT_OFFSET, 12).view(dtype='<u4')
        secondary_effects = self.savegame.read(self.offset + SECONDARY_EFFECT_OFFSET, 12).view(dtype='<u4')

        for i, (effect1, effect2) in enumerate(zip(primary_effects, secondary_effects)):
            if effect1 == 0xFFFFFFFF:
                break
            effects[i] = int(effect1)
            if effect2 != 0xFFFFFFFF:
                effects[i + 3] = int(effect2)
        return effects

    
    def update_effect(self, effect_position, effect_id):
        assert(effect_position >= 0 and effect_position < 6)
        if effect_position < 3:
            offset = self.offset + PRIMARY_EFFECT_OFFSET + 4 * effect_position
        else:
            offset = self.offset + SECONDARY_EFFECT_OFFSET + 4 * (effect_position - 3)
        self.savegame.write(offset, self.translate_effect(effect_id))
    
    def get_id(self):
        id = self.savegame.read(self.offset + ID_OFFSET, 3)
        return int(id[2]) << 16 | int(id[1]) << 8 | int(id[0])
    
    def get_num(self):
        num = self.savegame.read(self.offset, 2)
        return int(num[1]) << 8 | int(num[0])
    
    def get_color(self):
        color_id = self.get_id() % 1e3
        if color_id >= 3e2:
            return Color.GREEN
        elif color_id >= 2e2:
            return Color.YELLOW
        elif color_id >= 1e2:
            return Color.BLUE
        else:
            return Color.RED
    
    def get_size(self):
        return (self.get_id() % 10) + 1
    
    def get_type(self):
        id = self.get_id()
        if id >= 2e6:
            return Type.DON
        elif id >= 1e6:
            return Type.NORMAL
        #todo: pattern of remaining relics
        else:
            return None
            
    def translate_effect(self, id: int):
        ar = [0] * 4
        ar[3] = id >> 24
        ar[2] = (id >> 16) & 0xFF
        ar[1] = (id >> 8) & 0xFF
        ar[0] = (id) & 0xFF
        return ar

    def to_array(self):
        return [self.get_id(), self.get_num(), self.get_type(), self.get_color(), self.get_size()] + self.get_effects()