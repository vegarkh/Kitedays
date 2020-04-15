import requests
import pandas as pd
from fastparquet import write, ParquetFile
from tqdm import tqdm

# set period for loading wind data
startDate = '6/26/2016'
endDate = '6/26/2016'

# set station (place) for loading wind data
station = '3'

# make list of dates
d = pd.date_range(start=startDate, end=endDate, freq='D')
dates = d.date

# progress bar
with tqdm(total=len(dates)) as pbar:
    # fetch urls and save files locally
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

        # create a subset of day (exclude night)
        day = pd.DataFrame(data=df.between_time('07:00', '22:00'))
        print(day.head())

        # convert to parquet file
        # day_parquet = day.to_parquet('./WindData/testfile.parquet', index= True)
        write('./WindData/spot{}date{}'.format(station, date), day)
        df_parquet = ParquetFile('./WindData/spot{}date{}'.format(station, date)).to_pandas()
        print(df_parquet.head())

        pbar.update()

# maybe make this a function?
# day: choose the columns I want
