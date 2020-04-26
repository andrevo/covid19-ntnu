use_beta = 0;
[numP,denP] = padecoef(24,n_pade);
[A,B,C,D] = tf2ss(numP,denP);
%A = [-0.086, -0.005; 1, 0];
%B = [1; 0];
%C = [0, 8.7657e-05];
%D = [0];
params.A = A;
params.B = B;
params.C = C;
params.D = D;
params.a = -27.659;
params.b = 11.549;
params.c = 0.059728;
params.d = 0.0092737;
params.alpha = 0.1113;
control_list = [0.0997,0.2477,0.2813,0.2964,0.3340];
n_control = length(control_list);
x_val = 0:1:(n_control-1);    
y_val = control_list;         % for testing: y_val = [0.01 0.09 0.12 0.17 0.23]; 
p = polyfit(x_val,y_val,length(x_val)-1);
model.beta_fun = @(u) polyval(p',u);
model.dyn_fun = @(x,u) dynamics_SIR_ICU_d_1(x,u,0,params,model.beta_fun,n_pade);
model.nx = 2 + n_pade;
model.nu = 1;
% Objective
C_d = 0.9*ICU_max; % ICU Capacity [num individuals]
q = 100;            % (Stage) output error weight
r = 10;    % (Stage) control weight
q_T = 10;          % Terminal output error weight

ICU_state = @(z,u) C*z + D*u;
objective.stage_cost = @(x,u) q*(N*ICU_state(x(3:3+n_pade-1),x(2)*(params.c*x(2) + params.d)) - C_d)^2 + r*(n_control-1-u)^2;
objective.term_cost = @(x) q_T*(N*ICU_state(x(3:3+n_pade-1),x(2)*(params.c*x(2) + params.d)) - C_d)^2;
% Constraints
objective.constraints.u_max = n_control-1;
objective.constraints.u_min = 0;

objective.constraints.x_max = ones(model.nx,1);
objective.constraints.x_min = zeros(model.nx,1);

objective.constraints.x_max(3:3+n_pade-1) = Inf(n_pade,1);
objective.constraints.x_min(3:3+n_pade-1) = -Inf(n_pade,1);

%objective.constraints.x_max(3) = (1/C);

%objective.constraints.x_max(2) = C_d/(N*k_icu);

%objective.constraints.du_max = 1;
%objective.constraints.du_min = -1;

% Simulation parameters
opt.horizon  = 100;  % [days] time horizon
% At the moment horizon/dt_u need to be integer..
opt.RK4_steps = 2;
opt.integer = 0; % set to one to use mixed integer optimization
opt.only_decrease = 0; % setting this to one limits change in u to decrease only