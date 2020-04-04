%close all;
%clear;

addpath('C:\Users\emcoates\CasADi\casadi-windows-matlabR2016a-v3.4.5')

% Set basic parameters
N = 200000;
control_list = [.08, .12, .16, .20, .24];
n_control = length(control_list);

ICU_max = 100;
k_icu = 1/3;
param.xi = 0.01;
param.mu = 0.01;
param.alpha_I = 0.1;
param.alpha_H = 0.1;

% Run model init script
init_SIHRD_1;
%init_SIHRD_1_icuConstraint;

% Sample time for discretization [days]
dt_u = 10.0;

% states: [p^I p^H p^R p^D]^T
% State [fraction of total population]
I_0 = 1.0; % Num individuals
p_I_0 = I_0/N;
p_H_0 = 0.0;
p_R_0 = 0.0;
p_D_0 = 0.0;

x = [p_I_0; p_H_0; p_R_0; p_D_0];
u_prev = 0.0; % assume full stop in beginning

% Run MPC function
%[u,info] = step_nmpc(x,u_prev,dt_u,model,objective,opt);

%% Solve optimal control and simulate control solution open-loop
dyn_fun = model.dyn_fun;
nx      = model.nx;
nu      = model.nu;

stage_cost  = objective.stage_cost;
term_cost   = objective.term_cost;
constraints = objective.constraints;

horizon       = opt.horizon;
RK4_steps     = opt.RK4_steps;
only_decrease = opt.only_decrease;
integer       = opt.integer;

u_0 = 0.0; % full stop
x_0 = x;

[u_opt,x_opt,t] = optimal_control(dyn_fun,stage_cost,term_cost,horizon,dt_u,RK4_steps,x_0,u_0,nx,nu,constraints,only_decrease,integer);
%%
if(round_off)
    if(use_beta)
        u = interp1(control_list,control_list,u_opt,'nearest')
    else
        u = round(u_opt);
    end
else
    u = u_opt;
end

[x_out,t_out] = sim_open_loop(x_0,u,dt_u,model);

figure
plot(t,u)
title('u')
xlabel('t [days]')

figure
plot(t_out,x_out)
title('Predicted')
legend('p^I','p^H','p^R','p^D')
xlabel('t [days]')
ylabel('Fraction of population')

figure
plot(t_out,N*k_icu*x_out(:,2)); hold on
plot(t_out,ICU_max*ones(size(t_out))); hold off
legend('ICU','ICU_{MAX}')

%% Run uncontrolled case
x_0 = x;
u = 4; % uncontrolled
simTime = 2*opt.horizon;
[x_out,t_out] = sim_constant_u(x_0,u,dt_u,simTime,model);

figure
plot(t_out,x_out)
title('Constant control (uncontrolled)')
legend('p^I','p^H','p^R','p^D')
xlabel('t [days]')
ylabel('Fraction of population')

figure
plot(t_out,N*k_icu*x_out(:,2)); hold on
plot(t_out,ICU_max*ones(size(t_out))); hold off
legend('ICU','ICU_MAX')

