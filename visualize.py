from fastparquet import write, ParquetFile
import pandas as pd

station = '3'

# load wind data file from local disk
winddata = ParquetFile('./WindData/spot{}'.format(station)).to_pandas()

print(winddata.head())