# store functions useful for storing & evaluating predictions
library(forecast)
library(MLmetrics)
library(caret)
# this function builds a standard dataframe with predictions
forecast_df_builder <- function(fc.date, fc_name, fc_var, fc_value) {
  tmp_df <- as.data.frame(fc.date)
  tmp_df$fc.name <- fc_name
  tmp_df$fc.var <- fc_var
  tmp_df$fc.value <- fc_value
  return(tmp_df)
}

group_forecast_eval <- function(pred_eval, fc_name, fc_var) {
  #print(c(fc_name, fc_var))
  tmp_eval <- subset(pred_eval, fc.name == fc_name & fc.var==fc_var)
  tmp_accu <- as.data.frame(accuracy(tmp_eval$fc.value, x = tmp_eval$obs.value))
  tmp_accu$fc.name <- fc_name
  tmp_accu$fc.var <- fc_var
  tmp_accu$n.days <- nrow(tmp_eval)
  return(tmp_accu)
}

group_prcp_eval <- function(pred_eval, fc_name, fc_var) {
  #print(c(fc_name, fc_var))
  tmp_eval <- subset(pred_eval, fc.name == fc_name & fc.var==fc_var)
  tmp_accu <- data.frame(fc.name = fc_name, fc.var = fc_var)
  # probabilistic evaluation
  tmp_accu$logLoss <- LogLoss(y_pred=tmp_eval$fc.value, y_true = tmp_eval$obs.value)
  # discrete predictions
  tmp_eval$pred <- factor(ifelse(tmp_eval$fc.value >= 0.5, 'rain', 'norain'), levels = c('rain', 'norain'))
  tmp_eval$obs <- factor(ifelse(tmp_eval$obs.value >= 0.5, 'rain', 'norain'), levels = c('rain', 'norain'))
  # accuracy evaluation
  cm <- confusionMatrix(tmp_eval$pred, tmp_eval$obs, mode = "prec_recall",
                  positive = "rain")
  tmp_accu$Accuracy <- cm$overall[['Accuracy']]
  tmp_accu$Precision <- cm$byClass[['Precision']]
  tmp_accu$Recall <- cm$byClass[['Recall']]
  tmp_accu$n.days <- nrow(tmp_eval)
  return(tmp_accu)
}