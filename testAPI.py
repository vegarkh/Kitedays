# Import packages
import requests
import pandas as pd
from flask import Flask, request, jsonify

# Flask app global
app = Flask(__name__)


@app.route('/kite-days/<int:station>')
def get_n_kite_days(station):
    params = {}

    for param in ['startDate', 'endDate']:
        params[param] = request.args.get(param)

        if not params[param]:
            return jsonify({
                "error": "missing non-optional param: %s" % param
            })

    # generate dates (DateTimeIndex)
    dates = pd.date_range(start=params['startDate'], end=params['endDate'], freq='D').date

    # import data from API: http://vindsiden.no/api/stations/...
    kite_days = 0
    for date in dates:
        url = 'http://vindsiden.no/api/stations/{}?n=100&date={}'.format(station, date)
        r = requests.get(url)
        json_data = r.json()

        # make a DataFrame with columns time, wind speed and wind direction
        df = pd.DataFrame(json_data['Data'], columns=['Time', 'WindAvg', 'DirectionAvg'])

        # convert the column 'Time' to datetime format
        df['Time'] = pd.to_datetime(df['Time'])

        # set 'Time' as index
        df.set_index('Time', inplace=True)

        # create a subset of day (exclude night)
        day = pd.DataFrame(data=df.between_time('05:00', '20:00'))

        # list readings within wind speed average (m/s) and direction average (degrees) limits
        kite_wind = [speed > 6 and 225 > direction > 135 for speed, direction in
                     zip(day.loc[:, 'WindAvg'], day.loc[:, 'DirectionAvg'])]
        # consider "good kite day" if n entries within limits is above 6
        if sum(kite_wind) > 6:
            kite_days += 1

    msg = "During the period from %s to %s, there were %d good kite days" % (dates[0],
                                                                             dates[-1], kite_days)
    return jsonify({
        "msg": msg,
        "kite_days": kite_days
    })


# only start server if run as main process
if __name__ == "__main__":
    app.run(debug=True)
