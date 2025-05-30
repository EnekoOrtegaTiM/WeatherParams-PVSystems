# -*- coding: utf-8 -*-
#   WEATHER_DATA is a function that takes the latitude ('lat'), longitude ('lon'),
# and UTC timezone offset ('UTC') values for a given location, along with
# a Visual Crossing Weather user API key ('api_key'). It returns a DataFrame 
# containing a selection of meteorological parameters measured in real time,
# provided by the "Current Conditions Weather API".

# ==== DEPENDENCIES ===
if __name__ == "Programak.radiation_class":
    import programak.radiation_class as rc_mod
else:
    import radiation_class as rc_mod

# ==== FUNCTION ===
def weather_data(lat, lon, UTC, api_key):
    call = rc_mod.radiation("", lat, lon, UTC, api_key)
    call.df_eguneratu()
    call_df = call.get_datu_df()
    return(call_df)
