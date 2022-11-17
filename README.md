# evn-smartmeter

#### A python library for fetching data from the EVN smart meter API

## Usage

```python
from src.smartmeter import Smartmeter

sc = Smartmeter('USERNAME', 'PASSWORD')

# Get a list of all metering points
metering_points = sc.get_all_metering_points()

for mp in metering_points:
    sc.get_consumption_month(mp['meteringPointId'], 2022, 11)
    sc.get_consumption_day(mp['meteringPointId'], 2022, 11, 16)

```

## TODO

* convert day/month data to a more readable format
* Home Assistant integration