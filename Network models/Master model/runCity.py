from modelFuncs import *
from InitializeProbability import *

#layers, attrs, cliques = readModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt')
layers, attrs, cliques = initModel('idAndAge_'+city+'.txt', 'socialNetwork_'+city+'.txt', '', baseP, [10, 3, -0.75], 20)
#genBlankState(attrs)
#seedState(attrs, 20)

strat = {'S': 1, 'W': 1, 'R': 3}
inVec = convertVector(strat)

#stateLog, infLog, infLogByLayer, i = fullRun(attrs, layers, cliques, strat, baseP)
stateLog, infLog, infLogByLayer, i = timedRun(attrs, layers, cliques, strat, baseP, 0, 20)


#Adjusting layers for control
controlCliques = {}
for layer in layers:
    controlCliques[layer] = []

for layer in ['NH', 'HH', 'BH', 'R']:
    controlCliques[layer] = copy.deepcopy(cliques[layer])

for layer in ['BS', 'US', 'VS']:
    for clique in cliques[layer]:
        controlCliques[layer].append(filterCliqueAttribute(clique, attrs, 'age', 0, 'lowPass'))

for clique in cliques['W']:
    if random.random() < 0.5:
        controlCliques['W'].append(copy.copy(clique))

controlAttrs = copy.deepcopy(attrs)
for node in attrs:
    controlAttrs[node]['act'] = min(attrs[node]['act'], 5)


stateLogC, infLogC, infLogByLayerC, i = timedRun(controlAttrs, layers, controlCliques, strat, baseP, 20, 60)

