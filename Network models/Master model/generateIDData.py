from modelFuncs import *
import scipy.io
import numpy
from joblib import Parallel, delayed
import multiprocessing

strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 1, 'R': 2},
              {'S': 1, 'W': 1, 'R': 3}]  # Schools

def run_u(u,days):
    layers, attrs, cliques = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    strat = strats[u]
    inVec = convertVector(strat)
    stateLog, infLog, infLogByLayer, i, = fullRun(attrs, layers, cliques, strat, baseP, days - 1)
    return stateLog


def test_all_strats(days,k):
    logs = []
    for u in range(len(strats)):
        stateLog = run_u(u,days)
        logs.append(stateLog)
    process_logs(logs,k)
    return logs

def test_all_strats_multi(days,N):
    num_cores = multiprocessing.cpu_count()
    #print num_cores
    Parallel(n_jobs=num_cores, verbose=10)(delayed(test_all_strats)(days,j) for j in range(N))

def test_strat_multi(u,days,N):
    num_cores = multiprocessing.cpu_count()
    logs = Parallel(n_jobs=num_cores, verbose=10)(delayed(run_u)(u,days) for j in range(N))
    for k in range(len(out)):
        data = {}
        for comp in stateList:
            data[comp] = numpy.array([d[comp] for d in logs[k]])
        fileName = 'data/data_dict_test_u' + str(u) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)

# Process state log
# stateList = ['S', 'E', 'Ia', 'Ip', 'Is', 'R', 'H', 'ICU', 'D']
def process_logs(logs,k):
    for u in range(len(logs)):
        data = {}
        for comp in stateList:
            data[comp] = numpy.array([d[comp] for d in logs[u]])
        fileName = 'data/data_dict_test_u' + str(u) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)

maxDays = 2
N = 2
for u in range(len(strats)):
    test_strat_multi(u,maxDays,N)