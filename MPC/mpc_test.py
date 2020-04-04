import matlab.engine

eng = matlab.engine.start_matlab()
eng.addpath(r'C:\Users\emcoates\CasADi\casadi-windows-matlabR2016a-v3.4.5')
eng.addpath(r'C:/Users/emcoates/covid19-ntnu/MPC',nargout=0)

# states: [p^I p^H p^R p^D]^T
# time units: days

# Population size
N = 200000.0
eng.workspace['N'] = N
# Max ICU capacity [num individuals]
eng.workspace['ICU_max'] = 100.0
# Recovery rate [1/days]
eng.eval('param.alpha_I = 0.1;',nargout=0)
eng.eval('param.alpha_H = 0.1;',nargout=0)
eng.eval('param.xi = 0.01;',nargout=0)
eng.eval('param.mu = 0.01;',nargout=0)

# Fraction of infected that need ICU
eng.workspace['k_icu'] = 0.3333
# Number of discrete control combinations
n_control = 5.0
eng.workspace['n_control'] = n_control
# Resulting beta values for each control combination (sorted in increasing order)
eng.workspace['control_list'] = matlab.double([.08, .12, .16, .20, .24])

# Run init script
eng.init_SIHRD_1(nargout=0)

# Sample time for discretization [days]
eng.workspace['dt_u'] = 10.0

# State [fraction of total population]
I_0 = 1.0 # Num individuals
p_I_0 = I_0/N
p_H_0 = 0.0
p_R_0 = 0.0
p_D_0 = 0.0

x = matlab.double([[p_I_0],[p_H_0],[p_R_0],[p_D_0]])
eng.workspace['x'] = x
eng.workspace['u_prev'] = 0.0 # assume full stop at start

# Run MPC step function
u = eng.eval('step_nmpc(x,u_prev,dt_u,model,objective,opt);')

# Simulate constant control (e.g. use the u calculated above, or try the uncontrolled case, i.e. u = n_control-1)
eng.workspace['x_0'] = x
eng.workspace['u'] = n_control - 1.0
eng.workspace['simTime'] = 240.0
[x_out,t_out] = eng.eval('sim_constant_u(x_0,u,dt_u,simTime,model);',nargout=2)

# Open-loop simualation (u vector)
eng.eval('u = (n_control-1)*ones(24,1);',nargout=0)
[x_out,t_out] = eng.eval('sim_open_loop(x_0,u,dt_u,model);',nargout=2)
