estimateParameters <- function(dist, estimate=NULL) {
  est <- if(!is.null(estimate)) estimate else estimate_xmin(dist)
  dist$setXmin(est)
  
  pars <- estimate_pars(dist)
  dist$setPars(pars)
  
  return(dist)
}

getData <- function(path) {
  data <- data.frame(read_csv(path))
  data <- data[data$degree.centrality != 0,]
  data <- sort(as.integer(data[[2]]), decreasing=T)
  dist <- displ$new(data)
  
  dist <- estimateParameters(dist)
  
  return(list(data=data, dist=dist))
}

plotFit <- function(dist, name) {
  plot(dist, pch=20, cex=0.5, type="p", main=name,
       ylab="CDF", xlab="degree")
  lines(dist, col="red", lwd=2)
}

compareAlternative <- function(data, dist, dname) {
  # Poisson
  pois <- list()
  pois$dist <- dispois$new(data)
  pois$dist$setXmin(dist$getXmin())
  pois$dist$setPars(estimate_pars(pois$dist))
  pois$p <- compare_distributions(dist, pois$dist)$p_two_sided
  
  # Log-normal
  lognorm <- list()
  lognorm$dist <- dislnorm$new(data)
  lognorm$dist$setXmin(dist$getXmin())
  lognorm$dist$setPars(estimate_pars(lognorm$dist))
  lognorm$p <- compare_distributions(dist, lognorm$dist)$p_two_sided
  
  # Exponential
  expo <- list()
  expo$dist <- disexp$new(data)
  expo$dist$setXmin(dist$getXmin())
  expo$dist$setPars(estimate_pars(expo$dist))
  expo$p <- compare_distributions(dist, expo$dist)$p_two_sided
  
  pvalues <- matrix(c(pois$p, lognorm$p, expo$p), nrow=1, ncol=3)
  colnames(pvalues) <- c("Poisson", "Log-normal", "Exponential")
  rownames(pvalues) <- dname
  
  print(pvalues)
}