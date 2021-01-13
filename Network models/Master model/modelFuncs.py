import sys
import random
import numpy as np
import copy
import time
#import networkx as nx
from InitializeParams import *



stateList = ['S', 'E', 'Ia', 'Ip', 'Is', 'R', 'H', 'ICU', 'D']

#age rounding function
def roundAge(age):
    return min(age-age%10, 80)


#Initialize full model
def initModel(ageFile, cliqueFile, riskTableFile, baseP, dynParams, n):
    layers, attrs = readModel(ageFile, cliqueFile)
    #setRisk(ageFile, riskTableFile, attrs)
    genActivity(attrs, dynParams)

    
    genBlankState(attrs)
    seedState(attrs, n)

    return layers, attrs
    
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
        nodeID = line[0]
        age = int(line[1])
        
        attrs[nodeID] = {}
        attrs[nodeID]['age'] = age
        attrs[nodeID]['decade'] = min(age-age%10, 80)
#        if (nodeID-prevID) != 1:
#            print ('Out of sequence IDs'), nodeID, prevID
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

    layers = {'BH':{}, 'BS':{}, 'US':{}, 'VS':{}, 'W':{}, 'HH':{}, 'NH':{}, 'R':{}}

    for node in attrs:
        attrs[node]['cliques'] = []
        attrs[node]['state'] = 'S'
        attrs[node]['quarantine'] = False
        attrs[node]['sick'] = False
        attrs[node]['inNursing'] = False
        attrs[node]['present'] = {}
        for layer in layers:
            attrs[node]['present'][layer] = True
    
        
    translations = {'Kindergarten': 'BH', 'PrimarySchool': 'BS', 'Household':'HH', 'SecondarySchool': 'US', 'UpperSecondarySchool': 'VS', 'Workplace': 'W', 'NursingHome':'NH'}




    for layer in layers:
        layers[layer]['cliques'] = []
        layers[layer]['open'] = True

    f = open(cliqueFile)
    for line in f:

        splitLine = line.rstrip().split(';')

        
        if (splitLine[1] != '') & (splitLine[0].split('_')[0] != 'Commuters'):
            clique = {}
            clique['open'] = True
            clique['nodes'] = []
            for i in splitLine[1:]:
                if i.isdigit():
                    clique['nodes'].append(i)
            
            cName = translations[splitLine[0]]
            if cName == 'NH':
                for node in clique['nodes']:
                    if attrs[node]['age'] > 70:
                        attrs[node]['inNursing'] = True
                
            layers[cName]['cliques'].append(clique)
            for node in clique['nodes']:
                attrs[node]['cliques'].append([cName, len(layers[cName]['cliques'])-1])


    for clique in layers['W']['cliques']:
        clique['openRating'] = random.random()
        
    f.close()
    layers['R']['cliques'] = [list(attrs.keys())]
    return layers, attrs


def splitHHs(layers, attrs, p):
    newHHLayer = {'cliques': [], 'open': True}
    for clique in layers['HH']['cliques']:
        adults = []
        children = []
        
        for node in clique['nodes']:
            if attrs[node]['age'] > 18:
                adults.append(node)
            else:
                children.append(node)
        if ((len(adults) > 1) & (random.random() < p)):
            c = []
            c.append({'nodes': [adults[0]], 'open': True})
            c.append({'nodes': [adults[1]], 'open': True})
            if len(adults) > 2:
                for adult in adults[2:]:
                    c[random.randint(0, 1)]['nodes'].append(adult)
                for child in children:
                    c[random.randint(0, 1)]['nodes'].append(child)
            newHHLayer['cliques'].append(c[0])
            newHHLayer['cliques'].append(c[1])
        else:
            newHHLayer['cliques'].append(clique)
    layers['HH'] = newHHLayer

def mergeHHs(layers, attrs, p):
    newHHLayer = {'cliques': [], 'open': True}
    seq = range(len(layers['HH']['cliques']))
    random.shuffle(seq)
    for i in range(0, len(layers['HH']['cliques'])-1, 2):
        if random.random() < p:
            newClique = {'nodes': [], 'open': True}
            newClique['nodes'].extend(layers['HH']['cliques'][seq[i]]['nodes'])
            newClique['nodes'].extend(layers['HH']['cliques'][seq[i+1]]['nodes'])
            newHHLayer['cliques'].append(newClique)
        else:
            newHHLayer['cliques'].append(layers['HH']['cliques'][seq[i]])
            newHHLayer['cliques'].append(layers['HH']['cliques'][seq[i+1]])

    if len(layers['HH']['cliques']) % 2 == 1:
        newHHLayer['cliques'].append(layers['HH']['cliques'][seq[-1]])
    layers['HH'] = newHHLayer


                    
def infectNode(attrs, node, anc, layer, day):
    attrs[node]['state'] = 'E'
    attrs[node]['lastDay'] = day
    attrs[node]['nextDay'] = day+1+np.random.poisson(dur['I-E'])          
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
            if attrs[node]['age'] > 10:
                susClique.append(node)
            else:
                if random.random() < childSusceptibility:
                    susClique.append(node)
        if attrs[node]['present'][layer] & attrs[node]['sick']:
            infClique.append(node)
    infected = len(infClique)
    susceptible = len(susClique)
    #effP = 1-pow(1-p, infected)
    effP = 1
    for node in infClique:
        #print infClique, attrs[node]
        effP = effP*(1-p*attrs[node]['relInfectivity'])
    effP = 1 - effP
        
    newInfs = random.sample(susClique, np.random.binomial(susceptible, effP))
    for nb in newInfs:
        ancestor = random.choice(infClique)
        infectNode(attrs, nb, ancestor, layer, day)
        
    return newInfs


#Daily state progress check and branching functions
def incubate(node, attrs, p, day):
    if day == attrs[node]['nextDay']:
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
    for layer in attrs[node]['present']:
        attrs[node]['present'][layer] = True
        
    if random.random() < p['NI']:
        attrs[node]['nextState'] = 'S'

        
def turnAsymp(node, attrs, p, day):
    attrs[node]['state'] = 'Ia'
    attrs[node]['nextState'] = 'R'
    attrs[node]['nextDay'] = day+1+np.random.poisson(dur['AS-R'])
    attrs[node]['sick'] = True
    attrs[node]['relInfectivity'] = 0.5
    if attrs[node]['age'] < 13:
        attrs[node]['relInfectivity'] = childInfectivity

    
def turnPresymp(node, attrs, p, day):
    attrs[node]['state'] = 'Ip'
    attrs[node]['nextState'] = 'Is'
    attrs[node]['nextDay'] = day+1+np.random.poisson(dur['PS-I'])
    attrs[node]['sick'] = True
    attrs[node]['relInfectivity'] = 3.0
    if attrs[node]['age'] < 13:
        attrs[node]['relInfectivity'] = 3.0*childInfectivity


    
def activateSymptoms(node, attrs, p, day):
    attrs[node]['state'] = 'Is'
    attrs[node]['lastDay'] = day
    for layer in ['BH', 'BS', 'US', 'VS', 'W', 'NH', 'R']:
        attrs[node]['present'][layer] = False
        
    if attrs[node]['inNursing']:
        if random.random() < p['NHDage'][attrs[node]['decade']]:
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
    attrs[node]['relInfectivity'] = 1
    if attrs[node]['age'] < 13:
        attrs[node]['relInfectivity'] = childInfectivity

        
def hospitalize(node, attrs, p, day):
    attrs[node]['state'] = 'H'
    attrs[node]['lastDay'] = day
    for layer in ['HH', 'NH']:
        attrs[node]['present'][layer] = False 



        
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
    for layer in attrs[node]['present']:
        attrs[node]['present'][layer] = False

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
def systemDay(layers, attrs, p, day, startDay, testRules = {}):

    
    cont = 0
    lInfs = {}
    dailyInfs = 0
    for layer in layers:
        lInfs[layer] = 0

        if (layers[layer]['open']) & (layer != 'R') & (layer != 'NTNUSocial'): #i > rel[layer]:
            for clique in layers[layer]['cliques']:
                if clique['open']:
                    infs = cliqueDay(clique['nodes'], attrs, layer, p['inf'][layer], day)
                    lInfs[layer] += len(infs)
                    dailyInfs += len(infs)
        
    lInfs['Rp'] = dynRandomLayer(attrs, layers['R']['cliques'][0], p['inf']['dynR'], day)
    if ('NTNUSocial' in layers):
        lInfs['NTNUSocial'] = dynRandomLayer(attrs, layers['NTNUSocial']['cliques'][0], p['inf']['dynR'], day)
    
    dailyInfs += lInfs['Rp']

    ageCount = countAge(attrs)
        
    for node in attrs:
        if (attrs[node]['sick'] | (attrs[node]['state'] == 'E')):
            stateFunction(attrs[node]['state'])(node, attrs, p, day)
            #ifSwitch(node, attrs, p, day)
            cont = True


    if testRules:
#        print testRules['strat']
        if testRules['strat'] != 'Symptomatic':
            #if (day-startDay) % testRules['freq'] == 0:
            if testRules['mode'] == 'FullHH':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool['testDay']:
                        testAndQuar(pool, attrs, day, testRules['fpr'], testRules['fnr'])
            if testRules['mode'] == 'Adults':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool['testDay']:
                        testAndQuarAdults(pool, attrs, day, testRules['age'], testRules['fpr'], testRules['fnr'])
                    
 #                
        else:
            for node in attrs:
                if attrs[node]['state'] == 'Is':
                    
                    if attrs[node]['lastDay'] == (day-2):
                    
                        indTestAndQuar(node, attrs, layers, day)
            
    
    return cont, lInfs, dailyInfs, ageCount


def test(node, attrs, day, fpr=0, fnr=0):
    
    if attrs[node]['state'] in {'Ip', 'Ia'}:
        #if (attrs[node]['lastDay'] < day-1):
        return random.random() > fnr
        #else:
        #    return random.random() < fpr
    elif attrs[node]['state'] == 'Is':
        return random.random() > fnr        
    else:
        return random.random() < fpr


def pooledTest(clique, attrs, day, fpr=0, fnr=0):    
    for node in clique['nodes']:
        if test(node, attrs, day):
            if random.random() < fnr:
                return False
            else:
                return True
    return False

def pooledTestAdultOnly(clique, attrs, day, fpr=0, fnr=0, age=18):
    for node in clique['nodes']:
        if attrs[node]['age'] > age:
            if test(node, attrs, day, fpr, fnr):
                return True
    return False


def quarNode(node, attrs):
    for layer in {'W', 'US', 'VS', 'BS', 'BH', 'R', 'NH'}:
        attrs[node]['present'][layer] = False

def dequarNode(node, attrs):
    for layer in {'W', 'US', 'VS', 'BS', 'BH', 'R', 'NH'}:
        attrs[node]['present'][layer] = True


def quarClique(clique, attrs):
    for node in clique['nodes']:
        quarNode(node, attrs)

def dequarClique(clique, attrs):
    for node in clique['nodes']:
        dequarNode(node, attrs)

        
def testAndQuar(clique, attrs, day, fpr=0, fnr=0):
    if pooledTest(clique, attrs, day, fpr, fnr):
        quarClique(clique, attrs)
    else:
        dequarClique(clique, attrs)

def testAndQuarAdults(clique, attrs, day, age, fpr=0, fnr=0):
    if pooledTestAdultOnly(clique, attrs, day, fpr, fnr, age):
        quarClique(clique, attrs)
    else:
        dequarClique(clique, attrs)

def indTestAndQuar(node, attrs, layers, day):
    if test(node, attrs, day):

        if attrs[node]['inNursing'] == False:
            for clique in attrs[node]['cliques']:
                if clique[0] == 'HH':
                    hhID = clique[1]
                    quarClique(layers['HH']['cliques'][hhID], attrs)
            
            
def genTestPoolsRandomHH(layers, attrs, capacity):

    return random.sample(layers['HH']['cliques'], capacity)


def genTestPoolsHHaboveSize(layers, attrs, capacity, size):

    i = 0
    validHHs = []
    for hh in layers['HH']['cliques']:
        if len(hh['nodes']) > size:
            validHHs.append(hh)

    return random.sample(validHHs, capacity)

def getHHsize(hh):
    return len(hh['nodes'])

def genTestPoolsTopFraction(layers, attrs, capacity, compliance=1.0):
    sortedHHs = sorted(layers['HH']['cliques'], key = getHHsize, reverse = True)
    if (compliance == 1.0):
        return sortedHHs[:capacity]
    else:
        i = 0
        j = 0
        pools = []
        while i < capacity:
            if random.random() < compliance:
                pools.append(sortedHHs[j])
                i += 1
            j += 1
        return pools
    

def genTestPoolsStudents(layers, attrs, capacity, size):
    i = 0
    validHHs = []
    for hh in layers['HH']['cliques']:
        if (len(hh['nodes']) > size) & (hh['nodes'][0][0] == 's'):
            validHHs.append(hh)
    return random.sample(validHHs, capacity)



def genTestPoolsNHPersonnel(layers, attrs):
    testPool = []
    for nh in layers['NH']['cliques']:
        clique = {'nodes': []}
        for node in nh['nodes']:
            if attrs[node]['inNursing'] == False:
                clique['nodes'].append(node)
        testPool.append(clique)
    return testPool

def testTargeted(layers, attrs, capacity, size):
    pool = genTestPoolsHHaboveSize(layers, attrs, capacity, size)
    for clique in pool:
        testAndQuar(clique, attrs)

def findsymptomatic(attrs, layers):
    symptPool = []
    for node in  attrs:
        if attrs[node]['state'] == 'Is':
            symptPool.append(node)
    return symptPool

def findsymptomatic(attrs, layers):
    symptPool = []
    for node in  attrs:
        if attrs[node]['state'] == 'Is':
            symptPool.append(node)
    return symptPool

            
        
        
    
    
        
    
        
def workFrac(layers, frac):
    for clique in layers['W']['cliques']:
        clique['open'] = (clique['openRating'] < frac)



def closeGrade(school, age, attrs):
    for node in school['nodes']:
        if attrs[node]['age'] == age:
            attrs[node]['present']['VS'] = False
            attrs[node]['present']['BS'] = False
            attrs[node]['present']['US'] = False
            attrs[node]['present']['BH'] = False

                

            
def closeGradesBelow(school, age, attrs):
    for node in school['nodes']:
        if attrs[node]['age'] < age:
            attrs[node]['present']['VS'] = False
            attrs[node]['present']['BS'] = False
            attrs[node]['present']['US'] = False
            attrs[node]['present']['BH'] = False
    for node in school['nodes']:
        if attrs[node]['age'] > 19:
            if age > 15:
                attrs[node]['present']['VS'] = False
            if age > 12:
                attrs[node]['present']['US'] = False
            if age > 5:
                attrs[node]['present']['BS'] = False
            if age > 0:
                attrs[node]['present']['BH'] = False
            
def closeGradesAbove(school, age, attrs):
    for node in school['nodes']:
        if attrs[node]['age'] > age:
            attrs[node]['present']['VS'] = False
            attrs[node]['present']['BS'] = False
            attrs[node]['present']['US'] = False
            attrs[node]['present']['BH'] = False
    for node in school['nodes']:
        if attrs[node]['age'] > 19:
            if age > 15:
                attrs[node]['present']['VS'] = True
            if age > 12:
                attrs[node]['present']['US'] = True
            if age > 5:
                attrs[node]['present']['BS'] = True
            if age > 0:
                attrs[node]['present']['BH'] = True

            

def openAllGrades(school, attrs):
    for node in school['nodes']:
        attrs[node]['present']['VS'] = True
        attrs[node]['present']['BS'] = True
        attrs[node]['present']['US'] = True
        attrs[node]['present']['BH'] = True

    


def countState(attrs, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in attrs:
        count[attrs[node]['state']] += 1
    return count

def countAge(attrs):
    ageCount = {}
    for node in attrs:
        if attrs[node]['state'] == 'E':
            if (attrs[node]['decade'] not in ageCount):
                ageCount[attrs[node]['decade']] = 1
            else:
                ageCount[attrs[node]['decade']] += 1
    return ageCount
    

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


def setTestRules(testing, layers, attrs):
    testRules = {}
    
    if testing:

        testRules['strat'] = testing['testStrat']
        if testing['testStrat'] in ['TPHT', 'TPHTA']:
            if 'Stud' not in testing:
                testRules['pools'] = genTestPoolsHHaboveSize(layers, attrs, testing['capacity'], testing['cutoff'])
            else:
                testRules['pools'] = genTestPoolsHHaboveSize(layers, attrs, testing['capacity'], testing['cutoff'])
                testRules['pools'].extend(genTestPoolsStudents(layers, attrs, testing['Stud']['capacity'], testing['Stud']['cutoff']))
        if testing['testStrat'] in ['TPHT2']:
            if 'compliance' in testing:
                testRules['pools'] = genTestPoolsTopFraction(layers, attrs, testing['capacity'], testing['compliance'])
            else:
                testRules['pools'] = genTestPoolsTopFraction(layers, attrs, testing['capacity'])
            testRules['mode'] = 'FullHH'
        if testing['testStrat'] in ['TPHTA2']:
            testRules['pools'] = genTestPoolsTopFraction(layers, attrs, testing['capacity'])
            testRules['mode'] = 'Adults'
            testRules['age'] = testing['age']
        if testing['testStrat'] in ['RPHT']:
            testRules['pools'] = genTestPoolsRandomHH(layers, attrs, testing['capacity'])
            testRules['mode'] = 'FullHH'
            
        if testing['testStrat'] in ['NH']:
            testRules['pools'] = genTestPoolsNHPersonnel(layers, attrs)
            testRules['mode'] = 'FullHH'
        if testing['testStrat'] in ['NHTPHT']:
            testRules['pools'] = genTestPoolsNHPersonnel(layers, attrs)+genTestPoolsHHaboveSize(layers, attrs, testing['capacity'], testing['cutoff'])
            testRules['mode'] = 'FullHH'

        if testing['testStrat'] in ['RIT']:
            testRules['pools'] = [{'nodes': [node]} for node in random.sample(list(attrs.keys()), testing['capacity'])]
            testRules['mode'] = 'FullHH'

        if testing['testStrat'] in ['TPHTA']:
            testRules['mode'] = 'Adults'
            testRules['age'] = testing['age']
        if testing['testStrat'] in ['TPHT', 'RPHT']:
            testRules['mode'] = 'FullHH'
        if 'freq' in testing:
            testRules['freq'] = testing['freq']
        else:
            testRules['freq'] = 7

        for pool in testRules['pools']:
            pool['testDay'] = random.randint(0, testRules['freq']-1)

        if 'fnr' in testing:
            testRules['fnr'] = testing['fnr']
        else:
            testRules['fnr'] = 0
        if 'fpr' in testing:
            testRules['fpr'] = testing['fpr']
        else:
            testRules['fpr'] = 0
            
    return testRules

def setStrategy(inputVector, probs, layers, attrs):

    newP = copy.deepcopy(probs)
        
    if 'poolSelection' in inputVector:
        if layers['poolSelection'] == 'largeHH':
            genTestPoolsHHaboveSize(layers, attrs, 50000, 3)
            
            
    layers['W']['open'] = bool(inputVector['W'])
    layers['R']['open'] = bool(inputVector['R'])

    
    for layer in ['BH', 'BS', 'US', 'VS']:
        layers[layer]['open'] = bool(inputVector['S'])

        for school in layers[layer]['cliques']:
            openAllGrades(school, attrs)
            closeGradesAbove(school, inputVector['S'], attrs)

    workFrac(layers, float(inputVector['W']))

    layers['NH']['open'] = True
    layers['HH']['open'] = True
    layers['R']['open'] = True
    
    #qFac = [0.1, 0.25, 0.5, 1]

    
    newP['inf']['R'] = inputVector['R']*probs['inf']['R']
    newP['inf']['dynR'] = inputVector['R']*probs['inf']['dynR']
    
    return newP



def fullRun(seedAttrs, layers, strat, baseP):
    
    cont = 1
    i = 0

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)
    
    inVec = convertVector(strat)        
    p = setStrategy(inVec, baseP, layers, attrs)

    stateLog.append(countState(attrs, stateList))
    
    while cont:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
            


        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i, 0)
        stateLog.append(countState(attrs, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i


def timedRun(attrs, layers, strat, baseP, curDay, runDays, testing={}):
    
    cont = 1
    i = curDay
    #inVec = convertVector(strat)
    p = setStrategy(strat, baseP, layers, attrs)

    stateLog = []
    infLog = []
    infLogByLayer = []
    ageLog = []
    endDay = curDay+runDays


    testRules = setTestRules(testing, layers, attrs)
                   
    while i < endDay:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
        
        dailyInfs = 0
    
        cont, linfs, dailyInfs, ageCount = systemDay(layers, attrs, p, i, curDay, testRules)

        stateLog.append(countState(attrs, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
        ageLog.append(ageCount)
    
    return stateLog, infLog, infLogByLayer, ageLog, i



def timedRunTesting(attrs, layers, strat, baseP, curDay, runDays, testPools, mode='All'):
    
    cont = 1
    i = curDay
    #inVec = convertVector(strat)
    p = setStrategy(strat, baseP, layers, attrs)


    stateLog = []
    infLog = []
    infLogByLayer = []
    endDay = curDay+runDays
    #testPools = genTestPoolsRandomHH(layers, attrs, 20000)
    #testPools = genTestPoolsHHaboveSize(layers, attrs, 20000, 4)
    #testPools = [[node] for node in random.sample(attrs, 20000)]
    
    
    while i < endDay:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
        
        dailyInfs = 0
        
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i)
        

        stateLog.append(countState(attrs, stateList))
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
    
    return stateLog, infLog, infLogByLayer, i


def initRun(attrs, layers, strat, baseP, threshold):

    cont = 1
    i = 0
    #inVec = convertVector(strat)
    p = setStrategy(strat, baseP, layers, attrs)



    stateLog = []
    infLog = []
    infLogByLayer = []
    
    while cont:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
        
        dailyInfs = 0
    
        cont, linfs, dailyInfs, ageCount = systemDay(layers, attrs, p, i, 0)


        stateLog.append(countState(attrs, stateList))
        if stateLog[-1]['Is'] > threshold:
            cont = False
            
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
        
        
    return stateLog, infLog, infLogByLayer, i

def hospThresholdRun(attrs, layers, strat, baseP, threshold):

    cont = 1
    i = 0
    #inVec = convertVector(strat)
    p = setStrategy(strat, baseP, layers, attrs)



    stateLog = []
    infLog = []
    infLogByLayer = []
    
    while cont:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')
        
        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i)


        stateLog.append(countState(attrs, stateList))
        if stateLog[-1]['H'] > threshold:
            cont = False
            
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
        
        
    return stateLog, infLog, infLogByLayer, i



def fullRunControl(seedAttrs, layers, strat, baseP, testing=''):
    
    cont = 1
    i = 0
    inVec = convertVector(strat)
    p = setStrategy(inVec, baseP, layers)

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)
    
    while cont:
        i+=1
        sys.stdout.flush()
        sys.stdout.write(str(i)+'\r')

        dailyInfs = 0
    
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i, testing)
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


# def analyticalR(layers, openLayers, attrs, p):
#     expInfs = [0]*len(attrs)
#     for layer in layers:
            
#         if openLayers[layer]:
#             for clique in cliques[layer]:
#                 for node in clique:
                        
#                     expInfs[node] += p['inf'][layer]*len(clique)

#     rByNode = []

#     for node in expInfs:
#         rByNode.append(node/p['rec'])
#     return np.mean(rByNode)


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


#Node-based power law spread on a random layer
def dynRandomLayer(attrs, layer, p, day):
    infs = 0
    for node in layer:
        if attrs[node]['present']['R'] & attrs[node]['sick']:
            conns = min(random.randint(0, attrs[node]['act']), len(layer))
            for nNode in random.sample(layer, conns):
                if attrs[nNode]['present']['R'] & (attrs[nNode]['state'] == 'S'):
                    if attrs[nNode]['age'] > 10:
                        if random.random() < p*attrs[node]['relInfectivity']:
                            infectNode(attrs, nNode, node, 'R', day)
                            infs += 1
                    else:
                        if random.random() < childSusceptibility*p*attrs[node]['relInfectivity']:
                            infectNode(attrs, nNode, node, 'R', day)
                            infs += 1
                            

                
        if attrs[node]['present']['R'] & (attrs[node]['state'] == 'S'):
            conns = min(random.randint(0, attrs[node]['act']), len(layer))
            iNeighbors = 0
            nbP = 1
            for nNode in random.sample(layer, conns):
                if attrs[nNode]['present']['R'] & attrs[nNode]['sick']:
                    iNeighbors += 1
                    nbP = nbP*(1-p*attrs[nNode]['relInfectivity'])
            nbP = 1-nbP


            if random.random() < nbP:
                
                if attrs[node]['age'] > 10:
                    infectNode(attrs, node, nNode, 'R', day)
                    infs += 1
                else:
                    if random.random() < childSusceptibility:
                        infectNode(attrs, node, nNode, 'R', day)
                        infs += 1
                    


    return infs


def genVaccPoolAllAboveAge(attrs, layers, age):
    pool = []
    for node in attrs:
        if attrs[node]['age'] > age:
            pool.append(node)
    random.shuffle(pool)
    return pool

def genVaccPoolByHouseholdsDecreasing(attrs, layers):
    pool = []
    sortedHHs = sorted(layers['HH']['cliques'], key = getHHsize, reverse = True)
    for hh in layers['HH']['cliques']:
        for node in hh:
            pool.append(node)
    return pool

def genVaccPoolHouseholdsRolling(attrs, layers):
    pool = []
    hhBySize = {}
    for hh in layers['HH']['cliques']:
        sz = len(hh['nodes'])
        if sz in hhBySize:
            hhBySize[sz].append(list(hh['nodes']))
        else:
            hhBySize[sz] = [list(hh['nodes'])]


    for sz in range(1, max(hhBySize.keys())):
        if sz not in hhBySize:
            hhBySize[sz] = []

        
    for sz in reversed(range(1, max(hhBySize.keys()))):
        random.shuffle(hhBySize[sz])
        for hh in hhBySize[sz]:
            pool.append(hh[0]) #Add first individual to pool
            del hh[0] #Remove said individual from household
            if sz > 1:
                hhBySize[sz-1].append(hh) #Bump household down to slice below
        del hhBySize[sz] #Clean-up, has to be done outside loop to prevent returning error
        
    return pool

def genVaccPoolRandom(attrs, layers):
    pool = list(attrs.keys())
    random.shuffle(pool)
    return pool
        

def vaccinatePool(attrs, node, pool, p=1.0):
    for node in pool:
        vaccinateNode(attrs, node, p)

def vaccinateNode(attrs, node, p=1.0):
    if random.random() < p:
        attrs[node]['state'] = 'R'
        attrs[node]['sick'] = False
        for layer in attrs[node]['present']:
            attrs[node]['present'][layer] = True
    

def partialVaccination(attrs, vaccPool, n, p):
    for node in vaccPool[0:n]:
        vaccinateNode(attrs, node, p)
    del vaccPool[:n]    
    
        


def genBlankState(attrs):
    for node in attrs:
        attrs[node]['state'] = 'S'
        attrs[node]['sick'] = False
        attrs[node]['infAnc'] = -1
        attrs[node]['infDesc'] = []

def seedState(attrs, n):
    for node in random.sample(attrs.keys(), n):
        attrs[node]['state'] = 'E'
        attrs[node]['lastDay'] = 0
        attrs[node]['nextDay'] = 1+np.random.poisson(dur['I-E'])          
        attrs[node]['infAnc'] = ['init', 'init']


        #attrs[node]['state'] = 'E'
        #attrs[node]['sick'] = True

def seedStateStudents(attrs, n):
    pool = []
    for node in attrs:
        if node[0] == 's':
            pool.append(node)
        
    for node in random.sample(pool, n):
        attrs[node]['state'] = 'E'
        attrs[node]['sick'] = True


def seedStateNew(attrs, n):
    for node in random.sample(attrs.keys(), n):
        if random.random() < 0.5:
            attrs[node]['state'] = 'Ip'
            attrs[node]['sick'] = True
        else:
            attrs[node]['state'] = 'Ia'
            attrs[node]['sick'] = True
