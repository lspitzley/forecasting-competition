# -*- coding: utf-8 -*-
"""
Extra functions that are useful for 
the forecasting process.

@author: Lee Spitzley
"""
import pandas as pd

#%% function to create a dataframe for the means
def construct_mean_forecast_df(fc_dates, username, fc_var, avg_val):
    """
    Create a dictionary to add to the forecast dataframe.
    This version repeats the average value of a variable
    over the number of days.
    
    This function could be copied and modified to accept
    a list of forecast values instead of a single value
    repeated.

    Parameters
    ----------
    fc_dates : list 
        list of dates in the forecast
    avg_val : float
        Value to repeat across days.
    fc_var : str
        Name of value you are forecasting. Should be 
        one of MAX, MIN, P_PRCP.

    Returns
    -------
    mean_df : pandas.DataFrame()
        Dataframe with column names and list of values for 
        each column.

    """
    
    nrow = len(fc_dates)
    mean_dict = {'fc_date': fc_dates, 
              'fc_name': [username] * nrow, 
              'fc_var': [fc_var] * nrow, 
              'fc_value': [avg_val] * nrow}
    
    mean_df = pd.DataFrame.from_dict(mean_dict)
    return mean_df