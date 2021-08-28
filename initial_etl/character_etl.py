from bs4 import BeautifulSoup
import pandas as pd
import requests
import initial_etl.general_transformer as general_transformer
import html5lib

class CharacterETL:
    """ Class to extract, transform, and load data from a list of BeautifulSoup objects of characters. """
    def __init__(self, url):
        """ Initializes the list to extract data from, as well as a list of existing characters to reduce redundancy. """
        page = requests.get(url)
        html_page = BeautifulSoup(page.content, 'html5lib')
        self._character_list = html_page.find_all('div', class_='char_sea_cont')
        self._general_character_csv = pd.read_csv("char_data/chars.csv")
        self._existing_characters = self._general_character_csv['Name'].tolist()
        self._existing_characters.append('')
        self._transformer = general_transformer.GeneralTransformer()

    def etl_data(self):
        """ Extracts, transforms, and loads each character's general data (name, element, weapon, and icon) to a general csv. Also extracts,
            transforms, and loads a separate set of data for the character's specific stats abilities. """
        for character in self._character_list:
            #Extract and transform name
            name = character.find('span', class_='sea_charname').text.strip()
            
            #Extract and transform element
            elem_src = character.find('img', class_='char_portrait_card_sea_element')['src']
            element = elem_src.replace('/img/icons/element/', '').split('_')[0].capitalize()
            
            #Specific case because there is data for mutliple Travelers 
            if name == 'Traveler':
                name += ' (' + element + ')'
            
            if name not in self._existing_characters:
                print("Adding new character: " + name)
                self._existing_characters.append(name)
                #Extract and transform weapon
                weapon_src = character.find('img', class_='sea_weptype_element')['src']
                weapon = weapon_src.replace('/img/icons/weapon_types/','').split('_')[0].capitalize()
                
                #Extract, transform, and load icon
                icon_name = name + ".png"
                img_url = 'https://genshin.honeyhunterworld.com' + character.find('img', class_='char_portrait_card_sea')['src']
                self._transformer.url_to_png(icon_name, img_url, 'char_icons')

                #Extracts, transforms, and loads the character's specific stats from its webpage
                character_src = 'https://genshin.honeyhunterworld.com' + character.find('a')['href']
                character_stats = self.extract_character_stats(name, character_src)
                self.load_character_csv(name, character_stats)

                #Loads the new character's general data
                new_char = {'Name':name,'Lowercase':name.lower(),'Element':element,'Weapon':weapon}
                self._general_character_csv = self._general_character_csv.append(new_char, ignore_index=True)
        self._general_character_csv.to_csv('char_data/chars.csv', index=False, encoding='utf-8')

    def extract_character_stats(self, name, character_url):
        """ Extracts data that can be found on a character's information page """
        #Order: stat progression, ascension stat, ascension stat increase, attack data (icon, name, attack components, stat scaling via levels), 
        #skill data, burst data, passive talent data, constellation data
        extracted_data = {}

        character_page = requests.get(character_url)
        character_html = BeautifulSoup(character_page.content, 'html5lib')

        relevant_html = character_html.find(id='live_data')
        stat_tables = relevant_html.find_all('div', class_='skilldmgwrapper')
        description_tables = relevant_html.find_all('table', class_='item_main_table')

        #Calculate all level-up stat increases
        stat_progression = stat_tables[0].find_all('tr')
        self._transformer.table_to_text(stat_progression)

        #Level up basic stats
        #Order of list: base HP, base ATK, base DEF
        for i in range(15):
            extracted_data[stat_progression[i][0]] = [stat_progression[i][j] for j in range(1, 4)]
        #Ascension specialized stat
        ascension_stat = stat_progression[0][4]
        ascension_stat_increase = float(stat_progression[5][4].strip(' %'))
        extracted_data['Ascension Bonus Stat'] = ascension_stat
        extracted_data['Ascension Bonus Stat Increase'] = ascension_stat_increase
        
        #Extract and transform the name, description, and scalings of each active talent
        active_talents = {1:'attack',2:'skill',-1:'burst'}
        for i in active_talents:
            #Extract the name/description
            full_talent_description = description_tables[i].find_all('tr')
            extracted_data.update(self.extract_active_talent_descriptions(full_talent_description,name,active_talents[i]))
            
            #Extract talent scalilngs
            talent_scalings = stat_tables[i].find_all('tr')
            extracted_data.update(self.extract_active_talent_scalings(talent_scalings, active_talents[i]))

        #Extract and transform the name and description of passive talents
        passive_talents = description_tables[-2].find_all('tr')
        passive_talent_levels = ['20','60']
        extracted_data.update(self.extract_passive_talent_descriptions(passive_talents, name, passive_talent_levels))

        #Extract and transform the name and description of constellations
        constellations = description_tables[-1].find_all('tr')
        extracted_data.update(self.extract_constellation_descriptions(constellations, name, 6))
        return extracted_data

    def extract_active_talent_descriptions(self, description, name, talent):
        """ Extracts the description and icon of a character's active ability (attack, skill, or burst) """
        returned_data = {}

        #Extracts the ability's icon
        icon_name = name + '_' + talent + '.png'
        img_url = "https://genshin.honeyhunterworld.com" + description[0].find('img')['src']
        self._transformer.url_to_png(icon_name,img_url,'ability_icons')

        #Extracts the ability's name
        ability_name = description[0].text.strip()
        returned_data[talent.capitalize() + ' Name'] = ability_name
        
        #Extracts names of the ability's components
        component_names = description[1].find_all('span')
        component_names = [component.text.strip() for component in component_names]

        #Extracts descriptions of the ability's components, and groups them based on the component names' positions
        full_string_description = list(description[1].stripped_strings)
        i = 0
        component_descriptions = ['']
        for description in full_string_description:
            if i < len(component_names) and description == component_names[i]:
                i += 1
                component_descriptions.append('')
            else:
                component_descriptions[i] += description + ' '

        #Transform component names and descriptions into the desired storage format
        for i in range(len(component_names)):
            returned_data[talent.capitalize() + ' Component ' + str(i)] = component_names[i] + ': ' + component_descriptions[i]
        return returned_data

    def extract_active_talent_scalings(self, table, talent):
        """ Extracts the scalings of each ability (what each part of an ability scales with, and by how much, depending on level) """
        self._transformer.table_to_text(table)
        
        returned_data = {}
        #Extract ability scalings name and stats per level
        for i in range(1, len(table)):
            scaling_name = talent.capitalize() + ' ' + table[i][0]
            scaling = talent.capitalize() + ' Scaling ' + str(i)
            returned_data[scaling] = scaling_name
            for j in range(1, 16):
                returned_data[scaling + ' Level ' + str(j)] = table[i][j]
        return returned_data

    def extract_passive_talent_descriptions(self, descriptions, name, passive_talent_levels):
        """ Extracts the name, icon, and description of passive talents 1 and 2, attained at level 20 and 60 respectively. """
        returned_data = {}

        for i in range(len(passive_talent_levels)):
            #Index in "descriptions" of the talent name
            talent_idx = -4+2*i

            #Extract icon
            icon_name = name + '_talent_' + passive_talent_levels[i] + '.png'
            img_url = "https://genshin.honeyhunterworld.com" + descriptions[talent_idx].find('img')['src']
            self._transformer.url_to_png(icon_name, img_url,'ability_icons')
            
            #Extract talent name and description
            talent_name = descriptions[talent_idx].text.strip()
            talent_description = descriptions[talent_idx+1].text.strip()
            returned_data['Level ' + passive_talent_levels[i] + ' Talent'] = talent_name + ': ' + talent_description
        
        return returned_data
    
    def extract_constellation_descriptions(self, descriptions, name, num_constellations):
        """ Extracts the icon, name, and description of a character's constellations """
        returned_data = {}
        
        for i in range(num_constellations):
            constellation_number = str(i+1)

            #Extract icon
            icon_name = name + '_const_' + constellation_number + '.png'
            img_url = "https://genshin.honeyhunterworld.com" + descriptions[i*2].find('img')['src']
            self._transformer.url_to_png(icon_name,img_url,'ability_icons')
            
            #Extract name and description
            const_name = descriptions[i*2].text.strip()
            const_description = descriptions[i*2+1].text.strip()
            returned_data['Constellation ' + constellation_number] = const_name + ': ' + const_description
        return returned_data

    def load_character_csv(self, name, character_data):
        character_df = pd.DataFrame(character_data)
        df_name = 'char_data/' + name + '.csv'
        character_df.to_csv(df_name, index=False, encoding='utf-8')