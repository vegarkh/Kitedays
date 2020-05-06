import pandas as pd

def cleaning(df, date, station):
    seven = str(date) + " 07:00:00"
    seven = pd.to_datetime(seven).tz_localize('Europe/Oslo')
    ten = str(date) + " 22:00:00"
    ten = pd.to_datetime(ten).tz_localize('Europe/Oslo')

    # if DataFrame is empty, add rows with NaN-values at 7:00 and 22:00
    if len(df.index) < 1:
        df = df.append(pd.DataFrame(index=[seven])).sort_index()
        df = df.append(pd.DataFrame(index=[ten])).sort_index()
    else:
        # convert the column 'Time' to datetime format
        df['Time'] = pd.to_datetime(df['Time'])

        # convert timezone from UTC to Europe/Oslo
        time_utc = df['Time']
        time_oslo = time_utc.dt.tz_convert('Europe/Oslo')

        # set 'Time' as index
        df.set_index(time_oslo, inplace=True)

    # delete 'Time' column
    df = df.drop("Time", axis=1)
    df = df.sort_index()

    # create a subset of day (exclude night)
    day = pd.DataFrame(data=df.between_time('07:00', '22:00'))

    # some preparing for resampling data
    # read time for the first measurement and compare to 7:00
    day_first = day.first_valid_index()
    if day_first == None:
        day_first = pd.to_datetime(seven)

    # seven_am = datetime(day_first.year, day_first.month, day_first.day, 7, 0, 0)
    # seven_am = pd.to_datetime(seven_am).tz_localize('Europe/Oslo')
    time_gap_morning = day_first - seven

    # read time for the last measurement and compare to 22:00
    day_last = day.last_valid_index()
    if day_last == None:
        day_last = pd.to_datetime(ten)

    # ten_pm = datetime(day_last.year, day_last.month, day_last.day, 22, 0, 0)
    # ten_pm = pd.to_datetime(ten_pm).tz_localize('Europe/Oslo')
    time_gap_night = ten - day_last

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
    if len(day.index) < 3:
        # day = day.append(pd.DataFrame(index=[seven_am])).sort_index()
        # day = day.append(pd.DataFrame(index=[ten_pm])).sort_index()
        time_diff_str = "15min"

    # add NaN to missing values between 7:00 and 22:00
    if time_gap_morning.seconds / 60 > int(time_diff_mode):
        day = day.append(pd.DataFrame({'StationID': [station]}, index=[seven])).sort_index()
    if time_gap_night.seconds / 60 > int(time_diff_mode):
        day = day.append(pd.DataFrame({'StationID': [station]}, index=[ten])).sort_index()
    day_resamp = day.resample(time_diff_str).first()
    day_resamp['StationID'] = station
    return(day_resamp)