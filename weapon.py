import math
import pandas as pd

class Weapon:
    """ Represents the aspects of a weapon """

    def __init__(self, name, grade, type, level='1', refine=1):
        self._name = name
        self._icon = 'weapon_icons/' + name + '.png'
        self._grade = grade
        self._type = type
        self._level = level
        self._refinement = refine
        self._weapon_data_df = pd.read_csv('weapon_data/weapon_data.csv')
        self._weapon_index = self._weapon_data_df[self._weapon_data_df['Name'] == self._name].index.tolist()[0]

    def get_name(self):
        return self._name
    def get_icon(self):
        return self._icon
    def get_grade(self):
        return self._grade
    def get_type(self):
        return self._type
    def get_level(self):
        return self._level

    def set_level(self, level):
        if self._grade <= 2 and 0 < level <= 70:
            self._level = level
        elif self._grade <= 5 and 0 < level <= 90:
            self._level = level

    def get_refinement(self):
        return self._refinement

    def set_refinement(self, num):
        if(num < 5):
            self._refinement = num

    def __str__(self) -> str:
        return "R" + str(self._refinement) + " Level " + self._level + " " + self._name + "(" + self._type + ")"
    
    def full_str(self) -> str:
        stats = self.calculate()
        ans = str(self) + "/// Base ATK:" + str(stats['Base ATK'])
        for key in stats.keys():
            if key != 'Base ATK':
                ans += ", " + key + ":" + str(stats[key]) + "%"
        return ans

    def calculate(self):
        ans = {}
        #Main Stat: Always Base Attack
        level = int(self._level.replace('+', ''))
        ans['Base ATK'] = math.ceil(self._weapon_data_df.at[self._weapon_index, 'Level 1 Base Attack'] + 
                        self._weapon_data_df.at[self._weapon_index, 'Base Attack Per Level']*(level-1))
        if level > 20 or self._level == '20+':
            ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '20+']
            if(int(self._level.strip('+'))) > 40 or self._level == '40+':
                ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '40+']
                if(int(self._level.strip('+'))) > 50 or self._level == '50+':
                    ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '50+']
                    if(int(self._level.strip('+'))) > 60 or self._level == '60+':
                        ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '60+']
                        if(int(self._level.strip('+'))) > 70 or self._level == '70+':
                            ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '70+']
                            if(int(self._level.strip('+'))) > 80 or self._level == '80+':
                                ans['Base ATK'] += self._weapon_data_df.at[self._weapon_index, '80+']

        #Substat: Cannot be flat HP, ATK, or DEF
        weapon_substat = self._weapon_data_df.at[self._weapon_index, 'Substat']
        if weapon_substat == 'Elemental Mastery':
            weapon_substat_amount = round(self._weapon_data_df.at[self._weapon_index, 'Level 1 Substat'] + 
                                (level-1)*self._weapon_data_df.at[self._weapon_index, 'Substat Per Level'])
        else:
            weapon_substat_amount = round(self._weapon_data_df.at[self._weapon_index, 'Level 1 Substat'] + 
                                (level-1)*self._weapon_data_df.at[self._weapon_index, 'Substat Per Level'], 1)
        if weapon_substat == 'HP' or weapon_substat == 'ATK' or weapon_substat == 'DEF':
                ans[weapon_substat+'%'] = weapon_substat_amount
        elif weapon_substat != 'none':
            ans[weapon_substat] = weapon_substat_amount
        
        return ans