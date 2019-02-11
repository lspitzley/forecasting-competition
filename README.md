<header>
BFOR 416/516 Forecasting Competition
====================================
</header>
<main>


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

# Forecasts
You should submit the forecasts for the daily high temparature (`MAX`),
daily low temperature (`MIN`), the probability of precipitation (`P_PRCP`). Preciptation
will be have occurred when the value of the `PRCP` column is greater than `0.00`.

# Submission Format

| fc.date    | fc.name   | fc.var   | fc.value    |
|------------|-----------|----------|-------------|
| YYYY-MM-DD | your_name | VAR_NAME | Degrees (C) |

Example:

| fc.date    | fc.name   | fc.var   | fc.value    |
|------------|-----------|----------|-------------|
| 2019-02-04 | lspitzley | MAX      | 5.5776      |
| 2019-02-04 | lspitzley | MIN      | -0.5468     |
| 2019-02-04 | lspitzley | P_PRCP   | 0.2556      |



# Evaluation

Continuous forecasts will be evaluated with functions from the `forecast` package.
Binary predictions will be scored with standard methods and those contained in
the `scoring` package. 



</main>