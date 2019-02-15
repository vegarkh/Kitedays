# Import package
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

d = pd.date_range(start='5/12/2016', end='5/12/2018',freq='D')
dates = d.date
urls = []
for i in dates :
    urls.append('http://vindsiden.no/api/stations/3?n=100&date={}'.format(i))
data = []
for i in urls :
    # Package the request, send the request and catch the response: r
    r = requests.get(i)
    # Decode the JSON data into a dictionary: json_data
    json_data = r.json()
    #make a DataFrame with columns Time, average wind speed and wind direction
    df = pd.DataFrame(json_data['Data'], columns=['Time','WindAvg','DirectionAvg'])
    print(df)
    data.append(df)
#problem: lager datoer som ikke finnes -> gir feilmelding
#mulig løsning: bruke datetime-pakke:
#(https://stackoverflow.com/questions/13784192/creating-an-empty-pandas-dataframe-then-filling-it)

# colors = []
# for x in list(df['WindAvg']) :
#     if x>5.5 :
#         colors.append('g')
#     else :
#         colors.append('r')
#
# plt.scatter(df['Time'],df['WindAvg'],c=colors)
# plt.grid()
# plt.show()
