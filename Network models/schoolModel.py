#S = 0, E=1, I=2, R=3

import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt


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
        if state[node] == 'S':
            susClique.append(node)
        if state[node] == 'I':
            infected += 1
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)
    newInfs = np.random.binomial(susceptible, effP)
    
    for nb in random.sample(susClique, newInfs):
        state[nb] = 'E'

    return newInfs
    
def incubate(node, state, p):
    r = random.random()
    if r < p:
        state[node] = 'I'

def recover(node, state, pr, pd):
    r = random.random()
    if r < pr:
        state[node] = 'R'
    if r > 1-pd:
        state[node] = 'D'

hhWeights = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5]

cliques = []

nNodes = 2*pow(10, 5)

seq = list(range(nNodes))

pD = {'BS': 0.0001, 'US': 0.0001, 'VS': 0.0001, 'A': 0.01, 'E':0.1 } 


state = ['S']*nNodes
ageGroup = [0]*nNodes
adults = []
children = []

#Household assignment

i = 0
cn = 0


random.shuffle(seq)

nBs = 30
nUs = 20
nVs = 15

hhCliques = []
bsCliques = []
for i in range(nBs):
    bsCliques.append([])
usCliques = []
for i in range(nUs):
    usCliques.append([])
vsCliques = []
for i in range(nVs):
    vsCliques.append([])


while(i < nNodes):
    fs = hhWeights[random.randint(0,len(hhWeights)-1)]
    t = min(i+fs, nNodes)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])

    ar = random.random()
    for j in range(i, min(t, i+2)):

        adults.append(seq[j])
        if fs > 2:
            ageGroup[seq[j]] = 'A'
        else:
            if ar < 1:
                ageGroup[seq[j]] = 'E'
        

        
    
    fBs = random.randint(0, nBs-1)
    fUs = random.randint(0, nUs-1) #Antar barne- og ungdomsskole er uavhengig
    #VGS er tilfeldig

    if fs > 2:
        for j in range(i+2, t):
            year = random.randint(0, 23)
            #if year < 6:
            #    ageGroup[seq[j]] = 'BH'
            if  (year < 13):
                ageGroup[seq[j]] = 'BS'
                bsCliques[fBs].append(j)
            elif year < 16:
                ageGroup[seq[j]] = 'US'
                usCliques[fUs].append(j)

            elif year < 19:
                ageGroup[seq[j]] = 'VS'
                vsCliques[random.randint(0, nVs-1)].append(j)

            else:
                ageGroup[seq[j]] = 'A'

            if year < 19:
                children.append(seq[j])
            else:
                adults.append(seq[j])

            
    hhCliques.append(clique)
    i = t


print "Households and schools created"
    



#Work assignment

i = 0

random.shuffle(adults)
wCliques = []
nAdults = len(adults)

while(i < nAdults):
    fs = random.randint(10, 500)
    t = min(i+fs, nAdults)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])
    wCliques.append(clique)
    i = t

print "Workplaces created"
    

#Random cliques

i = 0
random.shuffle(seq)
rCliques = []



sPinf = 0.001 #0.003 approx epidemic threshold for unrestricted
wPinf = 0.0005
hhPinf = 0.1
rPinf = 1*pow(10, -6)
rPinfQ = 1*pow(10, -7)

pinc = 1
prec = 0.2

i0 = 200

for i in range(i0):
    state[seq[i]] = 'I'

ht = []
lt = []
it = []
rt = []
hhinfs = 0
sinfs = 0
winfs = 0
rinfs = 0

relBs = 0000
relUs = 0000
relVs = 0000
relW = 1000
relR = 1000

cont = 1
i = 0
repeats = 0

while cont:
    
    cont = 0
    i+=1
    if i%10 == 0:
        print i
        
    for clique in hhCliques:
        hhinfs += day(clique, state, hhPinf)
        
        
    if i > relBs:
        for clique in bsCliques:
            sinfs += day(clique, state, pinf)
    if i > relUs:
        for clique in usCliques:
            sinfs += day(clique, state, pinf)
    if i > relVs:
        for clique in vsCliques:
            sinfs += day(clique, state, pinf)

    if i > relW:
        for clique in wCliques:
        #if len(clique) < 400:
    #    if random.random() < 0.8:
            winfs += day(clique, state, pinf)
        
    if i > relR:
        rinfs += day(seq, state, rPinf)
    else:
        rinfs += day(seq, state, rPinfQ)
    #for n in range(nNodes):
    #    if state[n] == 'I':
            
    #    day(genRandomClique(seq, nNodes), state, pinf)

        
    for node in range(nNodes):
        if state[node] == 'E':
            incubate(node, state, pinc)
        if state[node] == 'I':
            recover(node, state, prec, prec*pD)

    healthy = 0
    latent = 0
    infected = 0
    recovered = 0
    for j in state:
        if j == 'S':
            healthy+=1
        if j == 'E':
            latent+=1
            cont = 1
        if j == 'I':
            infected+=1
            cont = 1
        if j == 'R':
            recovered+=1
    ht.append(healthy)
    lt.append(latent)
    it.append(infected)
    rt.append(recovered)
    if (cont == 0):
        print i, "Reinfect", recovered, "Cases", hhinfs, "Household", sinfs, "School", winfs, "Work", rinfs, "Random"
        repeats += 1
        relBs = 0
        relUs = 0
        relVs = 0
        relW = 0
        relR = 0
        
        if repeats < 2:
            cont = 1
            random.shuffle(seq)
            for j in range(10):
                state[seq[j]] = 'I'
            #print seq[i], state[seq[i]]
        #for j in range(nNodes):
        #    if state[j] == 'I':
        #        print j
print max(ht), max(lt), max(it), max(rt)
print healthy, latent, infected, recovered
