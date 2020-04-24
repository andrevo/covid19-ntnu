from modelFuncs import *
import scipy.io
import numpy
import matplotlib.pyplot as plt
import matlab.engine
from joblib import Parallel, delayed
import multiprocessing
import os

def controlledRun(simDays,k):
    layers, seedAttrs, cliques = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    cont = 1
    i = 0
    
    strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 1, 'R': 2},
              {'S': 1, 'W': 1, 'R': 3}]  # Schools

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)

    eng = matlab.engine.start_matlab()
    eng.addpath(r'/home/ubuntu/software/casadi')
    eng.addpath(r'/home/ubuntu/software/covid19_master/MPC', nargout=0)
    eng.addpath(r'/home/ubuntu/software/covid19_master/MPC/models', nargout=0)

    # Population size
    N = 213999.0
    eng.workspace['N'] = N
    # Max ICU capacity [num individuals]

    ICU_max = 50.0
    if (k<8):
        ICU_max = 50
    elif (k < 16):
        ICU_max = 100
    elif (k < 24):
        ICU_max = 150
    else:
        ICU_max = 200

    
    eng.workspace['ICU_max'] = ICU_max

    # Run init script
    n_pade = 3
    eng.workspace['n_pade'] = matlab.double([n_pade])
    eng.init_SI_ICU_pade(nargout=0)
    eng.eval('opt.horizon = 80;', nargout=0)
    eng.eval('opt.integer = 0;', nargout=0)

    # Sample time for discretization [days]
    dt_u = 10.0
    eng.workspace['dt_u'] = dt_u

    # State [fraction of total population]
    p_S_0 = (N - 20.0) / N
    p_I_0 = 20.0 / N

    # NB! this is used from day 0 to day 1!
    u = 4.0  # assume no control at start

    # Disturbance estimate (integral action)
    d_est = 0.0
    k_I = 0.0#25.0

    # Initial condition for actual pade states
    z_0 = []
    for l in range(n_pade):
        z_0.append([0])
    eng.workspace['z_0'] = matlab.double(z_0)

    count = countState(attrs, stateList)

    d_est_out = []
    d_est_out.append(d_est)
    u_round_out = []
    u_raw_out = []
    ICU_pred= []
    S_preds = []
    I_preds = []
    z1_preds = []
    z2_preds = []
    z3_preds = []

    while cont and (i < simDays):
        I = float(count['Ia'] + count['Ip']) / N 

        if (i % dt_u == 1):
            S = float(count['S']) / N
            
            ICU = float(count['ICU']) / N

            x = [[S], [I]]
            eng.workspace['x'] = matlab.double(x)

            eng.workspace['d_est'] = d_est
            eng.eval('model.dyn_fun = @(x,u) dynamics_SIR_ICU_d_1(x,u,d_est,params,model.beta_fun,n_pade);', nargout=0)

            eng.workspace['u_prev'] = round(u)

            [u,info] = eng.eval('step_nmpc([x;z_0],u_prev,dt_u,model,objective,opt);',nargout=2)
            #u = eng.eval('step_nmpc([x;zeros(n_pade,1)],u_prev,dt_u,model,objective,opt);',nargout=2)

            S_preds.append(info["x_opt"][0])
            I_preds.append(info["x_opt"][1])
            z1_preds.append(info["x_opt"][2])
            z2_preds.append(info["x_opt"][3])
            z3_preds.append(info["x_opt"][4])

            e_y = 0.9 * ICU_max / N - ICU
            d_est += k_I * e_y

            #e_pred_out.append(N * e_y)
            d_est_out.append(d_est)
 
        if(i>0):
            eng.workspace['p_I'] = I
            eng.eval('u_z = p_I*(params.c*p_I + params.d);', nargout=0)
            eng.eval('z_0 = sim_z(params.A,params.B,u_z,z_0);', nargout=0) # NB! This is open-loop. Use observer?

            ICU_pred.append(eng.eval('params.C*z_0 + params.D*u_z'))


        i += 1
        print i
        #sys.stdout.flush()
        #sys.stdout.write(str(i) + '\r')

        dailyInfs = 0

        u_rounded = int(round(u))

        u_round_out.append(u_rounded)
        u_raw_out.append(u)

        strat = strats[u_rounded]
        inVec = convertVector(strat)
        openLayers, p = setStrategy(inVec, baseP, layers)

        cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
        count = countState(attrs, stateList)
        stateLog.append(count)
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)

    data = {}
    data['d_est'] = d_est_out
    data['u_raw'] = u_raw_out
    data['u_rounded'] = u_round_out
    data['S_preds'] = S_preds
    data['I_preds'] = I_preds
    data['z1_preds'] = z1_preds
    data['z2_preds'] = z2_preds
    data['z3_preds'] = z3_preds
    data['ICU_pred'] = ICU_pred
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])

    dir = os.path.join(os.getcwd(),"cl_data")
    if not os.path.exists(dir):
        os.mkdir(dir)
    fileName = 'cl_data/closedLoop_test_run' + str(k) + '.mat'
    scipy.io.savemat(fileName,data)


days = 10000
num_cores = multiprocessing.cpu_count()
N = num_cores
Parallel(n_jobs=num_cores, verbose=10)(delayed(controlledRun)(days,k) for k in range(N))








