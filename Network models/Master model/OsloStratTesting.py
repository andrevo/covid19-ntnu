import matplotlib.pyplot as plt
from modelFuncs import *
from runParams import *
import datetime
import pickle
from joblib import Parallel, delayed
import multiprocessing

ncores = multiprocessing.cpu_count()

baseP['inf'] = {'BH': 0.00015, 'BS': 0.00015, 'US': 0.00015, 'VS': 0.00015, 'W': 0.00015, 'R': 0.5*pow(10, -6), 'HH': 0.30, 'NH':0.2, 'dynR': 0.0075}

layers, attrs= initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -0.5], 20)
for node in attrs:
    attrs[node]['act'] = min(attrs[node]['act'], 100)


lockDay = 20
schoolOpenDays = 40


def testRun(attrs, layers, baseP):

    genBlankState(attrs)
    seedState(attrs, 20)
    strat = {'S': 20, 'W': 1, 'R': 3}
    stateLog1, infLog1, infLogByLayer1, i1 = initRun(attrs, layers, strat, baseP, 400)

    strat = {'S': 0, 'W': 0.5, 'R': 1}
    stateLog2, infLog2, infLogByLayer2, i2 = timedRun(attrs, layers, strat, baseP, i1, 39)
    strat = {'S': 6, 'W': 0.5, 'R': 1}
    stateLog3, infLog3, infLogByLayer3, i3 = timedRun(attrs, layers, strat, baseP, i2, 7)
    
    strat = {'S': 10, 'W': 0.5, 'R': 1}

    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("TPHT test")

    testing = {'testStrat': 'TPHT', 'capacity':50000, 'cutoff': 3}
    stateLogTPHT, infLogTPHT, infLogByLayerTPHT, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50, testing)

    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("TPHTA test")

    testing = {'testStrat': 'TPHTA', 'capacity':50000, 'cutoff': 3, 'age':18}    
    stateLogTPHTA, infLogTPHTA, infLogByLayerTPHTA, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50, testing)

    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("TPHTA test")

    testing = {'testStrat': 'TPHTA', 'capacity':50000, 'cutoff': 3, 'age': 12}    
    stateLogTPHTA2, infLogTPHTA2, infLogByLayerTPHTA2, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50, testing)


    
    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("RPHT test")
    testing = {'testStrat': 'RPHT', 'capacity':50000}

    stateLogRPHT, infLogRPHT, infLogByLayerRPHT, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50, testing)

    
    
    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("RIT test")
    testing = {'testStrat': 'RIT', 'capacity':50000}

    stateLogRIT, infLogRIT, infLogByLayerRIT, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50, testing)

    attrsFork = copy.deepcopy(attrs)
    layersFork = copy.deepcopy(layers)
    print("NT test")
    stateLogNT, infLogNT, infLogByLayerNT, i = timedRun(attrsFork, layersFork, strat, baseP, i2, 50)
    
    return stateLog1, stateLog2, stateLog3, stateLogTPHT, stateLogTPHTA, stateLogTPHTA2, stateLogRPHT, stateLogRIT, stateLogNT, i1




for i in range(1):
    print("Run "+str(i))
    stateLog1, stateLog2, stateLog3, stateLogTPHT, stateLogTPHTA, stateLogTPHTA2, stateLogRPHT, stateLogRIT, stateLogNT, lockDay = testRun(attrs, layers, baseP)

    stateLog = {'1': stateLog1, '2': stateLog2, '3': stateLog3, 'TPHT': stateLogTPHT, 'RPHT': stateLogRPHT, 'TPHTA': stateLogTPHTA, 'RIT': stateLogRIT, 'NT': stateLogNT, 'LockDay': lockDay}


    f = open("StratRuns/StratRun"+str(i)+".pkl", "wb")
    pickle.dump(stateLog, f)
    f.close()


#processed_list = Parallel(n_jobs=ncores)(delayed(twoStepRun)(attrs, layers, cliques, baseP, 0, 16, 60) for i in range(ncores))
#stateLog, infLogByLayer, infLog = twoStepRun(attrs, layers, cliques, baseP, 0, 16, 50)

# strat = {'S': 0, 'W': 0, 'R': 2}
# stateLog1, infLog1, infLogByLayer1, i1 = timedRun(attrs, layers, cliques, strat, baseP, 0, 16) #Initial



lockDate = datetime.date(2020, 3, 13)
delta = datetime.timedelta(days=1)
startDate = lockDate-delta*lockDay

