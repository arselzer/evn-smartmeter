# evn-smartmeter

#### A python library for fetching data from the EVN smart meter API

## Usage

```python
from src.smartmeter import Smartmeter
import datetime

sc = Smartmeter('USERNAME', 'PASSWORD')

# Get a list of all metering points
metering_points = sc.get_all_metering_points()

for mp in metering_points:
    sc.get_consumption_month(mp['meteringPointId'], 2022, 11)
    
    
    sc.get_consumption_day(mp['meteringPointId'],
                           datetime.date.today() - datetime.timedelta(days=1))

    # [QuarterHourlyConsumption(metered_value=0.044, estimated_value=None, grid_usage_leftover_values=None, self_coverage_values=None, joint_tenancy_proportion_values=None, metered_peak_demand=0.176, estimated_peak_demand=None, start=datetime.datetime(2022, 11, 16, 0, 0), end=datetime.datetime(2022, 11, 16, 0, 15)),
    # QuarterHourlyConsumption(metered_value=0.107, estimated_value=None, grid_usage_leftover_values=None, self_coverage_values=None, joint_tenancy_proportion_values=None, metered_peak_demand=0.428, estimated_peak_demand=None, start=datetime.datetime(2022, 11, 16, 0, 15), end=datetime.datetime(2022, 11, 16, 0, 30)),
    # ...

```

## TODO

* Home Assistant integration