import networkx as nx
import numpy as np
import pandas as pd
from classes import *
from utilities import *
from parameters import *
from model import *

def loadNetwork(filename):
    nodes = pickle
    try:
        nodes = pickle.load( open('data/{}.pkl'.format(filename), 'rb'))
        print('Loaded nodes from pickle file')
    except:
        print('Failed loading network...')
    
    return nodes


def saveNetwork(filename, nodes):
    pickle.dump(nodes, open('data/{}.pkl'.format(filename), 'wb'))
    
    try:
        pickle.dump(nodes, open('data/{}.pkl'.format(filename), 'wb'))
    except:
        print('Failed saving network...')


def createNetwork(nodes):
    G = nx.Graph
    for node in nodes.values():
        if node.state == 'R' or node.state == 'E':
            print(node.infAnc, len(node.infDesc))


def main():
    createNetwork(nodes)


if __name__ == '__main__':
    main()
