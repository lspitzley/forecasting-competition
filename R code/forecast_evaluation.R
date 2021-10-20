#### INSTRUCTIONS ---------------------------------------
# Run this file from the top-level directory.
# Forecasts should be in 'forecasts' directory
#### evaluation ------------------------------------------
library(reshape2)
library(forecast)
library(plyr)
library(lubridate)
source('R code/forecast_functions.R')

# load files into a single data frame
last_ten_years <- readRDS('last_ten_alb.rds')

file_list <- list.files('forecasts/', pattern = '.csv|.CSV')
raw_files <- lapply(file_list, function(x) {print(x)
  read.csv(paste0('forecasts/', x), stringsAsFactors = FALSE)})
pred_df <- do.call(rbind.fill, raw_files)

#### DATA CLEANING -----------------------------------------------------------------------------

# fix dates (only works if dates are in fc.date or fc.dates)
pred_df$fc_date <- ifelse(is.na(pred_df$fc_date), pred_df$fc.date, pred_df$fc_date)
pred_df$fixed_date <- parse_date_time(x = pred_df$fc_date, c('ymd', 'mdy'))

# fix mislabled P_PRCP var
pred_df[which(pred_df$fc_var == 'P_PRCP' | pred_df$fc_var == 'PRCP'), 'fc_var'] <- 'I_PRCP'

# clean up bad values
pred_df$fc_value <- as.numeric(pred_df$fc_value)

# adjust names to be lowercase
pred_df$fc_name <- tolower(pred_df$fc_name)

# clean up columns and remove duplicates
fc_cols <- c('fc_name', 'fc_var', 'fixed_date', 'fc_value')
pred_df <- pred_df[complete.cases(pred_df[,fc_cols]),fc_cols]
pred_df <- pred_df[!duplicated(pred_df[,c('fc_name', 'fc_var', 'fixed_date')]),]

##### merge historical data with predictions  --------------------------------------------------
eval_df <- melt(data = last_ten_years, id.vars = c('YEARMODA'), 
                measure.vars = c('MAX', 'MIN', 'I_PRCP'), 
                value.name = 'obs.value')
pred_eval <- merge(x = pred_df, y=eval_df, 
                   by.x = c('fixed_date', 'fc_var'),
                   by.y = c('YEARMODA', 'variable'))

#### evaluate by entry/week --------------------------------------------------------------------

week_beginning <- c('2021-09-29', '2021-10-06', '2021-10-13')
for (week in week_beginning) {
  week_of <- date(week)
  print(week_of)
  week_prediction <- subset(pred_eval, fixed_date >= week_of &fixed_date <= week_of + days(6))
  if (nrow(week_prediction) == 0) break
  unique_entries <- as.data.frame(unique(week_prediction[,c('fc_name', 'fc_var')]))
  temperature_entries <- subset(unique_entries, !is.na(fc_name) & fc_var %in% c('MAX', 'MIN'))
  precip_entries <- subset(unique_entries, !is.na(fc_name) & fc_var == 'I_PRCP')
  eval_results <- lapply(1:nrow(temperature_entries), 
                         FUN = function(x) group_forecast_eval(week_prediction,
                                                               temperature_entries[x,1],
                                                               temperature_entries[x,2]))
  
  
  eval_results_df <- do.call(rbind, eval_results)
  eval_results_df$week_of <- week_of
  rownames(eval_results_df) <- NULL
  print(eval_results_df)
  write.csv(eval_results_df, paste0('output/temperature-results_', week, '.csv'))
  
  # precipitation forecasts
  prcp_results <- lapply(1:nrow(precip_entries), 
                         FUN = function(x) group_prcp_eval(week_prediction,
                                                               precip_entries[x,1],
                                                               precip_entries[x,2]))
  prcp_results_df <- do.call(rbind, prcp_results)
  prcp_results_df$week_of <- week_of
  rownames(prcp_results_df) <- NULL
  print(prcp_results_df)
  write.csv(prcp_results_df, paste0('output/precip-results_', week, '.csv'))
}

#### overall predictions ----------------------------------------------------------------------
full_prediction <- subset(pred_eval, fixed_date >= date('2021-09-29'))

unique_entries <- as.data.frame(unique(full_prediction[,c('fc_name', 'fc_var')]))
temperature_entries <- subset(unique_entries, !is.na(fc_name) & fc_var %in% c('MAX', 'MIN'))
precip_entries <- subset(unique_entries, !is.na(fc_name) & fc_var == 'I_PRCP')
eval_results <- lapply(1:nrow(temperature_entries), 
                       FUN = function(x) group_forecast_eval(full_prediction,
                                                             temperature_entries[x,1],
                                                             temperature_entries[x,2]))


eval_results_df <- do.call(rbind, eval_results)
eval_results_df$as_of <- Sys.Date()
rownames(eval_results_df) <- NULL
print(eval_results_df)
write.csv(eval_results_df, paste0('output/temperature-results_cumulative.csv'))

# precipitation forecasts
prcp_results <- lapply(1:nrow(precip_entries), 
                       FUN = function(x) group_prcp_eval(full_prediction,
                                                         precip_entries[x,1],
                                                         precip_entries[x,2]))
prcp_results_df <- do.call(rbind, prcp_results)
prcp_results_df$as_of <- Sys.Date()
rownames(prcp_results_df) <- NULL
print(prcp_results_df)
write.csv(prcp_results_df, paste0('output/precip-results_cumulative.csv'))

