from modelFuncs import *
from InitializeProbability import *

#layers, attrs, cliques = readModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt')
layers, attrs, cliques = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -1], 20)
#genBlankState(attrs)
#seedState(attrs, 20)

strat = {'S': 1, 'W': 1, 'R': 3}
inVec = convertVector(strat)

stateLog, infLog, infLogByLayer, i, = fullRun(attrs, layers, cliques, strat, baseP)


