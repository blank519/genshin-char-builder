# Genshin Character Builder WIP 
### Description:  
A Discord bot to assist people in building characters in Genshin Impact based on what they currently have, by allowing users to see the stats and damage of different combinations of characters and equipment without the tedious process required to do the same thing in-game.  

Upon being run, the bot first updates all data by web scraping Honey Hunter to add new character and item data. Then, it waits for command messages from users in the server, then acts accordingly. 

### Commands:  
**$new**: Create and select a new character, weapon, or artifact, according to given specifications. Not case sensitive.  
**For characters**: ```$new char (full name of character) level (level) c(number of constellation) (attack talent level) (skill talent level) (burst talent level)```. Only the name is required.  
*Ex:* ```$new char amber level 20 c4 6 2 6```  
**For weapons**: ```$new weapon (full name of weapon) level (level) r(number of refinements)```. Only the name is required.  
*Ex:* ```$new weapon raven bow level 40*```  
**For artifacts**: ```$new artifact (set name) (artifact slot) (grade)-star (main stat) +(lv) (substat:substat val)x4```. Set name, artifact type, grade, and main stat are required.  
*Ex:* ```$new artifact adventurer flower 3-star HP +8 atk%:2.5 hp%:2.5 crit rate:1.6```  

**$display char**: Give a summary of the selected character, any equipped items, and all of their stats.  
**$display weapon**: Give a summary of the selected weapon and its stats.  
**$display artifacts**:Give a summary of all selected artifacts and their stats.  
**$display (artifact slot)**: Give a summary of the selected artifact and its stats. Artifact slots include flower, feather, sands, goblet, and circlet.  

**$stats**: Show the total stats of the selected character with his/her equipped items.  
**$dmg**: Shows a number representing a character's average damage output, by calculating how the ATK stat/reaction damage is amplified by CRIT, Elemental Mastery, and DMG bonus.  
*Note: For non-standard levels of characters, data on base stats (HP, ATK, DEF) and reaction damage is estimated and may be slightly inaccurate. Standard character levels are 1, 20, 40, 50, 60, 70, 80, and 90. The displayed numbers for the $dmg command are NOT how much damage your character will output, but rather a representation of how strong your character is.*  

**$equip weapon**: Equip the selected character with the selected weapon. If something was already equipped, gives the option to select it or keep selection on the newly equipped weapon.  
**$equip artifact**: Equip the selected character with all selected artifacts. If something was already equipped, gives the option to select it or keep selection on the newly equipped artifacts.  
**$equip (artifact slot)**: Equip the selected character with the selected artifact. If something was unequipped, gives the option to select it or keep selection on the newly equipped artifact.  
**$unequip weapon**: Unequip the selected character\'s weapon/artifacts/artifact. Gives the option to select it.  
**$unequip artifacts**: Unequip the selected character\'s weapon/artifacts/artifact. Gives the option to select it.  
**$unequip (artifact slot)**: Unequip the selected character\'s weapon/artifacts/artifact. Gives the option to select it.

Genshin Impact™ is a registered trademark of MiHoYo Co., Ltd.
This program is made for educational and research purposes. Images and data ©MiHoYo Co., Ltd.
© 2021 Honey Impact - Genshin Impact DB and Tools.