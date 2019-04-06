# Import packages
import requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# Flask app global
app = Flask(__name__)


@app.route('/kite-days/<int:station>')
def get_n_kiteable_days(station):
    params = {}

    for param in ['startDate', 'endDate']:
        params[param] = request.args.get(param)

        if not params[param]:
            return jsonify({
                "error": "missing non-optional param: %s" % param
            })

    # generate dates (DateTimeIndex)
    d = pd.date_range(start=params['startDate'], end=params['endDate'], freq='D')

    # remove time from d
    dates = d.date

    # make a list of urls representing each date
    urls = []
    for date in dates:
        urls.append('http://vindsiden.no/api/stations/{}?n=100&date={}'.format(station, date))

    data = []
    # import data from API: http://vindsiden.no/api/stations/...
    for url in urls:
        r = requests.get(url)
        json_data = r.json()

        # make a DataFrame with columns time, wind speed and wind direction
        df = pd.DataFrame(json_data['Data'], columns=['Time', 'WindAvg', 'DirectionAvg'])

        # convert the column 'Time' to datetime format
        df['Time'] = pd.to_datetime(df['Time'])

        # make a new column "Kitewind"
        df['Kitewind'] = np.nan

        # set 'Time' as index
        df.set_index('Time', inplace=True, drop=True)

        # Each element in this list is supposed to be a DataFrame consisting of
        # wind data from a spesific date
        data.append(df)

    # make a new list with wind data from time 07:00AM - 22:00PM in a list, data_day.
    # Consider the wind data to be two hours delayed (05:00AM in data corresponds to 7:00AM in real time)
    data_days = []

    for day in data:
        relevant = pd.DataFrame(data=day.between_time('05:00', '20:00'), copy=True)
        data_days.append(relevant)

    number_of_kitedays = 0

    for data_day in data_days:
        data_day.loc[:, 'Kitewind'] = [i > 6 and 225 > j > 135 for i, j in
                                       zip(data_day.loc[:, 'WindAvg'], data_day.loc[:, 'DirectionAvg'])]
        if sum(data_day['Kitewind']) > 6:
            number_of_kitedays += 1

    msg = "During the period from %s to %s, there was %d kiteable days" % (dates[0],
                                                                           dates[-1], number_of_kitedays)
    return {
        "msg": msg,
        "number_of_kitedays": number_of_kitedays
    }


# only start server if run as main process
if __name__ == "__main__":
    app.run(debug=True)
