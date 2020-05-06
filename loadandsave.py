import requests
import pandas as pd
from fastparquet import write, ParquetFile
from tqdm import tqdm
from cleaning import cleaning
from datetime import datetime

# set period for loading wind data
startDate = '3/25/2018'
endDate = '3/25/2018'

# set station (place) for loading wind data
station = '3'

# make list of dates
d = pd.date_range(start=startDate, end=endDate, freq='D')
dates = d.date

# progress bar
with tqdm(total=len(dates)) as pbar:
    # fetch urls -> load, clean and save files on local disk
    for date in dates:
        # Package the request, send the request and catch the response: r
        r = requests.get('http://vindsiden.no/api/stations/{}?n=100&date={}'.format(station, date))

        # Decode the JSON data into a dictionary: json_data
        json_data = r.json()

        # make a DataFrame with columns time, wind speed and wind direction
        df = pd.DataFrame(json_data['Data'], columns=['Time', 'StationID', 'WindAvg', 'WindStDev', 'WindMax', 'WindMin',
                                                      'DirectionAvg', 'DirectionStDev', 'Temperature1'])
        #clean and resample wind data and exclude night
        day_resamp = cleaning(df, date, station)

        # load wind data file from local disk
        #winddata = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()

        # merging dataframes together
        #winddata = pd.concat([winddata, day], axis= 0, verify_integrity= True)


        # convert to parquet file
        write('./WindData/spot{}'.format(station), day_resamp)
        #
        # # load parquet file from local disk
        # df_parquet = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()
        # pd.options.display.max_rows = 500
        # print(winddata)

        pbar.update()

# maybe make this a function?
# day: choose the columns I want
