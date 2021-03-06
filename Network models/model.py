#S = 0, E=1, I=2, R=3

import networkx as nx
import random
import numpy as np


def infect(network, node, state, p):
    susNbs = []
    for nb in list(nx.neighbors(network, node)):
        if state[nb] == 0:
            susNbs.append(nb)
    infs = np.random.binomial(len(susNbs), p)
    newInf = random.sample(susNbs, infs)
    for nb in newInf:
        state[nb] = 1
    
def incubate(node, state, p):
    r = random.random()
    if r < p:
        state[node] = 2

def recover(node, state, p):
    r = random.random()
    if r < p:
        state[node] = 3

hhWeights = [1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6]

cliques = []

nNodes = pow(10, 3)

seq = list(range(nNodes))

state = [0]*nNodes


#Household assignment
hhNet = nx.Graph()

i = 0
cn = 0

random.shuffle(seq)

while(i < nNodes):
    fs = hhWeights[random.randint(0,len(hhWeights)-1)]
    t = min(i+fs, nNodes)
    for j in range(i, t):
        hhNet.add_node(seq[j])
    for j in range(i, t):
        for k in range(i, t):
            if (j != k):
                hhNet.add_edge(seq[j], seq[k])
    i = t
    


#Work assignment
wNet = nx.Graph()

i = 0

random.shuffle(seq)

while(i < nNodes):
    fs = random.randint(10, 500)
    t = min(i+fs, nNodes)
    for j in range(i, t):
        for k in range(i, t):
            if (j != k):
                wNet.add_edge(seq[j], seq[k])
    i = t


combo = hhNet.copy()

for edge in wNet.edges():
    combo.add_edge(edge[0], edge[1])



pinf = 0.005
pinc = 0.1
prec = 0.1

state[0] = 1

for i in range(100):
    print i
    for node in range(nNodes):
        if state[node] == 1:
            incubate(node, state, pinc)
        if state[node] == 2:
            infect(wNet, node, state, pinf)
            infect(hhNet, node, state, pinf)
            recover(node, state, prec)
