import random
import numpy as np
import copy
import networkx as nx



stateList = ['S', 'E', 'I', 'R', 'H', 'ICU', 'VT', 'D']

#Initialize full model
def initModel(ageFile, cliqueFile, riskTableFile, baseP, dynParams, n):
    layers, attrs, cliques = readModel(ageFile, cliqueFile)
    #setRisk(ageFile, riskTableFile, attrs)
    genActivity(attrs, dynParams)

    
    genBlankState(attrs)
    seedState(attrs, n)

    return layers, attrs, cliques
    
#Sets binary risk from file

def setRisk(ageFile, riskTableFile, attrs):
    riskTable = {}
    f = open(riskTableFile)
    for line in f:
        splitLine = line.rstrip().split('\t')
        riskTable[splitLine[0]] = float(splitLine[1])
    f.close()

    
    f = open(ageFile)
    
    for line in f:
        splitLine = line.rstrip().split('\t')
        if random.random() < riskTable[splitLine[1]]:
            attrs[splitLine[0]]['atRisk'] = True
        else:
            attrs[splitLine[1]]['atRisk'] = False


            
#Builds household/school/work structure from file
def readModel(ageFile, cliqueFile):

    f = open(ageFile)
    nodeID = -1
    attrs = {}
    
    for line in f:
        prevID = nodeID
        line = line.rstrip().split(';')
        nodeID = int(line[0])-1
        age = int(line[1])
        
        attrs[nodeID] = {}
        attrs[nodeID]['age'] = age
        if (nodeID-prevID) != 1:
            print ('Out of sequence IDs'), nodeID, prevID
        if age < 19:
            attrs[nodeID]['ageGroup'] = 'B'
        elif age < 55:
            attrs[nodeID]['ageGroup'] = 'A1'
        elif age < 65:
            attrs[nodeID]['ageGroup'] = 'A2'
        elif age < 80:
            attrs[nodeID]['ageGroup'] = 'E1'
        else:
            attrs[nodeID]['ageGroup'] = 'E2'



    f.close()


    layers = ['BH', 'BS', 'US', 'VS', 'W', 'HH', 'NH', 'R']
    translations = {'Kindergarten': 'BH', 'PrimarySchool': 'BS', 'Household':'HH', 'SecondarySchool': 'US', 'UpperSecondarySchool': 'VS', 'Workplace': 'W', 'NursingHome':'NH'}


    cliques = {}

    
    for layer in layers:
        cliques[layer] = []    

    f = open(cliqueFile)
    for line in f:

        splitLine = line.rstrip().split(';')

        if (splitLine[1] != ''):
            clique = []
            for i in splitLine[1:]:
                clique.append(int(i)-1)
            
            cliques[translations[splitLine[0]]].append(clique)

    f.close()
    cliques['R'] = [range(len(attrs))]
    return layers, attrs, cliques








def filterCliqueAge(clique, age, cutoff, mode):
    newClique = []
    for node in clique:
        if mode == 'highPass':
            if attrs[node]['age'] > cutoff:
                newClique.append(node)
        if mode == 'lowPass':
            if attrs[node]['age'] < cutoff:
                newClique.append(node)
    return newClique



def filterCliqueRisk(clique, atRisk, mode):
    newClique = []
    for node in clique:
        if mode == 'highPass':
            if atRisk[node]:
                newClique.append(node)
        if mode == 'lowPass':
            if not atRisk[node]:
                newClique.append(node)
    return newClique    



def filterCliqueAttribute(clique, attrs, attrID, cutoff, mode):
    newClique = []
    for node in clique:
        if mode == 'highPass':
            if attribute[attrID] > cutoff:
                newClique.append(node)
        if mode == 'lowPass':
            if attribute[attrID] < cutoff:
                newClique.append(node)
    return newClique


#Runs infections over a day
def cliqueDay(clique, attrs, p, day):

    susceptible = 0
    infected = 0
    susClique = []
    for node in clique:
        if attrs[node]['state'][0] == 'S':
            susClique.append(node)
        if attrs[node]['state'][0] == 'I':
            infected += 1
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)

    newInfs = random.sample(susClique, np.random.binomial(susceptible, effP))
    for nb in newInfs:
        attrs[nb]['state'] = ['E', day, max(day+1, round(day+np.random.normal(10, 3)))]

        
    return newInfs



#Turns latent into infectious
def incubate(node, attrs, p, day):
    r = random.random()
    if r < p:
        attrs[node]['state'][0] = 'I'
        
#Infectious to recovered, hospital, or back into susceptible
def recover(node, attrs, pr, ph, pni, day):
    r = random.random()
    if r < pr:
        attrs[node]['state'] = ['R', day]
    elif r < pr+ph:
        attrs[node]['state'] = ['H', day]
    elif r < pr+ph+pni:
        attrs[node]['state'] = ['S', day]

#Recovery on predetermined time schedule
def recoverTimed(node, attrs, ph, pni, picu, day):
    
    if attrs[node]['state'][2] == day:
        r = random.random()
        if r < ph:
            if random.random() < picu:
                attrs[node]['state'] = ['H', day, max(day+1, round(day+np.random.normal(6,3))), 'ICU flag']
            else:
                attrs[node]['state'] = ['H', day, max(day+1, round(day+np.random.normal(8,3)))]
        elif r < ph+pni:
            attrs[node]['state'] = ['S', day]
        else:
            attrs[node]['state'] = ['R', day]


    
#Hospitalized to dead or recovered
def hospital(node, attrs, pr, pc, day):
    r = random.random()
    if r < pr:
        attrs[node]['state'] = ['R', day]
    elif r < pr+pc:
        attrs[node]['state'] = ['D', day]
        
#Hospitalization on predetermined time schedule
def hospitalTimed(node, attrs, pc, day):
    if attrs[node]['state'][2] == day:
        r = random.random()
        if len(attrs[node]['state']) == 4:
            attrs[node]['state'] = ['ICU', day, max(day+1, round(day+np.random.normal(10,3)))]
        elif r < pc:
            attrs[node]['state'] = ['D', day]
        else:
            attrs[node]['state'] = ['R', day]

            
def systemDay(cliques, attrs, openLayer, p, day):

    cont = 0

    lInfs = {}
    dailyInfs = 0
    for layer in cliques:
        lInfs[layer] = 0

        if (openLayer[layer] & (layer != 'R')): #i > rel[layer]:
            for clique in cliques[layer]:
                infs = cliqueDay(clique, attrs, p['inf'][layer], day)
                #print infs
                lInfs[layer] += len(infs)
                dailyInfs += len(infs)
        
    lInfs['Rp'] = dynRandomLayer(attrs, cliques['R'][0], p['inf']['dynR'], day)
                
        
    for node in range(len(attrs)):
        if attrs[node]['state'][0] == 'E':
            incubate(node, attrs, p['inc'], day)
            cont = True
        if attrs[node]['state'][0] == 'I':
            #recover(node, state, p['rec'], p['rec']*p['H'][ageGroup[node]], p['NI'], day)
            recoverTimed(node, attrs, p['H'][attrs[node]['ageGroup']], p['NI'], 0.3, day)
            cont = True
        if attrs[node]['state'][0] == 'H':
            #hospital(node, state, p['rec'], p['rec']*p['D'][ageGroup[node]], day)
            hospitalTimed(node, attrs, p['D'][attrs[node]['ageGroup']], day)
            cont = True
        if attrs[node]['state'][0] == 'ICU':
            hospitalTimed(node, attrs, p['D'][attrs[node]['ageGroup']], day)
    
    return cont, lInfs, dailyInfs


def countState(attrs, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in attrs:
        count[attrs[node]['state'][0]] += 1
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


def fullRun(seedAttrs, layers, cliques, strat, baseP):
    
    cont = 1
    i = 0
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)
    
    while cont:
        i+=1
        if i%10 == 0:
            print i

        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
        stateLog.append(countState(attrs, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i

def fullRunControl(seedAttrs, layers, cliques, strat, baseP):
    
    cont = 1
    i = 0
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)
    
    while cont:
        i+=1
        if i%10 == 0:
            print i

        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
        stateLog.append(countState(attrs, stateList))

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


def analyticalR(cliques, openLayers, attrs, p):
    expInfs = [0]*len(attrs)
    for layer in cliques:
            
        if openLayers[layer]:
            for clique in cliques[layer]:
                for node in clique:
                        
                    expInfs[node] += p['inf'][layer]*len(clique)

    rByNode = []

    for node in expInfs:
        rByNode.append(node/p['rec'])
    return np.mean(rByNode)


#Generate activity for a set of nodes, according to power law
def genActivity(attrs, dynParams):
    mode = dynParams[0]
    var = dynParams[1]
    exp = dynParams[2]
    for node in range(len(attrs)):
        attrs[node]['act'] = int(max(np.random.normal(mode, var), 1) + pow(random.random(), exp))


#Generate random cliques according to power law
def genRandomClique(seq, ub):
    rs = pow(random.random(), 0.5)
    cSize = min(1+int(1/rs), len(seq), ub)
    clique = random.sample(seq, cSize)
    return clique

#Generate random cliques centered around nodes and infects them
def randomLayer(attrs, p, day):
    for node in attrs:
        n = random.randint(1, attrs[node]['act'])
    clique = random.sample(attrs, n)
    newInfs = cliqueDay(clique, attrs, p, day)
    return newInfs


#Node-based power law spread on a random layer
def dynRandomLayer(attrs, layer, p, day):
    infs = 0
    for node in layer:
        if attrs[node]['state'][0] == 'I':
            conns = min(random.randint(0, attrs[node]['act']), len(layer))
            for nNode in random.sample(layer, conns):
                #print node, nNode, attrs[nNode]['state']
                if attrs[nNode]['state'][0] == 'S':
                    if random.random() < p:
                        attrs[nNode]['state'] = ['E', day, max(day+1, round(day+np.random.normal(10, 3)))]
                                            
                        infs += 1
                #print node, nNode, attrs[nNode]['state']
                
        if attrs[node]['state'] == 'S':
            conns = random.randint(0, attrs[node]['act'])
            iNeighbors = 0
            for nNode in random.sample(layer, conns):
                if attrs[nNode]['state'][0] == 'I':
                    iNeighbors += 1
            if random.random() < 1-pow(1-p, iNeighbors):
                if random.random() < p:
                    attrs[node]['state'] = ['E', day, max(day+1, round(day+np.random.normal(10, 3)))]
                    infs += 1


    return infs



def genBlankState(attrs):
    for node in attrs:
        attrs[node]['state'] = ['S', 0]
        

def seedState(attrs, n):
    for node in random.sample(attrs.keys(), n):
        attrs[node]['state'] = ['I', 0, random.randint(1, 10)]

