import random
import numpy as np
import copy
import networkx as nx



stateList = ['S', 'E', 'I', 'R', 'H', 'D']

def setRisk(ageFile, riskTableFile):
    riskTable = {}
    f = open(riskTableFile)
    for line in f:
        splitLine = line.rstrip().split('\t')
        riskTable[splitLine[0]] = float(splitLine[1])

    f.close()
    f = open(ageFile)
    atRisk = {}
    for line in f:
        splitLine = line.rstrip().split('\t')
        if random.random() < riskTable[splitLine[1]]:
            atRisk[splitLine[0]] = True
        else:
            atRisk[splitLine[1]] = False


def readModel(ageFile, cliqueFile):
    f = open(ageFile)
    ageGroup = []
    nodeID = 0
    for line in f:
        prevID = nodeID
        line = line.rstrip().split(';')
        nodeID = float(line[0])
        age = float(line[1])
        if (nodeID-prevID) != 1:
            print ('Out of sequence IDs')
        if age < 19:
            ageGroup.append('B')
        elif age < 55:
            ageGroup.append('A1')
        elif age < 65:
            ageGroup.append('A2')
        elif age < 80:
            ageGroup.append('E1')
        else:
            ageGroup.append('E2')
        

    f.close()
        
    layers = ['BH', 'BS', 'US', 'VS', 'W', 'HH', 'NH', 'R']
    translations = {'Kindergarten': 'BH', 'PrimarySchool': 'BS', 'Household':'HH', 'SecondarySchool': 'US', 'UpperSecondarySchool': 'VS', 'Workplace': 'W', 'NursingHome':'NH'}
    

    
    cliques = {}
    
    for layer in layers:
        cliques[layer] = []    

    f = open(cliqueFile)
    for line in f:
        #print line
        splitLine = line.rstrip().split(';')
        #print splitLine
        if (splitLine[1] != ''):
            clique = []
            for i in splitLine[1:]:
                clique.append(int(i)-1)
            
            cliques[translations[splitLine[0]]].append(clique)

    f.close()
    cliques['R'] = [range(len(ageGroup))]
    return layers, ageGroup, cliques

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
        state[nb] = ['E', day, max(day+1, round(day+np.random.normal(10, 3)))]
        
        
    return newInfs




#Turns latent into infectious
def incubate(node, state, p, day):
    r = random.random()
    if r < p:
        state[node][0] = 'I'
        
#Infectious to recovered, hospital, or back into susceptible
def recover(node, state, pr, ph, pni, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+ph:
        state[node] = ['H', day]
    elif r < pr+ph+pni:
        state[node] = ['S', day]

#Recovery on predetermined time schedule
def recoverTimed(node, state, ph, pni, day):

    if state[node][2] == day:
        r = random.random()
        if r < ph:
            state[node] = ['H', day, max(day+1, round(day+np.random.normal(10,3)))]
        elif r < ph+pni:
            state[node] = ['S', day]
        else:
            state[node] = ['R', day]

#Hospitalized to dead or recovered
def hospital(node, state, pr, pc, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+pc:
        state[node] = ['D', day]

#Hospitalization on predetermined time schedule
def hospitalTimed(node, state, pc, day):
    if state[node][2] == day:
        r = random.random()
        if r < pc:
            state[node] = ['D', day]
        else:
            state[node] = ['R', day]

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
            #recoverTimed(node, state, p['H'][ageGroup[node]], p['NI'], day)
            cont = True
        if state[node][0] == 'H':
            hospital(node, state, p['rec'], p['rec']*p['D'][ageGroup[node]], day)
            #hospitalTimed(node, state, p['D'][ageGroup[node]], day)
            cont = True
    
    return cont, lInfs, dailyInfs


def countState(state, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in state:
        count[node[0]] += 1
    return count

def genVector(layers):
    vec = {}
    for layer in layers:
        vec[layer] = 1
    return vec

def convertVector(inputVector):
    newVec = {}
    newVec = {}
    for layer in inputVector:
        if layer == 'S':
            newVec['BH'] = inputVector[layer]
            newVec['BS'] = inputVector[layer]
            newVec['US'] = inputVector[layer]
            newVec['VS'] = inputVector[layer]
        else:
            newVec[layer] = inputVector[layer]
    return newVec


def setStrategy(inputVector, probs, layers):

    newP = copy.deepcopy(probs)
    isOpen = {}
    for layer in inputVector:
        isOpen[layer] = bool(inputVector[layer])

    isOpen['NH'] = True
    isOpen['HH'] = True
    qFac = [0.1, 0.2, 0.5, 1]
    isOpen['R'] = True

    
    newP['inf']['R'] = qFac[inputVector['R']]*probs['inf']['R']
    
    return isOpen, newP


def fullRun(seedState, layers, cliques, ageGroup, strat, baseP):
    
    cont = 1
    i = 0
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    state = copy.copy(seedState)
    
    while cont:
        i+=1
        if i%10 == 0:
            print i

        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
        stateLog.append(countState(state, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i

def fullRunControl(seedState, layers, cliques, ageGroup, strat, baseP):
    
    cont = 1
    i = 0
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    state = copy.copy(seedState)
    
    while cont:
        i+=1
        if i%10 == 0:
            print i

        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
        stateLog.append(countState(state, stateList))

        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i


def findR(stateLog):
    newInfs = 0
    newRecs = 0
    
    for i in range(1, len(stateLog)):
        newRecs = stateLog[i]['R']-stateLog[i-1]['R']
        newInfs = stateLog[i-1]['S']-stateLog[i]['S']
        if newRecs > 10:
            return float(newInfs)/float(newRecs)
    return 0

def analyticalR(cliques, openLayers, state, p):
    expInfs = [0]*len(state)
    for layer in cliques:
            
        if openLayers[layer]:
            for clique in cliques[layer]:
                for node in clique:
                        
                    expInfs[node] += p['inf'][layer]*len(clique)

    rByNode = []

    for node in expInfs:
        rByNode.append(node/p['rec'])
    return np.mean(rByNode)

def genActivity(n, exp):
    activity = {}
    for node in range(n):
        activity[n] = int(pow(1-random.random(), exp))
    return activity
        
def randomLayer(act, state, p, day):
    for node in act:
        n = random.randint(1, act[node])
    clique = random.sample(state, n)
    newInfs = cliqueDay(clique, state, p, day)
    return newInfs
    
def genBlankState(n):
    state = []
    for i in range(n):
        state.append(['S', 0])
    return state
    

def seedState(state, n):
    for node in random.sample(range(len(state)), n):
        state[node] = ['I', 0, random.randint(1, 10)]
