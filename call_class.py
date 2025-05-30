# -*- coding: utf-8 -*-
"""
@author: Sonia Rodríguez
"""

#   class CALL models a request-type object based on the data received 
# from the Visual Crossing Weather Current Conditions API.
# Its main purpose is to enable the building of a function which returns a 
# selection of meteorogical parameters provided by the API as a DataFrame 
# object, so the information can be directly integrated in a PV module.
# However, class methods allow the user to manage data in other multiple ways: 
# - A text-formated response of a single request can be printed or written in a
#   .csv file.  (see ... methods)
# - The construction of a database containing a set of multiple request
#   responses can be carried.


import os
import requests
import csv
import math
import ephem
from datetime import datetime, time, timedelta
import pandas as pd
import pickle


class call:
    # ===== Constructor method ===== 
    # INPUTS:
    #   pkl : the PKL file where each row/measurement will be written upon 
    #         execution if the user's aim is to build a dataset by 
    #   lat : latitude of the location, in degrees
    #   lon : longitude of the location, in degrees
    #   UTC : UTC timezone offset of the location (difference from UTC time)
    #   api_key : API KEY from VC
    # PURPOSE:
    # Initializes the class atributes related to an specific location and timezone.
    # Information is obtained from two different API calls: a Visual Crossing 
    # Weather Current Conditions API request and a geocoder.maps API request.
    
    def __init__(self, pkl, lat, lon, UTC, api_key):
        # Input atributes
        self.filename = pkl   
        self.key = api_key
        self.lat = lat
        self.lon = lon
        # Address for making a request to the Geocoder
        self.gcurl = f'https://geocode.maps.co/reverse?lat={self.lat}&lon={self.lon}'
        # Precise description of the location, obtained via the geocoder
        self.location = self.get_loc()
        # Location based on latitude and longitude, formatted for inclusion in the request
        self.flocation = str(self.lat)+","+str(self.lon)
        # Time change relative to UTC, in hours
        self.timezoneoffset = UTC
        
        # Defaults
        self.iturria = 'Visual Crossing Weather'
        # Flag for response value verification (initialization)
        self.none_flag = False


        # Address for making a request to the Visual Crossing API
        # Parameters in the base unit system
        self.vcurl = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{self.flocation}?unitGroup=base&include=current&key={self.key}&contentType=json&elements=%2Belevation'
        # API call
        self.deitu()

        # Weather parameters collection
        # Weather description
        self.eg_deskr = self.params['currentConditions']['conditions']
        # YYYY-MM-DD formated date of the request
        self.data = self.params['days'][0]['datetime']
        # Year of the request
        self.urtea = int(self.data.split('-')[0])
        # Month number of the request
        self.hilabetea = int(self.data.split('-')[1])
        # Day of the month of the request
        self.eguna = int(self.data.split('-')[2])
        # Time in ISO 8061 system (standard 24-hour range), in HH:MM:SS format
        self.ordua_ISO = self.params['currentConditions']['datetime'] 
        # Hour (between 0 and 24) of the request
        self.ordua = int(self.ordua_ISO.split(':')[0])
        # Minute of the request
        self.minutua = int(self.ordua_ISO.split(':')[1])
        # YYYY-MM-DDTHH:MM:SS formated timestamp          
        self.timestamp = (str(self.urtea) + "-" + str(self.hilabetea) + "-" + \
                          str(self.eguna) + "T" + str(self.ordua) + ":" + str(self.minutua) + ":" + "00")
        # Initialization of the timestamp of the first request in the database
        # (in case that the database is built)
        self.begintimestamp = self.timestamp
        # Initialization of the timestamp of the last request in the database
        # (in case that the database is built)
        self.endtimestamp = self.timestamp
        # Temperature, in Kelvin degrees
        self.tenpk = self.params['currentConditions']['temp']
        # Temperature (Tdry), in Celsius degrees
        self.tenpc = float(self.params['currentConditions']['temp']) - 273.15
        # Precipitation (PrecipAccum), in milimeters
        self.euria = self.params['currentConditions']['precip']
        # Clouds (%)
        self.hodeiak = self.params['currentConditions']['cloudcover']
        # Wind speed (Wspd), in meters per second
        self.haizeab = self.params['currentConditions']['windspeed']
        # Wind direction (Wdir), in degrees
        self.haizenor = self.params['currentConditions']['winddir']
        # Wind gusts, in meters per second
        self.haizebol = self.params['currentConditions']['windgust']
        # Relative Humidity (RH%)
        self.hezetasuna = self.params['currentConditions']['humidity']
        # Pressure (Pres), in hectopascals <==> milibars
        self.presioa = self.params['currentConditions']['pressure']
        # Altitude, in meters
        self.elevation = self.params['elevation']
        # Global Horizontal Irradiance (GHI), in Watts per square meters
        self.ghi = self.params['currentConditions']['solarradiation']
        # Initialization of the Direct Normal Irradiance (DNI) and Diffuse
        # Horizontal Irradiance (DHI) with a default value
        self.dni = 9999.99
        self.dhi = 9999.99  
        
        # Initialization of the DataFrames of the database
        self.sortu_goiburu_df()   
        self.sortu_datu_df()
        
        
    # Returns and saves as class atributes detailed information about the 
    # location, provided by geocode.maps's geocoding API 
    def get_loc(self):
        # request
        response = requests.get(self.gcurl)
        if response.status_code == 200:
            # Parse data in JSON format
            location_data = response.json()
            address = location_data.get('address', 'Ez da helbidea aurkitu')
            csp_keys = ['amenity', 'town', 'province', 'state']
            country_keys = ['country', 'country_code']
            self.CSP = self.format_address(location_data['address'], csp_keys)
            self.country = self.format_address(location_data['address'], country_keys)
            return (location_data.get('display_name'))
        else:
            errormsj = f'Error: {response.status_code}'
            return (errormsj)
   
    
    # Returns a formatted string containing list elements 
    # selected based on their corresponding key elements.    
    def format_address(self, data, keys):
        return ", ".join([data[key] for key in keys if key in data and data[key]])

   
    # Visual Crossing Weather API request
    def deitu(self):  
        erantzuna = requests.get(self.vcurl)
        if erantzuna.status_code == 200:
            self.params = erantzuna.json()
        else:
            print("ERROR: the request was not made correctly.")
    
    
    # Creates a header DataFrame containing common information 
    # for the entire database or a single measurement. 
    # Includes data related to location and timestamp.
    def sortu_goiburu_df(self):
        # In case that self.filename atribute is not empty, and if the file doesn't exist,
        # a new header DataFrame is written with the first (or unique) requested information
        if not os.path.exists(self.filename):
            self.gzut = ['City,State or Province' , 'Country', 'Latitude(deg N+)' ,
                         'Longitude(deg E+)' , 'Elevation(m)' , 'Time Zone(E+)' , 
                         'Begin Time(yyyy-mm-ddThh:mm)' , 
                         'End Time(yyyy-mm-ddThh:mm)' , 'Data Source']
            
            self.gil = [[self.CSP, self.country, self.lat, self.lon, self.elevation, self.timezoneoffset, 
                        self.begintimestamp[:-3], self.endtimestamp[:-3] , self.iturria]]
            self.goiburu_df = pd.DataFrame(self.gil, columns=self.gzut)
            return
        # If self.filename named file already exists, its header is loaded as a DataFrame
        with open(self.filename, 'rb') as fitx:
            try:
                kargatu = pickle.load(fitx)  
                goiburua = kargatu['Goiburua'] 
                datuak = kargatu['Datuak']      
                # Update of the self.endtimestamp parameter of the header with 
                # the current request timestamp
                self.endtimestamp = self.timestamp
                goiburua['End Time(yyyy-mm-ddThh:mm)'] = self.endtimestamp[:-3]               
                self.goiburu_df = goiburua   
            except EOFError:
                self.gzut = ['City,State or Province' , 'Country', 'Latitude(deg N+)' ,
                            'Longitude(deg E+)' , 'Elevation(m)' , 'Time Zone(E+)' , 
                            'Begin Time(yyyy-mm-ddThh:mm)' , 
                            'End Time(yyyy-mm-ddThh:mm)' , 'Data Source']
                self.gil = [[self.params['address'], self.params['resolvedAddress'].split(',')[-1], 
                           self.lat, self.lon, self.elevation, self.timezoneoffset, 
                           self.begintimestamp[:-3], self.endtimestamp[:-3], self.iturria]]
                self.goiburu_df = pd.DataFrame(self.gil, columns=self.gzut)
        
        
        

    # Creates an empty DataFrame with the corresponding columns. 
    # It will contain information of the measurements obtained from each request.
    # If the VC pickle file is empty or does not exist, it means this is the 
    # first call to the database or that an only request has been made.
    # If the database has already been initialized, load the previously stored 
    # data from the VC file into the current DataFrame.
    # Then, add the data from the current request and apply the necessary 
    # updates to the file.
    # self.zutabeak: a list atribute containing column names of the DataFrame
    # self.ilarak: a list atribute containing the rows/measurements existing in
    #              the database before making this request (it will be empty if
    #              no database exists)
    # self.deia_index: Represents the current request number (index).
    def sortu_datu_df(self):
        # If it does not exist, an empty data DataFrame is created, just by 
        # defining the columns.
        if not os.path.exists(self.filename):
            self.zutabeak = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'GHI(W/m2)',
                             'DNI(W/m2)', 'DHI(W/m2)', 'Tdry(deg C)', 'RH(%)',
                             'Wspd(m/s)', 'Wdir(deg)', 'Pres(mBar)', 'PrecipAccum(mm)']
            self.ilarak = []
            self.deia_index = 0
            self.datu_df = pd.DataFrame(self.ilarak, columns=self.zutabeak)
            return
        # If the database exists, load in a DataFrame structure rows containing 
        # measurements recorded prior to the current request.
        with open(self.filename, 'rb') as fitx:
            try:
                data = pickle.load(fitx)  
                goiburua = data['Goiburua'] 
                datuak = data['Datuak']      
                self.zutabeak = datuak.columns.tolist()
                self.ilarak = datuak.values.tolist()
                self.deia_index = len(self.ilarak)
            except EOFError:
                self.zutabeak = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'GHI(W/m2)',
                                 'DNI(W/m2)', 'DHI(W/m2)', 'Tdry(deg C)', 'RH(%)',
                                 'Wspd(m/s)', 'Wdir(deg)', 'Pres(mBar)', 'PrecipAccum(mm)']
                self.ilarak = []
                self.deia_index = 0
        self.datu_df = pd.DataFrame(self.ilarak, columns=self.zutabeak)


    
    # Inclusion of new data from the current request in the DataFrame
    def df_eguneratu(self):        
        ilaraberri = [ str(self.urtea), str(self.hilabetea), 
                        str(self.eguna), str(self.ordua), 
                        str(self.minutua), 
                        self.ghi, self.dni, self.dhi, self.tenpc, 
                        self.hezetasuna, self.haizeab, self.haizenor,
                        self.presioa, self.euria ]
        
        self.none_flag = any(element is None for element in ilaraberri)       
        if self.none_flag == False:    
            self.ilarak.append(ilaraberri)
        else:
            self.ilarak.append([9999.99] * 14)        
        self.datu_df.loc[self.deia_index] = self.ilarak[self.deia_index]
        
        
    
    # Converts hour angle to HH:MM:SS format
    def graduetatik_ordu_formatora(self, graduak): 
        abs_graduak = abs(graduak)    
        orduak = int(abs_graduak// 15) #h.h daukagu hemen, orain HH:MM:SS.S-ra
        minutuak = int((abs_graduak % 15) * 4)    
        segunduak = (((abs_graduak % 15) * 4) - minutuak) * 60    
        ordu_formateatuta = f"{orduak:02}:{minutuak:02}:{segunduak:04.1f}"
        if graduak < 0:
            ordu_formateatuta = f"-{ordu_formateatuta}"    
        return ordu_formateatuta

    
    # Converts HH,MM,SS (numeric values) to decimal hours (values going from 0 to 24)
    def orduak_deformateatu(self, HH, MM, SS):
        ordu_hamartarrak = HH + MM / 60 + SS / 3600
        return ordu_hamartarrak
        
        
    # Write a double DataFrame structure, consisting on a header and measurements
    # in a self.filename .pkl file. If the file already exists, it will be overwritten    
    def df_to_pkl(self):
        with open(self.filename, 'wb') as f:
            pickle.dump({'Goiburua': self.goiburu_df, 'Datuak': self.datu_df}, f)
         
            
    # Write the information of a .pkl file on an equally named .csv file 
    def pkl_to_csv(self):
        with open(self.filename, 'rb') as f:
            Kargatu = pickle.load(f)
        csv_file = self.filename.replace("pkl", "csv")
        if isinstance(Kargatu, pd.DataFrame):
            Kargatu.to_csv(csv_file, index=False)
        elif isinstance(Kargatu, dict): 
            with open(csv_file, 'w', newline='') as f:
                for key, df in Kargatu.items():
                    df.to_csv(f, index=False)
                    f.write("\n")  
        else:
            raise ValueError("ERROR: there is no DataFrame in the pkl file.")  
            
            
    # Returns a DataFrame containing all the measurements in the database
    def get_datu_df(self):
        self.datu_df = self.datu_df.apply(pd.to_numeric, errors='ignore')
        print(self.datu_df)
        return self.datu_df


    # Returns a DataFrame containing the measurements of the current request
    def get_deiko_datu_df(self):
        return self.datu_df.iloc[self.deia_index]
    

    
    # Print weather parameters of the current request.
    def print_deia(self): 
        print(f"The weather data for {self.lat}°,{self.lon}° location at {self.data} {self.ordua_ISO} is: ")
        print(f" ")
        print(f"- Location address: {self.location}")
        print(f"- Tenperature: {str(self.tenpk)}K")
        print(f"- Weather conditions: {self.eg_deskr}")
        print(f"- Pressure: {str(self.presioa)}hPa")
        print(f"- Relative humidity: %{str(self.hezetasuna)}")
        print(f"- Wind speed: {str(self.haizeab)}m/s")
        print(f"- Wind direction: {str(self.haizenor)}°")
        print(f"- Wind gusts: {str(self.haizebol)}m/s")
        print(f"- Precipitation: {str(self.euria)} mm")
        print(f"- Clouds: %{str(self.hodeiak)}")
        print(f"- Global Horizontal Irradiance (GHI): {str(self.ghi)}W/m^2")
        print(f"- Direct Normal Irradiance (DNI): {str(self.dni)}W/m^2")
        print(f"- Diffuse Horizontal Irradiance (DHI): {str(self.dhi)}W/m^2")
        print(f"- Solar time, in hours: {self.eg_ordua}")
        print(f"- UTC timezone offset, in hours: {self.timezoneoffset}")


    # Write the parameters of the current request to a CSV file (fitxategia)
    def csv_deia(self, fitxategia):  
        idatzi = [
            [],
            [f"The weather data for {self.lat}°,{self.lon}° location at {self.data} {self.ordua_ISO} is: "],
            [],
            [f"Location address: {self.location}"],
            [f"Tenperature: {str(self.tenpk)}K"],
            [f"Weather conditions: {self.eg_deskr}"],
            [f"Pressure: {str(self.presioa)}hPa"],
            [f"Relative humidity: %{str(self.hezetasuna)}"],
            [f"Wind speed: {str(self.haizeab)}m/s"],
            [f"Wind direction: {str(self.haizenor)}°"],
            [f"Wind gusts: {str(self.haizebol)}m/s"],
            [f"Precipitation: {str(self.euria)} mm"],
            [f"Clouds: %{str(self.hodeiak)}"],
            [f"Global Horizontal Irradiance (GHI): {str(self.ghi)}W/m^2"],
            [f"Direct Normal Irradiance (DNI): {str(self.dni)}W/m^2"],
            [f"Diffuse Horizontal Irradiance (DHI): {str(self.dhi)}W/m^2"],
            [f"Solar time, in hours: {self.eg_ordua}"],
            [f"UTC timezone offset, in hours: {self.timezoneoffset}"],
        ]
        with open(fitxategia, mode='w', newline='') as fitx:
            idatzi_csv = csv.writer(
                fitx, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            idatzi_csv.writerows(idatzi)
