function problem = initNLP(model,cost,constraints,options,x_0,u_0)

% Input:
% - ns
% - stage_cost
import casadi.*

N = options.T/options.dt; % number of control intervals

x = MX.sym('x',model.nx);
u = MX.sym('u',model.nu);

xnext = model.dyn_fun(x,u);
stage = cost.stage_cost(x,u);


f = Function('f', {x, u}, {xnext, stage}, {'x','u'}, {'xnext', 'stage'});

% Simulate dt time units at a time
X0 = MX.sym('X0',model.nx);
U  = MX.sym('U', model.nu);
Q = 0;  % Total cost for dt time unit
X = X0; % State vector at end of period
for j=1:options.dt
    [X,stage] = f(X, U);
    Q = Q + stage; % add stage for 7 time steps at a time
end
F = Function('F', {X0, U}, {X, Q}, {'x0','u'}, {'xf', 'qf'});

% Initial guess for u
u_start = u_0*ones(1,N);

% Get a feasible trajectory as an initial guess
xk = x_0;
x_start = [xk];
for k =1:N
    ret = F('x0',xk, 'u',u_start(k));
    xk = ret.xf;
    x_start = [x_start xk];
end

% Start with an empty NLP
% NB: Equality constraints are equality constraints where the bounds are zero!
w={};     % Decision variables
w0 = [];  % Initial guess
lbw = []; % Lower and upper bounds on decision variables
ubw = [];
discrete = []; % one if integer variable, zero otherwise
J = 0;    % Cost function
g={};     % Nonlinear function of decision variables
lbg = []; % Lower and upper bounds for g
ubg = []; %

% "Lift" initial conditions
Xk = MX.sym('X0', model.nx);
w = {w{:}, Xk};
lbw = [lbw; x_0];
ubw = [ubw; x_0];
w0 = [w0; x_0];
discrete = [discrete; zeros(model.nx,1)];

U_prev = u_0;

% Formulate the NLP
for k=0:N-1
    % new NLP variable for the control
    Uk = MX.sym(['U_' num2str(k)],model.nu);
    w = {w{:}, Uk};
    lbw = [lbw; constraints.u_min];
    ubw = [ubw; constraints.u_max];
    w0 = [w0;  u_start(:,k+1)];
    discrete = [discrete; options.integer*ones(model.nu,1)];

    % Cost on change in u:
    J = J + cost.weight_du*(Uk-U_prev)'*(Uk-U_prev);
    
    % Constraint on du
    g = [g, {Uk-U_prev}];
    lbg = [lbg; constraints.du_min];
    ubg = [ubg; constraints.du_max];

    U_prev = Uk;
    
    % Integrate till the end of the interval
    Fk = F('x0', Xk, 'u', Uk);
    Xk_end = Fk.xf;
    J=J+Fk.qf;
    
    % New NLP variable for slack variable
    Sk = MX.sym(['S_' num2str(k)],constraints.ns);
    w = {w{:}, Sk};
    lbw = [lbw; zeros(constraints.ns,1)];
    ubw = [ubw; Inf(constraints.ns,1)];
    w0 = [w0; zeros(constraints.ns,1)];
    discrete = [discrete;zeros(constraints.ns,1)];
    
    % Cost on slack variable
    J = J + cost.weight_s*Sk'*Sk;
    
    % New NLP variable for state at end of interval
    Xk = MX.sym(['X_' num2str(k+1)], model.nx);
    w = [w, {Xk}];
    lbw = [lbw; constraints.x_min];
    ubw = [ubw; constraints.x_max];
    w0 = [w0; x_start(:,k+1)];
    discrete = [discrete;zeros(model.nx,1)];

    % Add equality constraint
    g = [g, {Xk_end-Xk}];
    lbg = [lbg; zeros(model.nx,1)];
    ubg = [ubg; zeros(model.nx,1)];
    
    % Constraint on ICU using slack variable
    for i=1:length(constraints.soft_indices)
        g = [g, {Xk(constraints.soft_indices(i))-Sk(i)}];
    end
    lbg = [lbg; constraints.soft_min];
    ubg = [ubg; constraints.soft_max];
end

% Terminal cost
J = J + cost.term_cost(Xk);

% Create an NLP solver
nlp = struct('f', J, 'x', vertcat(w{:}), 'g', vertcat(g{:}));

opt = struct;
%opt.ipopt.print_level = 0;
%opt.ipopt.sb = 'yes';
%opt.print_time = 0;
%opt.ipopt.warm_start_init_point = 'yes';
solver = nlpsol('solver', 'ipopt', nlp, opt);

if(options.integer)
   opt = struct;
   opt.discrete = discrete;
   solver = nlpsol('solver', 'bonmin', nlp, opt);
end

problem.solver      = solver;
problem.w0          = w0;
problem.lbw         = lbw;
problem.ubw         = ubw;
problem.lbg         = lbg;
problem.ubg         = ubg;
problem.N           = N;
problem.model       = model;
problem.cost        = cost;
problem.constraints = constraints;
problem.options     = options;
end