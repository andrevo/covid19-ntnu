import matlab.engine # NB: needs to come before we import modelFuncs (don't know why)
import scipy.io
import numpy
import os
import sys
from joblib import Parallel, delayed
import multiprocessing
from collections import deque
from modelFuncs import *

# 6 strats
strats = [{'S':0, 'W':0.0, 'R':0}, {'S':9, 'W':0.0, 'R':0}, {'S':9, 'W':0.4, 'R':1}, {'S':20, 'W':0.4, 'R':1}, {'S':20, 'W':0.8, 'R':2}, {'S':20, 'W':1.0, 'R':3}]

def controlledRun(simDays,k):
    layers, attrs = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    #layers, attrs = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
    
    # Start matlab engine and set paths to casadi and MPC code
    eng = matlab.engine.start_matlab()
    eng.addpath(r'/home/ubuntu/software/casadi')
    eng.addpath(r'/home/ubuntu/software/covid19_master/Control', nargout=0)
    
    # Run init script
    eng.problemDef(nargout=0)
    dt_u = 7
    N = eng.workspace['N_pop']

    # NB! this is used from day 0 to day 1!
    u = 0

    # History of previous I-vals
    I_prevs = deque(14*[[0]])
    # newest in front: [ [I[t-1]], [I[t-2]], ..., [I[t-14]] ]

    count = countState(attrs, stateList)

    # Define lists to store results
    stateLog = []
    infLog = []
    infLogByLayer = []
    u_out = []
    x_preds = []
    u_preds = []
    slack_vars = []
    t_preds = []

    cont = 1
    i = 0

    while cont and (i < simDays):
        S = float(count['S']) / N
        I = float(count['Ia'] + count['Ip']) / N
        ICU = float(count['ICU']) / N

        if (i % dt_u == 1):
            x = [[S], [I], [ICU]] + list(I_prevs)

            eng.workspace['x'] = matlab.double(x)
            eng.workspace['u'] = float(u)
            eng.eval('problem = initNLP(model,cost,constraints,options,x,u);',nargout=0)
            [x_opt,u_opt,s_opt,t_opt] = eng.eval('solveNLP(problem);',nargout=4)

            u = u_opt[0][0]

            x_preds.append(x_opt)
            u_preds.append(u_opt)
            slack_vars.append(s_opt)
            t_preds.append(t_opt)

        # Update list of previous I-vals
        I_prevs.appendleft([I])
        I_prevs.pop() # Removes from the right

        i += 1
        print i

        dailyInfs = 0
        
        strat = strats[int(u)]
        u_out.append(u)
        p = setStrategy(strat, baseP, layers, attrs)
        
        testRules = {}
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i, testRules)
        count = countState(attrs, stateList)
        stateLog.append(count)
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)

    data = {}
    data['x_preds'] = x_preds
    data['u_preds'] = u_preds
    data['slack_vars'] = slack_vars
    data['t_preds'] = t_preds
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])

    dir = os.path.join(os.getcwd(),"new_model")
    if not os.path.exists(dir):
        os.mkdir(dir)
    fileName = 'new_model/closedLoop_test_run' + str(k) + '.mat'
    scipy.io.savemat(fileName,data)

#if __name__ == "__main__":
days = 200
num_cores = 10 # multiprocessing.cpu_count()
N = 10 # num_cores
Parallel(n_jobs=num_cores, verbose=10)(delayed(controlledRun)(days,k) for k in range(N))








