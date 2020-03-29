import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random
import operator

def infectSIR(network, state, node, p):
    for nb in network[node]:
        if state[nb] == 'S':
            if random.random() < p:
                state[nb] = 'I'

def infectSEIR(network, state, node, p):
    for nb in network[node]:
        if state[nb] == 'S':
            if random.random() < p:
                state[nb] = 'E'

def incubate(state, node, p):
    if random.random() < p:
        state[node] = 'I'
                
def recover(state, node, p):
    if random.random() < p:
        state[node] = 'R'
        

                
def SEIRday(network, pi, pe, pr, state, cont):
    for node in network:
        if state[node] == 'I':
            cont[0] = 1
            infectSEIR(network, state, node, pi)
            recover(state, node, pr)
        if state[node] == 'E':
            incubate(state, node, pe)

def SIRday(network, pi, pr, state, cont):

    for node in network:
        if state[node] == 'I':
            cont[0] = 1
            infectSIR(network, state, node, pi)
            recover(state, node, pr)

def initializeStates(network, i0):
    state = []
    for node in range(max(network)+1):
        state.append('S')
    for i in random.sample(network.nodes(), i0):
        state[i] = 'I'
        
    return state


def SEIR(network, pi, pe, pr, i0):

    infDay = [0]*(max(network)+1)
    state = initializeStates(network, i0)
    cont = [1] #Ugly as hell to allow pass by reference
    days = 0
    
    while (cont[0]):
        cont = [0]
        days += 1

        SEIRday(network, pi, pe, pr, state, cont)

        for node in network:
            if (state[node] == 'S'):
                infDay[node] = days

    cases = 0
    for node in network:
        if state[node] == 'R':
            cases += 1
    return (cases, days, infDay)

def BTT(network, pi, pe, pr, i0, qr, db, dt):

    infDay = [0]*(max(network)+1)
    state = initializeStates(network, i0)
    cont = [1] #Ugly as hell to allow pass by reference
    days = 0

    #Bait
    
    for i in range(db):
        days +=1
        SEIRday(network, pi, pe, pr, state, cont)
        for node in network:
            if (state[node] == 'S'):
                infDay[node] = days

    #Trap
    pq = pi*qr

    for j in range(dt):
        days += 1
        
        SEIRday(network, pq, pe, pr, state, cont)
        for node in network:
            if (state[node] == 'S'):
                infDay[node] = days

    #Tame
    stillHealthy = []
    for i in range(len(state)):
        if state[i] == 'S':
            stillHealthy.append(i)

    for i in random.sample(stillHealthy, i0):
        state[i] = 'I'
    
    while (cont[0]):
        cont = [0]
        days += 1

        SEIRday(network, pi, pe, pr, state, cont)

        for node in network:
            if (state[node] == 'S'):
                infDay[node] = days

            
    cases = 0
    for node in network:
        if state[node] == 'R':
            cases += 1
    return (cases, days, infDay)



def SIR(network, pi, pr, i0):

    infDay = [0]*(max(network)+1)
    state = initializeStates(network, i0)
    cont = [1] #Ugly as hell to allow pass by reference
    days = 0
    
    while (cont[0]):
        cont = [0]
        days += 1

        SIRday(network, pi, pr, state, cont)

        for node in network:
            if (state[node] == 'S'):
                infDay[node] = days

    cases = 0
    for node in network:
        if state[node] == 'R':
            cases += 1
    return (cases, days, infDay)


n = 10000
k = 4

pi = 0.05
pe = 0.1
pr = 0.2
i0 = 50
qr = 0.05
db = 10
dt = 100

network = nx.barabasi_albert_graph(n, k)

#run = SIR(network, pi, pr, i0)
#run = SEIR(network, pi, pe, pr, i0)

bttAvg = []
ctrAvg = []
ratioAvg = []

for db in range(100):
    #print db
    bttRes = []
    ctrRes = []
    ratio = []
    for i in range(10):
        run = BTT(network, pi, pe, pr, i0, qr, db, dt)
        control = SEIR(network, pi, pe, pr, i0)
        bttRes.append(run[0])
        ctrRes.append(control[0])
        ratio.append(float(run[0])/float(control[0]))
        #print run[0], control[0]
    bttAvg.append(np.mean(bttRes))
    ctrAvg.append(np.mean(ctrRes))
    ratioAvg.append(np.mean(ratio))
    print db, bttAvg[db], ctrAvg[db], ratioAvg[db], np.median(ratio), '\t',  max(ratio), min(ctrRes)
#print run[0], control[0]
degList = []
for node in range(max(network)+1):
    degList.append(network.degree(node))


hist = []
for i in range(max(degList)+1):
    hist.append([0]*(run[1]+1))

for i in range(max(network)+1):
    hist[degList[i]][run[2][i]] += 1
    


#plt.plot(degList, run[2], 'ro')
#plt.show()




