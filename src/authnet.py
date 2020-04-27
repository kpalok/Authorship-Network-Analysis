import os.path
import argparse
import pickle
import queries
import csv
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

def generate_affiliation_graph(author_dict, affiliation_dict, all_nodes):
    coauthor_graph = nx.Graph()
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

def show_graph(graph):
    nx.draw_networkx(graph, node_size=30, alpha=0.75, with_labels=False, width=0.1)
    plt.show()

def save_graph(graph):
    index = 0
    while os.path.isfile("graph_{}.pdf".format(index)):
        index += 1

    plt.figure(num=None, figsize=(20, 20), dpi=100)
    plt.axis('off')
    nx.draw_networkx(graph, node_size=5, alpha=0.75, with_labels=False, width=0.1)
    plt.savefig("graph_{}.pdf".format(index), bbox_inches="tight")

def search_communities(graph, graph_name):
    community_gen = community.k_clique_communities(graph, 2)
    print(list(community_gen))

    with open('communities/{}'.format(graph_name[13:]), 'wb') as file:
        pickle.dump(list(community_gen), file, protocol=pickle.HIGHEST_PROTOCOL)

def get_degree_centrality_csv(graph):
    dc_dict = nx.degree_centrality(graph)

    index = 0
    while os.path.isfile("dc_{}.csv".format(index)):
        index += 1
    
    with open("dc_{}.csv".format(index), "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["node", "degree centrality"])
        writer.writeheader()
        for key, value in dc_dict.items():
            writer.writerow({"node": key, "degree centrality": value})

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
    parser.add_argument("--degree", action="store_true", default=False, help="Get csv file of the degree centrality values.")
    parser.add_argument("--prune", nargs=2, type=float, metavar=("LOWER", "UPPER"),
                        help="Prune the graph with degree centrality. E.g. --prune 0.0001 0.001")
    parser.add_argument("--aff", help=".pickle file containing affiliation dictionary")
    args = parser.parse_args()
 
    if args.d:
        author_dict = queries.loadPickleDict(args.d)
    else:
        print("Using example graph\n")
        author_dict = generate_example_dict()

    if author_dict:
        if args.aff:
            affiliation_dict = queries.loadPickleDict(args.aff)
            coauthor_graph = generate_affiliation_graph(author_dict, affiliation_dict, args.a)
        else:
            coauthor_graph = generate_graph(author_dict, args.a)

        if args.prune:
            coauthor_graph = prune_graph(coauthor_graph, args.prune[0], args.prune[1])
        if args.c:
            search_communities(coauthor_graph, args.d if args.d else "example.pickle")
        if args.p:
            show_graph(coauthor_graph)
        if args.s:
            save_graph(coauthor_graph)
        if args.degree:
            get_degree_centrality_csv(coauthor_graph)
    