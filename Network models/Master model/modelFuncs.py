import random
import numpy as np

stateList = ['S', 'E', 'I', 'R', 'H', 'D']

def genRandomClique(seq, ub):
    rs = pow(random.random(), 0.5)
    cSize = min(1+int(1/rs), len(seq), ub)
    clique = random.sample(seq, cSize)
    return clique


#Runs infections over a day 
def cliqueDay(clique, state, p, day):

    susceptible = 0
    infected = 0
    susClique = []
    for node in clique:
        if state[node][0] == 'S':
            susClique.append(node)
        if state[node][0] == 'I':
            infected += 1
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)
    #newInfs = np.random.binomial(susceptible, effP)
    newInfs = random.sample(susClique, np.random.binomial(susceptible, effP))
    for nb in newInfs:
        state[nb] = ['E', day]
        
        
    return newInfs




#Turns latent into infectious
def incubate(node, state, p, day):
    r = random.random()
    if r < p:
        state[node] = ['I', day]

#Infectious to recovered, hospital, or back into susceptible
def recover(node, state, pr, ph, pni, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+ph:
        state[node] = ['H', day]
    elif r < pr+ph+pni:
        state[node] = ['S', day]

#Hospitalized to dead or recovered
def hospital(node, state, pr, pc, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+pc:
        state[node] = ['D', day]


def systemDay(cliques, state, ageGroup, openLayer, p, day):

    cont = 0

    lInfs = {}
    dailyInfs = 0
    for layer in cliques:
        lInfs[layer] = 0
        if openLayer[layer]: #i > rel[layer]:
            for clique in cliques[layer]:
                infs = cliqueDay(clique, state, p['inf'][layer], day)
                #print infs
                lInfs[layer] += len(infs)
                dailyInfs += len(infs)
                
                           
        
    for node in range(len(state)):
        if state[node][0] == 'E':
            incubate(node, state, p['inc'], day)
            cont = True
        if state[node][0] == 'I':
            recover(node, state, p['rec'], p['rec']*p['H'][ageGroup[node]], p['NI'], day)
            cont = True
        if state[node][0] == 'H':
            hospital(node, state, p['rec'], p['rec']*p['D'][ageGroup[node]], day)
            cont = True
    
    return cont, lInfs, dailyInfs


def countState(state, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in state:
        count[node[0]] += 1
    return count


def convertVector(inputVector):
    newVec = []
    for i in range(4):
        newVec.append(inputVector[0])
    newVec.append(inputVector[1])
    newVec.append(1)
    newVec.append(inputVector[2])

    return newVec


def setStrategy(inputVector, probs, layers):

    newP = probs.copy()
    isOpen = {}
    for i in range(len(inputVector)):
        for layer in range(len(layers)):

            isOpen[layers[i]] = bool(inputVector[i])

    qFac = [0.1, 0.2, 0.5, 1]

    
    newP['inf']['R'] = qFac[inputVector[-1]]*probs['inf']['R']
    
    return isOpen, newP


