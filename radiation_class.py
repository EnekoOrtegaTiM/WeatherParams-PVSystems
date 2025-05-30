# -*- coding: utf-8 -*-
"""
@author: Sonia Rodríguez
"""

# The RADIATION class is a subclass of the CALL class.
# It inherits the attributes and utilities of the CALL class.
# Additionally, it expands its functionality by incorporating radiation 
# parameter calculations in order to get the values of the DHI and DNI attributes.


import os
import csv
import requests
import math
from datetime import datetime

if __name__ == "Programak.call_class":
    import Programak.call_class as cc_mod
else:
    import call_class as cc_mod


class radiation(cc_mod.call):
    # ===== Constructor method ===== 
    # INPUTS:
    #   pkl : the PKL file where each row/measurement will be written upon 
    #         execution if the user's aim is to build a dataset by 
    #   lat : latitude of the location, in degrees
    #   lon : longitude of the location, in degrees
    #   UTC : UTC timezone offset of the location (difference from UTC time)
    #   api_key : API KEY from VC
    # PURPOSE:
    # (Inherited from the superclass)   
    # Initializes the class atributes related to an specific location and timezone.
    # Information is obtained from two different API calls: a Visual Crossing 
    # Weather Current Conditions API request and a geocoder.maps API request
    # (New)
    # Does the calculations of vaious radiation parameters and keeps them as attributes 
        
    def __init__(self, pkl, lat, lon, UTC, api_key):
        super().__init__(pkl, lat, lon, UTC, api_key)

        if self.none_flag == False:
            # Latitude, in radians
            self.lat_rad = self.gradu_to_rad(self.lat)
            # Extraterrestrial radiation, in W/m^2
            self.Bo = 1367 
            # Day number of the year (out of 365/366)
            self.urteko_egun_zbk = self.urteko_eguna()
            # Solar declination based on the day, in degrees
            self.deklinazio = 23.45*math.sin(2*math.pi/365*(self.urteko_egun_zbk+284.))
            # Solar declination based on the day, in radians
            self.deklinazio_rad = self.gradu_to_rad(self.deklinazio)
            # Distance between the Sun and the Earth based on the day
            self.eszentrizitatea = 1+0.033*math.cos(math.pi*2*self.urteko_egun_zbk/365)
            # Sunrise in solar hours
            self.egunsentia = ( - \
                math.acos(-math.tan(self.deklinazio_rad) * math.tan(self.lat_rad))*12/math.pi)
            # Sunrise in solar hours converted to radians
            self.egunsentia_rad = self.ordu_to_rad(self.egunsentia)
            
            # Solar time, in hours going from -12 to 12
            self.eg_ordua = self.eguzki_ordua() 
            # Solar time, in radians
            self.eg_ordua_h_rad = self.ordu_to_rad(self.eg_ordua)
            # Cenital distance
            self.dist_zen = math.sin(self.deklinazio_rad) * \
                                 math.sin(self.lat_rad) + \
                                     math.cos(self.deklinazio_rad) * \
                                     math.cos(self.lat_rad) * \
                                         math.cos(self.eg_ordua_h_rad)  
            # Solar radiation passing through the atmosphere.
            self.Boh = self.Bo*self.eszentrizitatea*self.dist_zen
            # Clearness index
            self.KT = self.ghi/self.Boh  
            if self.KT < 0.2:
                self.KD = 0.996 + 0.00424*self.KT - 0.586*self.KT**2
            elif 0.2 < self.KT < 0.7:
                self.KD = 1.11 - 0.203*self.KT - 2.52 * \
                    self.KT**2 + 0.617*self.KT** \
                        3 + 1.603*self.KT**3
            elif self.KT > 0.7:
                self.KD = -0.0169 - 0.99*self.KT + 1.63*self.KT**2
    
    
            # Diffuse Horizontal Irradiance, in W/m^2
            self.dhi = self.ghi * self.KD
            # Direct Normal Irradiance, in W/m^2
            self.dni = self.ghi - self.dhi

        
    # Superclass inherited method. It adds DNI and DHI values to the current 
    # request DataFrame, enabling call_class to add them to the database
    def df_eguneratu(self):
        super().df_eguneratu()
        
        if self.none_flag == False:
        
            ilaraberri = [ str(self.urtea), str(self.hilabetea), 
                            str(self.eguna), str(self.ordua), 
                            str(self.minutua), 
                            str(round(self.ghi,1)), 
                            str(round(self.dni,1)), \
                                str(round(self.dhi,1)), 
                            str(round(self.tenpc)), 
                            str(self.hezetasuna), str(self.haizeab)+"\t", 
                            str(self.haizenor),
                            str(self.presioa), str(self.euria)+"\t" ]
            
            self.ilarak[self.deia_index] = ilaraberri
                        
    
    
    # Returns the day number of the year for the given date, considering leap years.
    def urteko_eguna(self):
        data = datetime.strptime(self.data, '%Y-%m-%d')
        eguna = data.timetuple().tm_yday
        return (eguna)
    
    

    # Solar time is returned in decimal hours, with values within the range 
    # form -12 to 12 hours (not in HH:MM:SS format).
    def eguzki_ordua(self):
        # Number of days since start of the year
        B = 360/365 * (float(self.urteko_egun_zbk)-81)
        # Equation of Time
        EoT = 9.87*math.sin(2*B)-7.53*math.cos(B)-1.5*math.sin(B)
        # Local Standard Time Meridian 
        LSTM = 15 * self.timezoneoffset
        # Time Correction factor --- 1º every 4 minutes
        TC = 4*(self.lon - LSTM) + EoT
        # Local Time
        LT = self.orduak_deformateatu(int(self.ordua), \
                                      int(self.minutua), 0.0)
        # Local Solar Time in hours, from 0 to 24h
        LST = LT + TC/60   
        # Hour angle in degrees (hour taken from -12 to 12)
        HRA = 15*(LST-12)
        # Hour angle in radians 
        HRA_rad = HRA *math.pi /180
        return(LST-12)


    # Conversion from degrees to radians
    def gradu_to_rad(self, x):
        return (x * math.pi / 180)


    # Conversion from hours to radians
    def ordu_to_rad(self, x):
        return (x * math.pi / 12)
    
    
    # Superclass inherited method
    def print_deia(self):
        super().print_deia()
        if self.none_flag == False:
            self.print_eguzki_lurra_pos()
            self.print_ordua_parametroak()
            self.print_horizontala_erradiazioa()
        else:
            print(f"ERROR: some of the data received in the response is wrong.")
    
    
    
    # Superclass inherited method
    def csv_deia(self, fitxategia):
        super().csv_deia(fitxategia)
        self.csv_eguzki_lurra_pos(fitxategia)
        self.csv_ordua_parametroak(fitxategia)
        self.csv_horizontala_erradiazioa(fitxategia)
        
        
    def print_eguzki_lurra_pos(self):
        print(f"-------------------------------------------------------------------------------")
        print(f"Sun-Earth Position")
        print(f"Latitude : {str(self.lat)}°")
        print(f"Latitude : {str(self.lat_rad)} rad")
        print(f"Day of the Year : {str(self.urteko_egun_zbk)}")
        print(f"Solar Declination : {str(self.deklinazio)}°")
        print(f"Solar Declination : {str(self.deklinazio_rad)} rad")
        print(f"Eccentricity : {str(self.eszentrizitatea)}")
        print(f"Sunrise (solar hours): {str(self.egunsentia)}")
        print(f"-------------------------------------------------------------------------------")
        print(f"Extraterrestrial Solar Radiation (Bo): {str(self.Bo)} W/m^2")



    def print_ordua_parametroak(self):
        print(f"-------------------------------------------------------------------------------")
        print(f"Solar Time (h): {self.eg_ordua}")
        print(f"Solar Time in Radians (w): {self.eg_ordua_h_rad}")
        print(f"Zenith Distance (cos(theta_zs)): {str(self.dist_zen)}")
        print(f"Solar Radiation Passing Through the Atmosphere (Boh(0)): {str(self.Boh)} W/m^2")
        print(f"KT: {str(self.KT)}")
        print(f"KD: {str(self.KD)}")
        print(f"-------------------------------------------------------------------------------")

        
    def print_horizontala_erradiazioa(self):
        print(f"-------------------------------------------------------------------------------")
        print(f"Global Horizontal Irradiance (GHI or Gh(0)): {str(self.ghi)} W/m^2")
        print(f"Direct Normal Solar Irradiance (DNI or Bh(0)): {str(self.dni)} W/m^2")
        print(f"Diffuse Horizontal Irradiance (DHI or Dh(0)): {str(self.dhi)} W/m^2")
        print(f"-------------------------------------------------------------------------------")

        
       
    def csv_eguzki_lurra_pos(self,fitxategia):
        if self.none_flag == False:
            idatzi = [                
                ['-------------------------------------------------------------------------------'],
                [f"Sun-Earth Position"],
                [f"Latitude (phi): {str(self.lat)}°"],
                [f"Latitude (phi): {str(self.lat_rad)} rad"],
                [f"Day of the Year (dn): {str(self.urteko_egun_zbk)}"],
                [f"Solar Declination (delta): {str(self.deklinazio)}°"],
                [f"Solar Declination (delta): {str(self.deklinazio_rad)} rad"],
                [f"Eccentricity (epsilon_0): {str(self.eszentrizitatea)}"],
                [f"Sunrise in Solar Hours (w_s): {str(self.egunsentia)}"],
                [f"Sunrise in Radians (w_s): {str(self.egunsentia_rad)}"],
                ['-------------------------------------------------------------------------------'],
                [f"Extraterrestrial Solar Radiation (Bo): {str(self.Bo)} W/m^2"],

            ]
            
        else:
            idatzi = [f"ERROR: some of the data received in the response is wrong."]
        with open(fitxategia, mode='a', newline='') as fitx:
            idatzi_csv = csv.writer(
                fitx, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            idatzi_csv.writerows(idatzi)
            
            
    # def print_ordua_parametroak(self):
    def csv_ordua_parametroak(self, fitxategia):
        if self.none_flag == False:
            idatzi = [
                ['-------------------------------------------------------------------------------'],
                [f"Solar Time (h): {self.eg_ordua}"],
                [f"Solar Time in Radians (w): {self.eg_ordua_h_rad}"],
                [f"Zenith Distance (cos(theta_zs)): {str(self.dist_zen)}"],
                [f"Solar Radiation Passing Through the Atmosphere (Boh(0)): {str(self.Boh)} W/m^2"],
                [f"KT: {str(self.KT)}"],
                [f"KD: {str(self.KD)}"],
            ]

        else:
            idatzi = [f"ERROR: some of the data received in the response is wrong."]
        with open(fitxategia, mode='a', newline='') as fitx:
            idatzi_csv = csv.writer(
                fitx, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            idatzi_csv.writerows(idatzi)



    def csv_horizontala_erradiazioa(self, fitxategia):
        if self.none_flag == False:
            idatzi = [
                ['-------------------------------------------------------------------------------'],
                [f"Global Horizontal Solar Radiation on Earth (GHI or Gh(0), Global Horizontal Irradiance): {str(self.ghi)} W/m^2"],
                [f"Direct Normal Solar Radiation (DNI or Bh(0), Direct Normal Irradiance): {str(self.dni)} W/m^2"],
                [f"Diffuse Horizontal Solar Radiation (DHI or Dh(0), Diffuse Horizontal Irradiance): {str(self.dhi)} W/m^2"],
                ['-------------------------------------------------------------------------------'],
            ]

        else:
            idatzi = [f"ERROR: some of the data received in the response is wrong."]
        with open(fitxategia, mode='a', newline='') as fitx:
            idatzi_csv = csv.writer(
                fitx, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            idatzi_csv.writerows(idatzi)
