library(readr)
library(poweRlaw)
leung.data <- data.frame(read_csv("./data/dc_leung.csv"))
leung.data <- leung.data[leung.data$degree.centrality != 0, ]

yu.data <- data.frame(read_csv("./data/dc_yu.csv"))
yu.data <- yu.data[yu.data$degree.centrality != 0, ]

leung.dist <- conpl$new(leung.data$degree.centrality)
yu.dist <- conpl$new(yu.data$degree.centrality)

leung.xmin <- estimate_xmin(leung.dist)
yu.xmin <- estimate_xmin(yu.dist)

leung.dist$setXmin(leung.xmin)
yu.dist$setXmin(yu.xmin)

leung.pars <- estimate_pars(leung.dist)
yu.pars <- estimate_pars(yu.dist)

leung.bs <- bootstrap_p(leung.dist, no_of_sims=1000, xmins=leung.xmin$xmin, pars=leung.pars); leung.bs$p
yu.bs <- bootstrap_p(yu.dist, no_of_sims=1000, xmins=yu.xmin$xmin, pars=yu.pars); yu.bs$p
