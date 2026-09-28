# Majora's Mask: Definitive Edition

MMDE is a Zelda64: Recompiled modpack that provides a convenient way to download and install a collection of carefully chosen mods that enhance Majora's Mask without ruining the original experience.

Discuss the modpack and suggest changes: https://discord.gg/kUFaUjayPS

### Note
As Zelda64: Recompiled does not support mod managers, this is not a traditional modpack that installs mods automatically. This modpack is simply a python script that automates downloading the latest version of the listed mods.

### Before you begin
* Install [Python](https://www.python.org/downloads/) if you haven't already

### Instructions
1. Download the zip file
2. Extract the contents into their own folder
3. Open a terminal window **in that folder** and enter the command:
   * **Windows:** `python download_mods.py`
   * **macOS / Linux:** `python3 download_mods.py`
   * Note: To exclude the 3.5 GB MMN64HD texture pack, append the `-e` flag to that command. This is only recommended if you already have Nerrel's texture pack installed and want to skip the longer download time.
4. Wait for the script to finish downloading mods. It may take a while
5. Open the newly created `mods` subfolder, select all files (Ctrl+A / Command+A), and drag them into the main menu of Zelda64Recompiled
6. Wait for them to finish installing, and then enjoy the game!

### MMN64HD Link
To enable Nerrel's MMN64HD Link model, you have to open the Player Model Manager menu (default L + A), cycle right to "Human", choose "Improved Link", and hit apply.
