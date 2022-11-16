# evn-smartmeter

#### A python library for fetching data from the EVN smart meter API

## Usage

```python
from src.smartmeter import Smartmeter

# Authentication is automatically performed when
sc = Smartmeter('USERNAME', 'PASSWORD')

# Get a list of all metering points
sc.get_all_metering_points()

```