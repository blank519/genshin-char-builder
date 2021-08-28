import math
from numpy import integer
import pandas as pd
from pandas.core.indexes import base

class Character:
    """ Represents the aspects of a player's character """

    def __init__(self, name, element_type, weapon_type, optional_values = ['1','c0',1,1,1]):
        self._name = name
        self._icon = 'char_icons/' + name + '.png'
        self._element_type = element_type
        self._weapon_type = weapon_type

        default_values = ['1','c0',1,1,1]
        while len(optional_values) < len(default_values):
            optional_values.append(default_values[len(optional_values)])
        self._level = optional_values[0]
        self._constellations = int(optional_values[1].strip('c'))
        self._atk_level = optional_values[2]
        self._skill_level = optional_values[3]
        self._burst_level = optional_values[4]

        self._weapon = None
        self._artifacts = {'flower':None,'feather':None,'sands':None,'goblet':None,'circlet':None}
        self._sets = {}
        self._char_df = pd.read_csv('char_data/' + self._name + '.csv')

    def get_name(self):
        return self._name
    def get_icon(self):
        return self._icon
    def get_element_type(self):
        return self._element_type
    def get_weapon_type(self):
        return self._weapon_type
        
    def get_level(self):
        return self._level
    def set_level(self, level):
        self._level = level

    def get_weapon(self):
        return self._weapon
    def set_weapon(self, weapon):
        if weapon == None:
            self._weapon = None
        elif weapon.get_type() == self._weapon_type:
            self._weapon = weapon

    def get_artifact(self, slot):
        return self._artifacts[slot]
    def set_artifact(self, artifact):
        if self._artifacts[artifact.get_slot()] != None:
            self._sets[self._artifacts[artifact.get_slot()].get_set()] -= 1
        self._artifacts[artifact.get_slot()] = artifact
        if artifact.get_set() in self._sets and self._sets[artifact.get_set()] > 0:
            self._sets[artifact.get_set()] += 1
        else:
            self._sets[artifact.get_set()] = 1

    def remove_artifact(self, artifactType):
        if artifactType == 'flower':
            self._sets[self._flower.get_set()] -= 1
            self._flower = None
        elif artifactType == 'feather':
            self._sets[self._feather.get_set()] -= 1
            self._feather = None
        elif artifactType == 'sands':
            self._sets[self._sands.get_set()] -= 1
            self._sands = None
        elif artifactType == 'goblet':
            self._sets[self._goblet.get_set()] -= 1
            self._goblet = None
        elif artifactType == 'circlet':
            self._sets[self._circlet.get_set()] -= 1
            self._circlet = None

    def __str__(self) -> str:
        return "Level " + str(self._level) + " C" + str(self._constellations) + " " + self._name

    def full_str(self) -> str:
        stats = self.calculate_stats()
        ans = str(self) + "/// Base ATK: " + str(stats['Base ATK']) + ", Base HP: " + str(stats['Base HP']) + ", Base DEF: " + str(stats['Base DEF'])
        ans += ", " + self._char_df.at[0, 'Ascension Bonus Stat'] + ': ' + str(stats[self._char_df.at[0, 'Ascension Bonus Stat']]) + '%'
        ans += "\nAttack Level:" + str(self._atk_level) + ", Skill Level:" + str(self._skill_level) + ", Burst Level:" + str(self._burst_level) + "\n"
        if(self._weapon == None):
            ans += "Weapon: None"
        else:
            ans += "Weapon: " + self._weapon.full_str()
        for artifact in self._artifacts:
            if(self._artifacts[artifact] == None):
                ans += "\n" + artifact.capitalize() + ": None"
            else:
                ans += "\n" + artifact.capitalize() + ": " + self._artifacts[artifact].full_str()
        return ans

    def calculate_stats(self):
        """Calculates stats gained from leveling the character"""
        ans = {}
        standard_levels = ['1', '20', '20+', '40', '40+', '50', '50+', '60', '60+', '70', '70+', '80', '80+', '90']
        base_stats = ['Base HP','Base ATK','Base DEF']
        integer_level = int(self._level.strip('+'))

        if self._level in standard_levels:
            #Handles cases where the character's level is a standard level
            ans['Base HP'] = self._char_df.at[0, self._level]
            ans['Base ATK'] = self._char_df.at[1, self._level]
            ans['Base DEF'] = self._char_df.at[2, self._level]
        else:
            if 1 < integer_level < 20:
                min_level = '1'
                max_level = '20'
                divider = 19.0
            elif 20 < integer_level < 40:
                min_level = '20+'
                max_level = '40'
                divider = 20.0
            else: 
                tens_level = int(integer_level/10)*10
                min_level = str(tens_level) + '+'
                max_level = str(tens_level+10)
                divider = 10.0
            #Approximates the value of base stats at the given level by adding to the lower standard level the approximated stat gain
            #per level times the level difference between the lower standard level and the actual level.
            for i in range(len(base_stats)):
                min_stat = self._char_df.at[i, min_level]
                max_stat = self._char_df.at[i, max_level]
                per_level_average_increase = (max_stat - min_stat)/divider
                ans[base_stats[i]] = min_stat + math.ceil((integer_level - min_level)*per_level_average_increase)

        #Calculating the substat
        substat = self._char_df.at[0, 'Ascension Bonus Stat'] 
        #Modifying the substat name for exceptions
        if substat in ['HP','ATK','DEF']:
            substat += '%'
        substat_increase = self._char_df.at[0, 'Ascension Bonus Stat Increase']
        #Modifying the substat increase for exceptions
        if substat == 'Crit Rate':
            substat_increase -= 5
        elif substat == 'Crit DMG':
            substat_increase -= 50
        elif substat == 'Elemental Mastery':
            substat_increase = round(substat_increase)
        
        ans[substat] = 0
        for substat_increase_level in [40,50,70,80]:
            if self._level == str(substat_increase_level) + '+' or integer_level > substat_increase_level:
                ans[substat] += substat_increase
        return ans

    def calculate_total_stats(self):
        total_stats = {'Base HP':0.0, 'Base ATK':0.0, 'Base DEF':0.0, 'HP':0.0, 'ATK':0.0, 'DEF':0.0, 'HP%':0.0, 'ATK%':0.0, 
                'DEF%':0.0, 'Elemental Mastery':0.0, 'Crit Rate':5.0, 'Crit DMG':50.0, 
                'Healing Bonus':0.0, 'Incoming Healing Bonus':0.0, 'Energy Recharge':100.0, 'CD Reduction':0.0, 'Shield Strength':0.0, 
                'Pyro DMG Bonus':0.0, 'Pyro RES':0.0, 'Hydro DMG Bonus':0.0, 'Hydro RES':0.0, 'Dendro DMG Bonus':0.0, 'Dendro RES':0.0, 
                'Electro DMG Bonus':0.0, 'Electro RES':0.0, 'Anemo DMG Bonus':0.0, 'Anemo RES':0.0, 'Cryo DMG Bonus':0.0, 'Cryo RES':0.0, 
                'Geo DMG Bonus':0.0, 'Geo RES':0.0, 'Physical DMG Bonus':0.0, 'Physical RES':0.0, 'Normal Attack Bonus':0.0, 
                'Charged Attack Bonus':0.0, 'Plunging Attack Bonus':0.0, 'Skill Bonus':0.0, 'Burst Bonus':0.0, 'Elemental Bonus':0.0}
        stats = self.calculate_stats()
        for stat in stats:
            total_stats[stat] += stats[stat]
        if self._weapon != None:
            weapon_stats = self._weapon.calculate()
            for stat in weapon_stats:
                total_stats[stat] += weapon_stats[stat]
        for slot in self._artifacts:
            if self._artifacts[slot] != None:
                artifact_stats = self._artifacts[slot].calculate()
                for stat in artifact_stats:
                    total_stats[stat] += artifact_stats[stat]
        
        displayed_stats = {}
        for basic_stat in ['HP', 'ATK', 'DEF']:
            displayed_stats[basic_stat] = round(total_stats['Base '+basic_stat]*(1 + total_stats[basic_stat+'%']/100) + total_stats[basic_stat])
        for stat in total_stats:
            if not('HP' in stat or 'ATK' in stat or 'DEF' in stat):
                displayed_stats[stat] = total_stats[stat]
        return displayed_stats