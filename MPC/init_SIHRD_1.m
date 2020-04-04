% Assumes the following variables exist in workspace:
% - N: total population size
% - ICU_max: ICU capacity (will control to 90 percent of this)
% - k_icu: fraction of infected that need ICU
% - mu: death rate
% - xi: hospitalization rate of infected
% - alpha_I: recovery rate of infected not in hospital
% - alpha_H: recovery rate 
% - n_control: number of discrete control combinations
% - control_list: sorted, in increasing order, list of resulting beta-values

% states: [p^I p^H p^R p^D]^T
% time units: days
import casadi.*

% NB: important! look closer at this.
use_beta = 0;
round_off = 0;

model = struct;

if(use_beta)
    beta_fun = @(u) u;
    
    model.dyn_fun = @(x,u) dynamics_SIHRD_1(x,u,param,beta_fun);
else
    % Assuming that we have a finite number of interventions 
    % and the resulting beta each combination gives, with n_control combinations in
    % total.
    % The control u is in the discrete set {0,..,n_control-1}
    % model beta as a function of u
    x_val = 0:1:(n_control-1);    
    y_val = control_list;         % for testing: y_val = [0.01 0.09 0.12 0.17 0.23]; 
    p = polyfit(x_val,y_val,length(x_val)-1);
    beta_fun = @(u) polyval(p',u);
    
    model.dyn_fun = @(x,u) dynamics_SIHRD_1(x,u,param,beta_fun);
end
model.nx = 4;
model.nu = 1;

% Objective
C_d = 0.9*ICU_max; % ICU Capacity [num individuals]
q = 10;            % (Stage) output error weight
r = 10;    % (Stage) control weight
q_T = 10;          % Terminal output error weight
% Objective function % states: [p^I p^H p^R p^D]^T
objective = struct;
if(use_beta)
    objective.stage_cost = @(x,u) q*(N*k_icu*x(2) - C_d)^2 + r*(max(control_list)-u)^2;
    objective.term_cost = @(x) q_T*(N*k_icu*x(2) - C_d)^2;
    % Constraints
    objective.constraints.u_max = max(control_list);
    objective.constraints.u_min = min(control_list);
else
    objective.stage_cost = @(x,u) q*(N*k_icu*x(2) - C_d)^2 + r*(n_control-1-u)^2;
    objective.term_cost = @(x) q_T*(N*k_icu*x(2) - C_d)^2;
    % Constraints
    objective.constraints.u_max = n_control-1;
    objective.constraints.u_min = 0;
end

objective.constraints.x_max = ones(model.nx,1);
objective.constraints.x_min = zeros(model.nx,1);

% Simulation parameters
opt.horizon  = 360;  % [days] time horizon
% At the moment horizon/dt_u need to be integer..
opt.RK4_steps = 8;
opt.integer = 0; % set to one to use mixed integer optimization
opt.only_decrease = 0; % setting this to one limits change in u to decrease only
