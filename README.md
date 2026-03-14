# ERNightreignRelicEditor

Extract and modify relics from your savefile (NR0000.sl2).  
See [example.ipynb](example.ipynb) for how to use.  

I do not recommend using modified relics in online-mode. This can always lead to a ban, especially if your effects or combination of effects are not possible at all.

### Known Issues
- Unique relics (eg. from Nightlords, Remembrances, Shop) might not appear in the right color and size.
- The byte-signature of relics seem to change sometimes (Offset 2 varies between 0x80 and 0x81, but there might be more possible values). So if no relics are found, this should be the reason. If so, you need to look at the decrypted savegame and see what value differs.
- Sometimes relics appear more than one time in the savefile (no idea why lol). This is not taken into account during the extraction, but you can easily compare the ids to find these ones.
