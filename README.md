BFOR 416/516 Forecasting Competition
====================================



# Overview
Weather prediction is difficult.

Most data analytics courses only predict past data and use train/test sets. Predicting
real events which have yet to occur is far more difficult and exciting. The learning that comes
from genuine prediction will put you far ahead of peers.

We are going to attempt to predict the weather. Weather prediction is a great
way to learn data analytics because it contains continuous predictions (temperature),
discrete predictions (rain/no rain), and has many possibilities for using
unsupervised techniques (like clustering and visualization). Weather predictions
require careful thought about how to structure data. The data is public and comes in
daily, which makes evaluation easier.



# Data

The National Oceanic and Atmospheric Administration (NOAA) publishes hourly and
daily weather observations from weather stations around the world.

The [GSODR](https://ropensci.github.io/GSODR/index.html) R package makes it easy to
download the latest weather data. We will use the Albany Internation Airport
as the location for the weather data and forecasts. The station ID is `725180-14735`.

Since the course is using Python, and I have not found a suitable Python
replacement for `GSODR`, I will post the historical forecast data to
Slack using a bot. You can either use the data from Slack, or run the
`R` script `download_latest_data.R`.

# Forecasts
You should submit the forecasts for the daily high temparature (`MAX`),
daily low temperature (`MIN`), the probability of precipitation (`P_PRCP`). Preciptation
will be have occurred when the value of the `PRCP` column is greater than `0.00`.

The baseline prediction is named `mean_prev_seven`. It is simply the average temperature
from the last seven days.

# Submission Format

The submissions must be in a CSV file formatted exactly as the
values in the tables below. The easiest way to acheive this
format is to build your forecasts with the `baseline_predictions.py`
file. Modify the code in that file to include your forecasting technique.

| fc_date    | fc_name   | fc_var   | fc_value    |
|------------|-----------|----------|-------------|
| YYYY-MM-DD | your_name | VAR_NAME | Degrees (C) |

Example:

| fc_date    | fc_name   | fc_var   | fc_value    |
|------------|-----------|----------|-------------|
| 2019-02-04 | lspitzley | MAX      | 5.5776      |
| 2019-02-04 | lspitzley | MIN      | -0.5468     |
| 2019-02-04 | lspitzley | P_PRCP   | 0.2556      |


A one-week forecast will should have 21 rows.

You can test your format by running your forecasts through the
`forecast_evaluation.py` script.

# Evaluation

Continuous forecasts are evaluated with
[`sklearn` regression metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics).
Binary predictions are scored with standard methods that we covered
in class. 

The `forecast_evaluation.py` script reports scores to the console and to
a `.csv` file in the `output/` directory.

The RMSE will be the primary scoring metric for the temperature predictions.
Log loss and AUC are the primary metrics for precipitation predictions.
