# NDBC Add-on
Splunk add-on for [National Data Buoy Center](http://www.ndbc.noaa.gov/) observations

## Installation

Install this add-on the same way you would install any Splunk app:
- automatically from [SplunkBase](https://splunkbase.splunk.com/app/3077/) through *Browse more apps*
- manually: download the `ndbc.spl` file and install it in your instance

## Configuration
- Configure NDBC Data Inputs: `Settings > Data Inputs > NDBC`
- Enable the zones that would you like to receive buoy data from
- Alternatively, create a new data input with your own list of station identifiers

## Marine Data

The NDBC add-on fetches data from NOAA's NDBC stations. It uses data available from this URL: `http://www.ndbc.noaa.gov/get_observation_as_xml.php?station={station_id}` and produces JSON documents with sourcetype `ndbc`.

Example of data returned by NDBC station `46025`:
```xml
<observation id="46025" name="Santa Monica Basin - 33NM WSW of Santa Monica, CA" lat="33.749" lon="-119.053">
	<datetime>2016-03-04T20:50:00UTC</datetime>
	<winddir uom="degT">100</winddir>
	<windspeed uom="kt">1.9</windspeed>
	<windgust uom="kt">5.8</windgust>
	<waveht uom="ft">5.9</waveht>
	<domperiod uom="sec">16</domperiod>
	<avgperiod uom="sec">9.5</avgperiod>
	<meanwavedir uom="degT">272</meanwavedir>
	<pressure uom="in" tendency="falling">30.00</pressure>
	<airtemp uom="F">60.4</airtemp>
	<watertemp uom="F">62.4</watertemp>
	<dewpoint uom="F">51.4</dewpoint>
</observation>
```

Example of data produced by the NDBC add-on:
```json
{
    air_temp:  60.4 
    average_period:  9.5 
    datetime:  2016-03-04T20:50:00+00:00 
    dominant_period:  16 
    lat:  33.749 
    lon:  -119.053 
    mean_wave_direction:  272 
    meta: { 
      pressure: { 
        tendency:  falling 
     } 
   } 
    name:  Santa Monica Basin - 33NM WSW of Santa Monica, CA 
    station:  46025 
    units: {
      air_temp:  F 
      average_period:  sec 
      dewpoint:  F 
      dominant_period:  sec 
      mean_wave_direction:  degT 
      pressure:  in 
      water_temp:  F 
      wave_height:  ft 
      wind_direction:  degT 
      wind_gust:  kt 
      wind_speed:  kt 
   } 
    url:  http://www.ndbc.noaa.gov/station_page.php?station=46025 
    water_temp:  62.4 
    wave_height:  5.9 
    wind_direction:  100 
    wind_gust:  5.8 
    wind_speed:  1.9 
}
```

## Developers

To build the NDBC add-on input from source, clone the [github repository](http://github.com/jruaux/ndbc) and run this command from the top-level folder:

```python setup.py dist```
