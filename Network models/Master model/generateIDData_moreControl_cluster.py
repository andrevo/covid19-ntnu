from modelFuncs import *
import scipy.io
import numpy
import os
import sys

def run_strat_days(strat,days):
    folder = "covid19-ntnu/Network models/Master model/"
    layers, attrs = initModel(folder + 'idAndAge_Trondheim.txt', folder + 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    stateLog, infLog, infLogByLayer, i, = timedRun(attrs, layers, strat, baseP, 0, days)
    return stateLog


def run_strat_and_save(r,w,s,k,maxDays,W,age,prefix):
    strat = {'S': age, 'W': float(w)/float(W-1), 'R': r}
    stateLog = run_strat_days(strat,maxDays)
    data = {}
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])
        fileName = 'results/age' + str(age) + '_w' + str(w) + 'W' + str(W) + '_r' + str(r) + '_run' + str(k) + '.mat'
        scipy.io.savemat(fileName, data)
        print fileName + " saved!"


if __name__ == "__main__":
    ages = [0,5,9,15,20]
    
    W = 4

    if len(sys.argv)>5:
        #prefix = sys.argv[1]
        prefix = ''
        r = int(sys.argv[1])
        w = int(sys.argv[2])
        s = int(sys.argv[3])

        k = int(sys.argv[4])

        maxDays = int(sys.argv[5])

        run_strat_and_save(r,w,s,k,maxDays,W,ages[s],prefix)

    else:
        print "An insufficient number of arguments provided!"

