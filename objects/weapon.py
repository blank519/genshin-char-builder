import math

class Weapon:
    """ Represents the aspects of a weapon """

    def __init__(self, df, index, optional_values = ['1','r1']):
        self._name = df.at[index, 'Name']
        self._icon = 'weapon_icons/' + self._name + '.png'
        self._grade = df.at[index, 'Grade']
        self._type = df.at[index, 'Type'].capitalize()

        default_values = ['1','r1']
        while len(optional_values) < len(default_values):
            optional_values.append(default_values[len(optional_values)])
        self._level = optional_values[0]
        self._refinement = int(optional_values[1].strip('r'))
        self._weapon_df = df
        self._weapon_index = index
        self._substat = self._weapon_df.at[self._weapon_index,'Substat']
        if self._substat in ['HP','ATK','DEF']:
                self._substat += '%'

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
        if (self._grade <= 2 and 0 < level <= 70) or (self._grade <= 5 and 0 < level <= 90):
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
                ans += ", " + key + ":" + str(stats[key])
                if key != 'Elemental Mastery':
                    ans += '%'
        return ans

    def calculate(self):
        ans = {}
        #Initialize standard levels for which values are known 
        standard_levels = [i for i in range(5, 91, 5)]
        standard_levels.insert(0,1)

        integer_level = int(self._level.strip('+'))

        if integer_level in standard_levels:
            #Handles cases where the character's level is a standard level
            ans['Base ATK'] = self._weapon_df.at[self._weapon_index, 'Base ATK ' + self._level]
            ans[self._substat] = self._weapon_df.at[self._weapon_index, 'Substat ' + self._level]
        else:
            if 1 < integer_level < 5:
                min_level = '1'
                max_level = '5'
                divider = 4
            else: 
                ascension_levels = [20,40,50,60,70,80]
                max_level = 0
                i = 0
                while max_level == 0:
                    if integer_level < standard_levels[i]:
                        max_level = str(standard_levels[i])
                        min_level = str(standard_levels[i-1])
                        if standard_levels[i-1] in ascension_levels:
                            min_level += '+'
                    i += 1
                divider = 5
            #Approximates the value of base stats at the given level by adding to the lower standard level the approximated stat gain
            #per level times the level difference between the lower standard level and the actual level.
            for stat in ['Base ATK', 'Substat']:
                min_stat = self._weapon_df.at[self._weapon_index, stat + ' ' + min_level]
                max_stat = self._weapon_df.at[self._weapon_index, stat + ' ' + max_level]
                per_level_average_increase = (max_stat - min_stat)/divider
                if stat == 'Substat':
                    ans[self._substat] = min_stat + math.ceil((integer_level - min_level)*per_level_average_increase)
                else:
                    ans[stat] = min_stat + math.ceil((integer_level - min_level)*per_level_average_increase)
        return ans