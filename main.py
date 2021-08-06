import discord
import pandas as pd
import update
import character
import weapon
import artifact

client = discord.Client()

#Selected character, weapon, and artifacts. Commands will have effects on these objects only.
char = None
weap = None
art = {'flower':None, 'feather':None, 'sands':None, 'goblet':None, 'circlet':None}

#Data for checking validity of new objects
chars = pd.read_csv('char_data/chars.csv')
weapons = pd.read_csv('weapon_data/weapons.csv')
artifacts = pd.read_csv('artifact_data/artifacts.csv')
two_star_subs = pd.read_csv('artifact_data/two_star_sub_data.csv')
three_star_subs = pd.read_csv('artifact_data/three_star_sub_data.csv')
four_star_subs = pd.read_csv('artifact_data/four_star_sub_data.csv')
five_star_subs = pd.read_csv('artifact_data/five_star_sub_data.csv')
valid_mainstats = {'flower':['HP'],'feather':['ATK'],'sands':['HP%','ATK%','DEF%','Elemental Mastery','Energy Recharge'],
                         'goblet':['HP%','ATK%','DEF%','Elemental Mastery','Physical Dmg Bonus','Pyro DMG Bonus','Cryo DMG Bonus',
                         'Dendro DMG Bonus','Hydro DMG Bonus','Electro DMG Bonus','Geo DMG Bonus','Anemo DMG Bonus'],
                         'circlet':['HP%','ATK%','DEF%','Elemental Mastery','Crit rate','Crit DMG','Healing Bonus']}
reactions = pd.read_csv('reaction_data.csv')

for slot in valid_mainstats:
  lower_to_upper = [stat for stat in valid_mainstats[slot]]
  valid_mainstats[slot] = {}
  for stat in lower_to_upper:
    lower_stat = stat.lower()
    valid_mainstats[slot][lower_stat] = stat

#Helper function to remove '' from lists of strings
def clear_blanks(stringlist):
  num_blanks = 0
  for substring in stringlist:
    if substring == '':
      num_blanks += 1
  for i in range(num_blanks):
    stringlist.remove('')

@client.event
async def on_ready():
  print("Updating...")
  #Adds any new characters, weapons, or artifacts.
  update.update()
  print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  global char
  global weap
  global art
  global chars
  global weapons
  global artifacts
  global two_star_subs
  global three_star_subs
  global four_star_subs
  global five_star_subs

  msg = message.content
  channel = message.channel

  #Check function to confirm/deny commands
  def check(confirm):
    return (confirm.content == 'y' or confirm.content == 'Y' or confirm.content == 'n' or confirm.content == 'N') and confirm.channel == channel and message.author == confirm.author

  #Creation of a new character, weapon, or artifact, which becomes the selected object for its type.
  if msg == "$help":
    help_msg = "**$new**: Create and select a new character, weapon, or artifact, according to given specifications. Not case sensitive.\n"
    help_msg += "For characters: **$new char [full name of character] level [level] c[number of constellation] [attack talent level] [skill talent level] [burst talent level]**. Only the name is required.\n"
    help_msg += "*Ex: $new char amber level 20 c4 6 2 6*\n"
    help_msg += "For weapons: **$new weapon [full name of weapon] level [level] r[number of refinements]**. Only the name is required.\n"
    help_msg += "*Ex: $new weapon raven bow level 40*\n"
    help_msg += "For artifacts: **$new artifact [set name] [artifact slot] [grade]-star [main stat] +[lv] [substat:substat val]x4**. Set name, artifact type, grade, and main stat are required.\n"
    help_msg += "*Ex: $new artifact adventurer flower 3-star HP +8 atk%:2.5 hp%:2.5 crit rate:1.6*\n\n"
    help_msg += "**$display char**: Give a summary of the selected character and its stats.\n"
    help_msg += "**$display weapon/artifacts/[artifact slot]**: Give a summary of the selected weapon/artifacts/artifact and its stats.\n"
    help_msg += "**$stats**: Show the total stats of the selected character with his/her equipped items.\n"
    help_msg += "**$dmg**: Shows a number representing a character's average damage output, by calculating how the ATK stat/reaction damage is amplified by CRIT, Elemental Mastery, and DMG bonus.\n"
    help_msg += "*Note: For non-ascension levels of characters, data on base stats (HP, ATK, DEF) and reaction damage is estimated and may be slightly inaccurate.*\n\n"
    help_msg += "**$equip weapon/artifacts/[artifact slot]**: Equip the selected character with the selected weapon/artifacts/artifact. If something was unequipped, gives the option to select it.\n"
    help_msg += "**$unequip weapon/artifacts/[artifact slot]**: Unequip the selected character\'s weapon/artifacts/artifact. Gives the option to select it.\n"
    await channel.send(help_msg)

  elif msg.startswith("$new "):
    #Removes the '$new' segment, and turns the message to all lowercase
    remaining_msg = str(msg.split('$new',1)[1])
    remaining_msg = remaining_msg.lower()
    remaining_msg = remaining_msg.strip()

    #Splits off the first segment (new_obj) of the remaining message
    new_obj = remaining_msg.split(' ', 1)[0]
    if(len(remaining_msg.split(' ', 1)) > 1):
      remaining_msg = remaining_msg.split(' ', 1)[1].strip()
    else:
      remaining_msg = ''

    if new_obj == 'char':
      #Expected format: $new char [name] level [lv] c[constellations] [attack lv] [skill lv] [burst lv]. Only name is required.

      #Check if name exists in the string
      if len(remaining_msg) < 1:
        await channel.send("Please give the name of the character you want to create.")
      else:
        #Splits off the name portion of the string
        if 'level' in remaining_msg:
          name = remaining_msg.split('level',1)[0].strip()
          remaining_msg = remaining_msg.split('level')[1].strip()
        else:
          name = remaining_msg
          remaining_msg = ''

        char_names = chars['Lowercase']
        #Checks if the name is valid (in the list of names of characters implemented)
        if name not in list(char_names):
          await channel.send("Character not found. Please name a character that is currently implemented in the game.")
        else:
          #Splits the remaining msg into [[lv], c[constellations], [attack lv], [skill lv], [burst lv]]
          char_index = chars[char_names == name].index.tolist()[0]
          data = remaining_msg.split(' ')
          clear_blanks(data)

          #Checks the validity of unnecessary values if they exist. If invalid, displays an error message.
          #Check that level is between 1 and 90 inclusive, or a valid ascension level
          valid_ascensions = ['20+', '40+', '50+', '60+', '70+', '80+']
          if len(data) >= 1 and not(data[0].strip('+').isnumeric() and (data[0] in valid_ascensions or ('+' not in data[0] and 1 <= int(data[0]) <= 90))):
            await channel.send("Invalid character level. Please choose a number between 1 and 90, inclusive. Add a plus if the " +
                               "character is ascended but not yet leveled (ex: 20+).")
          #Check that the number of constellations is between 0 and 6, inclusive
          elif len(data) >= 2 and not(data[1].strip('cC').isnumeric() and (0 <= int(data[1].strip('cC')) <= 6)):
             await channel.send("Invalid constellation number. Please choose a number between 0 and 6, inclusive.")
          #Check that attack talent, skill talent, and burst talent are valid levels. Includes levels from constellations or other talents.
          elif len(data) >= 3 and not(data[2].isnumeric() and (1 <= int(data[2]) <= 15)):
             await channel.send("Invalid attack talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs.")
          elif len(data) >= 4 and not(data[3].isnumeric() and (1 <= int(data[3]) <= 15)):
             await channel.send("Invalid skill talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs.")
          elif len(data) == 5 and not(data[4].isnumeric() and (1 <= int(data[4]) <= 15)):
             await channel.send("Invalid burst talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs.")
          else:
            #All values are correct, creates the character
            if len(data) == 5:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'], data[0], int(data[1].strip('cC')), int(data[2]), int(data[3]), int(data[4]))
            elif len(data) == 4:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'], data[0], int(data[1].strip('cC')), int(data[2]), int(data[3]))
            elif len(data) == 3:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'], data[0], int(data[1].strip('cC')), int(data[2]))
            elif len(data) == 2:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'], data[0], int(data[1].strip('cC')))
            elif len(data) == 1:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'], data[0])
            else:
              char = character.Character(chars.at[char_index, 'Name'], chars.at[char_index, 'Element'], chars.at[char_index, 'Weapon'])

            await channel.send("Created new character: " + str(char))

    elif new_obj == 'weapon':
      #Expected format: $new weapon [name] level [lv] r[refinement]. Only name is required.
      
      #Checks if name exists in the string
      if len(remaining_msg) < 1:
        await channel.send("Please give the name of the weapon you want to create.")
      else:
        #Splits off the name portion of the string
        if 'level' in remaining_msg:
          name = remaining_msg.split('level',1)[0].strip()
          remaining_msg = remaining_msg.split('level',1)[1].strip()
        else:
          name = remaining_msg
          remaining_msg = ''

        #Checks if the name is valid (in the list of names of weapons implemented)
        weapon_names = weapons['Lowercase']
        if name not in list(weapon_names):
            await channel.send("Weapon not found. Please name a weapon that is currently implemented in the game.")
        else:
          #Splits the remaining msg into [[lv], r[refinement]]
          data = remaining_msg.split(' ')
          clear_blanks(data)
          
          #Checks the validity of unnecessary values if they exist
          level_cap = {1:70, 2:70, 3:90, 4:90, 5:90}
          weapon_index = weapons[weapon_names == name].index.tolist()[0]
          grade = weapons.at[weapon_index, 'Grade']
          valid_ascensions = ['20+', '40+', '50+', '60+', '70+', '80+']
          #Check that level is between 1 and the max level inclusive, or a valid ascension level
          if len(data) >= 1 and not(data[0].strip('+').isnumeric() and  1 <= int(data[0].strip('+')) <= level_cap[grade] and (data[0] in valid_ascensions or '+' not in data[0])):
            await channel.send("Invalid weapon level. Please choose a number between 1 and " + str(level_cap[grade]) + ", inclusive." +
                               " Add a plus if the weapon is ascended but not yet leveled (ex: 20+).")
          #Check that the number of refinements is between 1 and 5 inclusive
          elif len(data) >= 2 and not(data[1].strip('r').isnumeric() and (1 <= int(data[1].strip('r')) <= 5)):
             await channel.send("Invalid weapon refinement. Please choose a number between 1 and 5, inclusive.")
          else:
            #All values are correct, creates the weapon
            if len(data) == 2:
              weap = weapon.Weapon(weapons.at[weapon_index, 'Name'], grade, weapons.at[weapon_index, 'Type'], data[0], int(data[1].strip('r')))
            elif len(data) == 1:
              weap = weapon.Weapon(weapons.at[weapon_index, 'Name'], grade, weapons.at[weapon_index, 'Type'], data[0])
            else:
              weap = weapon.Weapon(weapons.at[weapon_index, 'Name'], grade, weapons.at[weapon_index, 'Type'])
            await channel.send("Created new weapon: " + str(weap))

    elif new_obj == 'artifact':
      #Expected format: $new artifact [set name] [artifact type] [grade]-star [main stat] +[lv] [substat:substat val]x4. Set name, 
      #artifact type, grade, and main stat are required.

      #Splits remaining_msg into words
      remaining_msg = remaining_msg.split(' ')
      clear_blanks(remaining_msg)

      #Check if the set name is given in the message
      if len(remaining_msg) == 0:
        await channel.send("Please give the set name of the artifact you want to create.")
      else:
        #Separates the set name from the rest of the string (up until it finds a word that indicates an artifact slot)
        set_name = remaining_msg.pop(0)
        while not(len(remaining_msg) == 0 or remaining_msg[0]=='flower' or remaining_msg[0]=='feather' or remaining_msg[0]=='sands' or remaining_msg[0]=='goblet' or remaining_msg[0]=='circlet'):
          substring = remaining_msg.pop(0)
          set_name += ' ' + substring

        #Checks if the name is valid (in the list of artifact sets implemented)
        artifact_names = artifacts['Lowercase']
        if set_name not in list(artifact_names):
          await channel.send("Artifact set not found. Please name a set that is currently implemented in the game.")
        #Checks if the artifact slot is given in the message
        elif len(remaining_msg) == 0:
          await channel.send("Please give the type of artifact you want to create (feather, goblet, etc).")
        else:
          set_index = artifacts[artifact_names == set_name].index.tolist()[0]
          #Checks if the artifact slot is valid (equal to 'flower', 'feather', 'sands', 'goblet', or 'circlet')
          slot = remaining_msg.pop(0)
          if slot not in art:
            await channel.send("Artifact type not found. Please select whether the artifact is a feather, flower, sands, " +
                                "goblet, or circlet.")
          #Checks if the grade of the artifact is given in the message
          elif len(remaining_msg) == 0:
            await channel.send("Please give the grade of the artifact you want to create. 1-star artifacts are not supported.")
          else:
            #Checks if the grade is valid (between 2-5), and switches to the appropriate data set for checking
            grade = remaining_msg.pop(0).replace('star','').strip('-')
            if grade == '2':
              artifact_substats = two_star_subs
            elif grade == '3':
              artifact_substats = three_star_subs
            elif grade == '4':
              artifact_substats = four_star_subs
            elif grade == '5':
              artifact_substats = five_star_subs
            if not(0 <= int(grade) - artifacts.at[set_index, 'Grade'] <= 1):
              await channel.send("Invalid artifact grade. Please select an artifact grade appropriate for the selected artifact set.")
            #Checks if a main stat is given in the message
            elif len(remaining_msg) == 0:
              await channel.send("Please give the main stat of the artifact you want to create.")
            else:
              #Checks if the given main stat is valid (in the list of valid mainstats)
              mainstat = remaining_msg.pop(0)
              while not(len(remaining_msg) == 0 or remaining_msg[0].strip('+').isnumeric()):
                mainstat += ' ' + remaining_msg.pop(0)
              if mainstat not in valid_mainstats[slot]:
                await channel.send("Invalid main stat. Please select a main stat appropriate for the selected artifact type.")
              else:
                make_artifact = True
                capital_substats = ['HP','ATK','DEF','HP%','ATK%','DEF%','Elemental Mastery','Energy Recharge','Crit Rate','Crit DMG']
                lower_substats = [substat.lower() for substat in capital_substats]
                valid_substats = {lower_substats[i]:capital_substats[i] for i in range(len(capital_substats))}
                #Checks if level is given in the message, and if so, whether it is a valid number (between 0 and 20 inclusive)
                if len(remaining_msg) >= 1 and not(remaining_msg[0].strip('+').isnumeric() and (0 <= int(remaining_msg[0]) <= 20)):
                  make_artifact = False
                  await channel.send("Invalid artifact level. Please choose a number between 0 and 20, inclusive.")
                #Checks if substats are given in the message, and if so, whether each given substat is valid
                elif len(remaining_msg) >= 2:
                  #Concatenates the names of multi-word substats that are separated in remaining_msg
                  x = 1
                  while x < len(remaining_msg):
                    if ':' not in remaining_msg[x]: 
                      remaining_msg[x + 1] = remaining_msg[x] + ' ' + remaining_msg[x + 1]
                      remaining_msg.pop(x)
                    x += 1
                  for i in range(1, len(remaining_msg)):
                    #Splits each substat into the name and value, then evaluates them
                    sub = remaining_msg[i].split(':')
                    sub[1] = float(sub[1])
                    if sub[0] not in valid_substats:
                      make_artifact = False
                      await channel.send("Invalid substat type (" + sub[0] + ").")
                    else:
                      valid_value = False
                      for valid_stat in artifact_substats[valid_substats[sub[0]]]:
                        if sub[1] == valid_stat:
                          valid_value = True
                          break
                      if not valid_value:
                        make_artifact = False
                        await channel.send("Invalid substat amount for " + grade + "-Star " + valid_substats[sub[0]] + " (" + str(sub[1]) + ").")
                if make_artifact:
                  #Makes the artifact with the g
                  if len(remaining_msg) >= 2:
                    subs = {}
                    for i in range(1, len(remaining_msg)):
                      sub = remaining_msg[i].split(':')
                      subs[valid_substats[sub[0]]] = float(sub[1])
                    art[slot] = artifact.Artifact(artifacts.at[set_index, 'Set Name'], slot, int(grade), valid_mainstats[slot][mainstat], int(remaining_msg[0].strip('+')), subs)
                  elif len(remaining_msg) == 1:
                    art[slot] = artifact.Artifact(artifacts.at[set_index, 'Set Name'], slot, int(grade), valid_mainstats[mainstat], int(remaining_msg[0].strip('+')))
                  else:
                    art[slot] = artifact.Artifact(artifacts.at[set_index, 'Set Name'], slot, int(grade), valid_mainstats[mainstat])
                  await channel.send("Created new " + str(art[slot]))

  elif msg.startswith("$equip "):
    #Expecting format $equip [thing to equip on char]
    if char == None:
      await channel.send("Select/create a character to equip your gear on.")
    else:
      #Removes the '$equip' segment
      item = msg.split('$equip ',1)[1]
      
      if item == 'weapon':
        if weap == None:
          await channel.send("Select/create a weapon to equip.")
        else:
          await channel.send(str(weap) + " has been equipped to " + str(char) + ".")
          #If a weapon was already equipped to the character, decides whether the user wants to switch the selected weapon
          #to the unequipped weapon or keep the newly equipped weapon selected
          if char.get_weapon() != None:
            await channel.send("Switch selected weapon to the unequipped weapon? (y/n)")
            confirm = await client.wait_for('message', check=check)
            if confirm.content == 'Y' or confirm.content == 'y':
              temp = char.get_weapon()
              char.set_weapon(weap)
              weap = temp
              await channel.send("Current weapon selected: " + weap.full_str() + ".")
            else:
              await channel.send(char.get_weapon().full_str() + " has been discarded. Current weapon selected: " + weap.full_str() + ".")
              char.set_weapon(weap)
          else:
            char.set_weapon(weap)
      elif item == 'artifacts':
        for slot in art:
          if art[slot] != None:
            await channel.send("New " + slot + " has been equipped to " + str(char) + ".")
            if char.get_artifact(slot) != None:
              await channel.send("Switch selected " + slot + " to the unequipped " + slot + "? (y/n)")
              confirm = await client.wait_for('message', check=check)
              if confirm.content == 'Y' or confirm.content == 'y':
                temp = char.get_artifact(slot)
                char.set_artifact(slot)
                art[slot] = temp
                await channel.send("Current " + slot + " selected: " + art[slot].full_str() + ".")
              else:
                await channel.send(char.get_artifact().full_str() + " has been discarded. Current " + slot + " selected: " + art[slot].full_str() + ".")
                char.set_artifact(art[slot])
            char.set_artifact(art[slot])
      elif item in art:
        if art[item] == None:
          await channel.send("Select/create a " + item + "to equip.")
        else:
          await channel.send("New " + item + " has been equipped to " + str(char) + ".")
          #If the artifact slot has something equipped, decides whether the user wants to switch the selected artifact to the
          #unequipped artifact or keep the newly equipped artifact selected
          if char.get_artifact(item) != None:
            await channel.send("Switch selected " + item + " to the unequipped " + item + "? (y/n)")
            confirm = await client.wait_for('message', check=check)
            if confirm.content == 'Y' or confirm.content == 'y':
              temp = char.get_artifact(item)
              char.set_artifact(item)
              art[item] = temp
              await channel.send("Current " + item + " selected: " + art[item].full_str() + ".")
            else:
              await channel.send(char.get_artifact(item).full_str() + " has been discarded. Current " + item + " selected: " + art[item].full_str() + ".")
              char.set_artifact(art[item])
          char.set_artifact(art[item])
  
  elif msg.startswith("$unequip"):
    #Expecting format $unequip [thing to unequip on char]
    if char == None:
      await channel.send("Select/create a character to unequip gear from.")
    else:
      item = msg.split('$unequip ',1)[1]
      if item == 'weapon':
        if char.get_weapon() == None:
          await channel.send("Character does not have a weapon to unequip.")
        else:
          #Unequips the weapon, and decides whether to switch the selected weapon to the newly unequipped weapon
          await channel.send(str(weap) + " has been unequipped " + "from " + str(char) + ".")
          await channel.send("Switch selected weapon to the unequipped weapon? (y/n)")
          confirm = await client.wait_for('message', check=check)
          if confirm.content == 'Y' or confirm.content == 'y':
            weap = char.get_weapon()
            char.set_weapon(None)
            await channel.send("Current weapon selected: " + weap.full_str() + ".")
          else:
            await channel.send(char.get_weapon().full_str() + "has been discarded. Current weapon selected: " + weap.full_str() + ".")
            char.set_weapon(None)
      elif item in art.keys():
        if art[item] == None:
          await channel.send("Character does not have a " + item + "to unequip.")
        else:
          #Unequips the artifact, and decides whether to switch the selected artifact to the newly unequipped artifact
          await channel.send(item + " has been unequipped from " + str(char) + ".")
          await channel.send("Switch selected " + item + " to the unequipped " + item + "? (y/n")
          confirm = await client.wait_for('message', check=check)
          if confirm.content == 'Y' or confirm.content == 'y':
            art[item] = char.get_artifact(item)
            char.set_artifact(None)
            await channel.send("Current " + item + " selected: " + art[item].full_str() + ".")
          else:
            await channel.send(char.get_artifact(item).full_str() + "has been discarded. Current " + item + " selected: " + art[item].full_str() + ".")
            char.set_artifact(None)

  elif msg.startswith("$display "):
    #Displays information to identify the currently selected character, weapon, artifact, or artifacts. Displays the information of
    #all items equipped to the selected character, too.
    displayable = msg.split("$display ", 1)[1]
    if displayable == 'char' or displayable == 'character':
      if char == None:
        await channel.send("No character selected.")
      else:
        await channel.send(char.full_str())
    elif displayable == 'weapon':
      if weap == None:
        await channel.send("No weapon selected.")
      else:
        await channel.send(weap.full_str())
    elif displayable == 'artifacts':
      sent = ""
      for slot in art:
        if art[slot] == None :
          sent += "No " + slot + " selected. \n"
        else:
          sent += art[slot].full_str() + " \n"
      await channel.send(sent)
    elif displayable in art:
      if art[displayable] == None:
        await channel.send("No " + displayable + " selected.")
      else:
        await channel.send(art[displayable].full_str())
    else:
      await channel.send("You can only display characters, weapons, or artifacts.")

  elif msg.startswith("$stats"):
    #Displays all the stats of the currently selected character, with current items equipped
    if char == None:
      await channel.send("Select the character whose stats you want to see.")
    else:
      ans = ""
      stats = char.calculate_total_stats()
      for stat in stats:
        ans += stat + ': ' + str(stats[stat]) 
        if not(stat == 'HP' or stat == 'ATK' or stat == 'DEF' or stat == 'Elemental Mastery'):
          ans += "%"
        ans += "\n"
      await channel.send(ans)

  elif msg.startswith("$dmg"):
    #Gives a number representing the selected character's average damage output, with current items equipped
    if char == None:
      await channel.send("Select the character whose damage output you want to see.")
    else:
      #Quantifies the strength of attacks, skills, and bursts.
      ans = ""
      stats = char.calculate_total_stats()
      char_element = char.get_element_type()
      crit_atk = stats['ATK']*((1-(stats['Crit Rate']/100)) + (stats['Crit Rate']/100)*(1+(stats['Crit DMG']/100)))
      phys_dmg = round(crit_atk*(1+(stats['Physical DMG Bonus']/100)))
      elemental_dmg = round(crit_atk*(1+(stats[char_element + ' DMG Bonus']/100)))
      ans += "Physical Power: " + str(phys_dmg) + "\n"
      ans += char_element + " Power: " + str(elemental_dmg) + "\n"
      
      #Quantifies the damage of reactions
      reaction_indices = []
      reaction_triggers = list(reactions['Trigger'])
      for i in range(len(reaction_triggers)):
        if char_element in reaction_triggers[i]:
          reaction_indices.append(i)
      for index in reaction_indices:
        if reactions.at[index,'Transformative'] == False:
          base_dmg = elemental_dmg
          em_bonus = 1+2.78*stats['Elemental Mastery']/(stats['Elemental Mastery']+1400)/100
          which_trigger = reaction_triggers[index].split(' ')
          if char_element == which_trigger[0]:
            em_bonus *= 2
          else:
            em_bonus *= 1.5
        else:
          if int(char.get_level().strip('+')) == 90:
            base_dmg = reactions.at[index,'90']
          elif int(char.get_level().strip('+')) >= 80:
            dmg_per_level = (reactions.at[index,'90']-reactions.at[index,'80'])/10
            base_dmg = reactions.at[index,'80'] + dmg_per_level*(int(char.get_level().strip('+'))-80)
          elif int(char.get_level().strip('+')) >= 70:
            dmg_per_level = (reactions.at[index,'80']-reactions.at[index,'70'])/10
            base_dmg = reactions.at[index,'70'] + dmg_per_level*(int(char.get_level().strip('+'))-70)
          elif int(char.get_level().strip('+')) >= 60:
            dmg_per_level = (reactions.at[index,'70']-reactions.at[index,'60'])/10
            base_dmg = reactions.at[index,'60'] + dmg_per_level*(int(char.get_level().strip('+'))-60)
          elif int(char.get_level().strip('+')) >= 50:
            dmg_per_level = (reactions.at[index,'60']-reactions.at[index,'50'])/10
            base_dmg = reactions.at[index,'50'] + dmg_per_level*(int(char.get_level().strip('+'))-50)
          elif int(char.get_level().strip('+')) >= 40:
            dmg_per_level = (reactions.at[index,'50']-reactions.at[index,'40'])/10
            base_dmg = reactions.at[index,'40'] + dmg_per_level*(int(char.get_level().strip('+'))-40)
          elif int(char.get_level().strip('+')) >= 30:
            dmg_per_level = (reactions.at[index,'40']-reactions.at[index,'30'])/10
            base_dmg = reactions.at[index,'30'] + dmg_per_level*(int(char.get_level().strip('+'))-30)
          elif int(char.get_level().strip('+')) >= 20:
            dmg_per_level = (reactions.at[index,'30']-reactions.at[index,'20'])/10
            base_dmg = reactions.at[index,'20'] + dmg_per_level*(int(char.get_level().strip('+'))-20)
          elif int(char.get_level().strip('+')) >= 10:
            dmg_per_level = (reactions.at[index,'20']-reactions.at[index,'10'])/10
            base_dmg = reactions.at[index,'10'] + dmg_per_level*(int(char.get_level().strip('+'))-10)
          else:
            dmg_per_level = (reactions.at[index,'10']-reactions.at[index,'1'])/9
            base_dmg = reactions.at[index,'1'] + dmg_per_level*(int(char.get_level().strip('+'))-1)

          if reactions.at[index,'Name'] == 'Crystallize':
            em_bonus = 1+4.44*stats['Elemental Mastery']/(stats['Elemental Mastery']+1400)/100
          else:
            em_bonus = 1+16*stats['Elemental Mastery']/(stats['Elemental Mastery']+2000)/100
        if reactions.at[index,'Name'] == 'Crystallize':
          ans += "Crystallize Shield: "
        else:
          ans += reactions.at[index,'Name'] + " Power: "
        ans += str(round(base_dmg*em_bonus)) + "\n"
      await channel.send(ans)

client.run('ODQ0MzI3ODYzMDMzNjU5NDMy.YKQzmQ.xm2bI_8jW3kZkgR0hfL72bsGvRI')
