import sys
import random
import numpy as np
import copy
import networkx as nx
from InitializeParams import *



stateList = ['S', 'E', 'Ia', 'Ip', 'Is', 'R', 'H', 'ICU', 'D']

#age rounding function
def roundAge(age):
    return min(age-age%10, 80)


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
        attrs[nodeID]['decade'] = min(age-age%10, 80)
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

    for node in attrs:
        attrs[node]['cliques'] = []
        attrs[node]['state'] = 'S'
        attrs[node]['aware'] = False
        attrs[node]['markForSymptoms'] = False
        attrs[node]['sick'] = False
        attrs[node]['inNursing'] = False
        attrs[node]['spreading'] = {}
        for layer in layers:
            attrs[node]['spreading'][layer] = False
    
        
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

            
            cName = translations[splitLine[0]]
            if cName == 'NH':
                for node in clique:
                    attrs[node]['inNursing'] = True
                
            cliques[cName].append(clique)
            for node in clique:
                attrs[node]['cliques'].append([cName, len(cliques[cName])-1])

        
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
            if attrs[node][attrID] > cutoff:
                newClique.append(node)
        if mode == 'lowPass':
            if attrs[node][attrID] < cutoff:
                newClique.append(node)
    return newClique


def infectNode(attrs, node, anc, layer, day):
    attrs[node]['state'] = 'E'
    attrs[node]['lastChangeDay'] = day
    attrs[node]['infAnc'] = [anc, layer]
    attrs[anc]['infDesc'].append([node, layer])

#Runs infections over a day
def cliqueDay(clique, attrs, layer, p, day):

    susceptible = 0
    infected = 0
    infClique = []
    susClique = []
    
    for node in clique:
        if attrs[node]['state'] == 'S':
            susClique.append(node)
        if attrs[node]['spreading'][layer]:
            infClique.append(node)
    infected = len(infClique)
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)

    newInfs = random.sample(susClique, np.random.binomial(susceptible, effP))
    for nb in newInfs:
        ancestor = random.choice(infClique)
        infectNode(attrs, nb, ancestor, layer, day)
        
    return newInfs


#Daily state progress check and branching functions
def incubate(node, attrs, p, day):
    if random.random() < p['inc']:
        if random.random() < p['S'][attrs[node]['decade']]:
            turnPresymp(node, attrs, p, day)
        else:
            turnAsymp(node, attrs, p, day)
    
def asymptomatic(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
        recover(node, attrs, p, day)

def preSymptomatic(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
        activateSymptoms(node, attrs, p, day)
        
def symptomatic(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
        if attrs[node]['nextState'] == 'D':
            die(node, attrs, p, day)
        elif attrs[node]['nextState'] == 'H':
            hospitalize(node, attrs, p, day)
        else:
            recover(node, attrs, p, day)

def hospital(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
        
        if attrs[node]['nextState'] == 'ICU':
            enterICU(node, attrs, p, day)
        elif attrs[node]['nextState'] == 'R':
            recover(node, attrs, p, day)
        elif attrs[node]['nextState'] == 'D':
            die(node, attrs, p, day)

def ICU(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
        if attrs[node]['nextState'] == 'D':
            die(node, attrs, p, day)
        elif attrs[node]['nextState'] == 'R':
            recover(node, attrs, p, day)

            
#State change functions
def recover(node, attrs, p, day):
    attrs[node]['state'] = 'R'
    attrs[node]['lastDay'] = day
    attrs[node]['sick'] = False
    for layer in attrs[node]['spreading']:
        attrs[node]['spreading'][layer] = False
        
    if random.random() < p['NI']:
        attrs[node]['nextState'] = 'S'

        
def turnAsymp(node, attrs, p, day):
    attrs[node]['state'] = 'Ia'
    attrs[node]['nextState'] = 'R'
    attrs[node]['nextDay'] = day+1+np.random.poisson(dur['AS-R'])
    attrs[node]['sick'] = True
    for layer in attrs[node]['spreading']:
        attrs[node]['spreading'][layer] = True
    
def turnPresymp(node, attrs, p, day):
    attrs[node]['state'] = 'Ip'
    attrs[node]['nextState'] = 'Is'
    attrs[node]['nextDay'] = day+1+np.random.poisson(dur['PS-I'])
    attrs[node]['sick'] = True
    for layer in attrs[node]['spreading']:
        attrs[node]['spreading'][layer] = True

    
def activateSymptoms(node, attrs, p, day):
    attrs[node]['state'] = 'Is'
    attrs[node]['lastDay'] = day
    for layer in ['BH', 'BS', 'US', 'VS', 'W', 'NH', 'R']:
        attrs[node]['spreading'][layer] = False
        
    attrs[node]['spreading'] 
    if attrs[node]['inNursing']:
        if random.random() < p['DRage'][attrs[node]['decade']]:
            attrs[node]['nextState'] = 'D'
            attrs[node]['nextDay'] = day+1+np.random.poisson(dur['I-D'])
        else:
            attrs[node]['nextState'] = 'R'
            attrs[node]['nextDay'] = day+1+np.random.poisson(dur['I-R'])

            
    elif random.random() < p['HRage'][attrs[node]['decade']]:
        attrs[node]['nextState'] = 'H'
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['I-H'])
    else:
        attrs[node]['nextState'] = 'R'
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['I-R'])

        
def hospitalize(node, attrs, p, day):
    attrs[node]['state'] = 'H'
    attrs[node]['lastDay'] = day
    for layer in ['HH', 'NH']:
        attrs[node]['spreading'][layer] = False 



        
    if random.random() < p['ICUage'][attrs[node]['decade']]:
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['H-ICU'])
        attrs[node]['nextState'] = 'ICU'
        
    elif random.random() < p['DRage'][attrs[node]['decade']]:
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['H-D'])
        attrs[node]['nextState'] = 'D'
    else:
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['H-R'])
        attrs[node]['nextState'] = 'R'

    
def enterICU(node, attrs, p, day):
    attrs[node]['state'] = 'ICU'
    attrs[node]['lastDay'] = day

    if random.random() < p['DRage'][attrs[node]['decade']]:
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['ICU-D'])
        attrs[node]['nextState'] = 'D'
    else:
        attrs[node]['nextDay'] = day+1+np.random.poisson(dur['ICU-R'])
        attrs[node]['nextState'] = 'R'

        
def die(node, attrs, p, day):
    attrs[node]['diedFrom'] = attrs[node]['state']
    attrs[node]['state'] = 'D'
    attrs[node]['lastDay'] = day
    attrs[node]['nextDay'] = -1
    attrs[node]['nextState'] = ''
    attrs[node]['sick'] = False
    for layer in attrs[node]['spreading']:
        attrs[node]['spreading'][layer] = False

def stateFunction(state):
    funcs = {
        'E': incubate,
        'Ia': asymptomatic,
        'Ip': preSymptomatic,
        'Is': symptomatic,
        'H': hospital,
        'ICU': ICU
        }
    return funcs[state]

def ifSwitch(node, attrs, p, day):
    if attrs[node]['state'] == 'E':
        incubate(node, attrs, p, day)
    

#Daily pulse
def systemDay(cliques, attrs, openLayer, p, day):

    cont = 0

    lInfs = {}
    dailyInfs = 0
    for layer in cliques:
        lInfs[layer] = 0

        if (openLayer[layer] & (layer != 'R')): #i > rel[layer]:
            for clique in cliques[layer]:
                infs = cliqueDay(clique, attrs, layer, p['inf'][layer], day)
                lInfs[layer] += len(infs)
                dailyInfs += len(infs)
        
    lInfs['Rp'] = dynRandomLayer(attrs, cliques['R'][0], p['inf']['dynR'], day)
                
        
    for node in attrs:
        if (attrs[node]['sick'] | (attrs[node]['state'] == 'E')):
            stateFunction(attrs[node]['state'])(node, attrs, p, day)
            #ifSwitch(node, attrs, p, day)
            cont = True
    return cont, lInfs, dailyInfs


def countState(attrs, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in attrs:
        count[attrs[node]['state']] += 1
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
    newP['inf']['dynR'] = qFac[inputVector['R']]*probs['inf']['dynR']
    
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

    stateLog.append(countState(attrs, stateList))
    
    while cont:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
            


        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
        stateLog.append(countState(attrs, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i

def timedRun(attrs, layers, cliques, strat, baseP, curDay, runDays):
    
    cont = 1
    i = curDay
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    endDay = curDay+runDays
    
    while i < endDay:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
        
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


def directR(attrs):
    ageGroups = ['B', 'A1', 'A2', 'E1', 'E2']
    infs = {}
    for grp in ageGroups:
        infs[grp] = 0
        
    for node in attrs:
        if attrs[node]['state'] == 'R':
            infs[attrs[node]['ageGroup']] += len(attrs[node]['infDesc'])

    return infs
    

#Generate activity for a set of nodes, according to power law
def genActivity(attrs, dynParams):
    mode = dynParams[0]
    var = dynParams[1]
    exp = dynParams[2]
    for node in attrs:
        if (attrs[node]['ageGroup'] in ['A1', 'A2', 'E1']):
            attrs[node]['act'] = int(max(np.random.normal(mode, var), 1) + pow(random.random(), exp))
        else:
            attrs[node]['act'] = int(max(np.random.normal(mode, var), 1))

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
    newInfs = cliqueDay(clique, attrs, 'R', p, day)
    return newInfs


#Node-based power law spread on a random layer
def dynRandomLayer(attrs, layer, p, day):
    infs = 0
    for node in layer:
        if attrs[node]['spreading']['R']:
            conns = min(random.randint(0, attrs[node]['act']), len(layer))
            for nNode in random.sample(layer, conns):
                #print node, nNode, attrs[nNode]['state']
                if attrs[nNode]['state'] == 'S':
                    if random.random() < p:
                        infectNode(attrs, nNode, node, 'dynR', day)
                        infs += 1
                #print node, nNode, attrs[nNode]['state']
                
        if attrs[node]['state'] == 'S':
            conns = min(random.randint(0, attrs[node]['act']), len(layer))
            iNeighbors = 0
            for nNode in random.sample(layer, conns):
                if attrs[nNode]['spreading']['R']:
                    iNeighbors += 1
            if random.random() < 1-pow(1-p, iNeighbors):
                infectNode(attrs, node, nNode, 'dynR', day)
                infs += 1


    return infs



def genBlankState(attrs):
    for node in attrs:
        attrs[node]['state'] = 'S'
        attrs[node]['infAnc'] = -1
        attrs[node]['infDesc'] = []

def seedState(attrs, n):
    for node in random.sample(attrs.keys(), n):
        attrs[node]['state'] = 'E'
        attrs[node]['sick'] = True
