# NDBC Modular Input
Modular Input for [National Data Buoy Center](http://www.ndbc.noaa.gov/) observations

## Installation
- Download this Modular Input (`ndbc.spl`)
- Install the Modular Input
- Configure NDBC Data Inputs: `Settings > Data Inputs > NDBC`
  - Enable the zones that would you like to receive buoy data from
  - Alternatively, create a new data input with your own list of station ids
- Enjoy an ocean breeze of data!

## Marine Data

The NDBC Modular Input fetches data from NOAA's NDBC stations. It uses data available from this URL: `http://www.ndbc.noaa.gov/get_observation_as_xml.php?station={station_id}`

Example of data returned by NDBC station `46025`:
```xml
<observation id="46025" name="Santa Monica Basin - 33NM WSW of Santa Monica, CA" lat="33.749" lon="-119.053">
  <datetime>2016-03-01T05:50:00UTC</datetime>
  <winddir uom="degT">140</winddir>
  <windspeed uom="kt">3.9</windspeed>
  <windgust uom="kt">5.8</windgust>
  <waveht uom="ft">4.3</waveht>
  <domperiod uom="sec">15</domperiod>
  <avgperiod uom="sec">9.3</avgperiod>
  <meanwavedir uom="degT">242</meanwavedir>
  <pressure uom="in" tendency="rising">30.04</pressure>
  <airtemp uom="F">54.1</airtemp>
  <watertemp uom="F">61.5</watertemp>
  <dewpoint uom="F">54.1</dewpoint>
</observation>
```

The sourcetype is `ndbc` and each input has its own `source` which is the name of the input.

## Developers

To build the NDBC modular input from source, clone this repository and run this command from the top-level folder:
```python setup.py dist```
