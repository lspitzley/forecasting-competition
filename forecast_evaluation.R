#### evaluation ------------------------------------------
library(reshape2)
library(forecast)
library(plyr)

# load files into a single data frame
file_list <- list.files('forecasts/', pattern = '*.csv')
raw_files <- lapply(file_list, function(x) read.csv(paste0('forecasts/', x)))
pred.df <- do.call(rbind.fill, raw_files)

# fix dates (only works if dates are in fc.date or fc.dates)
pred.df$fc.date <- ifelse(is.na(pred.df$fc.date), pred.df$fc.dates, pred.df$fc.date)
pred.df$fixed.date <- parse_date_time(x = pred.df$fc.date, c('ymd', 'mdy'))

# fix mislabled P_PRCP var
pred.df[which(pred.df$fc.var == 'I_PRCP' | pred.df$fc.var == 'PRCP'), 'fc.var'] <- 'P_PRCP'

# merge historical data with predictions
eval_df <- melt(data = last_ten_years, id.vars = c('YEARMODA'), 
                measure.vars = c('MAX', 'MIN', 'I_PRCP'), 
                value.name = 'obs.value')
pred_eval <- merge(x = pred.df, y=eval_df, 
                   by.x = c('fixed.date', 'fc.var'),
                   by.y = c('YEARMODA', 'variable'))

# evaluate by entry
week_beginning <- c('2019-02-11', '2019-02-18', '2019-02-25')
for (week in week_beginning){
  week_of <- date(week)
  print(week_of)
  week_prediction <- subset(pred_eval, fixed.date >= week_of &fixed.date <= week_of + days(6))
  unique_entries <- as.data.frame(unique(week_prediction[,c('fc.name', 'fc.var')]))
  temperature_entries <- subset(unique_entries, !is.na(fc.name) & fc.var %in% c('MAX', 'MIN'))
  precip_entries <- subset(unique_entries, !is.na(fc.name) & fc.var == 'P_PRCP')
  eval_results <- lapply(1:nrow(temperature_entries), 
                         FUN = function(x) group_forecast_eval(week_prediction,
                                                               temperature_entries[x,1],
                                                               temperature_entries[x,2]))
  
  
  eval_results_df <- do.call(rbind, eval_results)
  eval_results_df$week_of <- week_of
  rownames(eval_results_df) <- NULL
  print(eval_results_df)
  write.csv(eval_results_df, paste0('output/temperature-results_', week, '.csv'))
}

