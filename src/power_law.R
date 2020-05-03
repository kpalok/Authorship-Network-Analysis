library(readr)
library(poweRlaw)

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

# Get data
leung <- getData("../data/dc_auth_leung.csv")
yu <- getData("../data/dc_auth_yu.csv")
leung.aff <- getData("../data/dc_aff_leung.csv")
yu.aff <- getData("../data/dc_aff_yu.csv")
leung.country <- getData("../data/dc_aff_leung_country.csv")
yu.country <- getData("../data/dc_aff_yu_country.csv")


# Plot fit
par(mfrow=c(2,1), mar=c(4,4,3,2), oma=c(1,1,3,1))
plotFit(yu$dist, "Yu")
plotFit(leung$dist, "Leung")
mtext(text=expression(bold("Power law fit for authors when x"[min]*" is estimated")),
      outer=TRUE, cex=1)

plotFit(yu.aff$dist, "Yu")
plotFit(leung.aff$dist, "Leung")
mtext(text=expression(bold("Power law fit for all affiliations when x"[min]*" is estimated")),
      outer=TRUE, cex=1)

plotFit(yu.country$dist, "Yu")
plotFit(leung.country$dist, "Leung")
mtext(text=expression(bold("Power law fit for affiliations grouped by country")),
      outer=TRUE, cex=1)


# Set estimates of xmin to 120 (no need to do this for countries)
yu$dist <- estimateParameters(yu$dist, 120)
leung$dist <- estimateParameters(leung$dist, 120)
yu.aff$dist <- estimateParameters(yu.aff$dist, 120)
leung.aff$dist <- estimateParameters(leung.aff$dist, 120)


# Plot fit
plotFit(yu$dist, "Yu")
plotFit(leung$dist, "Leung")
mtext(text=expression(bold("Power law fit for authors when x"[min]*" is set to 120")),
      outer=TRUE, cex=1)

plotFit(yu.aff$dist, "Yu")
plotFit(leung.aff$dist, "Leung")
mtext(text=expression(bold("Power law fit for all affiliations when x"[min]*" is set to 120")),
      outer=TRUE, cex=1)


# Plot all values in a log-log plot
par(mfrow=c(2,3))
plot(sort(yu$data, decreasing=T), log="xy", ylab="degree",
     main="Yu", pch=20, cex=0.5, type="p")
plot(sort(yu.aff$data, decreasing=T), log="xy", ylab="degree",
     main="Yu Affiliations", pch=20, cex=0.5, type="p")
plot(sort(yu.country$data, decreasing=T), log="xy", ylab="degree",
     main="Yu Country", pch=20, cex=0.5, type="p")
plot(sort(leung$data, decreasing=T), log="xy", ylab="degree",
     main="Leung", pch=20, cex=0.5, type="p")
plot(sort(leung.aff$data, decreasing=T), log="xy", ylab="degree",
     main="Leung Affiliations", pch=20, cex=0.5, type="p")
plot(sort(leung.country$data, decreasing=T), log="xy", ylab="degree",
     main="Leung Country", pch=20, cex=0.5, type="p")


# Calculate P-values
yu$bsp <- bootstrap_p(yu$dist, no_of_sims=1000, threads=2)
yu.aff$bsp <- bootstrap_p(yu.aff$dist, no_of_sims=1000, threads=2)
yu.country$bsp <- bootstrap_p(yu.country$dist, no_of_sims=1000, threads=2)
leung$bsp <- bootstrap_p(leung$dist, no_of_sims=1000, threads=2)
leung.aff$bsp <- bootstrap_p(leung.aff$dist, no_of_sims=1000, threads=2)
leung.country$bsp <- bootstrap_p(leung.country$dist, no_of_sims=1000, threads=2)

pvalues <- matrix(c(yu$bsp$p, yu.aff$bsp$p, yu.country$bsp$p,
                    leung$bsp$p, leung.aff$bsp$p, leung.country$bsp$p),
                  nrow=1, ncol=6)
colnames(pvalues) <- c("Yu", "Yu Aff", "Yu Coun", "Leung", "Leung Aff", "Leung Coun")
rownames(pvalues) <- "P-values"
pvalues