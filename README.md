# ERNightreignRelicEditor

Extract and modify your Relics from your Savefile (NR0000.sl2).  
See [example.ipynb](example.ipynb) for how to use.  

I do not recommend using modified Relics in Online-Mode. This can always lead to a ban, especially if your Effects or Combination of Effects are not possible at all.

### Issues
- Unique Relics (eg. from Nightlords, Remembrances, Shop) might not appear in the right color and size.
- The Byte-Signature of Relics seem to change sometimes (Offset 2 varies between 0x80 and 0x81, but here might be more possible values). So if no Relics are found, this might be the reason. If so, you need to look at the decrypted savegame and see what value differs.
- Sometimes Relics appear more than one time in the Savefile (no idea why lol). This is not taken into account during the extraction, but you can easily compare the ids to find these ones.
