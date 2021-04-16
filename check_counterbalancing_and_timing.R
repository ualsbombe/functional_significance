rm(list = ls())

filename <- 'counterbalancing_and_timing_test_2021_01_06_162744_data.csv' ## good
filename <- 'timing_test_2021_01_08_144153_data.csv'
filepath <- paste(getwd(), 'data', filename, sep='/')

data <- read.table(filepath, header = TRUE, sep = ',')
data <- subset(data, select = -X)
print(table(data$trigger))

n_trials <- dim(data)[1]
data$time_difference <- numeric(n_trials)

for(trial_index in 1:n_trials)
{
  
  if(data$trigger[trial_index] == 3) 
  {
    data$time_difference[trial_index] <- data$trial_time[trial_index]
  } else
  {
    data$time_difference[trial_index] <- data$trial_time[trial_index] -
      data$trial_time[trial_index - 1]
  }

}

triggers <- sort(unique(data$trigger))
n_triggers <- length(triggers)

for(trigger_index in 1:n_triggers)
{
  trigger <- triggers[trigger_index]
  data_index <- data$trigger == trigger
  if(trigger_index == 1)
  {
    plot(rep(trigger_index, sum(data_index)), data$time_difference[data_index],
         xlim = c(1, n_triggers), ylim = c(1.0, 2.0), xaxt = 'n',
         xlab = 'Trigger Code', ylab = 'Duraction between triggers (s)')
    axis(1, at=1:n_triggers, labels = triggers[1:length(triggers)])
  } else
  {
    points(rep(trigger_index, sum(data_index)),
           data$time_difference[data_index])
  }
}
lines(c(1, n_triggers), rep(1.497 - 0.15*1.487, 2), col='red')
lines(c(1, n_triggers), rep(1.497 + 0.15*1.487, 2), col='red')

lines(c(1, n_triggers), rep(1.497 - 2*0.15*1.487, 2), col='blue')
lines(c(1, n_triggers), rep(1.497 + 2*0.15*1.487, 2), col='blue')

## more spread is expected for 37, as this is where the jitters
## can go in either direction

for(trigger in triggers)
{
  print(paste('Trigger:', trigger))
  print(summary(data$time_difference[data$trigger == trigger]))
}