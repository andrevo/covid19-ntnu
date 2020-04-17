from InitializeProbability import *
from modelFuncs import *
import scipy.io
import numpy
from joblib import Parallel, delayed
import multiprocessing

def run_n(u):
    n_realizations = 10
    simDays = 1000

    strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 1, 'R': 2},
              {'S': 1, 'W': 1, 'R': 3}]  # Schools

    strat = strats[int(round(u))]
    inVec = convertVector(strat)

    S_out = []
    I_out = []
    H_out = []
    R_out = []
    D_out = []
    indices = []

    for k in range(n_realizations):
        execfile('InitializeModel.py',globals())
        openLayers, p = setStrategy(inVec, baseP, layers)

        j = 0
        cont = 1
        while (j <= simDays) and cont:
            j += 1
            print u,k,j

            cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, j)

            count = countState(attrs, stateList)
            S_out.append(count['S'])
            I_out.append(count['I'])
            H_out.append(count['H'])
            R_out.append(count['R'])
            D_out.append(count['D'])
        indices.append(j)

    data = {}
    data['S'] = numpy.array(S_out)
    data['I'] = numpy.array(I_out)
    data['H'] = numpy.array(H_out)
    data['R'] = numpy.array(R_out)
    data['D'] = numpy.array(D_out)
    data['indices'] = numpy.array(indices)
    fileName = 'data_' + str(u) + '.mat'
    scipy.io.savemat(fileName,data)

num_cores = multiprocessing.cpu_count()
print num_cores
Parallel(n_jobs=num_cores)(delayed(run_n)(l) for l in range(5))

