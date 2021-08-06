import pandas as pd

data = {'Name':['Overloaded','Shattered','Electro-Charged','Superconduct','Swirl','Crystallize','Melt','Vaporize'],
        'Damage Type':['Pyro','Physical','Electro','Cryo','Trigger','None','Trigger','Trigger'],
        'Aura':['Pyro Electro','Cryo Hydro','Electro Hydro','Cryo Electro','Pyro Electro Cryo Hydro','Pyro Electro Cryo Hydro','Pyro Cryo','Hydro Pyro'],
        'Trigger':['Pyro Electro','Cryo Hydro','Electro Hydro','Cryo Electro','Anemo','Geo','Pyro Cryo','Hydro Pyro'],
        'Transformative':[True,True,True,True,True,True,False,False],
        '1':[34,26,21,9,10,91,0,0],
        '10':[68,51,41,17,20,159,0,0],
        '20':[161,121,97,40,48,304,0,0],
        '30':[273,204,164,68,82,438,0,0],
        '40':[415,311,249,104,124,585,0,0],
        '50':[647,485,388,162,194,787,0,0],
        '60':[979,734,587,245,294,1030,0,0],
        '70':[1533,1150,920,383,460,1315,0,0],
        '80':[2159,1619,1295,540,648,1597,0,0],
        '90':[2901,2176,1741,725,868,1851,0,0]}
df = pd.DataFrame(data)
df.to_csv('reaction_data.csv', index=False, encoding='utf-8')