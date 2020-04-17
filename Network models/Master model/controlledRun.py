import matplotlib.pyplot as plt
import matlab.engine
from InitializeModel import *
from InitializeProbability import *
from modelFuncs import *


eng = matlab.engine.start_matlab()
#eng.addpath(r'~/CASADI/')
#eng.addpath(r'~/Documents/Covid/MPC/models')
#eng.addpath(r'~/Documents/Covid/MPC',nargout=0)
eng.addpath(r'C:\Users\emcoates\CasADi\casadi-windows-matlabR2016a-v3.4.5')
eng.addpath(r'C:/Users/emcoates/covid19-ntnu/MPC', nargout=0)
eng.addpath(r'C:/Users/emcoates/covid19-ntnu/MPC/models', nargout=0)


# states: [p^S p^I p^H]^T
# time units: days

# Population size
N = 200000.0
eng.workspace['N'] = N
# Max ICU capacity [num individuals]
ICU_max = 50.0
eng.workspace['ICU_max'] = ICU_max

eng.eval('param.alpha_I = 0.11;', nargout=0)
eng.eval('param.alpha_H = 0.15;', nargout=0)
eng.eval('param.xi = 0.003;', nargout=0)
eng.eval('param.mu = 0.0;', nargout=0)

# Fraction of hospitalized that need ICU
k_icu = 1.0 / 3.0
eng.workspace['k_icu'] = k_icu
# Number of discrete control combinations
n_control = 5.0
eng.workspace['n_control'] = n_control
# Resulting beta values for each control combination (sorted in increasing order)
#eng.workspace['control_list'] = matlab.double([.01, .06, .09, .133, .183]) #Analytical numbers, workplaces first
#eng.workspace['control_list'] = matlab.double([.01, .062, .092, .133, .183]) #Analytical numbers, schools first

# Identified through model fitting:
eng.workspace['control_list'] = matlab.double([0.1017, 0.1504, 0.1868, 0.2648, 0.3112])

#eng.workspace['control_list'] = matlab.double([.1825, .210, .233, .254, .280]) #Empirical numbers

#eng.workspace['control_list'] = matlab.double([0.01, 0.09, 0.12, 0.17, 0.23])

# Run init script
eng.eval('use_beta = 0;', nargout=0)
eng.init_SIH_1(nargout=0)
eng.eval('opt.horizon = 50;', nargout=0)
eng.eval('opt.integer = 0;', nargout=0)

# Sample time for discretization [days]
dt_u = 10.0
eng.workspace['dt_u'] = dt_u

# State [fraction of total population]
p_S_0 = (N - 20.0) / N
p_I_0 = 20.0 / N
p_H_0 = 0.0

x = matlab.double([[p_S_0], [p_I_0], [p_H_0]])
eng.workspace['x'] = x
u = 0.0  # assume no control at start
eng.workspace['u_prev'] = u


seedState(attrs, 20)

cont = 1
i = 0

stateLog = []
infLog = []
infLogByLayer = []
#state = copy.copy(seedState)

strats = [{'S': 0, 'W': 0, 'R': 1}, {'S':0, 'W':1, 'R':1}, {'S':0, 'W':1, 'R':2}, {'S':1, 'W':1, 'R':2}, {'S':1, 'W':1, 'R':3}] #Workplaces first
strats = [{'S':0, 'W':0, 'R':1}, {'S':1, 'W':0, 'R':1}, {'S':1, 'W':0, 'R':2}, {'S':1, 'W':1, 'R':2}, {'S':1, 'W':1, 'R':3}] #Schools
uhist = []
ICU_hist = []
d_est_out = []

simDays = 1000

# Disturbance estimate (integral action)
d_est = 0.0
k_I = 25.0

while (i <= simDays) and cont:
    # Extract current state for control and plotting
    count = countState(attrs, stateList)
    S = float(count['S']) / N
    I = float(count['I']) / N
    H = float(count['H']) / N
    R = float(count['R']) / N
    D = float(count['D']) / N

    # Calculate next control
    if (i % dt_u == 0):
        eng.workspace['u_prev'] = u
        x = matlab.double([[S], [I], [H]])
        eng.workspace['x'] = x
        eng.workspace['d_est'] = d_est
        eng.eval('model.dyn_fun = @(x,u) dynamics_SIH_d(x,u,d_est,param,model.beta_fun);', nargout=0)
        u = eng.eval('step_nmpc(x,u_prev,dt_u,model,objective,opt);')
        print i, u
        print count
        print d_est

        e_y = k_icu*H - 0.9*ICU_max/N
        d_est += k_I*e_y
        d_est_out.append(d_est)

    uhist.append(u)
    ICU_hist.append(k_icu * H * N)

    # Implement control and advance to next day
    i+= 1
    strat = strats[int(round(u))]
    inVec = convertVector(strat)
    openLayers, p = setStrategy(inVec, baseP, layers)
    cont, linfs, dailyInfs = systemDay(cliques, attrs, openLayers, p, i)
    stateLog.append(countState(attrs, stateList))
    infLog.append(dailyInfs)
    infLogByLayer.append(linfs)
    uhist.append(u)

# Plotting
plt.figure()
plt.subplot(311)
plt.plot(ICU_hist)
plt.ylabel('ICU')
plt.subplot(312)
plt.plot(uhist)
plt.ylabel('u')
plt.subplot(313)
plt.plot(d_est_out)
plt.ylabel('dest')
plt.xlabel('days')
plt.show()
