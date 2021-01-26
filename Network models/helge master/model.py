'''
Author: Helge Bergo
Date: January 2021
File: model.py

This script contains the main agent based model, and loads in classes, utilities and parameters to run the simulation. 
'''

import random
import numpy as np
import pandas as pd
import time
from classes import *
from utilities import *
from parameters import *
from network import *
import networkx as nx


def initialiseModel(parameters):
    '''Create the layers and agents(attrs). '''
    layers, attrs = readModel(parameters)
    
    for node in attrs.values():
        node.generateActivity(parameters)
    
    seedState(attrs, parameters)

    if parameters.printResults:
        print('--Initialised {} Model--'.format(parameters.cityName))

    return layers, attrs


def seedState(attrs, parameters):
    '''Set the state of n persons to exposed.'''
    for node in random.sample(list(attrs.values()), parameters.n):
        node.state = 'E'
        # node.sick = True
        node.lastDay = 0
        node.nextDay = 1+np.random.poisson(dur['I-E'])          
        node.infAnc = ['init', 'init', 'init']
        
        if parameters.createNetwork:
            parameters.tree.add_node(node.id_number, decade=node.decade, layer='', day=-1)


def systemDay(layers, attrs, parameters, day):
    '''Daily pulse of the system.'''
    cont = 0

    infectedList = {}
    dailyInfected = 0
    for layer in layers:
        infectedList[layer] = 0

        if (layers[layer].open) & (layers[layer].name != 'R'): 
            for clique in layers[layer]:
                if clique.open & clique.cases > 0: 
                    infs = cliqueDay(clique, attrs, layer, parameters, day)
                    infectedList[layer] += len(infs)
                    dailyInfected += len(infs)
    
    # infectedList['R'] = randomLayerSpread(attrs, layers['R'].cliques[0], parameters, day)
    # infectedList['Rp'] = dynRandomLayer(attrs, layers['R'].cliques[0], p['inf']['dynR'], day)
    infectedList['R'] = simpleDynRandomLayer(attrs, layers['R'].cliques[0], parameters, day)
    dailyInfected += infectedList['R']
    
    for node in attrs.values():
        if node.sick or (node.state == 'E'):
            node.stateFunction()(parameters.p, day)
            cont = True

    tests = 0
    if parameters.testRules:
        tests = testing(layers, attrs, parameters, day)
    
    return cont, infectedList, dailyInfected, tests


def cliqueDay(clique, attrs, layer, parameters, day):
    '''Runs infections over a day for a given clique'''
    infectedInClique = []
    susceptibleInClique = []
    
    for node in clique:
        if node.state == 'S':
            if node.age > 10:
                susceptibleInClique.append(node)
            else:
                if random.random() < 0.3:
                    susceptibleInClique.append(node)
        if node.present[layer] & node.sick:
            infectedInClique.append(node)
    
    effP = 1 - pow(1-parameters.p['inf'][layer], len(infectedInClique))

    newlyInfected = random.sample(susceptibleInClique, np.random.binomial(len(susceptibleInClique), effP))
    for node in newlyInfected:
        ancestor = random.choice(infectedInClique)
        node.infectNode(ancestor, layer, day, parameters)
        
    return newlyInfected


def simpleDynRandomLayer(attrs, layer, parameters, day):           
    '''New and faster version'''                                                                           
    p = parameters.p['inf']['dynR']
    prevalence = 0                                                                                                                   
    sickNodes = []                                                                                                                   
    for node in attrs.values():                                                                                                               
        if node.sick & node.present['R']:  
            act = min(random.randint(0, node.activity), len(layer))                                                             
            prevalence += act * node.relInfectivity
            sickNodes.append(node)                 

    prevalence = float(prevalence)/len(attrs)                                                                                        
    infs = 0                                                                                                                         
    for node in attrs.values():                                                                                                               
        if (node.state == 'S') & node.present['R']:                                                              
            act = min(random.randint(0, node.activity), len(layer))                                                             
            if random.random() < (1-pow(1-p*prevalence, act)):                                                                       
                node.infectNode(random.choice(sickNodes), layer, day, parameters)                                                        
                infs += 1                                                                                                            
    return infs     


def randomLayerSpread(attrs, clique, parameters, day):
    '''Node based spread on the random layer'''
    newInfected = 0
    for node in clique:
        if node.present['R']:
            if node.sick:
                newInfected += nodeToNeighborSpread(node, clique, parameters, day)
            if node.state == 'S':
                newInfected += nodeFromNeighborSpread(node, clique, parameters, day)

    return newInfected


def nodeToNeighborSpread(node, clique, parameters, day):
    '''Random layer spread from infected node to neighbors'''
    newInfected = 0
    connections = min(random.randint(0, node.activity), len(clique))
    for neighborNode in random.sample(clique, connections):
        if neighborNode.present['R'] & (neighborNode.state == 'S'):
            if neighborNode.age > 10:
                if random.random() < parameters.p['inf']['dynR'] * node.relInfectivity:
                    neighborNode.infectNode(node, 'R', day, parameters)
                    newInfected += 1
            else:
                if random.random() < 0.3 * parameters.p['inf']['dynR'] * node.relInfectivity:
                    neighborNode.infectNode(node, 'R', day, parameters)
                    newInfected += 1
    return newInfected


def nodeFromNeighborSpread(node, clique, parameters, day):
    '''Random layer spread from infected neighbors to node'''
    newInfected = 0
    connections = min(random.randint(0, node.activity), len(clique))
    infectedNeighbors = 0
    infectedInClique = []
    neighborP = 1
    for neighborNode in random.sample(clique, connections):
        if neighborNode.present['R'] & neighborNode.sick:
            infectedNeighbors += 1
            infectedInClique.append(neighborNode)
            neighborP = neighborP * (1-parameters.p['inf']['dynR'] * neighborNode.relInfectivity)
    neighborP = 1 - neighborP

    if random.random() < neighborP:
        if node.age > 10:
            ancestor = random.choice(infectedInClique)
            node.infectNode(ancestor, 'R', day, parameters)
            newInfected += 1
        else:
            if random.random() < 0.3:
                ancestor = random.choice(infectedInClique)
                node.infectNode(ancestor, 'R', day, parameters)
                newInfected += 1
    return newInfected


def testing(layers, attrs, parameters, day):
    tests = 0
    testRules = parameters.testRules
    if testRules['strat'] != 'Symptomatic':
            if testRules['mode'] == 'FullHH':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool.testDay:
                        pool.testAndQuarantine(parameters, testRules['fnr'], testRules['fpr'])
                        tests += len(pool)
            if testRules['mode'] == 'Adults':
                for pool in testRules['pools']:
                    if (day % testRules['freq']) == pool['testDay']:
                        pool.testAndQuarantineAdults(parameters, testRules['fnr'], testRules['fpr'], testRules['age'])
                        tests += len(pool)
    else:
        for node in attrs.values():
            if node.state == 'Is':
                if node.lastDay == (day-2):
                    node.individualTestAndQuarantine(layers, day, parameters)
                    tests += 1
    
    return tests


def timedRun(attrs, layers, parameters):
    '''Run of the model for a given number of days'''
    parameters.p = setStrategy(strat, baseP, layers, attrs)
    parameters.testRules = setTestRules(parameters.testing, layers, attrs)

    stateLog = []
    infectedLog = []
    infectedLogByLayer = []

    cont = 1
    day = parameters.startDay
    endDay = day + parameters.runDays

    timeUsed = []
                   
    while cont and (day < endDay):
        day+=1
        dayTime = time.time() 

        dailyInfected = 0
    
        cont, linfs, dailyInfected, tests = systemDay(layers, attrs, parameters, day)

        states_ = countState(attrs, stateList)
        states_['T'] = tests
        stateLog.append(states_)
        infectedLog.append(dailyInfected)
        infectedLogByLayer.append(linfs)

        timeUsed.append(time.time() - dayTime)

        printProgress(day, parameters.runDays, timeUsed, bar_length=50) if parameters.printResults else None

    return stateLog, infectedLog, infectedLogByLayer


def runModel(parameters):
    layers, attrs = initialiseModel(parameters)

    parameters.inVec = convertVector(parameters.strategy)
    parameters.testing = {'testStrat': 'TPHT', 'capacity':5000, 'cutoff': 3}
    
    start = time.time()
    stateLog, infLog, infLogByLayer = timedRun(attrs, layers, parameters)
    
    runtime = time.time() - start


    '''Print and/ or save results (default: True)'''
    printResults(stateLog, infLogByLayer, parameters, runtime) if parameters.printResults else None
    saveResults(stateLog, infLogByLayer, parameters) if parameters.saveResults else None
    saveDiseaseTree(parameters) if parameters.createNetwork else None

    return stateLog, infLog, infLogByLayer


def profiler(saveStats=True):
    '''Profiling to benchmark the code'''
    import cProfile, pstats
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    # stats.strip_dirs()
    stats.print_stats(10)
    if saveStats:
        stats.dump_stats('profilers/profile')


def main():
    parameters = Parameters(
        infected=1000, 
        runDays=100, 
        cityName='Trondheim',
        saveResults=True, 
        createNetwork=False,
        printResults=True
        )

    runModel(parameters)


if __name__ == '__main__':
    # main()
    profiler()

