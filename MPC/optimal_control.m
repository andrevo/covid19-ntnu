function [u_opt,x_opt,t] = optimal_control(dyn_fun,stage_cost,term_cost,horizon,dt_u,RK4_steps,x_0,u_0,only_decrease,nx,nu)
import casadi.*

T  = horizon;  % [days] time horizon
dt = dt_u;   % [days] sample time for discretization
N = T/dt; % number of control intervals

x = MX.sym('x',nx);
u = MX.sym('u',nu);
%%
% Input Constraints
u_max = ones(nu,1);
u_min = zeros(nu,1);

% State Constraints
x_max = ones(nx,1);
x_min = zeros(nx,1);

% Objective function
xdot = dyn_fun(x,u);
stage = stage_cost(x,u);
f = Function('f', {x,u}, {xdot,stage}, {'x','u'}, {'xdot', 'L'});

%%
% Formulate discrete time dynamics
% Fixed step Runge-Kutta 4 integrator
M = RK4_steps;

X0 = MX.sym('X0', nx);
U  = MX.sym('U',nu);

X = X0;
Q = 0;

DT = T/N/M;

for j=1:M
   [k1, k1_q] = f(X, U);
   [k2, k2_q] = f(X + DT/2 * k1, U);
   [k3, k3_q] = f(X + DT/2 * k2, U);
   [k4, k4_q] = f(X + DT * k3, U);
   X = X + DT/6*(k1   + 2*k2   + 2*k3   + k4);
   Q = Q + DT/6*(k1_q + 2*k2_q + 2*k3_q + k4_q);
end
F = Function('F', {X0, U}, {X, Q}, {'x0','u'}, {'xf', 'qf'});

%% Formulate NLP

% Start with an empty NLP
% NB: Equality constraints are equality constraints where the bounds are
% zero!
w={};     % Decision variables
w0 = [];  % Initial guess
lbw = []; % Lower and upper bounds on decision variables
ubw = [];
J = 0;    % Cost function
g={};     % Nonlinear function of decision variables
lbg = []; % Lower and upper bounds for g
ubg = []; %

% "Lift" initial conditions
Xk = MX.sym('X0', nx);
w = {w{:}, Xk};
lbw = [lbw; x_0];
ubw = [ubw; x_0];
w0 = [w0; x_0];

U_prev = u_0;

% Formulate the NLP
for k=0:N-1
    % New NLP variable for the control
    Uk = MX.sym(['U_' num2str(k)],nu);
    w = {w{:}, Uk};
    lbw = [lbw; u_min];
    ubw = [ubw; u_max];
    w0 = [w0;  u_0];

    % Integrate till the end of the interval
    Fk = F('x0', Xk, 'u', Uk);
    Xk_end = Fk.xf;
    J=J+Fk.qf;
    
    % New NLP variable for state at end of interval
    Xk = MX.sym(['X_' num2str(k+1)], nx);
    w = [w, {Xk}];
    lbw = [lbw; x_min];
    ubw = [ubw; x_max];
    w0 = [w0; x_0];

    % Add equality constraint
    g = [g, {Xk_end-Xk}];
    lbg = [lbg; zeros(nx,1)];
    ubg = [ubg; zeros(nx,1)];
    
    if(only_decrease)
        g = [g, {Uk-U_prev}];
        lbg = [lbg; -1];
        ubg = [ubg; 0];

        U_prev = Uk;
    end
end

% Terminal cost
J=J + term_cost(Xk);

% Create an NLP solver
nlp = struct('f', J, 'x', vertcat(w{:}), 'g', vertcat(g{:}));

%opt.ipopt.print_level = 0;
%opt.ipopt.sb = 'yes';
%opt.print_time = 0;
opt.ipopt.warm_start_init_point = 'yes';

solver = nlpsol('solver', 'ipopt', nlp,opt);

% Solve the NLP
sol = solver('x0', w0, 'lbx', lbw, 'ubx', ubw,...
            'lbg', lbg, 'ubg', ubg);

% Extract solution
w_opt = full(sol.x);
w_opt = [w_opt; nan(nu,1)];
w_opt = reshape(w_opt,[nx+nu,N+1]);

x_opt = w_opt(1:length(x),:);
u_opt = w_opt(nx+1:end,:);
t = 0:dt:T;
end

