# store functions useful for storing & evaluating predictions
library(forecast)
# this function builds a standard dataframe with predictions
forecast_df_builder <- function(fc.dates, fc_name, fc_var, fc_values) {
  tmp_df <- as.data.frame(fc.dates)
  tmp_df$fc.name <- fc_name
  tmp_df$fc.var <- fc_var
  tmp_df$fc.value <- fc_values
  return(tmp_df)
}

group_forecast_eval <- function(pred_eval, fc_name, fc_var) {
  print(c(fc_name, fc_var))
  tmp_eval <- subset(pred_eval, fc.name == fc_name & fc.var==fc_var)
  tmp_accu <- as.data.frame(accuracy(tmp_eval$fc.value, x = tmp_eval$obs.value))
  tmp_accu$fc.name <- fc_name
  tmp_accu$fc.var <- fc_var
  return(tmp_accu)
}