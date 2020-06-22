% Options
options.integer = 1;
options.dt = 7;     % [days] control interval
options.T = 8*options.dt; % [days] time horizon

% Model
model = defineModel;
N_pop = 214004; % Population size
ICU_max = 74;
safety = 0.45;
n_control = 6; % integers 0-5

% Cost function
cost.weight_y = 100;
cost.weight_u = 0.1;
cost.weight_s = 900000000000;

cost.weight_du = 0;
%cost.stage_cost = @(x,u) cost.weight_u*(n_control-1-u)^2;
%cost.term_cost  = @(x)   0;
cost.stage_cost = @(x,u) cost.weight_y*(x(3) - safety*ICU_max/N_pop)^2 + cost.weight_u*(n_control-1-u)^2;
cost.term_cost  = @(x)   cost.weight_y*(x(3) - safety*ICU_max/N_pop)^2;

% Hard Constraints
constraints.u_max = 5;
constraints.u_min = 0;
constraints.x_max = ones(model.nx,1);
constraints.x_min = zeros(model.nx,1);
constraints.du_max = Inf(model.nu,1);
constraints.du_min = -Inf(model.nu,1);
% Soft Constraints
constraints.ns = 1; % number of slack variables (and number of soft constraints)
        % index of states with soft constraints
constraints.soft_indices = 3;
constraints.soft_max = safety*ICU_max/N_pop;
constraints.soft_min = -Inf;