rm(list = ls())

filename <- 'lau_2021_04_12_105149_detection.csv'
# filename <- 'lisbeth_2021_04_11_130622_detection.csv'
filename <- 'jordan_2021_04_16_100659_detection.csv'

filepath <- paste(getwd(), 'data', filename, sep='/')

data <- read.table(filepath, header = TRUE, sep = ',')
# data <- subset(data, select = -X)
n_trials <- dim(data)[1]
data$classification <- character(n_trials)

for(trial_index in 1:n_trials)
{
  if(data$trial_type[trial_index] == 'omission')
  {
    if(data$response[trial_index] == 'yes')
    {
      data$classification[trial_index] <- 'false_alarm'
    }
    if(data$response[trial_index] == 'no')
    {
      data$classification[trial_index] <- 'correct_rejection'
    }
  }
  if(data$trial_type[trial_index] == 'weak')
  {
    if(data$response[trial_index] == 'yes')
    {
      data$classification[trial_index] <- 'hit'
    }
    if(data$response[trial_index] == 'no')
    {
      data$classification[trial_index] <- 'miss'
    }
  }
}

hit_rate <- sum(data$classification == 'hit') / sum(data$trial_type == 'weak')
false_alarm_rate <- 
  sum(data$classification == 'false_alarm') / sum(data$trial_type == 'omission')

## correction
if(false_alarm_rate == 0)
{
  false_alarm_rate <- 1 / sum(data$trial_type == 'omission')
}
if(hit_rate == 1)
{
  hit_rate <- (sum(data$trial_type == 'weak') - 1) / sum(data$trial_type == 'weak')
}

d_prime <- qnorm(hit_rate) - qnorm(false_alarm_rate)
C <- -0.5 * (qnorm(hit_rate) + qnorm(false_alarm_rate))

print(paste('Current:', unique(data$current), 'mA'))
print(paste("d':", d_prime))
print(paste('C:', C)) # positive is conservative, negative liberal
print(paste('Hit rate:', hit_rate))
print(paste('False alarm rate:', false_alarm_rate))
print(table(data$classification))


