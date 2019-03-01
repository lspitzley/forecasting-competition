# script to download the latest GSOD data
library(GSODR) # easy access to weather data

#TODO get most recent year and rbind 2019
#last_ten_years <-  get_GSOD(years = 2009:2018, station = '725180-14735')
last_ten_years <- readRDS('last_ten_alb.rds')
current_year <- get_GSOD(years = 2019, station = '725180-14735')
# create column with precipitation indicator
current_year$I_PRCP <- ifelse(current_year$PRCP > 0, 1, 0)
new_rows <- subset(current_year, !(YEARMODA %in% last_ten_years$YEARMODA))
last_ten_years <- rbind(last_ten_years, new_rows)
saveRDS(object = last_ten_years, file = 'last_ten_alb.rds')



