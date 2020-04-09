from modelFuncs import *
from InitializeProbability import *

layers, ageGroup, ageNb, cliques = readModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt')
state = genBlankState(len(ageGroup))
seedState(state, 20)

strat = {'S': 1, 'W': 1, 'R': 3}
inVec = convertVector(strat)

stateLog, infLog, infLogByLayer, i, = fullRun(state, layers, cliques, ageGroup, strat, baseP)

