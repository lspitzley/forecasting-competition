# -*- coding: utf-8 -*-
"""
Script to evaluate forecasts.

First part is integrity checks

@author: Lee Spitzley
"""

#%% imports
import os
import re
import pandas as pd
from sklearn import metrics


#%% globals
forecast_dir = 'forecasts/'
column_names = ['fc_date', 'fc_name', 'fc_var', 'fc_value']

#%% create error messages
class MissingColumnError(Exception):
    pass

#%% load in forecast files
forecast_files = [s for s in os.listdir(forecast_dir) if s.lower().endswith('.csv')]

raw_dfs = []
df_all = pd.DataFrame(columns=column_names)
for file in forecast_files:
    # print(file)
    try:
        df = pd.read_csv(forecast_dir + file)
        
        # fix common misspellings
        if 'fc.date' in df.columns:
            df.rename(columns={"fc.date": 'fc_date'}, inplace=True)
            
        if 'fc_values' in df.columns:
            df.rename(columns={"fc_values": 'fc_value'}, inplace=True)
        # strip any other column except those needed
        df = df.loc[:, column_names]
        # check that all are there
        if len(df.columns) != 4:
            raise MissingColumnError()
            
        df['fc_date'] =pd.to_datetime(df['fc_date'])
            
        
        # if all checks pass, add to list
        df_all = df_all.append(df, ignore_index=True)
    except KeyError:
        print("Invalid column names in", file, "Columns must be", column_names)
        print("Included names were", list(df))
        
    except MissingColumnError:
        print("dataframe missing column(s).", file)


#%% clean dataframe
df_all = df_all.drop_duplicates(['fc_date', 'fc_name', 'fc_var'], keep='first')


#%% actual data