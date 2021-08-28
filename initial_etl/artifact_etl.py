import pandas as pd
from bs4 import BeautifulSoup
import initial_etl.general_transformer as general_transformer
import requests
import html5lib

class ArtifactETL:
    """ Class to extract, transform, and load data from a list of BeautifulSoup objects of artifact sets. """
    def __init__(self, url):
        """ Initializes the data to extract from, as well as a list of existing artifact sets to reduce redundancy. """
        page = requests.get(url)
        html_page = BeautifulSoup(page.content, 'html5lib')
        artifact_tables = html_page.find_all('table', class_='art_stat_table_new')
        self._artifact_list = []
        for table in artifact_tables:
            table = table.find_all('tr')
            #Remove the header of each table
            table.pop(0)
            self._artifact_list += table
        self._artifact_csv = pd.read_csv('equipment_data/artifacts.csv')
        self._existing_artifacts = self._artifact_csv['Set Name'].tolist()
        self._existing_artifacts.append('')
        self._transformer = general_transformer.GeneralTransformer()
    
    def etl_data(self):
        """ Extracts, transforms, and loads each artifact set's data (name, lowest grade, icon, and set effects). """
        #The artifact list contains an artifact every other row.
        for i in range(0, len(self._artifact_list), 2):
            untransformed_data = self._artifact_list[i].find_all('td')

            #Extract and transform set name
            set_name = untransformed_data[2].text.strip()

            if set_name not in self._existing_artifacts:
                print("Adding new artifact set: " + set_name)

                #Extract and transform grade
                stars = untransformed_data[3].find_all('div', class_='sea_char_stars_wrap')
                grade = int(len(stars)/2)

                #Extract, transform, and load icon
                icon_name = set_name + '.png'
                img_url = "https://genshin.honeyhunterworld.com" + untransformed_data[1].find('img', class_='itempic')['src']
                self._transformer.url_to_png(icon_name, img_url, 'artifact_icons')

                #Extract and transform set effects. If there is only 1, replaces the second with a filler.
                first_effect = untransformed_data[-1].text.strip()
                second_row = self._artifact_list[i+1].find_all('td')
                second_effect = second_row[-1].text.strip()
                if second_effect == '':
                    second_effect = 'None'

                new_artifact = {'Set Name':set_name,'Lowercase':set_name.lower(),'Grade':grade,'First Effect':first_effect,'Second Effect':second_effect}
                self._artifact_csv = self._artifact_csv.append(new_artifact,ignore_index=True)
        self._artifact_csv.to_csv('equipment_data/artifacts.csv', index=False, encoding='utf-8')