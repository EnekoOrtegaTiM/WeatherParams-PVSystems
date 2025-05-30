# -*- coding: utf-8 -*-
"""
@author: Sonia Rodríguez
"""
# CURRENT TIME REQUESTS APLICATIONS EXAMPLE SCRIPT

if __name__ == "Programak.radiation_class":
    import Programak.radiation_class as rc_mod
else:
    import radiation_class as rc_mod


# ===== FUNCTIONS =====

def create_call(pkl, lat, lon, UTC, api_key):
    #   pkl : the PKL file where each row/measurement will be written upon 
    #         execution if the user's aim is to build a dataset by 
    #   lat : latitude of the location, in degrees
    #   lon : longitude of the location, in degrees
    #   UTC : UTC timezone offset of the location (difference from UTC time)
    #   api_key : API KEY from VC
    eu = rc_mod.radiation(pkl, lat, lon, UTC, api_key)
    eu.df_eguneratu()
    return eu    


def fill_database(eu):
    eu.df_to_pkl()
    eu.pkl_to_csv()


def print_call(eu):
    eu.print_deia()
    
    
def csv_call(eu,fitxategia):
    eu.csv_deia(fitxategia)
       
 
def load_call_df(eu):
    return eu.get_deiko_datu_df()
    

def load_full_df(eu):    
    return eu.get_datu_df()


def weather_data(lat, lon, UTC, api_key):
    call = rc_mod.radiation("", lat, lon, UTC, api_key)
    call.df_eguneratu()
    call_df = call.get_datu_df()
    return(call_df)


# ===== MAIN =====
path = 'C:/Users/34678/Desktop/UPV/TFG Ingenieritza'
database_file = path + '/database_name.pkl'
current_call_file = path + '/call_name.csv'
vc_key = 'XXXXXXXXXXXXXXXXXXXXXXXXX'
latitude = 43.3314059  # Leioa, University of the Basque Country 
longitude = -2.9706058
UTC = 2

# Creation of an instance of the radiation subclass by making a request (
# either building the object from scratch or updating a previous one)
call = create_call(database_file, latitude, longitude, UTC, vc_key)

# Filling of the database (either create it from scratch or continue with the existing one)
fill_database(call)

# Print the response of a single (the current) request
print_call(call)

# Save the text-formatted response of a single (the current) request in a CSV file
csv_call(call, current_call_file)

# Creation of a DataFrame containing the response of a single (the current) request
call_df = load_call_df(call)

# Load and update a DataFrame with all the requests made in the database
database_df = load_full_df(call)


# Creation of a DataFrame containig the response of a single (the current) request
# Same as load_call_df, but with different inputs. This function can be used
# independently, same inputs as create_call
call_df = weather_data(latitude, longitude, UTC, vc_key)