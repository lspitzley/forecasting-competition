# predictions

library(ggplot2) # make nice plots
library(lubridate)
library(reshape2)
library(forecast)
source('competition/forecast_functions.R')

last_ten_years <-readRDS('last_ten_alb.rds')

#### define prediction scope ----------------------------------------
prediction_start <- readline("When should the prediction start? Enter date in YYYY-MM-DD: ")
prediction_start <- ymd(prediction_start)
start_prev_seven <- prediction_start - days(7)
eval.dates <- seq(prediction_start, prediction_start + 6, by='days')
eval_df_base <- as.data.frame(eval.dates)


# previous seven days - mean
forecast_name <- 'mean_prev_seven'
prev_seven <- subset(last_ten_years, YEARMODA >= start_prev_seven & 
                       YEARMODA < prediction_start)
mean.max <- mean(prev_seven$MAX) 
mean.min <- mean(prev_seven$MIN)
mean.prcp <- mean(prev_seven$I_PRCP)

pred.df.list <- list()
pred.df.list[['max']] <- forecast_df_builder(eval.dates, 'mean_prev_seven', 'MAX', 
                                             rep(mean.max, 7))
pred.df.list[['min']] <- forecast_df_builder(eval.dates, 'mean_prev_seven', 
                                             'MIN', rep(mean.min, 7))
pred.df.list[['prcp']] <- forecast_df_builder(eval.dates, 'mean_prev_seven', 
                                             'P_PRCP', rep(mean.prcp, 7))


pred.df <- do.call(rbind, pred.df.list)
write.csv(pred.df, paste0(prediction_start, '_forecast_baseline.csv'))
