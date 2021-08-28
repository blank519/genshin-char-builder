import pandas as pd

class Artifact:
    """ Represents the aspects of a player's artifact """
    
    def __init__(self, set, slot, grade, main_stat, main_stat_df, level=0, substats={}):
        self._icon = 'artifact_icons/' + set + '.png'
        self._slot = slot
        self._grade = grade
        self._set = set
        self._level = level

        self._main_stat = main_stat
        self._main_stat_df = main_stat_df
        self._substats = substats

    def get_slot(self):
        return self._slot
    def get_grade(self):
        return self._grade
    def get_set(self):
        return self._set

    def get_level(self):
        return self._level
    def set_level(self, level):
        if (level <= 4 and self._grade <= 2) or (level <= 12 and self._grade == 3) or (level <= 16 and self._grade == 4) or (level <= 20 and self._grade == 5):
            self._level = level

    def get_main_stat(self):
        return self._main_stat

    def get_substats(self):
        ans = {}
        for substat in self._substats.keys:
            ans[substat] = self._substats[substat]
        return self._substats
    def set_substat(self, substat, num):
        if len(self._substats) < 4 or self._substats.has_key(substat):
            self._substats[substat] = num

    def __str__(self) -> str:
        return str(self._grade) + "-Star " + self._set + " " + self._slot.capitalize() + " +" + str(self._level)

    def full_str(self) -> str:
        ans = str(self) + "/// " + self._main_stat + ":" + str(self._main_stat_df.at[self._level, str(self._grade) + ' ' + self._main_stat])
        for sub in self._substats:
            ans += ", " + sub + ":" + str(self._substats[sub])
            if not (sub == 'HP' or sub == 'ATK' or sub == 'DEF'):
                ans += '%'
        return ans

    def calculate(self):
        """Calculate and return the total stat boost from the artifact"""
        ans = {}
        ans[self._main_stat] = self._main_stat_df.at[self._level, str(self._grade) + ' ' + self._main_stat]

        for substat in self._substats:
            if substat in ans:
                ans[substat] += self._substats[substat]
            else:
                ans[substat] = self._substats[substat]
        return ans