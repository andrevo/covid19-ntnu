from InitializeModel import *
from modelFuncs import *

baseP = {}
baseP['inf'] = {'BH': 0.0002, 'BS': 0.0002, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -7), 'HH': 0.1, 'NH':0.01}
baseP['rec'] = 0.1
baseP['inc'] = 1
baseP['H'] = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184} 
baseP['D'] = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 } 
baseP['NI'] = 0


cont = 1
i = 0

stateLog = []
infLog = []
infLogByLayer = []
#state = copy.copy(seedState)

state = genBlankState(2*pow(10, 5))
seedState(state, 20)

strats = [{'S':0, 'W':0, 'R':1}, {'S':0, 'W':1, 'R':1}, {'S':0, 'W':1, 'R':2}, {'S':1, 'W':1, 'R':2}, {'S':1, 'W':1, 'R':3}]

strat = strats[4]
inVec = convertVector(strat)


openLayers, p = setStrategy(inVec, baseP, layers)

#Initial uncontrolled spread
while i < 20:
    i+= 1
    
    if i%10 == 0:
        print i

    cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
    stateLog.append(countState(state, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)


#Full restriction

strat = strats[0]
inVec = convertVector(strat)


openLayers, p = setStrategy(inVec, baseP, layers)

while i < 40:
    i+= 1
    
    if i%10 == 0:
        print i
    
    cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
    stateLog.append(countState(state, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)




#Testing release state
parStates = []
infLogs = []
infLogsByLayer = []
stateLogs = []
openLayers['W'] = True
openLayers['BH'] = True
ratio = [0.01, 0.5, 1, 3, 100]

for j in range(5):
    parStates.append(copy.deepcopy(state))
    stateLogs.append(copy.deepcopy(stateLog))
    infLogs.append(copy.deepcopy(infLog))
    infLogsByLayer.append(copy.deepcopy(infLogsByLayer))
    i = 40
    cont = True

    p['inf']['BH'] = baseP['inf']['BH']*ratio[j]
    
    while cont:

        i += 1
        if i%10 == 0:
            print j, i
        cont, linfs, dailyInfs = systemDay(cliques, parStates[j], ageGroup, openLayers, p, i)
        stateLogs[j].append(countState(parStates[j], stateList))
        infLogs[j].append(dailyInfs)
        infLogsByLayer[j].append(linfs)

        if i == 100:
            cont = False
    


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
