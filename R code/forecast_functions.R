# store functions useful for storing & evaluating predictions
library(forecast)
library(MLmetrics)
library(caret)
# this function builds a standard dataframe with predictions
forecast_df_builder <- function(fc.date, fc_name, fc_var, fc_value) {
  tmp_df <- as.data.frame(fc.date)
  tmp_df$fc_name <- fc_name
  tmp_df$fc_var <- fc_var
  tmp_df$fc_value <- fc_value
  return(tmp_df)
}

# test code (get pred_eval from forecast_evaluation first)
fc_name <- 'lspitzley'
fc_var <- 'MAX'
group_forecast_eval <- function(pred_eval, fc_name, fc_var) {
  print(c(fc_name, fc_var))
  # tmp_eval <- subset(pred_eval, fc_name==fc_name & fc_var==fc_var) # no longer working?
  tmp_eval <- pred_eval[which(pred_eval$fc_name==fc_name & pred_eval$fc_var == fc_var),]
  # print(tmp_eval)
  tmp_accu <- as.data.frame(accuracy(tmp_eval$fc_value, x = tmp_eval$obs.value))
  tmp_accu$fc_name <- fc_name
  tmp_accu$fc_var <- fc_var
  tmp_accu$n.days <- nrow(tmp_eval)
  return(tmp_accu)
}

# debug vars
fc_var = 'I_PRCP'
fc_name = 'lspitzley'
group_prcp_eval <- function(pred_eval, fc_name, fc_var) {
  print(c(fc_name, fc_var))
  # tmp_eval <- subset(pred_eval, fc_name == fc_name & fc_var==fc_var)
  tmp_eval <- pred_eval[which(pred_eval$fc_name==fc_name & pred_eval$fc_var == fc_var),]
  tmp_accu <- data.frame(fc_name = fc_name, fc_var = fc_var)
  # probabilistic evaluation
  tmp_accu$logLoss <- LogLoss(y_pred=tmp_eval$fc_value, y_true = tmp_eval$obs.value)
  # discrete predictions
  tmp_eval$pred <- factor(ifelse(tmp_eval$fc_value >= 0.5, 'rain', 'norain'), levels = c('rain', 'norain'))
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