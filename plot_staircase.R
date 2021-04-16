rm(list = ls())


filename <- 'lisbeth_2021_04_11_130622_staircase.csv'
filename <- 'lau_2021_04_12_105149_staircase.csv'
filepath <- paste(getwd(), 'data', filename, sep='/')

data <- read.table(filepath, header = TRUE, sep = ',')
data <- subset(data, select = -X)

plot(data$current, type='b')