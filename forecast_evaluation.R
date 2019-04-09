#### evaluation ------------------------------------------
library(reshape2)
library(forecast)
library(plyr)
library(lubridate)
source('forecast_functions.R')

# load files into a single data frame
last_ten_years <- readRDS('last_ten_alb.rds')

file_list <- list.files('forecasts/', pattern = '.csv|.CSV')
raw_files <- lapply(file_list, function(x) {print(x)
  read.csv(paste0('forecasts/', x), stringsAsFactors = FALSE)})
pred.df <- do.call(rbind.fill, raw_files)

#### DATA CLEANING -----------------------------------------------------------------------------

# fix dates (only works if dates are in fc.date or fc.dates)
pred.df$fc.date <- ifelse(is.na(pred.df$fc.date), pred.df$fc.dates, pred.df$fc.date)
pred.df$fixed.date <- parse_date_time(x = pred.df$fc.date, c('ymd', 'mdy'))

# fix mislabled P_PRCP var
pred.df[which(pred.df$fc.var == 'P_PRCP' | pred.df$fc.var == 'PRCP'), 'fc.var'] <- 'I_PRCP'

# clean up bad values
pred.df$fc.value <- as.numeric(pred.df$fc.value)

# adjust names to be lowercase
pred.df$fc.name <- tolower(pred.df$fc.name)

# clean up columns and remove duplicates
fc.cols <- c('fc.name', 'fc.var', 'fixed.date', 'fc.value')
pred.df <- pred.df[complete.cases(pred.df[,fc.cols]),fc.cols]
pred.df <- pred.df[!duplicated(pred.df[,c('fc.name', 'fc.var', 'fixed.date')]),]

##### merge historical data with predictions  --------------------------------------------------
eval_df <- melt(data = last_ten_years, id.vars = c('YEARMODA'), 
                measure.vars = c('MAX', 'MIN', 'I_PRCP'), 
                value.name = 'obs.value')
pred_eval <- merge(x = pred.df, y=eval_df, 
                   by.x = c('fixed.date', 'fc.var'),
                   by.y = c('YEARMODA', 'variable'))

#### evaluate by entry/week --------------------------------------------------------------------

week_beginning <- c('2019-02-11', '2019-02-18', '2019-02-25', '2019-03-04', '2019-03-11', 
                    '2019-03-18', '2019-03-25', '2019-04-02')
for (week in week_beginning) {
  week_of <- date(week)
  print(week_of)
  week_prediction <- subset(pred_eval, fixed.date >= week_of &fixed.date <= week_of + days(6))
  if (nrow(week_prediction) == 0) break
  unique_entries <- as.data.frame(unique(week_prediction[,c('fc.name', 'fc.var')]))
  temperature_entries <- subset(unique_entries, !is.na(fc.name) & fc.var %in% c('MAX', 'MIN'))
  precip_entries <- subset(unique_entries, !is.na(fc.name) & fc.var == 'I_PRCP')
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
full_prediction <- subset(pred_eval, fixed.date >= date('2019-02-11'))

unique_entries <- as.data.frame(unique(full_prediction[,c('fc.name', 'fc.var')]))
temperature_entries <- subset(unique_entries, !is.na(fc.name) & fc.var %in% c('MAX', 'MIN'))
precip_entries <- subset(unique_entries, !is.na(fc.name) & fc.var == 'I_PRCP')
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
