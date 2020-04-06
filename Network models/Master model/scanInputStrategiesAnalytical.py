from InitializeModel import *
from modelFuncs import *

cont = 1
i = 0



#sP = 0.1

#baseP['inf']['BH'] = sP
#baseP['inf']['BS'] = sP
#baseP['inf']['VS'] = sP
#baseP['inf']['US'] = sP


f = open('anStrategyScanResults.txt', 'w')
for i in [0, 1]:
    for j in [0, 1]:
        for k in range(4):
            strat = [i, j, k]
            #stateLog, infLog, infLogByLayer = fullRun(state, cliques, ageGroup, strat, baseP)
            #R = modelFuncs.findR(R, 0)
            rs = []
            inVec = convertVector(strat)
            openLayers, p = setStrategy(inVec, baseP, layers)
            openLayers['HH'] = False
            state = genBlankState(len(state))
            seedState(state, 1000)
            
            r = analyticalR(cliques, openLayers, state, p)
            #print strat
 #           print openLayers
 #           print p['inf']
            #print 'Effective R:', r
            #print >> f, str(strat[0])+'\t'+str(strat[1])+'\t'+str(strat[2])+'\t'+str(r)
            print r
f.close()
