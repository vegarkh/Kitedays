import requests
import pandas as pd
from fastparquet import write, ParquetFile
from tqdm import tqdm
from datetime import datetime

# set period for loading wind data
startDate = '1/26/2017'
endDate = '1/26/2017'

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

        # if DataFrame is empty, add rows with NaN-values at 7:00 and 22:00


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
        day = pd.DataFrame(data=df.between_time('06:59', '22:00'))

        # some preparing for resampling data
        # read time for the first measurement and compare to 7:00
        day_first = day.first_valid_index()
        seven_am = datetime(day_first.year, day_first.month, day_first.day, 7, 0, 0)
        seven_am = pd.to_datetime(seven_am).tz_localize('Europe/Oslo')
        time_gap_morning = day_first - seven_am

        # read time for the last measurement and compare to 22:00
        day_last = day.last_valid_index()
        ten_pm = datetime(day_last.year, day_last.month, day_last.day, 22, 0, 0)
        ten_pm = pd.to_datetime(ten_pm).tz_localize('Europe/Oslo')
        time_gap_night = ten_pm - day_last

        # the frequency of measured data is not constant
        # find a suitable frequency: time_diff_str
        time_diff = day.index.to_series().diff().dt.round(freq="min")
        time_diff_mode = time_diff.mode().astype('timedelta64[m]')

        if int(time_diff_mode) > 30:
            time_diff_str = "15min"
        else:
            time_diff_str = str(int(time_diff_mode)) + "min"

        # in case of empty or almost empty dataframe
        # (0-1 measurements) add NaN to missing values at 7:00 and 22:00
        if len(day.index) < 2:
            day = day.append(pd.DataFrame(index=[seven_am])).sort_index()
            day = day.append(pd.DataFrame(index=[ten_pm])).sort_index()
            time_diff_str = "15min"
        # add NaN to missing values between 7:00 and 22:00
        if time_gap_morning.seconds/60 > int(time_diff_mode):
            day = day.append(pd.DataFrame(index=[seven_am])).sort_index()
        if time_gap_night.seconds/60 > int(time_diff_mode):
            day = day.append(pd.DataFrame(index=[ten_pm])).sort_index()
        day_resamp = day.resample(time_diff_str).first()
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
