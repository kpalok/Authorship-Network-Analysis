import os.path
import argparse
import pickle
import queries
import csv
import datetime
import re
import numpy as np
import community as community_louvain #pip install python-louvain
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import community
from pprint import pprint

def generate_example_dict():
    dict = {
        "author1": [("author2", "", 3), ("author3", "", 4), ("author4", "", 2)],
        "author2": [("author1", "", 3), ("author3", "", 3), ("author4", "", 5)],
        "author3": [("author1", "", 4), ("author2", "", 3), ("author5", "", 2)],
        "author4": [("author1", "", 2), ("author2", "", 5), ("author6", "", 1)]
        }

    return dict

def get_country(affiliation, countries):
    for country in countries:
        if re.search(country.strip(), affiliation, re.IGNORECASE):
            return country

    return None

def group_by_countries(affiliation_dict):
    with open("countries.txt") as c:
        countries = c.readlines()

    for key in affiliation_dict:
        if affiliation_dict[key] != None:
            affiliation_dict[key] = get_country(affiliation_dict[key], countries)
    
    return affiliation_dict

def generate_affiliation_graph(author_dict, affiliation_dict, all_nodes, group_countries):
    coauthor_graph = nx.Graph()

    if group_countries:
        affiliation_dict = group_by_countries(affiliation_dict)

    # gen only unique values without None value
    s = set()
    for aff in affiliation_dict.values():
        if aff != None:
            s.add(aff)

    if all_nodes:
        coauthor_graph.add_nodes_from(s)

    for author, coauthors in author_dict.items():
        author_aff = affiliation_dict[author]
        if author_aff != None:
            for coauthor in coauthors:
                coauthor_aff = affiliation_dict[coauthor[0]]
                if coauthor_aff != None and not coauthor_graph.has_edge(author_aff, coauthor_aff):
                    coauthor_graph.add_edge(author_aff, coauthor_aff)

    return coauthor_graph

def generate_graph(author_dict, all_nodes=False):
    coauthor_graph = nx.Graph()

    coauthor_graph.add_nodes_from(author_dict.keys())

    for author, coauthors in author_dict.items():
        for coauthor in coauthors:
            if coauthor[2] >= 2 and not coauthor_graph.has_edge(author, coauthor[0]):
                coauthor_graph.add_edge(author, coauthor[0])
            else:
                if not coauthor_graph.has_node(coauthor[0]) and all_nodes:
                    coauthor_graph.add_node(coauthor[0])

    return coauthor_graph

def show_graph(graph, best_partition=False):
    if best_partition:
        partition = community_louvain.best_partition(graph)

        size = int(len(set(partition.values())))
        pos = nx.spring_layout(graph)
        count = 0
        colors = plt.cm.hsv(np.linspace(0,1,size))

        for com in set(partition.values()):
            list_nodes = [node for node in partition.keys() if partition[node] == com]
            nx.draw_networkx_nodes(graph, pos, list_nodes, node_size=30, node_color=colors[count])
            count += 1

        nx.draw_networkx_edges(graph, pos, alpha=0.75)
    else:
        nx.draw_networkx(graph, node_size=30, alpha=0.75, with_labels=False, width=0.1)

    plt.show()

def save_graph(graph, dict_name, best_partition=False):
    index = 0
    while os.path.isfile("../images/graph_{}{}.pdf".format(dict_name, index)):
        index += 1

    plt.figure(num=None, figsize=(20, 20), dpi=100)
    plt.axis('off')

    if best_partition:
        partition = community_louvain.best_partition(graph)

        size = int(len(set(partition.values())))
        pos = nx.spring_layout(graph)
        count = 0
        colors = plt.cm.hsv(np.linspace(0,1,size))

        for com in set(partition.values()):
            list_nodes = [node for node in partition.keys() if partition[node] == com]
            nx.draw_networkx_nodes(graph, pos, list_nodes, node_size=20, node_color=colors[count])
            count += 1

        nx.draw_networkx_edges(graph, pos, alpha=0.75)
    else:
        nx.draw_networkx(graph, node_size=20, alpha=0.75, with_labels=False, width=0.1)
        
    plt.savefig("../images/graph_{}{}.pdf".format(dict_name, index), bbox_inches="tight")

def search_communities(graph, graph_name):
    community_gen = community.k_clique_communities(graph, 2)
    print(list(community_gen))

    with open('communities_{}'.format(graph_name[13:]), 'wb') as file:
        pickle.dump(list(community_gen), file, protocol=pickle.HIGHEST_PROTOCOL)

def get_degree_centrality_csv(graph, graph_name):
    dc_dict_norm = nx.degree_centrality(graph)
    dc_dict = { key:int(round(value * (nx.number_of_nodes(graph) - 1))) for (key,value) in dc_dict_norm.items() }
    
    with open("../data/dc_norm_{}.csv".format(graph_name), "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["node", "degree centrality"])
        writer.writeheader()
        for key, value in dc_dict_norm.items():
            writer.writerow({"node": key.replace("\n", ""), "degree centrality": value})
    
    with open("../data/dc_{}.csv".format(graph_name), "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["node", "degree centrality"])
        writer.writeheader()
        for key, value in dc_dict.items():
            writer.writerow({"node": key.replace("\n", ""), "degree centrality": value})

def prune_graph(graph, lower, upper):
    dc_dict = nx.degree_centrality(graph)
    filtered = { key:value for (key,value) in dc_dict.items() if value < lower or value > upper }
    graph.remove_nodes_from(filtered)

    return graph

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help=".pickle file containing the dictionary.")
    parser.add_argument("-p", action="store_true", default=False, help="Plot the graph.")
    parser.add_argument("-a", action="store_true", default=False, help="Include isolated nodes to graph.")
    parser.add_argument("-s", action="store_true", default=False, help="Save the graph.")
    parser.add_argument("-c", action="store_true", default=False, help="Analyse communities with k-clique k=2.")
    parser.add_argument("-b", action="store_true", default=False, help="Show communities by best partition.")
    parser.add_argument("--degree", action="store_true", default=False, help="Get csv file of the degree centrality values.")
    parser.add_argument("--prune", nargs=2, type=float, metavar=("LOWER", "UPPER"),
                        help="Prune the graph with degree centrality. E.g. --prune 0.0001 0.001")
    parser.add_argument("--aff", help=".pickle file containing affiliation dictionary")
    parser.add_argument("-countries",action="store_true", default=False, help="Group affiliations by countries")
    args = parser.parse_args()
 
    if args.d:
        author_dict = queries.loadPickleDict(args.d)
    else:
        print("Using example graph\n")
        author_dict = generate_example_dict()

    if author_dict:
        if args.aff:
            affiliation_dict = queries.loadPickleDict(args.aff)
            coauthor_graph = generate_affiliation_graph(author_dict, affiliation_dict, args.a, args.countries)
        else:
            coauthor_graph = generate_graph(author_dict, args.a)

        if args.prune:
            coauthor_graph = prune_graph(coauthor_graph, args.prune[0], args.prune[1])
        if args.c:
            search_communities(coauthor_graph, args.d if args.d else "example.pickle")
        if args.p:
            show_graph(coauthor_graph, args.b)
        if args.s:
            graph_name = args.aff.split('/')[1].split('.')[0] if args.aff else args.d.split('/')[1].split('.')[0]
            if (args.countries):
                graph_name += "_country"
            save_graph(coauthor_graph, graph_name, args.b)
        if args.degree:
            graph_name = args.aff.split('/')[1].split('.')[0] if args.aff else args.d.split('/')[1].split('.')[0]
            if (args.countries):
                graph_name += "_country"
            get_degree_centrality_csv(coauthor_graph, graph_name)
    