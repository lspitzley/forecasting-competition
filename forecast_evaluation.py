# -*- coding: utf-8 -*-
"""
Script to evaluate forecasts.

First part is integrity checks

@author: Lee Spitzley
"""

#%% imports
import os
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn import metrics
import matplotlib.pyplot as plt



#%% globals
forecast_dir = 'forecasts/'
column_names = ['fc_date', 'fc_name', 'fc_var', 'fc_value']

#%% create error messages
class MissingColumnError(Exception):
    pass


#%% variable name checks/fixes

def fix_prcp(fc_var_col):
    """
    Take the fc_var column and 
    fix common mistakes in P_PRCP

    Parameters
    ----------
    fc_var_col : pandas.Series()
        The values from the fc_var column.

    Returns
    -------
    pandas.Series().

    """

    fc_var_col.replace('PRCP', 'P_PRCP', inplace=True)
    fc_var_col.replace('I_PRCP', 'P_PRCP', inplace=True)

    return fc_var_col

#%% load in forecast files
forecast_files = [s for s in os.listdir(forecast_dir) if s.lower().endswith('.csv')]

raw_dfs = []
df_all = pd.DataFrame(columns=column_names)
for file in forecast_files:
    # print(file)
    try:
        df = pd.read_csv(forecast_dir + file, infer_datetime_format=True)
        
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
        # df['fc_date'] = df['fc_date'].apply(fix_date)
        
        # check the values in fc_var
        df['fc_var'] = fix_prcp(df['fc_var'])
        
        # make values numeric
        df['fc_value'] = df['fc_value'].apply(pd.to_numeric, errors='coerce')
        
        # drop missing values
        df.dropna(subset=column_names, inplace=True)
            
        
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
last_ten_alb = pd.read_csv('last_ten_alb.csv')

# set YEARMODA (Year-month-day) to datetime format
last_ten_alb['YEARMODA'] = pd.to_datetime(last_ten_alb['YEARMODA'])
print("Most recent date in data:", last_ten_alb['YEARMODA'].max())

eval_start = datetime.strptime('2021-09-29', "%Y-%m-%d")

# TODO restrict overall data to eval start or later

#%% get relevant columns into merged dataframe

merged = df_all.merge(last_ten_alb, left_on='fc_date', right_on='YEARMODA')


#%% run evaluation on 

result_table = pd.DataFrame(columns=['fc_name', 'fpr','tpr','auc', 
                                     'log_loss', 'precision', 'recall',
                                     'accuracy', 'f1_score', 'min_RMSE', 
                                     'max_RMSE'])

unique_forecasts = merged['fc_name'].unique()

for forecast in unique_forecasts:
    print(forecast)
    
    # get count of forecasts for grading purposes (probably could be cleaner)
    
    single_forecast = merged.loc[(merged['fc_name'] == forecast)]
    n_days = len(single_forecast['fc_date'].unique())
    
    
    yproba = single_forecast.loc[(single_forecast['fc_var'] == 'P_PRCP'), 'fc_value']
    yclass = np.where(yproba >= 0.5, 1, 0)
    yobsrv = single_forecast.loc[(single_forecast['fc_var'] == 'P_PRCP'), 'I_PRCP']
    
    # auc information
    fpr, tpr, _ = metrics.roc_curve(yobsrv,  yproba)
    auc = metrics.roc_auc_score(yobsrv, yproba)
    
    # log loss
    log_loss = metrics.log_loss(yobsrv, yproba)
    
    # cofusion matrix stats
    precision = metrics.precision_score(yobsrv, yclass, zero_division=0)
    recall = metrics.recall_score(yobsrv, yclass)
    accuracy = metrics.accuracy_score(yobsrv, yclass)
    fscore = metrics.f1_score(yobsrv, yclass)
    
    
    # get RMSE for min & max
    min_pred = single_forecast.loc[(single_forecast['fc_var'] == 'MIN'), 'fc_value']
    min_obsv = single_forecast.loc[(single_forecast['fc_var'] == 'MIN'), 'MIN']
    max_pred = single_forecast.loc[(single_forecast['fc_var'] == 'MAX'), 'fc_value']
    max_obsv = single_forecast.loc[(single_forecast['fc_var'] == 'MAX'), 'MAX']
    
    min_error = metrics.mean_squared_error(min_obsv, min_pred, squared=False)
    max_error = metrics.mean_squared_error(max_obsv, max_pred, squared=False)
    
    result_table = result_table.append({'fc_name': forecast,
                                    'fpr':fpr, 
                                    'tpr':tpr, 
                                    'auc':auc,
                                    'log_loss': log_loss,
                                    'precision': precision,
                                    'recall': recall,
                                    'accuracy': accuracy,
                                    'f1_score': fscore,
                                    'min_RMSE': min_error,
                                    'max_RMSE': max_error,
                                    'n_days': n_days}, ignore_index=True)


#%% 

as_of = datetime.today().strftime("%Y-%m-%d")
result_table.to_csv('output/scores_as_of_' + as_of + '.csv')


#%% plot roc

fig = plt.figure(figsize=(40,35))

for i in result_table.index:
    plt.plot(result_table.loc[i]['fpr'], 
             result_table.loc[i]['tpr'], 
             label="{}, AUC={:.3f}".format(result_table.loc[i]['fc_name'], result_table.loc[i]['auc']))
    
plt.plot([0,1], [0,1], color='orange', linestyle='--')

plt.xticks(np.arange(0.0, 1.1, step=0.1))
plt.xlabel("False Positive Rate", fontsize=15)

plt.yticks(np.arange(0.0, 1.1, step=0.1))
plt.ylabel("True Positive Rate", fontsize=15)

plt.title('ROC Curve Analysis', fontweight='bold', fontsize=15)
plt.legend(prop={'size':13}, loc='lower right')

plt.show()

