library(readr)
library(poweRlaw)

source("plfunc.R")

# Get data
yu <- getData("../data/dc_auth_yu.csv")
leung <- getData("../data/dc_auth_leung.csv")
yu.aff <- getData("../data/dc_aff_yu.csv")
leung.aff <- getData("../data/dc_aff_leung.csv")
yu.country <- getData("../data/dc_aff_yu_country.csv")
leung.country <- getData("../data/dc_aff_leung_country.csv")


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
yu.120 <- getData("../data/dc_auth_yu.csv")
yu.120$dist <- estimateParameters(yu.120$dist, 120)
leung.120 <- getData("../data/dc_auth_leung.csv")
leung.120$dist <- estimateParameters(leung.120$dist, 120)
yu.aff.120 <- getData("../data/dc_aff_yu.csv")
yu.aff.120$dist <- estimateParameters(yu.aff.120$dist, 120)
leung.aff.120 <- getData("../data/dc_aff_leung.csv")
leung.aff.120$dist <- estimateParameters(leung.aff.120$dist, 120)


# Plot fit
plotFit(yu.120$dist, "Yu")
plotFit(leung.120$dist, "Leung")
mtext(text=expression(bold("Power law fit for authors when x"[min]*" is set to 120")),
      outer=TRUE, cex=1)

plotFit(yu.aff.120$dist, "Yu")
plotFit(leung.aff.120$dist, "Leung")
mtext(text=expression(bold("Power law fit for all affiliations when x"[min]*" is set to 120")),
      outer=TRUE, cex=1)


# Calculate P-values
yu$bsp <- bootstrap_p(yu$dist, no_of_sims=1000, threads=2)
yu.120$bsp <- bootstrap_p(yu.120$dist, no_of_sims=1000, threads=2)
yu.aff$bsp <- bootstrap_p(yu.aff$dist, no_of_sims=1000, threads=2)
yu.aff.120$bsp <- bootstrap_p(yu.aff.120$dist, no_of_sims=1000, threads=2)
yu.country$bsp <- bootstrap_p(yu.country$dist, no_of_sims=1000, threads=2)
leung$bsp <- bootstrap_p(leung$dist, no_of_sims=1000, threads=2)
leung.120$bsp <- bootstrap_p(leung.120$dist, no_of_sims=1000, threads=2)
leung.aff$bsp <- bootstrap_p(leung.aff$dist, no_of_sims=1000, threads=2)
leung.aff.120$bsp <- bootstrap_p(leung.aff.120$dist, no_of_sims=1000, threads=2)
leung.country$bsp <- bootstrap_p(leung.country$dist, no_of_sims=1000, threads=2)

pvalues <- matrix(c(yu$bsp$p, leung$bsp$p, yu.120$bsp$p, leung.120$bsp$p,
                    yu.aff$bsp$p, leung.aff$bsp$p, yu.aff.120$bsp$p,
                    leung.aff.120$bsp$p, yu.country$bsp$p, leung.country$bsp$p),
                  nrow=1, ncol=10)
colnames(pvalues) <- c("Yu", "Leung", "Yu 120", "Leung 120", "Yu Aff", "Leung Aff",
                       "Yu Aff 120", "Leung Aff 120", "Yu Coun", "Leung Coun")
rownames(pvalues) <- "P-values"
pvalues


# Compare to alternative distributions
dat <- list(yu=yu, leung=leung, yu.120=yu.120, leung.120=leung.120, 
            yu.aff=yu.aff, leung.aff=leung.aff, yu.aff.120=yu.aff.120,
            leung.aff.120=leung.aff.120, yu.country=yu.country, leung.country=leung.country)
names <- list("Yu", "Leung", "Yu 120", "Leung 120", "Yu Aff", "Leung Aff",
              "Yu Aff 120", "Leung Aff 120", "Yu Coun", "Leung Coun")
i <- 0
for (d in dat) {
  i <- i+1
  compareAlternative(d$data, d$dist, names[i])
}

