from modelFuncs import *
from InitializeProbability import *

layers, ageGroup, cliques = readModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt')
state = genBlankState(len(ageGroup))
seedState(state, 100)



cont = 1
i = 0

stateLog = []
infLog = []
infLogByLayer = []
#state = copy.copy(seedState)

strats = [[0, 0, 1], [0, 1, 1], [0, 1, 2], [1, 1, 2], [1, 1, 3]]

strat = strats[4]
inVec = convertVector(strat)



while cont:
    i+= 1
    
    if i%10 == 0:
        print i

    if i == 20:
        strat = strats[2]
        inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)
    cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
    stateLog.append(countState(state, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)


dailyDeaths = []
iChange = []
hChange = []
dChange = []

dailyDeaths.append(0)

for i in range(1, len(stateLog)):
    dailyDeaths.append(stateLog[i]['D']-stateLog[i-1]['D'])
    iChange.append(stateLog[i]['I']-stateLog[i-1]['I'])
    hChange.append(stateLog[i]['H']-stateLog[i-1]['H'])
    dChange.append(dailyDeaths[i]-dailyDeaths[i-1])
