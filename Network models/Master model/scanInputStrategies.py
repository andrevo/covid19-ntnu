from InitializeModel import *
from modelFuncs import *

cont = 1
i = 0


f = open('strategyScanResults.txt', 'w')
for i in [0, 1]:
    for j in [0, 1]:
        for k in range(4):
            strat = [i, j, k]
            #stateLog, infLog, infLogByLayer = fullRun(state, cliques, ageGroup, strat, baseP)
            #R = modelFuncs.findR(R, 0)
            rs = []
            for l in range(100):
                inVec = convertVector(strat)
                openLayers, p = setStrategy(inVec, baseP, layers)
                state = genBlankState(len(state))
                seedState(state, 1000)
                cont, linf, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, 0)
                count = countState(state, stateList)
                r = float(dailyInfs)/count['R']
                rs.append(r)
            print strat, np.mean(rs), np.var(rs)
            print >> f, str(strat[0])+'\t'+str(strat[1])+'\t'+str(strat[2])+'\t'+str(np.mean(rs))+'\t'+str(np.var(rs))

f.close()
