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


#%% GSOD Scraper Tool

# https://github.com/tagomatech/ETL/tree/master/gsod

from utilities import gsod_scraper


gsod = gsod_scraper.GSOD()

last_ten_alb = gsod.get_data(station='725180-14735', start_year=2011, end=2021)

last_ten_alb.to_csv('last_ten_alb.csv')