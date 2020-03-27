#S = 0, E=1, I=2, R=3

import networkx as nx
import random
import numpy as np


def genRandomClique(seq, ub):
    rs = pow(random.random(), 0.5)
    cSize = min(1+int(1/rs), len(seq), ub)
    clique = random.sample(seq, cSize)
    return clique

def day(clique, state, p):

    susceptible = 0
    infected = 0
    susClique = []
    for node in clique:
        if state[node] == 0:
            susClique.append(node)
        if state[node] == 2:
            infected += 1
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)
    newInfs = np.random.binomial(susceptible, effP)

    
    for nb in random.sample(susClique, newInfs):
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

nNodes = pow(10, 5)

seq = list(range(nNodes))

state = [0]*nNodes


#Household assignment

i = 0
cn = 0


random.shuffle(seq)

hhCliques = []

while(i < nNodes):
    fs = hhWeights[random.randint(0,len(hhWeights)-1)]
    t = min(i+fs, nNodes)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])
    hhCliques.append(clique)
    i = t
    
#Work assignment

i = 0

random.shuffle(seq)
wCliques = []

while(i < nNodes):
    fs = random.randint(10, 500)
    t = min(i+fs, nNodes)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])
    wCliques.append(clique)
    i = t



#Random cliques

i = 0
random.shuffle(seq)
rCliques = []



pinf = 0.03 #0.003 approx epidemic threshold for unrestricted
pinc = 0.1
prec = 0.1

for i in range(10):
    state[i] = 1 

ht = []
lt = []
it = []
rt = []

for i in range(100):
    if i%1 == 0:
        print i
    for clique in hhCliques:
        day(clique, state, pinf)
    #for clique in wCliques:
        #if len(clique) < 400:
    #    if random.random() < 0.8:
    #        day(clique, state, pinf)

    for n in range(5*nNodes):
        day(genRandomClique(seq, nNodes), state, pinf)

        
    for node in range(nNodes):
        if state[node] == 1:
            incubate(node, state, pinc)
        if state[node] == 2:
            recover(node, state, prec)

    healthy = 0
    latent = 0
    infected = 0
    recovered = 0
    for i in state:
        if i == 0:
            healthy+=1
        if i == 1:
            latent+=1
        if i == 2:
            infected+=1
        if i == 3:
            recovered+=1
    ht.append(healthy)
    lt.append(latent)
    it.append(infected)
    rt.append(recovered)


print max(ht), max(lt), max(it), max(rt)
print healthy, latent, infected, recovered
