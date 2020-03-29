import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import operator

def infect(network, state, node, p):
    for nb in network[node]:
        if state[nb] == 'S':
            if random.random() < p:
                state[nb] = 'I'

def recover(state, node, p):
    if random.random() < p:
        state[node] = 'R'
            
def SIR(network, pi, pr, i0):
    state = []
    for node in range(max(network)+1):
        state.append('S')
    for i in random.sample(network.nodes(), i0):
        state[i] = 'I'
    cont = 1
    days = 0
    while (cont):
        cont = 0
        days += 1
        for node in network:
            if state[node] == 'I':

                cont = 1
                infect(network, state, node, pi)
                recover(state, node, pr)
    cases = 0
    for node in network:
        if state[node] == 'R':
            cases += 1
    return (cases, days)

n = 1000
k = 4

network = nx.barabasi_albert_graph(n, k)

degs = network.degree()

sorted_degs = sorted(degs.items(), key=operator.itemgetter(1))
sorted_degs.reverse()

i0 = 10
pi = 0.05
pr = 0.2

delNet = network.copy()
compSize = []
sick = []
print "Standard attack"

for i in sorted_degs[:-(i0+1)]:
    delNet.remove_node(i[0])
    comps = nx.connected_components(delNet)
    sRuns = []
    for i in range(50):
        sRuns.append(SIR(delNet, pi, pr, i0)[0])
    sick.append(np.mean(sRuns))
    #sick.append(SIR(delNet, pi, pr, i0)[0])
    sizes = [len(comp) for comp in comps]
    compSize.append(max(sizes))

totCases = []
for i in range(len(sick)):
    totCases.append(i+sick[i])


plt.subplot(311)
plt.plot(compSize, label='Full attack')
plt.subplot(312)
plt.plot(sick, label='Full attack')
plt.subplot(313)
plt.plot(totCases, label='Full attack')

saComp = compSize
saSick = sick




print "Fractional attack"

faComp = []
faSick = []

for pSafe in [0.75, 0.5, 0.25]:
    delNet = network.copy()
    compSize = []
    sick = []
    for i in sorted_degs[:-(i0+1)]:
        if random.random() < pSafe:
            delNet.remove_node(i[0])
            comps = nx.connected_components(delNet)
            sRuns = []
            for i in range(50):
                sRuns.append(SIR(delNet, pi, pr, i0)[0])
            sick.append(np.mean(sRuns))
            #sick.append(SIR(delNet, pi, pr, i0)[0])
            sizes = [len(comp) for comp in comps]
            compSize.append(max(sizes))

    totCases = []
    for i in range(len(sick)):
        totCases.append(i+sick[i])
    plt.subplot(311)
    plt.plot(compSize, label = 'Fractional, p='+str(pSafe))
    plt.subplot(312)
    plt.plot(sick, label='Fractional, p='+str(pSafe))
    plt.subplot(313)
    plt.plot(totCases, label='Fractional, p='+str(pSafe))

    faComp.append(compSize)
    faSick.append(sick)


seq = range(n)
random.shuffle(seq)
delNet = network.copy()
compSize = []
sick = []

print "Random failure"
for i in seq[:-(i0+1)]:

        delNet.remove_node(i)
        comps = nx.connected_components(delNet)
        sRuns = []
        for i in range(50):
            sRuns.append(SIR(delNet, pi, pr, i0)[0])
        sick.append(np.mean(sRuns))
        #sick.append(SIR(delNet, pi, pr, i0)[0])
        sizes = [len(comp) for comp in comps]
        compSize.append(max(sizes))

totCases = []
for i in range(len(sick)):
    totCases.append(i+sick[i])

raComp = compSize
raSick = sick


plt.subplot(311)
plt.plot(compSize, label='Random')
plt.subplot(312)
plt.plot(sick, label='Random')
plt.subplot(313)
plt.plot(totCases, label='Random')

plt.subplot(311)
plt.legend()

plt.subplot(312)
plt.legend()

plt.subplot(313)
plt.legend()

plt.savefig("FracAttack.png")
plt.show()
