from modelFuncs import *
import scipy.io
import numpy
from joblib import Parallel, delayed
import multiprocessing
import os

def run_strat_days(strat,days):
    layers, attrs = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    stateLog, infLog, infLogByLayer, i, = timedRun(attrs, layers, strat, baseP, 0, days)
    return stateLog


def run_strat_and_save(r,w,s,k,maxDays,W,age):
    strat = {'S': age, 'W': float(w)/float(W-1), 'R': r}
    stateLog = run_strat_days(strat,maxDays)
    data = {}
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])
        dir = os.path.join(os.getcwd(),"test_new_control")
        if not os.path.exists(dir):
            os.mkdir(dir)
        fileName = 'test_new_control/age' + str(age) + '_w' + str(w) + 'W' + str(W) + '_r' + str(r) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)

# Process state log
# stateList = ['S', 'E', 'Ia', 'Ip', 'Is', 'R', 'H', 'ICU', 'D']
def process_logs(logs,k):
    for u in range(len(logs)):
        data = {}
        for comp in stateList:
            data[comp] = numpy.array([d[comp] for d in logs[u]])
        
        fileName = 'data_trondheim_u2/data_dict_test_u' + str(u) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)

maxDays = 1000
N = 10
ages = [0,5,9,15,20]
S = len(ages)
W = 4
R = 4

#for u in range(len(strats)):
#    test_strat_multi(u,maxDays,N)

num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=num_cores, verbose=10)(delayed(run_strat_and_save)(r,w,s,k,maxDays,W,ages[s]) for r in range(R) for w in range(W) for s in range(S) for k in range(N) )






