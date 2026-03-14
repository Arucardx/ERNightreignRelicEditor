from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from numpy.typing import NDArray
import Effects
from Relic import Relic


AES_KEY = b'\x18\xF6\x32\x66\x05\xBD\x17\x8A\x55\x24\x52\x3A\xC0\xA0\xC6\x09'
IV_SIZE = 16
CHECKSUM_START = 4
CHECKSUM_END = 28

        
class Savegame:
    raw: NDArray[np.uint8]
    decrypted: NDArray[np.uint8] = None
    updated: bool
    payload: NDArray[np.uint8]
    iv: NDArray[np.uint8]
    size: int
    cipher: Cipher


    def __init__(self, raw):
        self.raw = raw
        self.decrypted = None
        self.updated = False
        self.iv = raw[:IV_SIZE]
        self.payload = raw[IV_SIZE:]
        self.cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(self.iv))
        self.decrypted = self.decrypt()
    
    
    def extract_relics(self):
        data = self.decrypted
        # first byte changes? usually 0x80 or 0x81, but might be more possibilities
        # filter = ((np.roll(data, -2) == 0x80) | (np.roll(data, -2) == 0x81)) & (np.roll(data, -3) == 0xC0) & (np.roll(data, -7) == 0x80) & (np.roll(data, -11) == 0x80)

        # should be unique too
        # ...ok its not lmao, other entries have this pattern too
        # filter = (np.roll(data, -3) == 0xC0) & (np.roll(data, -7) == 0x80) & (np.roll(data, -11) == 0x80) & (np.roll(data, -13) == 0xFF)
        window = sliding_window_view(data, 12)

        mask = (
            ((window[:,2] == 0x80) | (window[:,2] == 0x81)) &
            (window[:,3] == 0xC0) &
            (window[:,7] == 0x80) &
            (window[:,11] == 0x80)
        )

        return [Relic(self, i) for i in np.where(mask)[0]]
    
    def extract_relics_to_df(self, effects : Effects=None):
        df = pd.DataFrame([r.to_array() for r in self.extract_relics()])
        df.columns = ['relic_id', 'relic_num', 'type', 'color' ,'size', 'effect0', 'effect1', 'effect2', 'effect3', 'effect4', 'effect5']

        if effects is not None:
            for i in range(6):
                df[f'effect{i}_description'] = df.apply(lambda row: effects.translate(row[f'effect{i}']), axis=1)

        return df
            

    def decrypt(self):
        decryptor = self.cipher.decryptor()
        decr = bytearray(decryptor.update(self.payload.tobytes()) + decryptor.finalize())
        return np.frombuffer(decr, dtype=np.uint8)


    def encrypt(self):
        encryptor = self.cipher.encryptor()
        encr = encryptor.update(self.decrypted.tobytes()) + encryptor.finalize()
        return np.frombuffer(encr, dtype=np.uint8)
    
    def replace_checksum(self):
        start = CHECKSUM_START
        end = len(self.decrypted) - CHECKSUM_END
        checksum = np.frombuffer(hashlib.md5(self.decrypted[start:end]).digest(), dtype=np.uint8)
        self.decrypted[end:end + 16] = checksum
    
    def write(self, offset: int, data: NDArray[np.uint8]):
        assert(offset >= 0 and offset + len(data) <= len(self.decrypted))
        self.decrypted[offset:offset + len(data)] = data
        self.updated = True
    
    def read(self, offset: int, num_bytes: int):
        assert(offset >= 0 and offset + num_bytes <= len(self.decrypted))
        return self.decrypted[offset:offset + num_bytes]

    
    def finalize(self):
        if not self.updated:
            return
        assert(len(self.decrypted) == len(self.payload))
        self.replace_checksum()
        assert(len(self.decrypted) == len(self.payload))
        encr = self.encrypt()
        assert(len(encr) == len(self.payload))
        self.raw[IV_SIZE:] = encr
        self.updated = False