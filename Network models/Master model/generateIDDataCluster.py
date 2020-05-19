from modelFuncs import *
import scipy.io
import numpy
import os
import sys
from random import randint

# 6 strats
strats = [{'S':0, 'W':0.0, 'R':0}, {'S':9, 'W':0.0, 'R':0}, {'S':9, 'W':0.4, 'R':1}, {'S':20, 'W':0.4, 'R':1}, {'S':20, 'W':0.8, 'R':2}, {'S':20, 'W':1.0, 'R':3}]

def run_days(u,delay,delayCount,constant,runDays,controlInterval):
    folder = "covid19-ntnu/Network models/Master model/"
    layers, attrs = initModel(folder + 'idAndAge_Trondheim.txt', folder + 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)

    curDay = 0
    cont = 1
    i = curDay

    startStrat = {'S': 20, 'W': 1.0, 'R': 3}

    if(not delay):
        startStrat = strats[u]

    p = setStrategy(startStrat, baseP, layers, attrs)

    uLog = []
    stateLog = []
    infLog = []
    infLogByLayer = []
    endDay = curDay + runDays

    #testing = {'testStrat': 'TPHT', 'capacity': t, 'cutoff': 3}
    testing = {}
    testRules = setTestRules(testing, layers, attrs)

    init = False

    while cont and (i < endDay):
        if constant and delay and (not init) and (count['Ia'] >= delayCount):
            strat = strats[u]
            p = setStrategy(strat, baseP, layers, attrs)
            #testing = {'testStrat': 'TPHT', 'capacity': t, 'cutoff': 3}
            #testRules = setTestRules(testing, layers, attrs)
            init = True
        if not constant:
            if (delay and (count['Ia'] >= delayCount)) or not delay:
                if(not i % controlInterval):
                    u = randint(0, len(strats) - 1)
                    strat = strats[u]
                    p = setStrategy(strat, baseP, layers, attrs)
        
        i += 1
        sys.stdout.flush()
        sys.stdout.write(str(i) + '\r')

        dailyInfs = 0

        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i, testRules)
        count = countState(attrs, stateList)
        stateLog.append(count)
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)
        uLog.append(u)

    return uLog, stateLog, infLogByLayer

def run_strat_and_save(u,delay,delayCount,constant,maxDays,controlInterval,k):
    uLog, stateLog, infLogByLayer = run_days(u,delay,delayCount,constant,maxDays,controlInterval)

    data = {}
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])
    layers = ['HH','W','BH','BS','US','VS','NH','Rp']

    for layer in layers:
        data[layer] = numpy.array([d[layer] for d in infLogByLayer])

    data['u'] = numpy.array(uLog)

    fileName = 'results/u' + str(u) + '_run' + str(k) + '.mat'
    scipy.io.savemat(fileName, data)
    print fileName + " saved!"


if __name__ == "__main__":
    if len(sys.argv)>7:
        u = int(sys.argv[1])
        delay = t_vals[int(sys.argv[2])]
        delayCount = int(sys.argv[3])
        constant = int(sys.argv[4])
        maxDays = int(sys.argv[5])
        controlInterval = int(sys.argv[6])
        k = int(sys.argv[7])


        #delayCount = 100
        #maxDays = 200
        #controlInterval = 40

        run_strat_and_save(u, delay, delayCount, constant, maxDays, controlInterval, k)

    else:
        print "An insufficient number of arguments provided!"

