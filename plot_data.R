rm(list = ls())


# filename <- 'lau_2021_04_12_105149_data.csv'
# filename <- 'lisbeth_2021_04_11_130622_data.csv'
filename <- 'jordan_2021_04_16_100659_data.csv'
filepath <- paste(getwd(), 'data', filename, sep='/')

data <- read.table(filepath, header = TRUE, sep = ',')
data <- subset(data, select = -X)
n_trials <- dim(data)[1]

data$classification <- NA# character(n_trials)
data$trial_type <- character(n_trials)
data$jitter <- character(n_trials)

for(trial_index in 1:n_trials)
{
  if(data$trigger[trial_index] == 144 || data$trigger[trial_index] == 160)
  {
    data$trial_type[trial_index] <- 'omission'
    if(data$response[trial_index] == 'yes')
    {
      data$classification[trial_index] <- 'false_alarm'
    }
    if(data$response[trial_index] == 'no')
    {
      data$classification[trial_index] <- 'correct_rejection'
    }
    if(data$trigger[trial_index] == 144) data$jitter[trial_index] <- '0 %'
    if(data$trigger[trial_index] == 160) data$jitter[trial_index] <- '15 %'
  }
  if(data$trigger[trial_index] == 81 || data$trigger[trial_index] == 97)
  {
    data$trial_type[trial_index] <- 'weak'
    if(data$response[trial_index] == 'yes')
    {
      data$classification[trial_index] <- 'hit'
    }
    if(data$response[trial_index] == 'no')
    {
      data$classification[trial_index] <- 'miss'
    }
    if(data$trigger[trial_index] == 81) data$jitter[trial_index] <- '0 %'
    if(data$trigger[trial_index] == 97) data$jitter[trial_index] <- '15 %'
  }
}
# print(data)
print(table(data$classification))
print(table(data$classification, data$trial_type, data$jitter, 
            exclude=c(NA, '')))



hit_rate <- sum(data$classification == 'hit', na.rm=TRUE) /
  sum(data$trial_type == 'weak', na.rm=TRUE)
false_alarm_rate <- 
  sum(data$classification == 'false_alarm', na.rm=TRUE) /
  sum(data$trial_type == 'omission', na.rm=TRUE)
d_prime <- qnorm(hit_rate) - qnorm(false_alarm_rate)
C <- -0.5 * (qnorm(hit_rate) + qnorm(false_alarm_rate))


temp <- subset(data, data$jitter == '0 %')
hit_rate_0 <- sum(temp$classification == 'hit', na.rm=TRUE) /
  sum(temp$trial_type == 'weak', na.rm=TRUE)
false_alarm_rate_0 <- 
  sum(temp$classification == 'false_alarm', na.rm=TRUE) /
  sum(temp$trial_type == 'omission', na.rm=TRUE)
d_prime_0 <- qnorm(hit_rate_0) - qnorm(false_alarm_rate_0)
C_0 <- -0.5 * (qnorm(hit_rate_0) + qnorm(false_alarm_rate_0))

temp <- subset(data, data$jitter == '15 %')
hit_rate_15 <- sum(temp$classification == 'hit', na.rm=TRUE) /
  sum(temp$trial_type == 'weak', na.rm=TRUE)
false_alarm_rate_15 <- 
  sum(temp$classification == 'false_alarm', na.rm=TRUE) /
  sum(temp$trial_type == 'omission', na.rm=TRUE)
d_prime_15 <- qnorm(hit_rate_15) - qnorm(false_alarm_rate_15)
C_15 <- -0.5 * (qnorm(hit_rate_15) + qnorm(false_alarm_rate_15))

target_data <- subset(data, data$jitter != '')
target_data$correct <- ifelse(target_data$classification == 'hit' | 
           target_data$classification == 'correct_rejection', 1, 0)
binomial_model_weak <- glm(correct ~ jitter, family='binomial',
                      data=target_data, subset=target_data$trial_type == 'weak')
binomial_model_omission <- glm(correct ~ jitter, family='binomial',
                           data=target_data,
                           subset=target_data$trial_type == 'omission')

binomial_model_collapse <- glm(correct ~ jitter, family='binomial',
                               data=target_data)
