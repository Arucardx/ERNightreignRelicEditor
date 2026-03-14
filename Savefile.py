import numpy as np
from Savegame import Savegame


BND4H_LEN = 64
BND4H_PATTERN = b'BND4'
BND4_NUM_ENTRYS_OFF = 12
BND4EH_DATA_OFF = 16
BND4EH_LEN = 32
BND4EH_SIZE_OFF = 8
BND4EH_PATTERN = b'\x40\x00\x00\x00\xff\xff\xff\xff'
BND4EH_NAME_OFF = 20
BND4EH_FOOTER_LEN_OFF = 24

class Savefile:
    raw: bytes
    num_savegames: int
    savegames: list[Savegame]
    
    def __init__(self, path_sl2):
        self.raw = np.fromfile(path_sl2, dtype=np.uint8)
        assert(self.raw[:len(BND4H_PATTERN)].tobytes() == BND4H_PATTERN)
        self.num_savegames = self.raw[BND4_NUM_ENTRYS_OFF:BND4_NUM_ENTRYS_OFF + 4].view(dtype=np.uint8)[0]
        self.savegames = self.extract_savegames()

    def extract_savegames(self):
        entrys = []
        for i in range(self.num_savegames):
            pos = BND4H_LEN + i * BND4EH_LEN
            entry_header = self.raw[pos:pos + BND4EH_LEN]
            assert(entry_header[:len(BND4EH_PATTERN)].tobytes() == BND4EH_PATTERN)

            data_offset = entry_header[BND4EH_DATA_OFF:BND4EH_DATA_OFF + 4].view(dtype='<u4')[0]
            size = entry_header[BND4EH_SIZE_OFF:BND4EH_SIZE_OFF + 4].view(dtype='<u4')[0]
            sg =  Savegame(self.raw[data_offset:data_offset + size])
            sg.decrypt()
            entrys.append(sg)
        return entrys
    
    
    def finalize(self, path):
        for entry in self.savegames:
            entry.finalize()
        self.raw.tofile(path)
    


