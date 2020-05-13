from modelFuncs import *
import scipy.io
import numpy
import os
import sys

def run_strat_days(strat,t,days):
    folder = "covid19-ntnu/Network models/Master model/"
    layers, attrs = initModel(folder + 'idAndAge_Trondheim.txt', folder + 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    testing = {'testStrat': 'TPHT', 'capacity': t, 'cutoff': 3}
    stateLog, infLog, infLogByLayer, i, = timedRun(attrs, layers, strat, baseP, 0, days, testing)
    return stateLog


def run_strat_and_save(r,t,k,maxDays):
    strat = {'S': 20, 'W': 1.0, 'R': r}
    stateLog = run_strat_days(strat,t,maxDays)
    data = {}
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])
        fileName = 'results/r' + str(r) + '_t' + str(t)  + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)
        print fileName + " saved!"


if __name__ == "__main__":
    t_vals = [0, 4670, 9340, 14010, 18689]

    if len(sys.argv)>4:
        r = int(sys.argv[1])
        t = t_vals[int(sys.argv[2])]
        k = int(sys.argv[3])
        maxDays = int(sys.argv[4])

        run_strat_and_save(r,t,k,maxDays)

    else:
        print "An insufficient number of arguments provided!"

