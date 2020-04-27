import requests
import pandas as pd
from fastparquet import write, ParquetFile
from tqdm import tqdm

# set period for loading wind data
startDate = '4/18/2018'
endDate = '4/18/2018'

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

        # convert the column 'Time' to datetime format
        df['Time'] = pd.to_datetime(df['Time'])

        # convert timezone from UTC to Europe/Oslo
        time_utc = df['Time']
        time_oslo = time_utc.dt.tz_convert('Europe/Oslo')

        # set 'Time' as index and delete the "Time" column
        df.set_index(time_oslo, inplace=True)
        df = df.drop("Time", axis=1)
        df = df.sort_index()

        # create a subset of day (exclude night)
        day = pd.DataFrame(data=df.between_time('07:00', '22:00'))

        time_diff = day.index.to_series().diff()
        time_diff_mode = time_diff.mode().astype('timedelta64[m]')
        #make a function and make it a list comprehension
        #def timeintervall
        #i = 0
        #timesteps = []
        #for i in day.index() :
            #if day.index(i+1) - day.index(i) > 22 :
                # i+=1
            #elif day.index(i) == False : eller no sånt
                #break
            #else :
                # timesteps.append(day.index(i+1) - day.index(i))
                # i +=1
        #return timeintervall.mean()

        # resample data
        day_resamp = day.resample(time_diff_mode).first()
        print(day_resamp)

        # # load wind data file from local disk
        # winddata = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()
        #
        # # merging dataframes together
        # winddata = pd.concat([winddata, day], axis= 0, verify_integrity= True)
        #
        # # convert to parquet file
        # write('./WindData/spot{}'.format(station), winddata)
        #
        # # load parquet file from local disk
        # df_parquet = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()
        # pd.options.display.max_rows = 500
        # print(winddata)

        pbar.update()

# maybe make this a function?
# day: choose the columns I want
