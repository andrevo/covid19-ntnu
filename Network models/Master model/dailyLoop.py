from InitializeModel import *
from modelFuncs import *

cont = 1
i = 0



tCounts = {}
for s in stateList:
    tCounts[s] = []

hospt = []
Reff = []

stateLog = []
infLog = []
infLogByLayer = []

inVec = [0, 0, 1]
inVec = convertVector(inVec)

baseP = p.copy()
p = baseP.copy()
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
                
    
#     counts = {}
#     for s in stateList:
#         counts[s] = 0
    
#     for s in state:
#         counts[s] += 1

#     for s in stateList:
#         tCounts[s].append(counts[s])
        
#     if (i > 2):
#         recoveries = tCounts['R'][-1]-tCounts['R'][-2]
#         Reff.append(float(dailyInfs)/max(float(recoveries), 1))
#         dailyrec.append(recoveries)
    
#     dailyt.append(dailyInfs)


#     if (cont == 0):
#         print i, "Reinfect",
#         for layer in layers:
#             print layer, lInfs[layer],
#         print ''
#         repeats += 1
#         for cond in rel:
#             rel[cond] = 0

        
#         if repeats < 2:
#             cont = 1
#             random.shuffle(seq)
#             for j in range(10):
#                 state[seq[j]] = 'I'

# for s in stateList:     
#     print s, counts[s]
    
# #print healthy, latent, infected, recovered, dead


# dead = {}
# for group in ageGroups:
#     dead[group] = 0
    
# for node in seq:
#     if state[node] == 'D':
#         dead[ageGroup[node]] += 1
# print counts
# print "Death count"

# for group in ageGroups:
#     print group, dead[group], 'dead out of', len(ageLists[group])
