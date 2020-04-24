from modelFuncs import *
import scipy.io
import numpy
from joblib import Parallel, delayed
import multiprocessing
import os

strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 1, 'R': 2},{'S': 1, 'W': 1, 'R': 3}]  # Schools
#strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 0, 'W': 0, 'R': 2}, {'S': 0, 'W': 0, 'R': 3},{'S': 0, 'W': 1, 'R': 1}, {'S': 0, 'W': 1, 'R': 2}, {'S': 0, 'W': 1, 'R': 3},{'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 0, 'R': 3},{'S': 1, 'W': 1, 'R': 1}, {'S': 1, 'W': 1, 'R': 2}, {'S': 1, 'W': 1, 'R': 3}]  # All excep R=0


def run_u(u):
    layers, attrs, cliques = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs, cliques = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    strat = strats[u]
    inVec = convertVector(strat)
    stateLog, infLog, infLogByLayer, i, = fullRun(attrs, layers, cliques, strat, baseP)
    return stateLog

def run_u_days(u,days):
    layers, attrs, cliques = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs, cliques = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    strat = strats[u]
    inVec = convertVector(strat)
    stateLog, infLog, infLogByLayer, i, = fullRun(attrs, layers, cliques, strat, baseP, days)
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
    for k in range(len(logs)):
        data = {}
        for comp in stateList:
            data[comp] = numpy.array([d[comp] for d in logs[k]])
        fileName = 'data/data_dict_test_u' + str(u) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)

def run_u_and_save(u,k,days):
    stateLog = run_u(u)
    #stateLog = run_u_days(u,days)
    data = {}
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])
        dir = os.path.join(os.getcwd(),"data_trondheim_5u")
        if not os.path.exists(dir):
            os.mkdir(dir)
        fileName = 'data_trondheim_5u/data_dict_test_u' + str(u) + '_run' + str(k) + '.mat'
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

maxDays = 10000
N = 10
#for u in range(len(strats)):
#    test_strat_multi(u,maxDays,N)

num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=num_cores, verbose=10)(delayed(run_u_and_save)(u,k,maxDays) for k in range(N) for u in range(len(strats)))






