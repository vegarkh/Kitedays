from fastparquet import write, ParquetFile
import matplotlib.pyplot as plt
import pandas as pd

station = '3'

# load wind data file from local disk
winddata = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()

winddata['WindAvg'] = pd.to_numeric(winddata['WindAvg'], errors='coerce')

may_12 = winddata['2016-5-12 10:00':'2016-5-12 19:00']

#create figure and axes
fig, ax = plt.subplots(2,1)
pd.plotting.register_matplotlib_converters()
ax[0].plot(may_12.index, may_12['WindAvg'], color='g', marker='v', linestyle='--')
ax[0].set_ylabel('Wind speed, m/s')
ax[1].plot(may_12.index, may_12['DirectionAvg'], color='r', marker='v', linestyle='--' )
ax[1].set_ylabel('Wind direction')
ax[1].set_xlabel('Date')
plt.show()




