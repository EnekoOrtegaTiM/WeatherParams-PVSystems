# WeatherParams-PVSystems
Python function to obtain weather parameters using Visual Crossing API without additional sensors


## Repository description

-	CALL_CLASS and RADIATION_CLASS are two class scripts, which account for the creation of 'call' class objects and 'radiation' class objects. The methods defined within them are responsible for handling API requests, managing response data, and formatting it in different ways. 

-  	WEATHER_DATA is a function that takes the latitude ('lat'), longitude ('lon'), and UTC timezone offset ('UTC') values for a given location, along with a Visual Crossing Weather user API key ('api_key'). It returns a DataFrame containing a selection of meteorological parameters measured in real time, provided by the "Current Conditions Weather API".

-	USER_PROGRAM is a executable script which includes an example of the applications of the software tool beyond its primary function in WEATHER_DATA, whose usage is detailed below.
  
-	MAIN script example on the use of WEATHER_DATA

## Dependencies
from weather_data_function import weather_data

Required libraries: pandas, pickle, datetime, csv, math', requests, os

## Input arguments
-  	lat : latitude of the location, in degrees
-  	lon : longitude of the location, in degrees
-  	UTC : UTC offset of the location (difference from UTC time), in hours
-  	api_key : API KEY from VC

api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXX'
lat = 43.3314059  # Leioa, University of the Basque Country
lon = -2.9706058
UTC = 2

## Usage
```python
call_df = weather_data(lat, lon, UTC, api_key)
```
OUTPUT example:
```python
[1 rows x 14 columns]
   Year  Month  Day  Hour  Minute  GHI(W/m2)   DNI(W/m2)   DHI(W/m2)  Tdry(deg C)  RH(%)  Wspd(m/s)  Wdir(deg)  Pres(mBar)  PrecipAccum(mm)
0  2025      5   23    12       0      440.0  103.834708  336.165292        18.15   66.3        4.2      310.0      1023.0              0.0
```

## Citation

If you use this project in your research, please cite:

```bibtex
@inproceedings{rodriguez2025software,
  title={Software tool for weather parameters acquisition during photovoltaic systems monitoring},
  author={Rodriguez, Sonia Maria and Chicote, Beatriz and Ortega, Eneko and Aranguren, Gerardo and Jimeno, Juan Carlos},
  booktitle={2025 IEEE 53rd Photovoltaic Specialists Conference (PVSC)},
  pages={0621--0626},
  year={2025},
  organization={IEEE}
}
```

