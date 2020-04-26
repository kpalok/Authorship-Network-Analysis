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

def generate_graph(author_dict, all_nodes):
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
    nx.draw_networkx(graph, node_size=30, alpha=0.75, with_labels=False)
    plt.show()

def save_graph(graph, graph_name):
    plt.figure(num=None, figsize=(20, 20), dpi=100)
    plt.axis('off')
    nx.draw_networkx(graph, node_size=5, alpha=0.75, with_labels=False)
    plt.savefig("{}.pdf".format(graph_name[13:]), bbox_inches="tight")

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help=".pickle file containing the dictionary.")
    parser.add_argument("-p", action="store_true", default=False, help="Plot the graph.")
    parser.add_argument("-a", action="store_true", default=False, help="Include isolated nodes to graph.")
    parser.add_argument("-s", action="store_true", default=False, help="Save the graph.")
    parser.add_argument("-c", action="store_true", default=False, help="Analyse communities with k-clique k=2.")
    parser.add_argument("--degree", action="store_true", default=False, help="Get csv file of the degree centrality values.")
    args = parser.parse_args()

    if args.d:
        author_dict = queries.loadPickleDict(args.d)
    else:
        print("Using example graph\n")
        author_dict = generate_example_dict()

    if author_dict:
        coauthor_graph = generate_graph(author_dict, args.a)
        if args.c:
            search_communities(coauthor_graph, args.d if args.d else "example.pickle")
        if args.p:
            show_graph(coauthor_graph)
        if args.s:
            save_graph(coauthor_graph, args.d)
        if args.degree:
            get_degree_centrality_csv(coauthor_graph)
    