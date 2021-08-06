from os import altsep
import html5lib
from bs4.element import ResultSet
import requests
from bs4 import BeautifulSoup
import pandas as pd

def update():
    char_URL = "https://genshin.honeyhunterworld.com/db/char/characters/?"
    sword_URL = "https://genshin.honeyhunterworld.com/sword/"
    claymore_URL = "https://genshin.honeyhunterworld.com/claymore/"
    polearm_URL = "https://genshin.honeyhunterworld.com/polearm/"
    bow_URL = "https://genshin.honeyhunterworld.com/bow/"
    catalyst_URL = "https://genshin.honeyhunterworld.com/catalyst/"
    artifact_URL = "https://genshin.honeyhunterworld.com/db/artifact/?"

    df = pd.read_csv("char_data/chars.csv")
    page = requests.get(char_URL)
    soup = BeautifulSoup(page.content, 'html5lib')
    results = soup.find(id='post-349')

    #Updates the database of characters based on data from honeyhunterworld
    char_elems = results.find_all('div', class_='char_sea_cont')
    for char in char_elems:
        name = char.find('span', class_='sea_charname').text.strip()
        names = df['Name'].tolist()
        names.append('')

        if(name not in names):
                print("Adding new character: " + name)
                
                char_data = update_character_data(name)
                char_df = pd.DataFrame(char_data)

                df_name = 'char_data/' + name + '.csv'
                char_df.to_csv(df_name, index=False, encoding='utf-8') 

                elem_src = char.find('img', class_='char_portrait_card_sea_element')['src']
                element = None
                if('pyro' in elem_src):
                    element = 'Pyro'
                elif('hydro' in elem_src):
                    element = 'Hydro'
                elif('electro' in elem_src):
                    element = 'Electro'
                elif('cryo' in elem_src):
                    element = 'Cryo'
                elif('anemo' in elem_src):
                    element = 'Anemo'
                elif('geo' in elem_src):
                    element = 'Geo'
                elif('dendro' in elem_src):
                    element = 'Dendro'
            
                weapon_src = char.find('img', class_='sea_weptype_element')['src']
                weapon = None
                if('sword' in weapon_src):
                    weapon = 'Sword'
                elif('claymore' in weapon_src):
                    weapon = 'Claymore'
                elif('polearm' in weapon_src):
                    weapon = 'Polearm'
                elif('bow' in weapon_src):
                    weapon = 'Bow'
                elif('catalyst' in weapon_src):
                    weapon = 'Catalyst'
            
                icon_name = name + ".png"
                img_url = "https://genshin.honeyhunterworld.com" + char.find('img', class_='char_portrait_card_sea')['src']
                req = requests.get(img_url)
                file = open("char_icons/"+icon_name, "wb")
                file.write(req.content)
                file.close()

                new_char = {'Name':name,'Lowercase':name.lower(),'Icon':icon_name,'Element':element,'Weapon':weapon}
                df = df.append(new_char, ignore_index=True)
    df.to_csv('char_data/chars.csv', index=False, encoding='utf-8')

    #Updates the database of weapons based on data from honeyhunterworld
    df = pd.read_csv("weapon_data/weapons.csv")
    data_df = pd.read_csv("weapon_data/weapon_data.csv")
    for i in range(5):
        page = ""
        type = None
        if(i == 0):
            page = requests.get(sword_URL)
            type = 'Sword'
        elif(i == 1):
            page = requests.get(claymore_URL)
            type = 'Claymore'
        elif(i == 2):
            page = requests.get(polearm_URL)
            type = 'Polearm'
        elif(i == 3):
            page = requests.get(bow_URL)
            type = 'Bow'
        elif(i == 4):
            page = requests.get(catalyst_URL)
            type = 'Catalyst'

        soup = BeautifulSoup(page.content, 'html5lib')
        results = soup.find('table', class_='art_stat_table')
        weapons = results.find_all('tr')
        for weapon in weapons:
            info = weapon.find_all('td')
            if(len(info) == 9 and info[1].text.strip() != "Icon"):
                name = info[2].text.strip()
                names = df['Name'].tolist()
                names.append('')
                if(name not in names):
                    print("Adding new weapon: " + name)
                    
                    stars = info[3].find_all('div', class_='stars_wrap')
                    grade = len(stars)

                    new_weapon_data = update_weapon_data(info,name,grade)
                    data_df = data_df.append(new_weapon_data, ignore_index=True)

                    name = name
                    icon_name = name + ".png"
                    img_url = "https://genshin.honeyhunterworld.com" + info[1].find('img', class_='itempic')['src']
                    req = requests.get(img_url)
                    file = open("weapon_icons/"+icon_name, "wb")
                    file.write(req.content)
                    file.close()
                
                    new_weapon = {'Name':name,'Lowercase':name.lower(),'Icon':icon_name,'Grade':grade,'Type':type}
                    df = df.append(new_weapon, ignore_index=True)
    df.to_csv('weapon_data/weapons.csv', index=False, encoding='utf-8')
    data_df.to_csv('weapon_data/weapon_data.csv', index=False, encoding='utf-8')

    #Updates the database of artifacts based on data from honeyhunterworld
    df = pd.read_csv("artifact_data/artifacts.csv")
    page = requests.get(artifact_URL)
    soup = BeautifulSoup(page.content, 'html5lib')
    results = soup.find_all('table', class_='art_stat_table_new')
    for table in results:
        artifacts = table.find_all('tr')
        for i in range(1, len(artifacts), 2):
            info = artifacts[i].find_all('td')
            if(len(info) == 5):
                set_name = info[2].text.strip()
                names = df['Set Name'].tolist()
                names.append('')
                if(set_name not in names):
                    print("Adding new set: " + set_name)
                    set_name = set_name
                    stars = info[3].find_all('div', class_='sea_char_stars_wrap')
                    grade = int(len(stars)/2)

                    icon_name = set_name + ".png"
                    img_url = "https://genshin.honeyhunterworld.com" + info[1].find('img', class_='itempic')['src']
                    req = requests.get(img_url)
                    file = open("artifact_icons/"+icon_name, "wb")
                    file.write(req.content)
                    file.close()

                    two_piece_effect = info[-1].text.strip()
                    four_piece_row = artifacts[i+1].find_all('td')
                    four_piece_effect = four_piece_row[-1].text.strip()

                    new_artifact = {'Set Name':set_name,'Lowercase':set_name.lower(),'Icon':icon_name,'Grade':grade,'Two Piece':two_piece_effect,'Four Piece':four_piece_effect}
                    df = df.append(new_artifact, ignore_index=True)
    df.to_csv('artifact_data/artifacts.csv', index=False, encoding='utf-8')

def update_weapon_data(info, name, grade):
    """Helper function to update numbers on each weapon"""
    min_base_atk = int(info[4].text.strip())
    substat = info[5].text.strip()
    min_substat = float(info[6].text.strip())
    
    weapon_url = "https://genshin.honeyhunterworld.com/" + info[1].find('a')['href']
    weapon_page = requests.get(weapon_url)
    weapon_soup = BeautifulSoup(weapon_page.content, 'html5lib')
    
    passive = 'None'
    if(grade > 2):
        passive_results = weapon_soup.find('table', class_='item_main_table')
        passive_row = passive_results.find_all('tr')[5]
        passive_html = passive_row.find_all('td')[1]
        passive = passive_html.text.strip()

    weapon_results = weapon_soup.find('table', class_='add_stat_table')
    level_stats = weapon_results.find_all('tr')
    ascensions = []
    total_ascension_bonus = 0
    ascensions.append(int(level_stats[6].find_all('td')[1].text.strip())-int(level_stats[5].find_all('td')[1].text.strip()))
    ascensions.append(int(level_stats[11].find_all('td')[1].text.strip())-int(level_stats[10].find_all('td')[1].text.strip()))
    ascensions.append(int(level_stats[14].find_all('td')[1].text.strip())-int(level_stats[13].find_all('td')[1].text.strip()))
    ascensions.append(int(level_stats[17].find_all('td')[1].text.strip())-int(level_stats[16].find_all('td')[1].text.strip()))
    if(grade > 2):
        ascensions.append(int(level_stats[20].find_all('td')[1].text.strip())-int(level_stats[19].find_all('td')[1].text.strip()))
        ascensions.append(int(level_stats[23].find_all('td')[1].text.strip())-int(level_stats[22].find_all('td')[1].text.strip()))
    else:
        ascensions.append(0)
        ascensions.append(0)
    for ascension in ascensions:
        total_ascension_bonus += ascension

    max_stats = level_stats[-1].find_all('td')
    max_base_atk = int(max_stats[1].text.strip())
    base_atk_per_level = float(max_base_atk  - total_ascension_bonus - min_base_atk)
    max_substat = float(max_stats[2].text.strip())
    substat_per_level = float(max_substat-min_substat)

    if grade > 2:
        base_atk_per_level /= 89
        substat_per_level /= 89
    else:
        base_atk_per_level /= 69
        substat_per_level /= 69

    data = {'Name':name,'Level 1 Base Attack':min_base_atk,'Base Attack Per Level':base_atk_per_level,'20+':ascensions[0],'40+':ascensions[1],
    '50+':ascensions[2],'60+':ascensions[3],'70+':ascensions[4],'80+':ascensions[5],'Substat':substat,'Level 1 Substat':min_substat,'Substat Per Level':substat_per_level,'Passive':passive}
    return data

def update_character_data(name):
    """Creates a data table of stats on each character. Passive talent and constellation effects must be manually added,
       but descriptions can be saved."""
    data = {}

    if name == 'Yanfei':
        char_url = "https://genshin.honeyhunterworld.com/db/char/feiyan/?"
    elif name == 'Kaedehara Kazuha':
        char_url = "https://genshin.honeyhunterworld.com/db/char/kazuha/?"
    elif name == 'Kamisato Ayaka':
        char_url = "https://genshin.honeyhunterworld.com/db/char/ayaka/?"
    else:
        char_url = "https://genshin.honeyhunterworld.com/db/char/" + name + "/?"
        char_url = char_url.replace(' ', '')
    char_page = requests.get(char_url)
    char_soup = BeautifulSoup(char_page.content, 'html5lib')

    results = char_soup.find(id='live_data')
    tables = results.find_all('div', class_='skilldmgwrapper')
    descriptions = results.find_all('table', class_='item_main_table')

    #Calculate all level-up stat increases
    stat_progression = tables[0].find_all('tr')
    #Turns the list of "tr" objects into a list of lists of data
    for i in range(len(stat_progression)):
        stat_progression[i] = stat_progression[i].find_all('td')
        for j in range(len(stat_progression[i])):
            stat_progression[i][j] = stat_progression[i][j].text.strip()
    #Level up basic stats
    #Order of list: base HP, base ATK, base DEF
    for i in range(15):
        data[stat_progression[i][0]] = [stat_progression[i][j] for j in range(1, 4)]
    #Ascension specialized stat
    ascension_stat = stat_progression[0][4]
    ascension_stat_increase = stat_progression[5][4]
    stripped_stat_increase = ascension_stat_increase.strip(' %')
    ascension_stat_increase = float(stripped_stat_increase)
    data['Ascension Bonus Stat'] = ascension_stat
    data['Ascension Bonus Stat Increase'] = ascension_stat_increase

    #Calculate all attack descriptions and stats
    attack_description = descriptions[1].find_all('tr')
    parsed_attack = parse_active_descriptions(attack_description, name, 'Attack')
    attack_component_names = parsed_attack[2]
    attack_component_descriptions = parsed_attack[3]

    data['Attack Icon'] = parsed_attack[0]
    data['Attack Name'] = parsed_attack[1]

    for i in range(len(attack_component_names)):
        data['Attack Component ' + str(i)] = attack_component_names[i] + ': ' + attack_component_descriptions[i+1]

    attack_talent_table = tables[1].find_all('tr')
    parsed_attack_stats = parse_active_scalings(attack_talent_table, name, 'Attack')
    data.update(parsed_attack_stats)

    #Calculate all skill descriptions and stats
    skill_description = descriptions[2].find_all('tr')
    parsed_skill = parse_active_descriptions(skill_description, name, 'Skill')
    skill_component_names = parsed_skill[2]
    skill_component_descriptions = parsed_skill[3]

    data['Skill Icon'] = parsed_skill[0]
    data['Skill Name'] = parsed_skill[1]

    data['Skill Basic Description'] = skill_component_descriptions[0]
    for i in range(len(skill_component_names)):
        data['Skill Component ' + str(i)] = skill_component_names[i] + ': ' + skill_component_descriptions[i+1]
    

    skill_talent_table = tables[2].find_all('tr')
    parsed_skill_stats = parse_active_scalings(skill_talent_table, name, 'Skill')
    data.update(parsed_skill_stats)

    #Calculate all burst descriptions and stats
    burst_description = descriptions[3].find_all('tr')
    parsed_burst = parse_active_descriptions(burst_description, name, 'Burst')
    burst_component_names = parsed_burst[2]
    burst_component_descriptions = parsed_burst[3]

    data['Burst Icon'] = parsed_burst[0]
    data['Burst Name'] = parsed_burst[1]

    data['Burst Basic Description'] = burst_component_descriptions[0]
    for i in range(len(burst_component_names)):
        data['Burst Component ' + str(i)] = burst_component_names[i] + ': ' + burst_component_descriptions[i+1]

    burst_talent_table = tables[-1].find_all('tr')
    parsed_burst_stats = parse_active_scalings(burst_talent_table, name, 'Burst')
    data.update(parsed_burst_stats)

    #Save all passive talent and constellation descriptions
    passive_talent_descriptions = descriptions[-2].find_all('tr')
    passive_icon_1 = name + '_talent_20.png'
    img_url = "https://genshin.honeyhunterworld.com" + passive_talent_descriptions[-4].find('img')['src']
    req = requests.get(img_url)
    file = open("ability_icons/"+passive_icon_1, "wb")
    file.write(req.content)
    file.close()
    talent_name = passive_talent_descriptions[-4].text.strip()
    talent_description = passive_talent_descriptions[-3].text.strip()
    data['Level 20 Talent'] = talent_name + ': ' + talent_description


    passive_icon_2 = name + '_talent_60.png'
    if name == 'Traveler':
        x = 5
    img_url = "https://genshin.honeyhunterworld.com" + passive_talent_descriptions[-2].find('img')['src']
    req = requests.get(img_url)
    file = open("ability_icons/"+passive_icon_2, "wb")
    file.write(req.content)
    file.close()
    talent_name = passive_talent_descriptions[-2].text.strip()
    talent_description = passive_talent_descriptions[-1].text.strip()
    data['Level 60 Talent'] = talent_name + ': ' + talent_description
    
    constellation_descriptions = descriptions[-1].find_all('tr')
    for i in range(6):
        const_number = i+1
        const_icon = name + '_const_' + str(const_number) + '.png'
        img_url = "https://genshin.honeyhunterworld.com" + constellation_descriptions[i*2].find('img')['src']
        req = requests.get(img_url)
        file = open("ability_icons/"+const_icon, "wb")
        file.write(req.content)
        file.close()
        const_name = constellation_descriptions[i*2].text.strip()
        const_description = constellation_descriptions[i*2+1].text.strip()
        data['Constellation ' + str(const_number)] = const_name + ': ' + const_description
    
    return data

def parse_active_descriptions(description, name, type):
    """ For attacks, skills, and bursts, saves the icon for the ability
     and returns the icon file name, talent name, and component names + descriptions. """
    if(type == 'Attack'):
        icon_name = name + '_attack.png'
    elif(type == 'Skill'):
        icon_name = name + '_skill.png'
    else:
        icon_name = name + '_burst.png'
    img_url = "https://genshin.honeyhunterworld.com" + description[0].find('img')['src']
    req = requests.get(img_url)
    file = open("ability_icons/"+icon_name, "wb")
    file.write(req.content)
    file.close()

    talent_name = description[0].text.strip()

    component_names = description[1].find_all('span')
    component_names = [component.text.strip() for component in component_names]
    full_string_description = list(description[1].stripped_strings)
    i = 0
    component_descriptions = ['']
    for description in full_string_description:
        if i != len(component_names) and description == component_names[i]:
            i += 1
            component_descriptions.append('')
        else:
            component_descriptions[i] += description + ' '

    return [icon_name, talent_name, component_names, component_descriptions]

def parse_active_scalings(table, name, type):
    for i in range(len(table)):
        table[i] = table[i].find_all('td')
        for j in range(len(table[i])):
            table[i][j] = table[i][j].text.strip()

    ans = {}
    #Talent scalings title and numbers per level
    for i in range(1, len(table)):
        component_name = type + ' ' + table[i][0]
        ans[type + 'Component ' + str(i)] = component_name
        for j in range(1, 16):
            ans[component_name + ' Level ' + str(j)] = table[i][j]
    return ans

update()