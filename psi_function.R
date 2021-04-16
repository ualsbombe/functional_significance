# https://psychopy.org/api/data.html#psychopy.data.PsiHandler

rm(list =ls())

psi_function <- function(x, alpha, beta, delta)
{
    normCdf <- pnorm(x, mean=alpha, sd=beta)
    Y <- 0.5 * delta + (1 - delta) * (0.5 + 0.5 * normCdf)
}

x <- seq(-100, 100, 0.01)
y <- psi_function(x, 0.7, 100, 0.02)

plot(x, y, type='b')
