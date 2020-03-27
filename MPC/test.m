close all;
clear;

addpath('\\home.ansatt.ntnu.no\emcoates\Documents\CasADi\casadi-windows-matlabR2016a-v3.4.5')
import casadi.*

alpha = 0.1;
beta_2 = 0.1;
beta_1 = 0.4;

pop_size = 1000;


T  = 350;  % [days] time horizon
dt = 14;   % [days] sample time for discretization
N = T/dt; % number of control intervals

p_I   = MX.sym('p_I');
p_R   = MX.sym('p_R');
u     = MX.sym('u');

x = [p_I; p_R];

nx = length(x);
nu = length(u);
%%
% Input Constraints
u_max = 1;
u_min = 0;

% Setpoints
C_d = 5; % [m]
K_C = 0.1; % fraction of infected that needs hospitalization

% State Constraints
p_I_max = C_d/(K_C*pop_size);
p_I_min = 0;
p_R_max = 1;
p_R_min = 0;

x_max = [p_I_max; p_R_max];
x_min = [p_I_min; p_R_min];

% Initial conditions
I_0 = C_d/K_C;
p_I_0 = I_0/pop_size;
p_R_0 = 0;

x_0 = [p_I_0; p_R_0];
u_0 = 1.0;

% Continuous dynamics
dyn_fun = @(x,u) sir_dynamics(x,u,alpha,beta_1,beta_2);
xdot = dyn_fun(x,u);

% Objective function
q = 0; % cost on output error  (pop_size*k*p_I - C_d)
r = 1; % cost on control
L = q*(K_C*p_I - C_d/pop_size)^2 + r*u^2; % stage cost
q_T = 0; % for terminal cost, defined later
f = Function('f', {x,u}, {xdot,L}, {'x','u'}, {'xdot', 'L'});

%%
% Formulate discrete time dynamics
% Fixed step Runge-Kutta 4 integrator
M = 8; % RK4 steps per interval

X0 = MX.sym('X0', nx);
U  = MX.sym('U',nu);

X = X0;
Q = 0;

% Objective function (minimize final time)
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
end

% Terminal cost
J=J + q_T*(K_C*Xk(1) - C_d/pop_size)^2;


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
w_opt = full(sol.x);

%% Plot
w_opt = [w_opt; nan(nu,1)];
w_opt = reshape(w_opt,[nx+nu,N+1]);
t = 0:dt:T;
x_opt = w_opt(1:length(x),:);
u_opt = w_opt(nx+1:end,:);

%% 
%save('long_quad.mat','t','x_opt','u_opt');
%%

figure
plot(t,u_opt)
title('u')

figure
plot(t,x_opt(1,:))
title('p_I')
figure
plot(t,x_opt(2,:))
title('p_R')
figure
plot(t,1-x_opt(1,:)-x_opt(2,:))
title('p_S')
figure
plot(t,x_opt(1,:)*pop_size*K_C); hold on
plot(t,C_d*ones(size(t))); hold off
title('ICU')


