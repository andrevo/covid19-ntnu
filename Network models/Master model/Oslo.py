from modelFuncs import *
from InitializeParams import *

#layers, attrs, cliques = readModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt')
layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
#genBlankState(attrs)
#seedState(attrs, 20)

strat = {'S': 10, 'W': 1, 'R': 3}
inVec = convertVector(strat)

#stateLog, infLog, infLogByLayer, i, = fullRun(attrs, layers, strat, baseP)
stateLog, infLog, infLogByLayer, i, = timedRun(attrs, layers, strat, baseP, 0, 20)


