import networkx as nx
import statistics as stat
import matplotlib.pyplot as plt
import pandas as pd
import authnet
import argparse
import queries
import csv

def save_summary(name, data):
    with open(name, "w") as f:
        writer = csv.writer(f)
        writer.writerow([("Variable"), ("Value")])
        for i in data:
            writer.writerow(i)

def summarize_graph(graph, dictionary):
    calculations = []

    # average clustering coefficient
    coefficient_dict = nx.clustering(graph)
    coefficient = stat.mean(coefficient_dict.values())
    calculations.append(["Avg clustering coefficient", coefficient])

    # average and variance of degree centrality
    degree_centrality = nx.degree_centrality(graph)
    avg_degree_centrality = stat.mean(degree_centrality.values())
    var_degree_centrality = stat.pvariance(degree_centrality.values())
    calculations.append(["Avg degree centrality", avg_degree_centrality])
    calculations.append(["Var degree centrality", var_degree_centrality])

    # average and variance of closeness centrality
    closeness_centrality = nx.closeness_centrality(graph)
    avg_closeness_centrality = stat.mean(closeness_centrality.values())
    var_closeness_centrality = stat.pvariance(closeness_centrality.values())
    calculations.append(["Avg closeness centrality", avg_closeness_centrality])
    calculations.append(["Var closeness centrality", var_closeness_centrality])

    # average and variance of betweeness centrality
    betweeness_centrality = nx.betweenness_centrality(graph)
    avg_betweeness_centrality = stat.mean(betweeness_centrality.values())
    var_betweeness_centrality = stat.pvariance(betweeness_centrality.values())
    calculations.append(["Avg betweeness centrality", avg_betweeness_centrality])
    calculations.append(["Var betweeness centrality", var_betweeness_centrality])

    # diameter of the graph
    diameter_list = []
    for i in nx.connected_components(graph):
        sub = graph.subgraph(i)
        diameter_list.append(nx.diameter(sub))
    diameter = max(diameter_list)

    calculations.append(["Graph diameter", diameter])
    
    # giant component of the graph
    giant_component_size = len(max(nx.connected_components(graph), key = len))
    calculations.append(["Giant component size", giant_component_size])
    
    name = str(list(dictionary)[0]).replace(" ", "_")
    name = "_aff.".join((name, "csv"))

    save_summary(name, calculations)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", required=True, help=".pickle file containing the dictionary.")
    parser.add_argument("--aff", help=".pickle file containing affiliation dictionary")
    args = parser.parse_args()

    if args.d:
        author_dict = queries.loadPickleDict(args.d)

    if author_dict and args.aff:
        affiliation_graph = authnet.generate_affiliation_graph(author_dict, queries.loadPickleDict(args.aff), True, True)
        summarize_graph(affiliation_graph, author_dict)
    elif author_dict:
        coauthor_graph = authnet.generate_graph(author_dict)
        summarize_graph(coauthor_graph, author_dict)