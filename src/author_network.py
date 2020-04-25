import argparse
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint

def generate_example_dict():
    dict = {
        "author1": [("author2", "", 3), ("author3", "", 4), ("author4", "", 2)],
        "author2": [("author1", "", 3), ("author3", "", 3), ("author4", "", 5)],
        "author3": [("author1", "", 4), ("author2", "", 3), ("author6", "", 2)],
        "author4": [("author1", "", 2), ("author2", "", 5), ("author7", "", 1)]
        }

    return dict

def generate_graph(author_dict):
    coauthor_graph = nx.Graph()

    coauthor_graph.add_nodes_from(author_dict.keys())

    for author, coauthors in author_dict.items():
        for coauthor in coauthors:
            if coauthor[2] >= 2:
                coauthor_graph.add_edge(author, coauthor[0])
            else:
                if not coauthor_graph.has_node(coauthor[0]):
                    coauthor_graph.add_node(coauthor[0])

    return coauthor_graph

def show_graph(graph):
    nx.draw(graph)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help=".pickle file containing the dictionary.")
    parser.add_argument("-p", action="store_true", default=False, help="If set, plots the graph.")
    args = parser.parse_args()

    if args.d:
        with open(args.d, "rb") as file:
            author_dict = pickle.load(file)
    else:
        print("Using example graph\n")
        author_dict = generate_example_dict()

    if author_dict:
        coauthor_graph = generate_graph(author_dict)
        if args.p:
            show_graph(coauthor_graph)
    