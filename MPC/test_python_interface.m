% Population size
N = 100000.0;
% Max ICU capacity [num individuals]
ICU_max = 10.0;
% Recovery rate [1/days]
alpha = 0.1;

% Fraction of infected that need ICU
k_icu = 0.1;
% Number of discrete control combinations
n_control = 5.0;
% Resulting beta values for each control combination (sorted in increasing order)
control_list = [0.01, 0.09, 0.12, 0.17, 0.23];

% Run init script
init_SIR_1;

% Sample time for discretization [days]
dt_u = 10.0;

% State [fraction of total population]
I_0 = 1.0; % Num individuals
p_I_0 = I_0/N;
p_R_0 = 0.0;

x = [p_R_0; p_I_0];
u_prev = 1.0;

% Run MPC function
u = step_nmpc(x,u_prev,dt_u,model,objective,opt)
%%
x_0 = x;
u = 3;
simTime = 2*opt.horizon;
[x_out,t_out] = sim_constant_u(x_0,u,dt_u,simTime,model);

figure
plot(t_out,x_out)
title('Constant control')
legend('p^R','p^I')
xlabel('t [days]')
ylabel('Fraction of population')

%%

u = n_control-1*ones(24,1);

[x_out,t_out] = sim_open_loop(x_0,u,dt_u,model);

figure
plot(t_out,x_out)
title('Uncontrolled')
legend('p^R','p^I')
xlabel('t [days]')
ylabel('Fraction of population')

