from InitializeModel import *
from modelFuncs import *

cont = 1
i = 0

baseP = {}
baseP['inf'] = {'BH': 0.0002, 'BS': 0.0002, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -6), 'HH': 0.1}
baseP['rec'] = 0.1
baseP['inc'] = 1
baseP['H'] = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184}
baseP['D'] = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 }
baseP['NI'] = 0

stateLog = []
infLog = []
infLogByLayer = []


inVec = [1, 1, 3]
inVec = convertVector(inVec)
openLayers, p =  setStrategy(inVec, baseP, layers)



while cont:
    
    i+=1
    if i%10 == 0:
        print i

    dailyInfs = 0
    
    cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
    stateLog.append(countState(state, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)
                
    
# dette er en test
