from modelFuncs import *
import scipy.io
import numpy
import matplotlib.pyplot as plt
import matlab.engine

def controlledRun(seedAttrs, layers, cliques, baseP, simDays):
    cont = 1
    i = 0
    u = 4

    strats = [{'S': 0, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 1}, {'S': 1, 'W': 0, 'R': 2}, {'S': 1, 'W': 1, 'R': 2},
              {'S': 1, 'W': 1, 'R': 3}]  # Schools

    stateLog = []
    infLog = []
    infLogByLayer = []
    attrs = copy.copy(seedAttrs)

    eng = matlab.engine.start_matlab()
    eng.addpath(r'/home/ubuntu/software/casadi')
    eng.addpath(r'/home/ubuntu/software/casadi/covid19_master/MPC', nargout=0)
    eng.addpath(r'/home/ubuntu/software/casadi/covid19_master-ntnu/MPC/models', nargout=0)

    # Population size
    N = 617371.0
    eng.workspace['N'] = N
    # Max ICU capacity [num individuals]
    ICU_max = 50.0
    eng.workspace['ICU_max'] = ICU_max

    # Run init script
    n_pade = 3
    eng.workspace['n_pade'] = n_pade
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
    k_I = 25.0

    # Initial condition for actual pade states
    z_0 = []
    for i in range(n_pade):
        z_0.append([0])
    eng.workspace['z_0'] = matlab.double(z_0)

    count = countState(attrs, stateList)

    while cont and (i < simDays):

        if (i % dt_u == 1)
            S = float(count['S']) / N
            I = float(count['Ia'] + count['Ip']) / N
            ICU = float(count['ICU']) / N

            x = [[S], [I]]
            eng.workspace['x'] = matlab.double(x)

            eng.workspace['d_est'] = d_est
            eng.eval('model.dyn_fun = @(x,u) dynamics_SIR_ICU_d_1(x,u,d_est,param,model.beta_fun,n_pade);', nargout=0)

            eng.workspace['u_prev'] = int(round(u))

            u = eng.eval('step_nmpc([x;z_0],u_prev,dt_u,model,objective,opt);')

            eng.workspace['p_I'] = matlab.double(I)
            eng.eval('u_z = p_I*(params.c*p_I + params.d);', nargout=0)
            eng.eval('z_0 = sim_z(params.A,params.B,u_z,z_0);', nargout=0) # NB! This is open-loop. Use observer?

            print i, u, d_est

            e_y = 0.9 * ICU_max / N - ICU
            d_est += k_I * e_y

            #e_pred_out.append(N * e_y)
            #d_est_out.append(d_est)

        i += 1
        sys.stdout.flush()
        sys.stdout.write(str(i) + '\r')

        dailyInfs = 0

        u_rounded = int(round(u))
        strat = strats[u_rounded]
        inVec = convertVector(strat)
        openLayers, p = setStrategy(inVec, baseP, layers)

        cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
        count = countState(attrs, stateList)
        stateLog.append(count)
        infLog.append(dailyInfs)
        infLogByLayer.append(linfs)

    return stateLog, infLog, infLogByLayer, i

layers, attrs, cliques = initModel('idAndAge_Oslo.txt', 'socialNetwork_Oslo.txt', '', baseP, [10, 3, -.75], 20)
days = 3
stateLog, infLog, infLogByLayer, i, = controlledRun(attrs, layers, cliques, baseP, days)