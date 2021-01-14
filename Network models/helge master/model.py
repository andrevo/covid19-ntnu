# import sys
import random
import numpy as np
import pandas as pd
import time
from classes import *
from utilities import *
from parameters import *
from network import *


def initialiseModel(ageFile, cliqueFile, riskTableFile, baseP, params, n):
    '''Create the layers and agents(attrs). '''
    layers, attrs = readModel(ageFile, cliqueFile)
    
    for node in attrs.values():
        node.generateActivity(params)
    
    seedState(attrs, n)

    return layers, attrs


def seedState(attrs, n):
    '''Set the state of n persons to exposed.'''
    for node in random.sample(list(attrs.values()), n):
        node.state = 'E'
        node.sick = True
        node.lastDay = 0
        node.nextDay = 1+np.random.poisson(dur['I-E'])          
        node.infAnc = ['init', 'init']


def systemDay(layers, attrs, p, day, testRules={}):
    '''Daily pulse of the system.'''
    cont = 0

    infectedList = {}
    dailyInfected = 0
    for layer in layers:
        infectedList[layer] = 0

        if (layers[layer].open) & (layers[layer].name != 'R'): 
            for clique in layers[layer]:
                if clique.open & clique.cases > 0: 
                    infs = cliqueDay(clique, attrs, layer, p['inf'][layer], day)
                    infectedList[layer] += len(infs)
                    dailyInfected += len(infs)
    
    infectedList['Rp'] = dynRandomLayer(attrs, layers['R'].cliques[0], p['inf']['dynR'], day)
    dailyInfected += infectedList['Rp']
    
    for node in attrs.values():
        if node.sick or (node.state == 'E'):
            node.stateFunction()(p, day)
            cont = True

    if testRules:
        tests = testing(layers, attrs, p, day, testRules)
    
    return cont, infectedList, dailyInfected, tests


def cliqueDay(clique, attrs, layer, p, day):
    '''Runs infections over a day for a given clique'''
    susceptible = 0
    infected = 0
    infClique = []
    susClique = []
    
    for node in clique:
        if node.state == 'S':
            if node.age > 10:
                susClique.append(node)
            else:
                if random.random() < 0.3:
                    susClique.append(node)
        if node.present[layer] & node.sick:
            infClique.append(node)
    infected = len(infClique)
    susceptible = len(susClique)
    
    effP = 1 - pow(1-p, infected)
    # effP = 1

    newlyInfected = random.sample(susClique, np.random.binomial(susceptible, effP))
    for neighbour in newlyInfected:
        ancestor = random.choice(infClique)
        node.infectNode(ancestor, layer, day)
        
    return newlyInfected


def dynRandomLayer(attrs, clique, p, day):
    '''Node-based power law spread on the random layer'''
    newInfected = 0
    for node in clique:
        if node.present['R'] & node.sick:
            connections = min(random.randint(0, node.activity), len(clique))
            for newNode in random.sample(list(clique), connections):
                if newNode.present['R'] & (newNode.state == 'S'):
                    if newNode.age > 10:
                        if random.random() < p * node.relInfectivity:
                            newNode.infectNode(node, 'R', day)
                            newInfected += 1
                    else:
                        if random.random() < 0.3 * p * node.relInfectivity:
                            newNode.infectNode(node, 'R', day)
                            newInfected += 1

                
        if node.present['R'] & (node.state == 'S'):
            connections = min(random.randint(0, node.activity), len(clique))
            iNeighbors = 0
            neighborP = 1
            for newNode in random.sample(clique.nodes, connections):
                if newNode.present['R'] & newNode.sick:
                    iNeighbors += 1
                    neighborP = neighborP * (1-p*newNode.relInfectivity)
            neighborP = 1-neighborP

            if random.random() < neighborP:
                if node.age > 10:
                    node.infectNode(newNode, 'R', day)
                    newInfected += 1
                else:
                    if random.random() < 0.3:
                        node.infectNode(newNode, 'R', day)
                        newInfected += 1

    return newInfected


def testing(layers, attrs, p, day, testRules):
    tests = 0
    if testRules['strat'] != 'Symptomatic':
            if testRules['mode'] == 'FullHH':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool.testDay:
                        pool.testAndQuarantine(testRules['fpr'], testRules['fnr'])
                        tests += len(pool)
            if testRules['mode'] == 'Adults':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool['testDay']:
                        pool.testAndQuarantineAdults(testRules['age'], testRules['fpr'], testRules['fnr'])
                        tests += len(pool)
    else:
        for node in attrs.values():
            if node.state == 'Is':
                if node.lastDay == (day-2):
                    node.individualTestAndQuarantine(layers, day)
                    tests += 1
    
    return tests


def timedRun(attrs, layers, strat, baseP, currentDay, runDays, testing={}):
    '''Run of the model for a given number of days'''
    p = setStrategy(strat, baseP, layers, attrs)
    testRules = setTestRules(testing, layers, attrs)

    stateLog = []
    infectedLog = []
    infectedLogByLayer = []

    cont = 1
    i = currentDay
    endDay = currentDay + runDays
                   
    while cont and (i < endDay):
        i+=1
        
        printProgress(i, runDays)
        dailyInfected = 0
    
        cont, linfs, dailyInfected, tests = systemDay(layers, attrs, p, i, testRules)

        states_ = countState(attrs, stateList)
        states_['T'] = tests
        stateLog.append(states_)
        infectedLog.append(dailyInfected)
        infectedLogByLayer.append(linfs)

    return stateLog, infectedLog, infectedLogByLayer, i


def runModel(cityname='Trondheim'):
    start = time.time()
    params = {'mode':10, 'var':3, 'exp':-0.75}
    layers, attrs = initialiseModel('data/idAndAge_{}.txt'.format(cityname), 'data/socialNetwork_{}.txt'.format(cityname), '', baseP, params, 1000)

    strat = {'S': 12, 'W': 1, 'R': 1}
    inVec = convertVector(strat)
    testing = {'testStrat': 'TPHT', 'capacity':1000, 'cutoff': 3}
    days = (0, 100)
    
    stateLog, infLog, infLogByLayer, i = timedRun(attrs, layers, strat, baseP, *days, testing)
    
    runtime = time.time()-start
    print('\nFinished {} simulation in {:.0f} seconds; {:.2f} sec/day.\n'.format(cityname, runtime, runtime/days[1]))

    # createNetwork(attrs)

    return stateLog, infLog, infLogByLayer


def profiler():
    '''Profiling to benchmark the code'''
    import cProfile, pstats
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    # stats.strip_dirs()
    stats.print_stats(10)
    stats.dump_stats('results/profile')


def main():
    stateLog, infLog, infLogByLayer = runModel('Oslo')
    df = pd.DataFrame(stateLog)
    # saveResults(df)



if __name__ == '__main__':
    # main()
    profiler()

