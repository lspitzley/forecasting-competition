library(ggplot2)
last_ten_years <- readRDS('last_ten_alb.rds')

#### forecast plotting ------------------------------------------
# currently only works after running the forecast_evaluation.R
# script to get the pred_eval data frame
max_min <- subset(pred_eval, fc.var %in% c("MAX", "MIN"))
max.plots <- ggplot(max_min, aes(x=fixed.date, y=fc.value, color=fc.name,
                                   group=interaction(fc.name, fc.var),
                                   shape=fc.var))
max.plots + geom_point() + geom_line() + 
  geom_line(data=max_min, aes(y=obs.value, color=fc.var), size=1.5) +
  theme(axis.text.x=element_text(angle=45,hjust=1))



#### plot last ten years data
# do some quick visuals
qplot(x = last_ten_years$YEARMODA, y = last_ten_years$MAX)

yoy <- ggplot(last_ten_years, aes(x=YDAY, y=MAX, color=YEAR))
yoy + geom_point() + geom_smooth()