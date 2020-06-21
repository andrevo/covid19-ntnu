from modelFuncs import *
import scipy.io
import numpy
import matplotlib.pyplot as plt
import matlab.engine
from joblib import Parallel, delayed
import multiprocessing
import os

def controlledRun(simDays,k):
    layers, seedAttrs = initModel('idAndAge_Trondheim.txt', 'socialNetwork_Trondheim.txt', '', baseP, [10, 3, -.75], 20)
    cont = 1
    i = 0
    
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
    ICU_max = 74.0
    H_max   = 270.0 # this actually includes ICU.. correct for this in next iteration..
    
    eng.workspace['ICU_max'] = ICU_max
    eng.workspace['H_max']   = H_max;
    eng.workspace['safety_factor'] = 0.7

    # Run init script
    eng.eval('opt.integer = 0;', nargout=0) # NB: need to come before init script
    eng.init_SIRHICU(nargout=0)
    #252
    eng.eval('opt.horizon = 98;', nargout=0) # 22 weeks   NB: this should be long enough, especially when using mixed integer optimization
    eng.eval('opt.RK4_steps = 2;',nargout=0)  # TODO: test what is the best value here..

    # Sample time for discretization [days]
    dt_u = 7.0 # 7days/1 week
    eng.workspace['dt_u'] = dt_u

    # NB! this is used from day 0 to day 1!
    u = matlab.double([[0.0], [0.0], [0.0]])  # assume full control at start

    # Disturbance estimate (integral action)
    # NB: currently not implemented!
    d_I = 0.0
    d_H = 0.0
    d_ICU = 0.0
    k_I   = -0.1
    k_H   = -0.01
    k_ICU = -0.01
    I_pred_last = 0.0
    H_pred_last = 0.0
    ICU_pred_last = 0.0

    H_dot = 0.0
    ICU_dot = 0.0
    H_LP = 0.0
    ICU_LP = 0.0

    LPs_out = []
    dots_out = []

    T_H = 0.1
    T_ICU = 0.1

    count = countState(attrs, stateList)

    d_out = []
    u_round_out = []
    u_raw_out = []

    x_preds = []
    u_preds = []
    slack_vars = []

    while cont and (i < simDays):
        S = float(count['S']) / N
        I = float(count['Ia'] + count['Ip']) / N
        H = float(count['H']) / N
        ICU = float(count['ICU']) / N

        if (i % dt_u == 1):
            if(i>1):
                # Update disturbance estimates
                d_I   += k_I   * (I_pred_last   - I)
                d_H   += k_H   * (H_pred_last   - H)
                d_ICU += k_ICU * (ICU_pred_last - ICU)

            x = [[S], [I], [H], [ICU]]
            eng.workspace['x'] = matlab.double(x)
            #print x

            #d_est = matlab.double([[d_I],[d_H],[d_ICU]])
            d_est = matlab.double([[0.0],[0.0],[0.0]])
            print d_est
            eng.workspace['d_est'] = d_est
            eng.eval("model.dyn_fun = @(x,u) dynamics_SIRHICU(x,u',d_est,params,model.school_fun);", nargout=0)
            eng.workspace['u_prev'] = u

            eng.workspace['z_H_0'] = H_dot;
            eng.workspace['z_ICU_0'] = ICU_dot;

            [u,info] = eng.eval('step_nmpc([x;z_H_0;z_ICU_0],u_prev,dt_u,model,objective,opt);',nargout=2)
            #print u

            x_preds.append(info["x_opt"])
            u_preds.append(info["u_opt"])
            slack_vars.append(info["s_opt"])
            I_pred_last = info["x_opt"][1][1]
            H_pred_last = info["x_opt"][2][1]
            ICU_pred_last = info["x_opt"][3][1]
 	
        LPs_out.append([H_LP,ICU_LP])
        dots_out.append([H_dot,ICU_dot])
        
        if(i>0):
            [H_dot,H_LP] = eng.filt_diff(H_LP,H,T_H,nargout=2)
            [ICU_dot,ICU_LP] = eng.filt_diff(ICU_LP,ICU,T_ICU,nargout=2)
        #print H_dot, I_LP, ICU_dot, H_LP

        i += 1
        print i
        #sys.stdout.flush()
        #sys.stdout.write(str(i) + '\r')

        dailyInfs = 0

        u1 = u[0][0] # NB: Need to transform this when doing mixed integer..
        u2 = u[1][0]
        u3 = u[2][0]
        u1_rounded = int(round(u1))
        u2_rounded = int(round(u2))
        u3_rounded = int(round(u3))

        u_round_out.append([u1_rounded,u2_rounded,u3_rounded])
        u_raw_out.append([u1,u2,u3])
        d_out.append([d_I,d_H,d_ICU])
        strat = {'S': u1_rounded, 'W': u2, 'R': u3_rounded}
        #inVec = convertVector(strat)
        
        p = setStrategy(strat, baseP, layers, attrs)

        testRules = {}
        cont, linfs, dailyInfs = systemDay(layers, attrs, p, i, testRules)
        count = countState(attrs, stateList)
        stateLog.append(count)
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)

    data = {}
    data['d_out'] = d_out
    data['u_raw'] = u_raw_out
    data['u_rounded'] = u_round_out
    data['LPs']   = LPs_out
    data['dots'] = dots_out
    data['x_preds'] = x_preds
    data['u_preds'] = u_preds
    data['slack_vars'] = slack_vars
    for comp in stateList:
        data[comp] = numpy.array([d[comp] for d in stateLog])

    dir = os.path.join(os.getcwd(),"new_control5")
    if not os.path.exists(dir):
        os.mkdir(dir)
    fileName = 'new_control5/closedLoop_test_run' + str(k) + '.mat'
    scipy.io.savemat(fileName,data)


days = 200
num_cores = 10#multiprocessing.cpu_count()
N = 10#num_cores
Parallel(n_jobs=num_cores, verbose=10)(delayed(controlledRun)(days,k) for k in range(N))








