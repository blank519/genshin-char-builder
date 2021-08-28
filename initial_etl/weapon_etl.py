import pandas as pd
from bs4 import BeautifulSoup
import initial_etl.general_transformer as general_transformer
import requests
import html5lib

class WeaponETL:
    """ Class to extract, transform, and load data from a list of BeautifulSoup objects of weapons. """
    def __init__(self, url, weapon_type):
        """ Initializes the data to extract from, as well as a list of existing weapons to reduce redundancy. """
        page = requests.get(url)
        html_page = BeautifulSoup(page.content, 'html5lib')
        self._weapon_list = html_page.find('table', class_='art_stat_table').find_all('tr')
        #Remove the header from the list
        self._weapon_list.pop(0)
        self._weapon_csv = pd.read_csv("equipment_data/weapons.csv")
        self._existing_weapons = self._weapon_csv['Name'].tolist()
        self._existing_weapons.append('')
        self._weapon_type = weapon_type
        self._transformer = general_transformer.GeneralTransformer()
    
    def etl_data(self):
        """ Extracts, transforms, and loads each weapon's data (name, grade, element, icon, weapon type, and stats) """
        for weapon in self._weapon_list:
            untransformed_data = weapon.find_all('td')
            
            #Extract and transform name
            name = untransformed_data[2].text.strip()
            if name not in self._existing_weapons:
                print("Adding new weapon: " + name)
                
                #Extract and transform grade
                grade = len(untransformed_data[3].find_all('div', class_='stars_wrap'))
                
                #Extract, transform, and load icon
                icon_name = name + '.png'
                img_url = "https://genshin.honeyhunterworld.com" + untransformed_data[1].find('img', class_='itempic')['src']
                self._transformer.url_to_png(icon_name, img_url, 'weapon_icons')
                
                #Extract and transform weapon substat name. ATK, DEF, and HP are transformed into ATK%, DEF%, and HP%.
                substat = untransformed_data[5].text.strip()
                if substat in ['ATK','DEF','HP']:
                    substat += '%'

                #Extract and transform weapon stats
                weapon_url = "https://genshin.honeyhunterworld.com/" + untransformed_data[1].find('a')['href']
                new_weapon_data = self.extract_weapon_stats(weapon_url, grade)

                #Loads new weapon into the csv
                new_weapon = {'Name':name,'Lowercase':name.lower(),'Substat':substat,'Grade':grade,'Type':self._weapon_type}
                new_weapon.update(new_weapon_data)
                self._weapon_csv = self._weapon_csv.append(new_weapon,ignore_index=True)
        self._weapon_csv.to_csv('equipment_data/weapons.csv',index=False,encoding='utf-8')
    
    def extract_weapon_stats(self, weapon_url, grade):        
        """ Extract the base attack and substat gain of a weapon as it is leveled up/ascended, as well as the passive and refinement bonus. """
        weapon_page = requests.get(weapon_url)
        weapon_html = BeautifulSoup(weapon_page.content,'html5lib')
        extracted_data = {}
        #Extract and transform the passive name and description of the weapon, if it exists 
        if grade > 2:
            #Extract passive name and stat progression table
            passive_table = weapon_html.find('table',class_='item_main_table').find_all('tr')
            passive_name = passive_table[5].find_all('td')[1].text.strip()
            #Extract passive description
            stat_tables = weapon_html.find_all('table', class_='add_stat_table')
            refinement_table = stat_tables[1].find_all('tr')
            #Transform passive name and description
            self._transformer.table_to_text(refinement_table)
            for i in range(len(refinement_table)):
                extracted_data['Refinement ' + str(i+1)] = passive_name + ': ' + refinement_table[i][1]
            #For convenience, also finds the stat_progression table from the stat tables
            stat_progression = stat_tables[0].find_all('tr')
        else:
            #If there is no passive, replaces it with a filler value, and finds the stat_progression table
            for i in range(5):
                extracted_data['Refinement ' + str(i+1)] = "No Passive"
            stat_progression = weapon_html.find('table', class_='add_stat_table').find_all('tr')

        self._transformer.table_to_text(stat_progression)
        #Extract and transform base attack at standard levels (level 1, then multiples of 5). 
        for i in range(1, len(stat_progression)):
            extracted_data['Base ATK ' + stat_progression[i][0]] = stat_progression[i][1]
            extracted_data['Substat ' + stat_progression[i][0]] = stat_progression[i][2]
        #For weapons of grade 1 or 2, fills data for levels above 70 with 0.
        if grade <= 2:
            for filler_row in ['70+','75','80','80+','85','90']:
                extracted_data['Base ATK ' + filler_row] = 0
                extracted_data['Substat ' + filler_row] = 0
        return extracted_data

