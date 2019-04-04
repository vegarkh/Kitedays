# Import packages
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#generate dates (DateTimeIndex)
d = pd.date_range(start='5/31/2018', end='5/31/2018',freq='D')
#remove time from d
dates = d.date
#make a list of urls representing each date
urls = []
for i in dates :
    urls.append('http://vindsiden.no/api/stations/3?n=100&date={}'.format(i))
#make a empty list "data"
data = []
#import data from API: http://vindsiden.no/api/stations/...
for i in urls :
    # Package the request, send the request and catch the response: r
    r = requests.get(i)
    # Decode the JSON data into a dictionary: json_data
    json_data = r.json()
    #make a DataFrame with columns time, wind speed and wind direction
    df = pd.DataFrame(json_data['Data'], columns=['Time','WindAvg','DirectionAvg'])
    #convert the column 'Time' to datetime format
    df['Time'] = pd.to_datetime(df['Time'])
    #make a new column "Kitewind"
    df['Kitewind'] = np.nan
    #set 'Time' as index
    df.set_index('Time', inplace=True, drop = False)
    #Each element in this list is supposed to be a DataFrame consisting of
    #wind data from a spesific date
    data.append(df)
#make a new list with wind data from time 07:00AM - 22:00PM in a list, data_day.
#Consider the wind data to be two hours delayed (05:00AM in data corresponds to 7:00AM in real time)
data_day = []
for i in range(len(data)) :
    data_day.append(data[i].between_time('05:00','20:00'))
N = len(data_day)
number_of_kitedays = 0
for element in range(N) :
    data_day[element]['Kitewind'] = [i > 6 and 225 > j > 135 for i,j in zip(data_day[element].loc[:,'WindAvg'], data_day[element].loc[:,'DirectionAvg'])]
    if sum(data_day[element]['Kitewind']) > 6 :
        number_of_kitedays += 1
print("During the period from " + str(dates[0]) + " to " + str(dates[-1]) + ", there is " + str(number_of_kitedays) + " kiteable days!")
