close all;
clear;

addpath('C:\Users\emcoates\CasADi\casadi-windows-matlabR2016a-v3.4.5')

% Dont worry to much about this for now..
use_beta = 0;

% Set basic parameters
N = 200000; % Population size
control_list = [.08, .12, .16, .20, .24]; % Test vals
%control_list = [.01, .062, .092, .133, .183]; % From Andre

n_control = length(control_list);

ICU_max = 100;
k_icu = 1/3;
param.xi = 0.01;
param.mu = 0.01;
param.alpha_I = 0.1;
param.alpha_H = 0.1;

% Run model init script
init_SIHRD_1;
% make new init script, e.g. init_SIHRD_5;

% Sample time for discretization [days]
dt_u = 10.0;

% states: [p^I p^H p^R p^D]^T
% State [fraction of total population]
p_I_0 = 1/N;%1000/N;
p_H_0 = 0;%2*240/N;
p_R_0 = 0.0;
p_D_0 = 0.0;
% Initial state
x_0 = [p_I_0; p_H_0; p_R_0; p_D_0];

% Previous control
u_0 = 0.0; % full stop

% Closed-loop MPC
simTime = 150;
opt.horizon = 30;   % Possibility to use different horizon for MPC!
opt.integer = 1; % Turn on/off mixed-integer
opt.RK4_steps = 2;
numSteps = simTime/dt_u;
x0 = x_0;
t_mpc_out = [];
x_mpc_out = [];
u_mpc_out = [];

fprintf('Starting MPC..\n');
tic
for i=1:numSteps
    % Run MPC function
    [u_mpc,info] = step_nmpc(x0,u_0,dt_u,model,objective,opt);
    %figure(99)
    %plot(info.t,N*k_icu*info.x_opt(2,:))
    %pause
    
    % Implement first input only
    x_dot = @(t,x) model.dyn_fun(x,u_mpc);
    % Simulate
    [t_part,x_part] = ode45(x_dot,[(i-1)*dt_u,i*dt_u],x0);
    
    t_mpc_out = [t_mpc_out; t_part];
    x_mpc_out = [x_mpc_out; x_part];
    u_mpc_out = [u_mpc_out; u_mpc*ones(length(t_part),1)];
    
    x0 = x_part(end,:)';
    u_0 = u_mpc;
    
    fprintf('MPC iteration number %d finished!\n',i);
end
toc
fprintf('MPC completed!\n');

%% Plotting

t = datetime('today') + days(t_mpc_out);

figure
plot(t,ICU_max*ones(size(t)),'k'); hold on
plot(t,N*k_icu*x_mpc_out(:,2),'r','LineWidth',2); 
stairs(t,ICU_max*1.1*(n_control - 1 - u_mpc_out)./(n_control-1),'--b'); hold off
ylabel('ICU cases')
xtickformat('MMM')
axis tight
ylim([0 ICU_max*1.2])

figure
plot(t_mpc_out,x_mpc_out)