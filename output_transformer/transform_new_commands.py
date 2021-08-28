import re

class NewCommandChecker:
    """ Class for checking the $new command for errors, and returning the appropriate error message if there is an issue. """

    def group_strings(self, string_list, end_key):
        """ Takes a list of strings and concatenates them (separated by spaces) until a string that is the end_key is reached or there are 
        no more strings to concatenate. Assumes there is at least 1 string in the list. """
        ans = string_list.pop(0)
        while len(string_list) > 0 and string_list[0] not in end_key:
            ans += ' ' + string_list.pop(0)
        if len(string_list) > 0:
            key = string_list.pop(0)
        else:
            key = None
        return (ans, key)
    
    def is_valid_value(self, value, min_value, max_value):
        """ Returns whether an (integer) value is within a valid range from min_value to max value. """
        return min_value <= int(re.sub('[^0-9]','',value)) <= max_value

    def is_valid_level(self, level, max_level):
        """ Returns whether a level is valid or not for an object """
        valid_ascension_levels = ['20+','40+','50+','60+','70+','80+']
        if self.is_valid_value(level, 1, max_level) and ('+' not in level or level in valid_ascension_levels):
            return True
        return False

    def char_checker(self, split_msg, character_df):
        """ Checks whether a valid new character can be created. Returns the appropriate error message if there is an issue.
            If not, returns all relevant data in a list. """
        #Expected format: $new char [name] level [lv] c[constellations] [attack lv] [skill lv] [burst lv]. Only name is required.
        error_list = ["Please give the name of the character you want to create.",
                      "Character not found. Please name a character that is currently implemented in the game.",
                      "Invalid character level. Please choose a number between 1 and 90, inclusive. Add a plus if the character is ascended but not yet leveled (ex: 20+).",
                      "Invalid constellation number. Please choose a number between 0 and 6, inclusive.",
                      "Invalid attack talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs.",
                      "Invalid skill talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs.",
                      "Invalid burst talent level. Please choose a number between 1 and 15, inclusive. Include levels from talents, constellations, or buffs."]
        #Necessary condition: name is valid
        if len(split_msg) == 0:
            return error_list[0]
        lowercase_name = self.group_strings(split_msg, ['level'])[0]
        lowercase_names = character_df['Lowercase']
        if lowercase_name not in lowercase_names.tolist():
            return error_list[1]
        character_index = character_df[lowercase_names == lowercase_name].index.tolist()[0]

        #Unnecessary conditions: check only if they exist (if split_msg is long enough). In order: level, constellations, attack/skill/burst level
        if len(split_msg) >= 1 and not self.is_valid_level(split_msg[0], 90):
            return error_list[2]
        if len(split_msg) >= 2 and not self.is_valid_value(split_msg[1], 0, 6):
            return error_list[3]
        if len(split_msg) >= 3 and not self.is_valid_value(split_msg[2], 1, 15):
            return error_list[4]
        if len(split_msg) >= 4 and not self.is_valid_value(split_msg[3], 1, 15):
            return error_list[5]
        if len(split_msg) == 5 and not self.is_valid_value(split_msg[4], 1, 15):
            return error_list[6]
        #Adds the character's index in the dataframe to the end of the list, and returns None
        split_msg.append(character_index)
    
    def weapon_checker(self, split_msg, weapon_df):
        """ Checks whether or not a valid new weapon can be created. Returns the appropriate error message if there is an issue.
            If not, returns all relevant data in a list. """
        #Expected format: $new weapon [name] level [lv] r[refinement]. Only name is required.
        error_list = ["Please give the name of the weapon you want to create.",
                      "Weapon not found. Please name a weapon that is currently implemented in the game.",
                      "Invalid weapon level. Please choose a number between 1 and 90, inclusive (or 1 and 70 if the weapon is below grade 3). Add a plus if the character is ascended but not yet leveled (ex: 20+).",
                      "Invalid refinement number. Please choose a number between 1 and 5, inclusive."]
        #Necessary condition: name is valid
        if len(split_msg) == 0:
            return error_list[0]
        lowercase_name = self.group_strings(split_msg, ['level'])[0]
        lowercase_names = weapon_df['Lowercase']
        if lowercase_name not in lowercase_names.tolist():
            return error_list[1]
        weapon_index = weapon_index = weapon_df[lowercase_names == lowercase_name].index.tolist()[0]

        #Unnecessary conditions: check only if they exist (if split_msg is long enough). In order: level, refinement
        grade = weapon_df.at[weapon_index, 'Grade']
        max_level = [70, 70, 90, 90, 90]
        if len(split_msg) >= 1 and not self.is_valid_level(split_msg[0], max_level[grade-1]):
            return error_list[2]
        if len(split_msg) == 2 and not self.is_valid_value(split_msg[1], 1, 5):
            return error_list[3]
        #Adds the weapon's index in the dataframe to the end of the list, and returns None
        split_msg.append(weapon_index)

    def artifact_checker(self, split_msg, artifact_df, two_star_df, three_star_df, four_star_df, five_star_df):
        """ Checks whether or not a valid new artifact can be created. Returns the appropriate error message if there is an issue.
            If not, returns all relevant data in a list. """
        #Expected format: $new artifact [set name] [artifact type] [grade]-star [main stat] +[lv] [substat:substat val]x4. Set name, 
        #artifact type, grade, and main stat are required.
        error_list = ["Please give the set name of the artifact you want to create.",
                      "Artifact set not found. Please name a set that is currently implemented in the game.",
                      "Please give the type of artifact you want to create (feather, goblet, etc).",
                      "Please give the grade of the artifact you want to create. 1-star artifacts are not supported.",
                      "Invalid artifact grade. Please select an artifact grade appropriate for the selected artifact set. " + 
                      "1-star artifacts are not supported.",
                      "Please give the main stat of the artifact you want to create.",
                      "Invalid main stat. Please select a main stat appropriate for the selected artifact type.",
                      "Invalid artifact level. Please choose a number between 0 and 20, inclusive.",
                      "Invalid first substat type.", "Invalid first substate value.",
                      "Invalid second substat type.", "Invalid second substate value.",
                      "Invalid third substat type.", "Invalid third substate value.",
                      "Invalid fourth substat type.", "Invalid fourth substate value."]

        slot_list = ['flower','feather','sands','goblet','circlet']
        valid_main_stats = {'flower':['HP'],'feather':['ATK'],'sands':['HP%','ATK%','DEF%','Elemental Mastery','Energy Recharge'],
                             'goblet':['HP%','ATK%','DEF%','Elemental Mastery','Physical Dmg Bonus','Pyro DMG Bonus','Cryo DMG Bonus',
                             'Dendro DMG Bonus','Hydro DMG Bonus','Electro DMG Bonus','Geo DMG Bonus','Anemo DMG Bonus'],
                             'circlet':['HP%','ATK%','DEF%','Elemental Mastery','Crit rate','Crit DMG','Healing Bonus']}
        for slot in valid_main_stats:
            lower_to_upper = [stat for stat in valid_main_stats[slot]]
            valid_main_stats[slot] = {}
            for stat in lower_to_upper:
                valid_main_stats[slot][stat.lower()] = stat
        #Necessary conditions: set name, artifact type, grade, and main stat are valid
        if len(split_msg) == 0:
            return error_list[0]
        lowercase_name, slot = self.group_strings(split_msg, slot_list)
        lowercase_names = artifact_df['Lowercase']
        if lowercase_name not in lowercase_names.tolist():
            return error_list[1]
        artifact_index = artifact_df[lowercase_names == lowercase_name].index.tolist()[0]
        
        if slot == None:
            return error_list[2]
        #No need to check for invalid artifact slots because the name string grouping only stops at a valid slot.

        if len(split_msg) == 0:
            return error_list[3]
        grade = int(split_msg.pop(0).replace('-star',''))
        if not(0 <= grade - artifact_df.at[artifact_index, 'Grade'] <= 1):
            return error_list[4]
        #Selects the correct substat data based on the grade
        grade_to_substats = {2:two_star_df,3:three_star_df,4:four_star_df,5:five_star_df}
        substat_df = grade_to_substats[grade]

        if len(split_msg) == 0:
            return error_list[5]
        possible_levels = []
        for i in range(20):
            possible_levels.append('+' + str(i))
        lowercase_main_stat, level = self.group_strings(split_msg, possible_levels)
        if lowercase_main_stat not in valid_main_stats[slot]:
            return error_list[6]

        #Unnecessary conditions: check only if they exist (if split_msg is long enough). In order: level, substats type and value 1 to 4
        if level != None and not self.is_valid_value(split_msg[0], 0, 20):
            return error_list[7]
        
        capital_substats = ['HP','ATK','DEF','HP%','ATK%','DEF%','Elemental Mastery','Energy Recharge','Crit Rate','Crit DMG']
        lower_substats = [substat.lower() for substat in capital_substats]
        valid_substats = {lower_substats[i]:capital_substats[i] for i in range(len(capital_substats))}
        i = 0
        while i < len(split_msg):
            #Concatenates the names of multi-word substats that are separated in split_msg
            #Don't want to use group_strings because the list of end_keys would be ridiculously long
            if ':' not in split_msg[i]:
                split_msg[i + 1] = split_msg[i] + ' ' + split_msg[i + 1]
                split_msg.pop(i)
            else:
                i += 1
        for i in range(len(split_msg)):
            #Splits each substat into the name and value, then evaluates them
            substat_pair = split_msg[i].split(':')
            if substat_pair[0] not in valid_substats:
                return error_list[2*i+8]
            valid_value = False
            for valid_stat in substat_df[valid_substats[substat_pair[0]]]:
                if float(substat_pair[1]) == valid_stat:
                    valid_value = True
                    break
            if not valid_value:
                return error_list[2*i+9]
        
        #Adds the artifact's index in the dataframe, slot, grade, main stat, and level to the end of the list, and returns None
        split_msg += [artifact_index, slot, grade, valid_main_stats[slot][lowercase_main_stat]]
        if level != None:
            split_msg.append(int(level.strip('+')))
        else:
            split_msg.append(level)

    