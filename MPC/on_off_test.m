%close all;
clear;

% NB: important! look closer at this.
use_beta = 0;
round_off = 0;

% Set basic parameters
N = 200000;
control_list = [.08, .12, .16, .20, .28];
n_control = length(control_list);

ICU_max = 100;
k_icu = 1/3;
param.xi = 0.01;
param.mu = 0.01;
param.alpha_I = 0.1;
param.alpha_H = 0.1;

% Run model init script
init_SIHRD_1;

% states: [p^I p^H p^R p^D]^T
% State [fraction of total population]
p_I_0 = 1/N;
p_H_0 = 0;
p_R_0 = 0.0;
p_D_0 = 0.0;

x = [p_I_0; p_H_0; p_R_0; p_D_0];

dyn_fun = model.dyn_fun;

dt_u = 1;
simTime = 600;
numSteps = simTime/dt_u;
x0 = x;
t_mpc_out = [];
x_mpc_out = [];
u_mpc_out = [];

logic_state = 0;

on_trigger  = 60;
off_trigger = 10;

u_max = n_control-1;
u_min = 0;
for i=1:numSteps
    
    ICU = N*k_icu*x0(2);
    
    if(ICU<off_trigger)
        % slipp opp
        u = u_max;
        logic_state = 1; % going up 
    elseif(ICU < on_trigger) % but not less than off_trigger
        if(~logic_state) % going down
            u = u_min;
        else % logic_state == 1 going up
            u = u_max;
        end
    else % >= on_trigger
        % stram inn
        u = u_min;
        logic_state = 0; % going down
    end
   
    x_dot = @(t,x) dyn_fun(x0,u);
    
    [t_part,x_part] = ode45(x_dot,[(i-1)*dt_u,i*dt_u],x0);
    t_mpc_out = [t_mpc_out; t_part];
    x_mpc_out = [x_mpc_out; x_part];
    u_mpc_out = [u_mpc_out; u*ones(length(t_part),1)];
    x0 = x_part(end,:)';
end
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












