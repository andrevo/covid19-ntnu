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

def recover(node, state, p):
    r = random.random()
    if r < p:
        state[node] = 'R'

hhWeights = [1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6]

cliques = []

nNodes = pow(10, 5)

seq = list(range(nNodes))

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

    for j in range(i, min(t, i+2)):
        ageGroup[seq[j]] = 'A'
        adults.append(seq[j])

    fBs = random.randint(0, nBs-1)
    fUs = random.randint(0, nUs-1) #Antar barne- og ungdomsskole er uavhengig
    #VGS er tilfeldig

    if fs > 2:
        for j in range(i+2, t):
            year = random.randint(1, 13)
            if year < 8:
                ageGroup[seq[j]] = 'B'
                bsCliques[fBs].append(j)
            elif year > 10:
                ageGroup[seq[j]] = 'V'
                vgsCliques[random.randint(0, nVs-1)].append(j)
            else:
                ageGroup[seq[j]] = 'U'
                usCliques[fUs].append(j)                
            children.append(seq[j])

            
    hhCliques.append(clique)
    i = t


print "Households and schools created"
    
#School assignment
#random.shuffle(children)

#for nodes in children:
#    fs = random.randint(10, 500)
    


#print "Schools created"


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



pinf = 0.0005 #0.003 approx epidemic threshold for unrestricted
hhPinf = 0.1
rPinf = 2*pow(10, -6)
rPinfQ = 1*pow(10, -9)

pinc = 1
prec = 0.1

for i in range(10):
    state[seq[i]] = 'I'

ht = []
lt = []
it = []
rt = []

relBs = 0000
relUs = 0000
relVs = 0000
relW = 10000
relR = 10000
 
cont = 1
i = 0
repeats = 0
while cont:
    
    cont = 0
    i+=1
    if i%10 == 0:
        print i
        
    for clique in hhCliques:
        cont = day(clique, state, hhPinf)

    if i > relBs:
        for clique in bsCliques:
            day(clique, state, pinf)
    if i > relUs:
        for clique in usCliques:
            day(clique, state, pinf)
    if i > relVs:
        for clique in vsCliques:
            day(clique, state, pinf)

    if i > relW:
        for clique in wCliques:
        #if len(clique) < 400:
    #    if random.random() < 0.8:
            day(clique, state, pinf)

    # if i > relR:
    #     day(seq, state, rPinf)
    # else:
    #     day(seq, state, rPinfQ)
    #for n in range(nNodes):
    #    if state[n] == 'I':
            
    #    day(genRandomClique(seq, nNodes), state, pinf)

        
    for node in range(nNodes):
        if state[node] == 'E':
            incubate(node, state, pinc)
        if state[node] == 'I':
            recover(node, state, prec)

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
        print i, "Reinfect", recovered
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
