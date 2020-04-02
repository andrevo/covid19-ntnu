import matlab.engine
from InitializeModel import *
from modelFuncs import *


eng = matlab.engine.start_matlab()
eng.addpath(r'~/CASADI/')
eng.addpath(r'~/Documents/Covid/MPC/models')
eng.addpath(r'~/Documents/Covid/MPC',nargout=0)

# states: [p^R p^I]^T
# time units: days

# Population size
N = 200000.0
eng.workspace['N'] = N
# Max ICU capacity [num individuals]
eng.workspace['ICU_max'] = 100.0
# Recovery rate [1/days]
eng.workspace['alpha'] = 0.1

# Fraction of infected that need ICU
eng.workspace['k_icu'] = 0.1
# Number of discrete control combinations
n_control = 5.0
eng.workspace['n_control'] = n_control
# Resulting beta values for each control combination (sorted in increasing order)
eng.workspace['control_list'] = matlab.double([.1825, .210, .233, .254, .280])
#eng.workspace['control_list'] = matlab.double([0.01, 0.09, 0.12, 0.17, 0.23])

# Run init script
eng.init_SIR_1(nargout=0)

# Sample time for discretization [days]
eng.workspace['dt_u'] = 10.0

# State [fraction of total population]
I_0 = 1.0 # Num individuals
p_I_0 = I_0/N
p_R_0 = 0.0

x = matlab.double([[p_R_0],[p_I_0]])
eng.workspace['x'] = x
eng.workspace['u_prev'] = 0.0

# Run MPC step function
u = eng.eval('step_nmpc(x,u_prev,dt_u,model,objective,opt);')


cont = 1
i = 0

stateLog = []
infLog = []
infLogByLayer = []
#state = copy.copy(seedState)

strats = [[0, 0, 1], [0, 1, 1], [0, 1, 2], [1, 1, 2], [1, 1, 3]]
uhist = []

while cont:
    i+= 1
    
    #if i%10 == 0:
    print i, u
    strat = strats[int(round(u))]
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)
    cont, linfs, dailyInfs = systemDay(cliques, state, ageGroup, openLayers, p, i)
    stateLog.append(countState(state, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)
    count = countState(state, stateList)
    n = 2*pow(10, 5)
    I = float(count['I']/n)
    S = float(count['S']/n)
    R = 1-I-S
    x = matlab.double([[R],[I]])
    eng.workspace['x'] = x
    eng.workspace['u_prev'] = u
    if i%10 == 0:
        u = eng.eval('step_nmpc(x,u_prev,dt_u,model,objective,opt);')
    uhist.append(u)
    
# Simulate constant control (e.g. use the u calculated above, or try the uncontrolled case, i.e. u = n_control-1)
# eng.workspace['x_0'] = x
# eng.workspace['u'] = n_control - 1.0
# eng.workspace['simTime'] = 240.0
# [x_out,t_out] = eng.eval('sim_constant_u(x_0,u,dt_u,simTime,model);',nargout=2)

# # Open-loop simualation (u vector)
# eng.eval('u = (n_control-1)*ones(24,1);',nargout=0)
# [x_out,t_out] = eng.eval('sim_open_loop(x_0,u,dt_u,model);',nargout=2)
