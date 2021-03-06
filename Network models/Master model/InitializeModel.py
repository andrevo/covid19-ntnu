import random
from modelFuncs import *

stateList = ['S', 'E', 'I', 'R', 'H', 'D']


#Distribution of household sizes

hhWeights = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5]

nNodes = 2*pow(10, 5) #Trondheim
#nNodes = 7*pow(10, 5) #Oslo

hCap = 100 #Max hospital capacity

seq = list(range(nNodes)) #Initializes nodes


layers = ['BH', 'BS', 'US', 'VS', 'W', 'HH', 'R']

cliques = {}
for layer in layers:
    cliques[layer] = []



attrs = {}
for node in seq:
    attrs[node] = {}

for node in range(nNodes):
    attrs[node]['state']= ['S', 0]
    
    attrs[node]['ageGroup'] = 0
    
adults = [] #IDs of adults
children = [] #IDs of children
elderly = [] #IDs of elderly

#Household assignment

i = 0
cn = 0


random.shuffle(seq)

#Trondheim
n = {}
n['BH'] = 265
n['BS'] = 30
n['US'] = 20
n['VS'] = 15


#Oslo

#nBh = 733
#nBs= 115
#NUs = 62
#nVh = 29


#Generating 
for layer in ['BH', 'BS', 'US', 'VS']:
    for i in range(n[layer]):
        cliques[layer].append([])


#Generating age groups and creating individual containers
ageGroups = ['B', 'A1', 'A2', 'E1', 'E2']
ageLists = {}
for group in ageGroups:
    ageLists[group] = []


i = 0
while(i < nNodes):
    fs = hhWeights[random.randint(0,len(hhWeights)-1)]
    t = min(i+fs, nNodes)
    clique = []
    for j in range(i, t):
        clique.append(seq[j])

    ar = random.random()
    for j in range(i, min(t, i+2)):


        if fs > 2:
            if ar < 0.2:
                attrs[seq[j]]['ageGroup'] = 'A2'
            else:
                attrs[seq[j]]['ageGroup'] = 'A1'
            adults.append(seq[j])
        else:
            if ar < 0.3:
                attrs[seq[j]]['ageGroup'] = 'A1'
                adults.append(seq[j])
            elif ar < 0.6:
                attrs[seq[j]]['ageGroup'] = 'A2'
                adults.append(seq[j])
            elif ar < 0.9:
                attrs[seq[j]]['ageGroup'] = 'E1'
                elderly.append(seq[j])
            else:
                attrs[seq[j]]['ageGroup'] = 'E2'
                elderly.append(seq[j])

        
    fBh = random.randint(0, n['BH']-1)
    fBs = random.randint(0, n['BS']-1)
    fUs = random.randint(0, n['US']-1) #Antar barne- og ungdomsskole er uavhengig
    #VGS er tilfeldig

    if fs > 2:
        for j in range(i+2, t):
            year = random.randint(0, 23)
            if year < 6:
                attrs[seq[j]]['ageGroup'] = 'B'
                
                cliques['BH'][fBh].append(seq[j])
            if  (year < 13):
                attrs[seq[j]]['ageGroup'] = 'B'
                cliques['BS'][fBs].append(seq[j])
            elif year < 16:
                attrs[seq[j]]['ageGroup'] = 'B'
                cliques['US'][fUs].append(seq[j])

            elif year < 19:
                attrs[seq[j]]['ageGroup'] = 'B'
                cliques['VS'][random.randint(0, n['VS']-1)].append(seq[j])

            else:
                attrs[seq[j]]['ageGroup'] = 'A1'

            if year < 19:
                children.append(seq[j])

            else:
                adults.append(seq[j])

            
    cliques['HH'].append(clique)
    i = t



print "Households and schools created"

#Count number of people by age group
for node in seq:
    ageLists[attrs[node]['ageGroup']].append(node)


#Work assignment

i = 0

random.shuffle(adults)

nAdults = len(adults)

while(i < nAdults):
    fs = random.randint(10, 500)
    t = min(i+fs, nAdults)
    clique = []
    for j in range(i, t):
        clique.append(adults[j])
    cliques['W'].append(clique)
    i = t

print "Workplaces created"
    

#Random cliques

i = 0
random.shuffle(seq)
rCliques = []
cliques['R'].append(seq)


i0 = 20
#Initial infection
for i in range(i0):
    attrs[seq[i]]['state'] = ['I', 0, random.randint(1, 10)]



#"Vaccination"
for node in seq:
    if attrs[node]['ageGroup'] in ['B', 'A1', 'A2']:
        if random.random() < 0:
            attrs[node]['state'] = 'R'



genActivity(attrs, [10, 3, -.75])

