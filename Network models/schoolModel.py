#S = 0, E=1, I=2, R=3

import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
import argparse

stateList = ['S', 'E', 'I', 'R', 'H', 'D']

def genRandomClique(seq, ub):
    rs = pow(random.random(), 0.5)
    cSize = min(1+int(1/rs), len(seq), ub)
    clique = random.sample(seq, cSize)
    return clique


#Runs infections over a day 
def cliqueDay(clique, state, p):

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

#Turns latent into infectious
def incubate(node, state, p):
    r = random.random()
    if r < p:
        state[node] = 'I'

#Infectious to recovered, hospital, or back into susceptible
def recover(node, state, pr, ph, pni):
    r = random.random()
    if r < pr:
        state[node] = 'R'
    elif r < pr+ph:
        state[node] = 'H'
    elif r < pr+pni:
        state[node] = 'S'

#Hospitalized to dead or recovered
def hospital(node, state, pr, pc):
    r = random.random()
    if r < pr:
        state[node] = 'R'
    elif r < pr+pc:
        state[node] = 'D'


#Distribution of household sizes

hhWeights = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5]



nNodes = 2*pow(10, 5) #Trondheim
#nNodes = 7*pow(10, 5) #Oslo

hCap = 100 #Max hospital capacity

seq = list(range(nNodes)) #Initializes nodes

#pD = {'B': 0.0001, 'A1': 0.0005, 'A2':0.005, 'E1':0.05, 'E2': 0.2 }

#Probability of hospitalization
pH = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184 } 

#Probability of death, once hospitalized (@capacity)
pD = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 } 

#Probability of death, once hospitalized (@overcapacity), TBD

layers = ['BH', 'BS', 'US', 'VS', 'W', 'HH', 'R']

cliques = {}
for layer in layers:
    cliques[layer] = []

state = ['S']*nNodes
ageGroup = [0]*nNodes
adults = [] #IDs of adults
children = [] #IDs of children
elderly = [] #IDs of elderly

#Household assignment

i = 0
cn = 0


random.shuffle(seq)

#Trondheim
n = {}
n['BH'] = 265
n['BS'] = 30
n['US'] = 20
n['VS'] = 15


#Oslo

#nBh = 733
#nBs= 115
#NUs = 62
#nVh = 29





for layer in ['BH', 'BS', 'US', 'VS']:
    for i in range(n[layer]):
        cliques[layer].append([])


ageGroups = ['B', 'A1', 'A2', 'E1', 'E2']
ageLists = {}
for group in ageGroups:
    ageLists[group] = []


i = 0
while(i < nNodes):
    fs = hhWeights[random.randint(0,len(hhWeights)-1)]
    t = min(i+fs, nNodes)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])

    ar = random.random()
    for j in range(i, min(t, i+2)):


        if fs > 2:
            if ar < 0.2:
                ageGroup[seq[j]] = 'A2'
            else:
                ageGroup[seq[j]] = 'A1'
            adults.append(seq[j])
        else:
            if ar < 0.3:
                ageGroup[seq[j]] = 'A1'
                adults.append(seq[j])
            elif ar < 0.6:
                ageGroup[seq[j]] = 'A2'
                adults.append(seq[j])
            elif ar < 0.9:
                ageGroup[seq[j]] = 'E1'
                elderly.append(seq[j])
            else:
                ageGroup[seq[j]] = 'E2'
                elderly.append(seq[j])

        
    fBh = random.randint(0, n['BH']-1)
    fBs = random.randint(0, n['BS']-1)
    fUs = random.randint(0, n['US']-1) #Antar barne- og ungdomsskole er uavhengig
    #VGS er tilfeldig

    if fs > 2:
        for j in range(i+2, t):
            year = random.randint(0, 23)
            if year < 6:
                ageGroup[seq[j]] = 'B'
                
                cliques['BH'][fBh].append(seq[j])
            if  (year < 13):
                ageGroup[seq[j]] = 'B'
                cliques['BS'][fBs].append(seq[j])
            elif year < 16:
                ageGroup[seq[j]] = 'B'
                cliques['US'][fUs].append(seq[j])

            elif year < 19:
                ageGroup[seq[j]] = 'B'
                cliques['VS'][random.randint(0, n['VS']-1)].append(seq[j])

            else:
                ageGroup[seq[j]] = 'A1'

            if year < 19:
                children.append(seq[j])

            else:
                adults.append(seq[j])

            
    cliques['HH'].append(clique)
    i = t



print "Households and schools created"

#Count number of people by age group
for node in seq:
    ageLists[ageGroup[node]].append(node)


#Work assignment

i = 0

random.shuffle(adults)

nAdults = len(adults)

while(i < nAdults):
    fs = random.randint(10, 500)
    t = min(i+fs, nAdults)
    clique = []
    for j in range(i, t):
        clique.append(adults[j])
    cliques['W'].append(clique)
    i = t

print "Workplaces created"
    

#Random cliques

i = 0
random.shuffle(seq)
rCliques = []
cliques['R'].append(seq)

#Layerwise infection probabilities 
pInfs = {'BH': 0.0002, 'BS': 0.0002, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -6), 'HH': 0.1}
qpr = {'BH': 0, 'BS': 0.0, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -6), 'HH': 0.1}

sPinf = 0.0002 #0.003 approx epidemic threshold for unrestricted (lolno)
wPinf = 0.0002
hhPinf = 0.1
rPinf = 0.5*pow(10, -6)
rPinfQ = 2.5*pow(10, -7)

pinc = 1
prec = 0.1
#prec = 0 #Debug
pni = 0.00

i0 = 20

for i in range(i0):
    state[seq[i]] = 'I'

tCounts = {}
for s in stateList:
    tCounts[s] = []

hospt = []
Reff = []

lInfs = {}
for layer in layers:
    lInfs[layer] = 0


dailyt = []
dailyrec = []

rel = {'BH': 000, 'BS': 000, 'US': 000, 'VS': 000, 'W': 000, 'R': 000, 'HH': 0}


cont = 1
i = 0
repeats = 0

#"Vaccination"
for node in seq:
    if ageGroup[node] in ['B', 'A1', 'A2']:
        if random.random() < 0:
            state[node] = 'R'

while cont:
    
    cont = 0
    i+=1
    if i%10 == 0:
        print i

    dailyInfs = 0
    
    for layer in layers:
        if True: #i > rel[layer]:
            for clique in cliques[layer]:
                infs = cliqueDay(clique, state, pInfs[layer])
                lInfs[layer] += infs
                dailyInfs += infs
                           
        
    for node in range(nNodes):
        if state[node] == 'E':
            incubate(node, state, pinc)
            cont = True
        if state[node] == 'I':
            recover(node, state, prec, prec*pH[ageGroup[node]], pni)
            cont = True
        if state[node] == 'H':
            hospital(node, state, prec, prec*pD[ageGroup[node]])
            cont = True

    counts = {}
    for s in stateList:
        counts[s] = 0
    
    for s in state:
        counts[s] += 1

    for s in stateList:
        tCounts[s].append(counts[s])
        
    if (i > 2):
        recoveries = tCounts['R'][-1]-tCounts['R'][-2]
        Reff.append(float(dailyInfs)/max(float(recoveries), 1))
        dailyrec.append(recoveries)
    
    dailyt.append(dailyInfs)


    if (cont == 0):
        print i, "Reinfect",
        for layer in layers:
            print layer, lInfs[layer],
        print ''
        repeats += 1
        for cond in rel:
            rel[cond] = 0

        
        if repeats < 2:
            cont = 1
            random.shuffle(seq)
            for j in range(10):
                state[seq[j]] = 'I'

    

for s in stateList:     
    print s, counts[s]
    
#print healthy, latent, infected, recovered, dead


dead = {}
for group in ageGroups:
    dead[group] = 0
    
for node in seq:
    if state[node] == 'D':
        dead[ageGroup[node]] += 1
print counts
print "Death count"

for group in ageGroups:
    print group, dead[group], 'dead out of', len(ageLists[group])
