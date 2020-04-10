import json
import requests
import pandas as pd
from tqdm import tqdm


#set period for loading wind data
startDate = '6/25/2016'
endDate = '6/27/2016'

#set station (place) for loading wind data
station = '3'

#make list of dates
d = pd.date_range(start=startDate, end=endDate,freq='D')
dates = d.date

#progress bar
with tqdm(total=len(dates)) as pbar:
    #fetch urls and save files locally
    for date in dates :
        # Package the request, send the request and catch the response: r
        r = requests.get('http://vindsiden.no/api/stations/{}?n=100&date={}'.format(station,date))
        # Decode the JSON data into a dictionary: json_data
        json_data = r.json()
        #save json_data locally
        with open('./WindData/spot{}date{}.json'.format(station,date), 'w') as json_file:
            json.dump(json_data, json_file)
        pbar.update()


#maybe make this a function?