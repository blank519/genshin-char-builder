import math
import pandas as pd

class Character:
    """ Represents the aspects of a player's character """

    def __init__(self, name, element_type, weapon_type, level='1', constellations=0, ATK_lv=1, skill_lv=1, burst_lv=1):
        self._name = name
        self._icon = 'char_icons/' + name + '.png'
        self._element_type = element_type
        self._weapon_type = weapon_type
        self._level = level
        self._constellations = constellations
        self._ATK_lv = ATK_lv
        self._skill_lv = skill_lv
        self._burst_lv = burst_lv
        self._weapon = None
        self._artifacts = {'flower':None,'feather':None,'sands':None,'goblet':None,'circlet':None}
        self._sets = {}
        self._stats = {}
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
    def set_level(self, lv):
        self._level = lv

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
        ans += "\nAttack Level:" + str(self._ATK_lv) + ", Skill Level:" + str(self._skill_lv) + ", Burst Level:" + str(self._burst_lv) + "\n"
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
        DEFault_levels = ['1', '20', '20+', '40', '40+', '50', '50+', '60', '60+', '70', '70+', '80', '80+', '90']
        if self._level in DEFault_levels:
            self._stats['Base HP'] = self._char_df.at[0, self._level]
            self._stats['Base ATK'] = self._char_df.at[1, self._level]
            self._stats['Base DEF'] = self._char_df.at[2, self._level]
        else:
            if 1 < int(self._level) < 20:
                min_lv = '1'
                max_lv = '20'
                divider = 19.0
            elif 20 < int(self._level) < 40:
                min_lv = '20+'
                max_lv = '40'
                divider = 20.0
            else: 
                x = int(self._level)/10
                max_lv = str(math.ceil(x)*10)
                min_lv = str(math.floor(x)*10) + '+'
                divider = 10.0
            per_level_avg_increase = [(self._char_df.at[0, max_lv] - self._char_df.at[0, min_lv])/divider, 
                                      (self._char_df.at[1, max_lv] - self._char_df.at[1, min_lv])/divider,
                                      (self._char_df.at[2, max_lv] - self._char_df.at[2, min_lv])/divider]

            self._stats['Base HP'] = self._char_df.at[0, min_lv] + math.ceil((int(self._level) - math.floor(x)*10)*per_level_avg_increase[0])
            self._stats['Base ATK'] = self._char_df.at[1, min_lv] + math.ceil((int(self._level) - math.floor(x)*10)*per_level_avg_increase[1])
            self._stats['Base DEF'] = self._char_df.at[2, min_lv] + math.ceil((int(self._level) - math.floor(x)*10)*per_level_avg_increase[2])

        substat = self._char_df.at[0, 'Ascension Bonus Stat'] 
        if substat == 'HP' or substat == 'ATK' or substat == 'DEF':
            substat += '%'
        substat_increase = self._char_df.at[0, 'Ascension Bonus Stat Increase']
        if substat == 'Crit Rate':
            substat_increase -= 5
        elif substat == 'Crit DMG':
            substat_increase -= 50
        elif substat == 'Elemental Mastery':
            substat_increase = round(substat_increase)
        if int(self._level) > 80 or self._level == '80+':
            self._stats[substat] = 4*substat_increase
        elif int(self._level) > 70 or self._level == '70+':
            self._stats[substat] = 3*substat_increase
        elif int(self._level) > 50 or self._level == '50+':
            self._stats[substat] = 2*substat_increase
        elif int(self._level) > 40 or self._level == '40+':
            self._stats[substat] = substat_increase
        else:
            self._stats[substat] = 0
        return self._stats

    def calculate_total_stats(self):
        total_stats = {'Base HP':0.0, 'Base ATK':0.0, 'Base DEF':0.0, 'HP':0.0, 'ATK':0.0, 'DEF':0.0, 'HP%':0.0, 'ATK%':0.0, 
                'DEF%':0.0, 'Elemental Mastery':0.0, 'Crit Rate':5.0, 'Crit DMG':50.0, 
                'Healing Bonus':0.0, 'Incoming Healing Bonus':0.0, 'Energy Recharge':100.0, 'CD Reduction':0.0, 'Shield Strength':0.0, 
                'Pyro DMG Bonus':0.0, 'Pyro RES':0.0, 'Hydro DMG Bonus':0.0, 'Hydro RES':0.0, 'Dendro DMG Bonus':0.0, 'Dendro RES':0.0, 
                'Electro DMG Bonus':0.0, 'Electro RES':0.0, 'Anemo DMG Bonus':0.0, 'Anemo RES':0.0, 'Cryo DMG Bonus':0.0, 'Cryo RES':0.0, 
                'Geo DMG Bonus':0.0, 'Geo RES':0.0, 'Physical DMG Bonus':0.0, 'Physical RES':0.0, 'Normal Attack Bonus':0.0, 
                'Charged Attack Bonus':0.0, 'Plunging Attack Bonus':0.0, 'Skill Bonus':0.0, 'Burst Bonus':0.0, 'Elemental Bonus':0.0}
        self.calculate_stats()
        for stat in self._stats:
            total_stats[stat] += self._stats[stat]

        if self._weapon != None:
            weapon_stats = self._weapon.calculate()
            for stat in weapon_stats:
                total_stats[stat] += weapon_stats[stat]

        if self._artifacts['flower'] != None:
            flower_stats = self._artifacts['flower'].calculate()
            for stat in flower_stats:
                total_stats[stat] += flower_stats[stat]
        if self._artifacts['feather'] != None:
            feather_stats = self._artifacts['feather'].calculate()
            for stat in feather_stats:
                total_stats[stat] += feather_stats[stat]
        if self._artifacts['sands'] != None:
            sands_stats = self._artifacts['sands'].calculate()
            for stat in sands_stats:
                total_stats[stat] += sands_stats[stat]
        if self._artifacts['goblet'] != None:
            goblet_stats = self._artifacts['goblet'].calculate()
            for stat in goblet_stats:
                total_stats[stat] += goblet_stats[stat]
        if self._artifacts['circlet'] != None:
            circlet_stats = self._artifacts['circlet'].calculate()
            for stat in circlet_stats:
                total_stats[stat] += circlet_stats[stat]
        
        displayed_stats = {}
        displayed_stats['HP'] = round(total_stats['Base HP'] * (1 + total_stats['HP%']/100) + total_stats['HP'])
        displayed_stats['ATK'] = round(total_stats['Base ATK'] * (1 + total_stats['ATK%']/100) + total_stats['ATK'])
        displayed_stats['DEF'] = round(total_stats['Base DEF'] * (1 + total_stats['DEF%']/100) + total_stats['DEF'])
        for stat in total_stats:
            if not('HP' in stat or 'ATK' in stat or 'DEF' in stat):
                displayed_stats[stat] = total_stats[stat]
        return displayed_stats

    