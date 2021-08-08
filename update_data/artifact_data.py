import pandas as pd
import html5lib
import requests
from bs4 import BeautifulSoup
import pandas as pd
        

def process_artifact_table(table):
    ans = {}
    for i in range(len(table)):
        table[i] = table[i].find_all('td')
        for j in range(len(table[i])):
            table[i][j] = table[i][j].text.strip(' %')
    
    if len(table) == 19:
        prefix = '2 '
    elif len(table) == 27:
        prefix = '3 '
    elif len(table) == 35:
        prefix = '4 '
    else:
        prefix = '5 '
    
    table[0][3] += '%'
    table[0][4] += '%'
    table[0][5] += '%'

    for j in range(1, 13):
        col_title = prefix + table[0][j]
        ans[col_title] = []
        for i in range(1, 43, 2):
            if i >= len(table):
                ans[col_title].append(0)
            else:
                ans[col_title].append(table[i][j])
        test_title = prefix + 'DMG Bonus (Element)'
        if col_title == test_title:
            elements = ['Pyro ', 'Hydro ', 'Electro ', 'Cryo ', 'Geo ', 'Anemo ', 'Dendro ']
            for element in elements:
                element_title = prefix + element + 'DMG Bonus'
                ans[element_title] = [stat for stat in ans[col_title]]
    return ans
            
def process_substat_table(table):
    ans = [{},{},{},{}]
    stats = ['HP', 'ATK', 'DEF', 'HP%', 'ATK%', 'DEF%', 'Elemental Mastery', 'Energy Recharge', 'Crit Rate', 'Crit DMG']
    for i in range(1, len(table)):
        table[i] = table[i].find_all('td')
        for j in range(1, len(table[i])):
            table[i][j] = table[i][j].text
            table[i][j] = table[i][j].split('/')
            for k in range(len(table[i][j])):
                table[i][j][k] = table[i][j][k].strip(' %')
                table[i][j][k] = int(float(table[i][j][k])*100)

    for i in range(1, len(stats)+1):
        col_title = stats[i-1]
        rolls = []
        for j in range(1, 5):
            grade = j + 1
            rolls = [roll for roll in table[i][j]] 
            if col_title == 'ATK' or col_title == 'HP' or col_title == 'DEF':
                ans[j-1][col_title] = set([round(roll/100) for roll in rolls])
            else:
                ans[j-1][col_title] = set([round(roll/100, 1) for roll in rolls])
            last_layer = [roll for roll in rolls]
            if grade == 2:
                num_upgrades = grade - 1
            else:
                num_upgrades = grade
            for x in range(num_upgrades):
                new_layer = set([])
                
                for stat in last_layer:
                    for roll in rolls:
                        entry = int(stat + roll)
                        if col_title == 'ATK' or col_title == 'HP' or col_title == 'DEF':
                            ans[j-1][col_title].add(round(entry/100))
                        else:
                            ans[j-1][col_title].add(round(entry/100, 1))
                        new_layer.add(entry)
                last_layer = [new_stat for new_stat in new_layer]
            ans[j-1][col_title] = list(ans[j-1][col_title])
            ans[j-1][col_title].sort()
    
    for sub_data in ans:
        max_length = [0, "None"]
        for stat in sub_data:
            if len(sub_data[stat]) > max_length[0]:
                max_length[0] = len(sub_data[stat])
                max_length[1] = stat
        for stat in sub_data:
            while len(sub_data[stat]) < max_length[0]:
                sub_data[stat].append(0)
    
    return ans

main_data = {}

page = requests.get("https://genshin.honeyhunterworld.com/db/art/family/a_10010/?")
soup = BeautifulSoup(page.content, 'html5lib')
tables = soup.find_all('div', class_= 'skilldmgwrapper')
two_star_table = tables[1].find_all('tr')
three_star_table = tables[3].find_all('tr')

page = requests.get("https://genshin.honeyhunterworld.com/db/art/family/a_15008/?")
soup = BeautifulSoup(page.content, 'html5lib')
tables = soup.find_all('div', class_= 'skilldmgwrapper')
four_star_table = tables[1].find_all('tr')
five_star_table = tables[3].find_all('tr')

page = requests.get("https://genshin-impact.fandom.com/wiki/Artifacts/Stats")
soup = BeautifulSoup(page.content, 'html5lib')
table = soup.find_all('table', class_='wikitable')[6]
sub_table = table.find_all('tr')

main_data.update(process_artifact_table(two_star_table))
main_data.update(process_artifact_table(three_star_table))
main_data.update(process_artifact_table(four_star_table))
main_data.update(process_artifact_table(five_star_table))

two_data, three_data, four_data, five_data = process_substat_table(sub_table)

df = pd.DataFrame(main_data)
df.to_csv('artifact_data/artifact_main_data.csv', index=False, encoding='utf-8')
df = pd.DataFrame(two_data)
df.to_csv('artifact_data/two_star_sub_data.csv', index=False, encoding='utf-8')
df = pd.DataFrame(three_data)
df.to_csv('artifact_data/three_star_sub_data.csv', index=False, encoding='utf-8')
df = pd.DataFrame(four_data)
df.to_csv('artifact_data/four_star_sub_data.csv', index=False, encoding='utf-8')
df = pd.DataFrame(five_data)
df.to_csv('artifact_data/five_star_sub_data.csv', index=False, encoding='utf-8')
