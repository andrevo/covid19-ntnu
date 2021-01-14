import pickle
import random
import copy
import classes
from parameters import *


def loadModel(ageFile, cliqueFile):
    filename = ageFile.split('_')[1].split('.')[0]

    try:
        layers, agents = pickle.load( open('data/{}.pickle'.format(filename), 'rb'))
        print('Loaded model from pickle file')
    except:
        print('Read model from .txt files')
        layers, agents = readModel(ageFile, cliqueFile)
        pickle.dump((layers, agents), open('data/{}.pickle'.format(filename), 'wb'))
    
    return layers, agents


def readModel(ageFile, cliqueFile):
    '''Builds household/school/work structure from file'''

    f = open(ageFile)
    nodeID = -1
    agents = {}
    
    for line in f:
        line = line.rstrip().split(';')
        nodeID = line[0]
        age = int(line[1])

        node = classes.Person(nodeID, age)
        agents[nodeID] = node

    f.close()

    layers = {'BH':{}, 'BS':{}, 'US':{}, 'VS':{}, 'W':{}, 'HH':{}, 'NH':{}, 'R':{}}

    for layer in layers:
        layers[layer] = classes.Layer(layer)
    

    f = open(cliqueFile)
    for line in f:

        splitLine = line.rstrip().split(';')
        
        if (splitLine[1] != '') & (splitLine[0].split('_')[0] != 'Commuters'):
            clique = classes.Clique()

            for i in splitLine[1:]:
                if i.isdigit():
                    clique.nodes.append(agents[i])
            
            cliqueName = translations[splitLine[0]]
            if cliqueName == 'NH':
                for node in clique:
                    if node.age > 70:
                        node.inNursing = True

            layers[cliqueName].addClique(clique)
            layers['R'].addClique(clique)

            for node in clique: 
                node.cliques.append(clique)
            
    f.close()

    for clique in layers['W'].cliques:
        clique.openRating = random.random()

    return layers, agents


def setStrategy(inputVector, probs, layers, attrs):

    newP = copy.deepcopy(probs)
        
    if 'poolSelection' in inputVector:
        if layers['poolSelection'] == 'largeHH':
            genTestPoolsHHaboveSize(layers, attrs, 50000, 3)
            
            
    layers['W'].open = bool(inputVector['W'])
    layers['R'].open = bool(inputVector['R'])

    
    for layer in ['BH', 'BS', 'US', 'VS']:
        layers[layer].open = bool(inputVector['S'])

        for school in layers[layer].cliques:
            openAllGrades(school, attrs)
            closeGradesAbove(school, inputVector['S'], attrs)

    workFrac(layers, float(inputVector['W']))

    layers['NH'].open = True
    layers['HH'].open = True
    layers['R'].open = True
    
    qFac = [0.1, 0.25, 0.5, 1]

    
    newP['inf']['R'] = qFac[inputVector['R']]*probs['inf']['R']
    newP['inf']['dynR'] = qFac[inputVector['R']]*probs['inf']['dynR']
    
    return newP


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
            testRules['pools'] = genTestPoolsNHPersonnel(layers, attrs) + genTestPoolsHHaboveSize(layers, attrs, testing['capacity'], testing['cutoff'])
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
            pool.testDay = random.randint(0, testRules['freq']-1)

        if 'fnr' in testing:
            testRules['fnr'] = testing['fnr']
        else:
            testRules['fnr'] = 0
        if 'fpr' in testing:
            testRules['fpr'] = testing['fpr']
        else:
            testRules['fpr'] = 0
            
    return testRules


def genTestPoolsRandomHH(layers, attrs, capacity):
    return random.sample(layers['HH'].cliques, capacity)


def genTestPoolsHHaboveSize(layers, attrs, capacity, size):
    i = 0
    validHHs = []
    for hh in layers['HH'].cliques:
        if len(hh.nodes) > size:
            validHHs.append(hh)
    return random.sample(validHHs, capacity)


def genTestPoolsStudents(layers, attrs, capacity, size):
    i = 0
    validHHs = []
    for hh in layers['HH'].cliques:
        if (len(hh.nodes) > size) & (hh.nodes[0][0] == 's'):
            validHHs.append(hh)
    return random.sample(validHHs, capacity)


def genTestPoolsNHPersonnel(layers, attrs):
    testPool = []
    for nh in layers['NH'].cliques:
        clique = {'nodes': []}
        for node in nh.nodes:
            if attrs[node].inNursing == False:
                clique.nodes.append(node)
        testPool.append(clique)
    return testPool


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

def getHHsize(hh):
    return len(hh.nodes)

def openAllGrades(school, attrs):
    for node in school:
        node.present['VS'] = True
        node.present['VS'] = True
        node.present['BS'] = True
        node.present['US'] = True
        node.present['BH'] = True


def closeGradesAbove(school, age, attrs):
    for node in school.nodes:
        if node.age > age:
            node.present['VS'] = False
            node.present['BS'] = False
            node.present['US'] = False
            node.present['BH'] = False
    for node in school:
        if node.age > 19:
            if age > 15:
                node.present['VS'] = True
            if age > 12:
                node.present['US'] = True
            if age > 5:
                node.present['BS'] = True
            if age > 0:
                node.present['BH'] = True


def workFrac(layers, frac):
    '''Opens all workplaces with a high enough openrating.'''
    for clique in layers['W'].cliques:
        clique.open = (clique.openRating < frac)


def countState(attrs, stateList):
    '''Count through all persons and save states in a dict'''
    count = {}
    for s in stateList:
        count[s] = 0
    for node in attrs.values():
        count[node.state] += 1

    return count


def convertVector(inputVector):
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


def printProgress(iteration, total, bar_length=100):
    percents = f'{100 * (iteration / float(total)):.2f}'
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = f'{"█" * filled_length}{"-" * (bar_length - filled_length)}'
    print(f'\rProgress: |{bar}| {percents}% complete ', end=''),
    # if iteration == total:
    #     print("\n")
 

def saveResults(df):
    df.to_csv('results/stateLog_{}.csv'.format(len(df)), index=False)
    df.to_csv()


def main():
    # layers, agents = loadModel('data/idAndAge_Trondheim.txt', 'data/socialNetwork_Trondheim.txt')
    layers, agents = readModel('data/idAndAge_Trondheim.txt', 'data/socialNetwork_Trondheim.txt')



if __name__ == '__main__':
    main()
