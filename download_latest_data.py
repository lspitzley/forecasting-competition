#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 21:58:26 2020


Script to download daily historical data from 
the NOAA. 

https://github.com/paulokuong/noaa

https://gettecr.github.io/noaa-api.html

@author: leespitzley
"""

#%% imports

from noaa_sdk import noaa

import requests
import datetime
import numpy as np
import pandas as pd
import os
import sys

#%% globals/arguments
location = '12222'
start_date = '2020-06-01'
end_date = '2020-08-31'
# https://www.ncdc.noaa.gov/cdo-web/token
mytoken = 'cjDBSyJxHNVYtFnEOtvUCFlvYXaDAxsV'



#Use the datetime package to get a year ago today
lastyear = datetime.datetime.now()-datetime.timedelta(days=365)

#Use the same begin and end date for just one day's data. Format for the API request
begin_date = lastyear.strftime("%Y-%m-%d")
end_date = datetime.date.today()

#Location key for the region you are interested in (can be found on NOAA or requested as a different API as well)
locationid = 'FIPS:36' #location id for North Dakota
stationid = 'GHCND:US1NYAB0001'
datasetid = 'GSOD' #datset id for "Daily Summaries"




base_url_data = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'
base_url_stations = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/stations'



#%% download latest data

n = noaa.NOAA()
#alb = n.get_forecasts('12203', 'US', False)

observations = n.get_observations(location, 'US')   


for obs in observations:
    print(obs)

#%%
def get_weather(locationid, datasetid, begin_date, end_date, mytoken, base_url):
    token = {'token': mytoken}

    #passing as string instead of dict because NOAA API does not like percent encoding
    params = 'datasetid='+str(datasetid)+'&'+'stationid='+str(locationid)+'&'+'startdate='+str(begin_date)+'&'+'enddate='+str(end_date)+'&'+'limit=1000'+'&'+'units=standard'
    
    r = requests.get(base_url, params = params, headers=token)
    print("Request status code: "+str(r.status_code))
    print(r.content)
    try:
        #results comes in json form. Convert to dataframe
        df = pd.DataFrame.from_dict(r.json()['results'])
        print(df)
        print("Successfully retrieved "+str(len(df['station'].unique()))+" stations")
        dates = pd.to_datetime(df['date'])
        print("Last date retrieved: "+str(dates.iloc[-1]))

        return df

    #Catch all exceptions for a bad request or missing data
    except:
        print("Error converting weather data to dataframe. Missing data?")
        
        


def get_station_info(locationid, datasetid, mytoken, base_url):
    token = {'token': mytoken}

    #passing as string instead of dict because NOAA API does not like percent encoding
    
    stations = 'locationid='+str(locationid)+'&'+'datasetid='+str(datasetid)+'&'+'units=metric'+'&'+'limit=1000'
    r = requests.get(base_url, headers = token, params=stations)
    print("Request status code: "+str(r.status_code))

    try:
        #results comes in json form. Convert to dataframe
        df = pd.DataFrame.from_dict(r.json()['results'])
        print("Successfully retrieved "+str(len(df['id'].unique()))+" stations")
        
        if df.count().max() >= 1000:
            print('WARNING: Maximum data limit was reached (limit = 1000)')
            print('Consider breaking your request into smaller pieces')
 
        return df
    #Catch all exceptions for a bad request or missing data
    except:
        print("Error converting station data to dataframe. Missing data?")


#%% clean data



#%%
df_weather = get_weather(stationid, datasetid, begin_date, end_date, mytoken, base_url_data)

df_weather.head()

df_stations = get_station_info(locationid, datasetid, mytoken, base_url_stations)

df_stations.head()




#%%
df = df_weather.merge(df_stations, left_on = 'station', right_on = 'id', how='inner')

#Check for missing overlap between station weather info and location info
    
location_ismissing = df_weather[~df_weather['station'].isin(df_stations['id'])]
loc_miss_count = len(location_ismissing['station'].unique())
if loc_miss_count != 0:
    print("Missing location data for "+str(loc_miss_count)+" stations")
else:
    print("Successfully retrieved and combined location data")

df.head()


df.drop('id', inplace=True, axis=1)

df.drop(['maxdate','mindate'],inplace=True,axis=1)

#%% write to file

df.to_csv('weather_'+str(begin_date)+'_noaa.csv', encoding='utf-8', index=False)