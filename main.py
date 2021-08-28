from io import StringIO
from numpy import string_
from output_transformer.transform_new_commands import NewCommandChecker
from output_transformer.transform_display_command import DisplayCommand
import discord
import pandas as pd
import initial_etl.update_objects as update_objects
import objects.character as character
import objects.artifact as artifact
import objects.weapon as weapon
import re
import config

client = discord.Client()

#Selected character, weapon, and artifacts. Commands will have effects on these objects only.
selected_character = None
selected_weapon = None
selected_artifacts = {'flower':None, 'feather':None, 'sands':None, 'goblet':None, 'circlet':None}

@client.event
async def on_ready():
  print("Updating...")
  #Adds any new characters, weapons, or artifacts.
  char_url = "https://genshin.honeyhunterworld.com/db/char/characters/?"
  weapon_urls = {'sword':"https://genshin.honeyhunterworld.com/sword/", 
                 'claymore':"https://genshin.honeyhunterworld.com/claymore/",
                 'polearm':"https://genshin.honeyhunterworld.com/polearm/",
                 'bow':"https://genshin.honeyhunterworld.com/bow/",
                 'catalyst':"https://genshin.honeyhunterworld.com/catalyst/"}
  artifact_url = "https://genshin.honeyhunterworld.com/db/artifact/?"
  updater = update_objects.Updater(char_url, weapon_urls, artifact_url)
  updater.update()

  #Initialize csv's for data
  global characters, weapons, artifacts, artifact_main_data, two_star_substats, three_star_substats, four_star_substats, five_star_substats, reactions
  characters = pd.read_csv('char_data/chars.csv')
  weapons = pd.read_csv('equipment_data/weapons.csv')
  artifacts = pd.read_csv('equipment_data/artifacts.csv')
  artifact_main_data = pd.read_csv('equipment_data/artifact_main_data.csv')
  two_star_substats = pd.read_csv('equipment_data/two_star_sub_data.csv')
  three_star_substats = pd.read_csv('equipment_data/three_star_sub_data.csv')
  four_star_substats = pd.read_csv('equipment_data/four_star_sub_data.csv')
  five_star_substats = pd.read_csv('equipment_data/five_star_sub_data.csv')
  reactions = pd.read_csv('equipment_data/reaction_data.csv')

  print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  global selected_character, selected_weapon, selected_artifacts, characters, weapons, artifacts
  global artifact_main_data, two_star_substats, three_star_substats, four_star_substats, five_star_substats, reactions
  
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

  elif msg.startswith("$new"):
    #Removes the '$new' segment, and turns the message to all lowercase
    split_msg = str(msg.split('$new',1)[1])
    split_msg = split_msg.lower().strip()

    #Splits off the first segment (new_obj) from the remaining message
    split_msg = re.split(' +', split_msg)
    new_obj = split_msg.pop(0)
    message_checker = NewCommandChecker()

    if new_obj == 'char':
      #Expected format: $new char [name] level [lv] c[constellations] [attack lv] [skill lv] [burst lv]. Only name is required.
      checked_msg = message_checker.char_checker(split_msg, characters)
      if checked_msg != None:
        await channel.send(checked_msg)
      else:
        #If checked_msg returns None, then it is a valid command, and the character is created.
        character_index = split_msg.pop()
        selected_character = character.Character(characters.at[character_index,'Name'],characters.at[character_index,'Element'],characters.at[character_index,'Weapon'], split_msg)
        await channel.send("Created new character: " + str(selected_character))

    elif new_obj == 'weapon':
      #Expected format: $new weapon [name] level [lv] r[refinement]. Only name is required.
      checked_msg = message_checker.weapon_checker(split_msg, weapons)
      if checked_msg != None:
        await channel.send(checked_msg)
      else:
        #If checked_msg returns None, then it is a valid command, and the weapon is created.
        weapon_index = split_msg.pop()
        selected_weapon = weapon.Weapon(weapons, weapon_index, split_msg)
        await channel.send("Created new weapon: " + str(selected_weapon))

    elif new_obj == 'artifact':
      #Expected format: $new artifact [set name] [artifact type] [grade]-star [main stat] +[lv] [substat:substat val]x4. Set name, 
      #artifact type, grade, and main stat are required.
      checked_msg = message_checker.artifact_checker(split_msg, artifacts,two_star_substats,three_star_substats,four_star_substats,five_star_substats)
      if checked_msg != None:
        await channel.send(checked_msg)
      else:
        #If checked_msg returns None, then it is a valid command, and the artifact is created.
        level = split_msg.pop()
        main_stat = split_msg.pop()
        grade = split_msg.pop()
        slot = split_msg.pop()
        artifact_index = split_msg.pop()
        if level == None:
          selected_artifacts[slot] = artifact.Artifact(artifacts.at[artifact_index, 'Set Name'], slot, grade, main_stat, artifact_main_data)
        else:
          substats = {}
          for substat_pair in split_msg:
            substat_pair = substat_pair.split(':')
            substats[substat_pair[0]] = substat_pair[1]
          selected_artifacts[slot] = artifact.Artifact(artifacts.at[artifact_index, 'Set Name'], slot, grade, main_stat, artifact_main_data, level, substats)
        await channel.send("Created new " + str(selected_artifacts[slot]))

  elif msg.startswith("$equip"):
    #Expecting format $equip [thing to equip on selected_character]
    if selected_character == None:
      await channel.send("Select/create a character to equip your gear on.")
    else:
      #Removes the '$equip' segment
      item = msg.split('$equip ',1)[1]
      if item == 'weapon':
        if selected_weapon == None:
          await channel.send("Select/create a weapon to equip.")
        else:
          await equip_weapon(channel, check)
      elif item == 'artifacts':
        for slot in selected_artifacts:
          if selected_artifacts[slot] != None:
            await equip_artifact(channel, item, check)
      elif item in selected_artifacts:
        if selected_artifacts[item] == None:
          await channel.send("Select/create a " + item + "to equip.")
        else:
          await equip_artifact(channel, item, check)
  
  elif msg.startswith("$unequip"):
    #Expecting format $unequip [thing to unequip on selected_character]
    if selected_character == None:
      await channel.send("Select/create a character to unequip gear from.")
    else:
      item = msg.split('$unequip ',1)[1]
      if item == 'weapon':
        if selected_character.get_weapon() == None:
          await channel.send("Character does not have a weapon to unequip.")
        else:
          await unequip_weapon(channel, check)
      elif item == 'artifacts':
        for artifact_slot in selected_artifacts:
          if selected_artifacts[artifact_slot] != None:
            await unequip_artifact(channel, artifact_slot, check)
      elif item in selected_artifacts:
        if selected_artifacts[item] == None:
          await channel.send("Character does not have a " + item + "to unequip.")
        else:
          await unequip_artifact(channel, item, check)

  elif msg.startswith("$display"):
    #Displays information to identify the currently selected character, weapon, artifact, or artifacts. Displays the information of
    #all items equipped to the selected character, too.
    displayable = msg.split("$display ", 1)[1]
    transform_display = DisplayCommand()
    if displayable == 'character':
      await channel.send(transform_display.display(selected_character, displayable))
    elif displayable == 'weapon':
      await channel.send(transform_display.display(selected_weapon, displayable))
    elif displayable == 'artifacts':
      sent = ""
      for slot in selected_artifacts:
        sent += transform_display.display(selected_artifacts[slot], slot) + '\n'
      await channel.send(sent)
    elif displayable in selected_artifacts:
      await channel.send(transform_display.display(selected_artifacts[displayable], displayable))
    else:
      await channel.send("You can only display characters, weapons, an artifact slot, or all artifacts.")

  elif msg.startswith("$stats"):
    #Displays all the stats of the currently selected character, with current items equipped
    if selected_character == None:
      await channel.send("Select a character whose stats you want to see.")
    else:
      ans = ""
      stats = selected_character.calculate_total_stats()
      for stat in stats:
        ans += stat + ': ' + str(stats[stat]) 
        if not(stat == 'HP' or stat == 'ATK' or stat == 'DEF' or stat == 'Elemental Mastery'):
          ans += "%"
        ans += "\n"
      await channel.send(ans)

  elif msg.startswith("$dmg"):
    #Gives a number representing the selected character's average damage output, with current items equipped, based on their 
    #ATK, Crit Rate/DMG, and more.
    if selected_character == None:
      await channel.send("Select the character whose damage output you want to see.")
    else:
      #Quantifies the strength of attacks, skills, and bursts.
      ans = ""
      stats = selected_character.calculate_total_stats()
      char_element = selected_character.get_element_type()
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
          #Calculate base damage of the transformative reaction, approximated based on level
          char_level = int(selected_character.get_level().strip('+'))
          if char_level == 90:
            base_dmg = reactions.at[index,'90']
          elif 1 <= char_level <= 10:
            dmg_per_level = (reactions.at[index,'10']-reactions.at[index,'1'])/9
            base_dmg = reactions.at[index,'1'] + dmg_per_level*(int(selected_character.get_level().strip('+'))-1)
          else:
            reaction_benchmark = int(char_level/10)*10
            dmg_per_level = (reactions.at[index, str(reaction_benchmark + 10)] - reactions.at[index, str(reaction_benchmark)])/10
            base_dmg = reactions.at[index, str(reaction_benchmark)] + dmg_per_level*(char_level - reaction_benchmark)
          
          if reactions.at[index,'Name'] == 'Crystallize':
            em_bonus = 1+4.44*stats['Elemental Mastery']/(stats['Elemental Mastery']+1400)/100
          else:
            em_bonus = 1+16*stats['Elemental Mastery']/(stats['Elemental Mastery']+2000)/100
        if reactions.at[index,'Name'] == 'Crystallize':
          ans += "Crystallize Shield Strength: "
        else:
          ans += reactions.at[index,'Name'] + " Power: "
        ans += str(round(base_dmg)) + "\n"
      await channel.send(ans)

async def equip_artifact(channel, slot, checker):
  """ Function for equipping the selected_artifact to the selected_character """
  global selected_artifacts
  await channel.send("New " + slot + " has been equipped to " + str(selected_character) + ".")
  #If the artifact slot has something equipped, decides whether the user wants to switch the selected artifact to the
  #unequipped artifact or keep the newly equipped artifact selected
  if selected_character.get_artifact(slot) != None:
    await channel.send("Switch selected " + slot + " to the unequipped " + slot + "? (y/n)")
    confirm = await client.wait_for('message', check=checker)
    
    if confirm.content == 'Y' or confirm.content == 'y':
      temp = selected_character.get_artifact(slot)
      selected_character.set_artifact(slot)
      selected_artifacts[slot] = temp
      await channel.send("Current " + slot + " selected: " + selected_artifacts[slot].full_str() + ".")
    else:
      await channel.send(selected_character.get_artifact(slot).full_str() + " has been discarded. Current " + slot + " selected: " + selected_artifacts[slot].full_str() + ".")
      selected_character.set_artifact(selected_artifacts[slot])
  else:
    selected_character.set_artifact(selected_artifacts[slot])

async def equip_weapon(channel, checker):
  """ Function for equipping the selected_weapon to the selected_character """
  global selected_weapon
  await channel.send(str(selected_weapon) + " has been equipped to " + str(selected_character) + ".")
  #If a weapon was already equipped to the character, decides whether the user wants to switch the selected weapon
  #to the unequipped weapon or keep the newly equipped weapon selected
  if selected_character.get_weapon() != None:
    await channel.send("Switch selected weapon to the unequipped weapon? (y/n)")
    confirm = await client.wait_for('message', check=checker)
    if confirm.content == 'Y' or confirm.content == 'y':
      temp = selected_character.get_weapon()
      selected_character.set_weapon(selected_weapon)
      selected_weapon = temp
      await channel.send("Current weapon selected: " + selected_weapon.full_str() + ".")
    else:
      await channel.send(selected_character.get_weapon().full_str() + " has been discarded. Current weapon selected: " + selected_weapon.full_str() + ".")
      selected_character.set_weapon(selected_weapon)
  else:
    selected_character.set_weapon(selected_weapon)

async def unequip_artifact(channel, slot, checker):
  """ Function for unequipping the artifact slot from the selected_character """
  global selected_artifacts
  await channel.send(slot.capitalize() + " has been unequipped from " + str(selected_character) + ".")
  await channel.send("Switch selected " + slot + " to the unequipped " + slot + "? (y/n")

  #Decides whether the user wants to switch the selected artifact to the unequipped artifact or not
  confirm = await client.wait_for('message', check=checker)
  if confirm.content == 'Y' or confirm.content == 'y':
    selected_artifacts[slot] = selected_character.get_artifact(slot)
    selected_character.set_artifact(None)
    await channel.send("Current " + slot + " selected: " + selected_artifacts[slot].full_str() + ".")
  else:
    await channel.send(selected_character.get_artifact(slot).full_str() + "has been discarded. Current " + slot + " selected: " + selected_artifacts[slot].full_str() + ".")
    selected_character.set_artifact(None)

async def unequip_weapon(channel, checker):
  """ Unequips the weapon, and decides whether to switch the selected weapon to the newly unequipped weapon """
  global selected_weapon
  await channel.send(str(selected_character.get_weapon()) + " has been unequipped " + "from " + str(selected_character) + ".")
  await channel.send("Switch selected weapon to the unequipped weapon? (y/n)")

  #Decides whether the user wants to switch the selected weapon to the unequipped weapon or not
  confirm = await client.wait_for('message', check=checker)
  if confirm.content == 'Y' or confirm.content == 'y':
    selected_weapon = selected_character.get_weapon()
    selected_character.set_weapon(None)
    await channel.send("Current weapon selected: " + selected_weapon.full_str() + ".")
  else:
    await channel.send(selected_character.get_weapon().full_str() + "has been discarded. Current weapon selected: " + selected_weapon.full_str() + ".")
    selected_character.set_weapon(None)

client.run(config.token)