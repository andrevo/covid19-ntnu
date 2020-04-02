import random
import numpy as np

stateList = ['S', 'E', 'I', 'R', 'H', 'D']

def genRandomClique(seq, ub):
    rs = pow(random.random(), 0.5)
    cSize = min(1+int(1/rs), len(seq), ub)
    clique = random.sample(seq, cSize)
    return clique


#Runs infections over a day 
def cliqueDay(clique, state, p, day):

    susceptible = 0
    infected = 0
    susClique = []
    for node in clique:
        if state[node][0] == 'S':
            susClique.append(node)
        if state[node][0] == 'I':
            infected += 1
    susceptible = len(susClique)
    effP = 1-pow(1-p, infected)
    #newInfs = np.random.binomial(susceptible, effP)
    newInfs = random.sample(susClique, np.random.binomial(susceptible, effP))
    for nb in newInfs:
        state[nb] = ['E', day]
        
        
    return newInfs




#Turns latent into infectious
def incubate(node, state, p, day):
    r = random.random()
    if r < p:
        state[node] = ['I', day]

#Infectious to recovered, hospital, or back into susceptible
def recover(node, state, pr, ph, pni, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+ph:
        state[node] = ['H', day]
    elif r < pr+ph+pni:
        state[node] = ['S', day]

#Hospitalized to dead or recovered
def hospital(node, state, pr, pc, day):
    r = random.random()
    if r < pr:
        state[node] = ['R', day]
    elif r < pr+pc:
        state[node] = ['D', day]


def systemDay(cliques, state, ageGroup, p, day):

    cont = 0
    p = {}
    p['inf'] = {'BH': 0.0002, 'BS': 0.0002, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -6), 'HH': 0.1}
    p['rec'] = 0.1
    p['inc'] = 1
    p['H'] = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184} 
    p['D'] = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 } 
    p['NI'] = 0
    
    for layer in cliques:
        if True: #i > rel[layer]:
            for clique in cliques[layer]:
                infs = cliqueDay(clique, state, p['inf'][layer], day)
                #lInfs[layer] += len(infs)
                #dailyInfs += len(infs)
                
                           
        
    for node in range(len(state)):
        if state[node][0] == 'E':
            incubate(node, state, p['inc'], day)
            cont = True
        if state[node][0] == 'I':
            recover(node, state, p['rec'], p['rec']*p['H'][ageGroup[node]], p['NI'], day)
            cont = True
        if state[node][0] == 'H':
            hospital(node, state, p['rec'], p['rec']*p['D'][ageGroup[node]], day)
            cont = True
    
    return cont


def countState(state, stateList):
    count = {}
    for s in stateList:
        count[s] = 0
    for node in state:
        count[node[0]] += 1
    return count
