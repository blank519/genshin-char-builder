import initial_etl.character_etl as character_etl
import initial_etl.weapon_etl as weapon_etl
import initial_etl.artifact_etl as artifact_etl

class Updater:
    """ Class to update/ETL all objects  """
    def __init__(self,char_url,weapon_urls,artifact_url):
        self._char_url =  char_url
        self._weapon_urls = weapon_urls
        self._artifact_url = artifact_url
        
    def update(self):
        #Updates data on characters
        char_updater = character_etl.CharacterETL(self._char_url)
        char_updater.etl_data()

        #Updates data on weapons
        for weapon in self._weapon_urls:
            weapon_updater = weapon_etl.WeaponETL(self._weapon_urls[weapon], weapon)
            weapon_updater.etl_data()
    
        #Updates data on artifacts
        artifact_updater = artifact_etl.ArtifactETL(self._artifact_url)
        artifact_updater.etl_data()


