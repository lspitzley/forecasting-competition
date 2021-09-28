# -*- coding: utf-8 -*-
"""
baseline_predictions using python

Adapted from baseline_predictions.R

#######################################
              INSTRUCTIONS
#######################################

Change the value of USERNAME to match 
your university email ID.

Running the script will prompt you for the 
date that you wish to start your forecast.
Hitting return will select tomorrow's date


@author: Lee Spitzley
"""

# change this to match your university email ID
USERNAME = 'mean_prev_seven'


#%% imports
import pandas as pd
from datetime import datetime, timedelta
import forecast_functions

#%% import data
last_ten_alb = pd.read_csv('last_ten_alb.csv')

# set YEARMODA (Year-month-day) to datetime format
last_ten_alb['YEARMODA'] = pd.to_datetime(last_ten_alb['YEARMODA'])
print("Most recent date in data:", last_ten_alb['YEARMODA'].max())


#%% prediction scope
# get date from user to start forecasting
prompt_str = "When should the prediction start? Enter date in YYYY-MM-DD [Enter=tomorrow]: "
prediction_start = input(prompt_str)

# user hits enter, then just give tomorrow's date
if not prediction_start:
    prediction_start = datetime.today() + timedelta(days=1)
    prediction_start = prediction_start.strftime("%Y-%m-%d")
    

# establish important dates
prediction_start = datetime.strptime(prediction_start, "%Y-%m-%d")
start_prev_seven = prediction_start - timedelta(days=7)

# create list of dates to submit for forecast evaluation
eval_dates = pd.date_range(prediction_start, periods=7).tolist()


#%% create training subset
"""
In this example, I am only using the last seven days of data
to create a training set. 

A more sophisticated method would be the use of lagged variables.
For example, sea level pressure (SLP) could be useful in predictions.
You would then include the previous day's pressure in a column (SLP_1)
and you could also go back further (as many days as you would like). 

If using this method, predicting further than one day into the future will 
either require a separate model, or interpolation of the lagged measures
that are empty.
"""



train_dates = pd.date_range(start_prev_seven, periods=7)
train_data = last_ten_alb.loc[last_ten_alb['YEARMODA'].isin(train_dates)]


#%% get average values based on last 7 days
avg_max = train_data['MAX'].mean()
avg_min = train_data['MIN'].mean()
avg_prcp = train_data['I_PRCP'].mean()



#%% create dataframe

# format forecasts
fc_max = forecast_functions.construct_mean_forecast_df(eval_dates, USERNAME, 'MAX', avg_max)
fc_min = forecast_functions.construct_mean_forecast_df(eval_dates, USERNAME, 'MIN', avg_min)
fc_prcp = forecast_functions.construct_mean_forecast_df(eval_dates, USERNAME, 'P_PRCP', avg_prcp)

# define columns
column_names = ['fc_date', 'fc_name', 'fc_var', 'fc_value']
# create empty df
eval_df_base = pd.DataFrame(columns=column_names)


# append forecasts to dataframe
eval_df_base = eval_df_base.append(fc_max, ignore_index=True)
eval_df_base = eval_df_base.append(fc_min, ignore_index=True)
eval_df_base = eval_df_base.append(fc_prcp, ignore_index=True)



#%% save output
outfile_name = 'output/' + USERNAME + '_' + prediction_start.strftime("%Y-%m-%d") + '.csv'
eval_df_base.to_csv(outfile_name, index=False)
