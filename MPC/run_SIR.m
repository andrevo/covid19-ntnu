close all;
clear;

addpath('\\home.ansatt.ntnu.no\emcoates\Documents\CasADi\casadi-windows-matlabR2016a-v3.4.5')
import casadi.*

time = datestr(datetime('now'),'mmdd-HHMM');

% Model
A = 1; % num age groups: children, adults and old people
alpha = 0.1;
beta_2 = 0.01; % Full control
beta_1 = 0.23; % No control
K = 0.1; % Fraction of infected that needs hospitalization
pop_size = 100000;
ICU_max  = 10;
timeUnit = 'days';
prefix = 'SIR';
% Model info
nx = 2;
nu = 1;
state_names = {'p^R','p^I'};

% Assuming that we have a finite number of interventions 
% and the resulting beta each combination gives, with 5 combinations in
% total.
% The control u is in the discrete set {1,2,3,4,5}
% model beta as a function of u
x_val = 1:1:5;
y_val = [0.01 0.09 0.12 0.17 0.23];
p = polyfit(x_val,y_val,length(y_val)-1);
beta_fun = @(u) polyval(p',u);

integer = 1; % set to one to use mixed integer optimization
% if integer = 0, u is in the interval [1,5] (approximation)
only_decrease = 0; % setting this to one limits change in u to decrease only

constraints.u_max = 5;
constraints.u_min = 1;
constraints.x_max = ones(nx,1);
constraints.x_min = zeros(nx,1);

% Dynamic equations
dyn_fun = @(x,u) dynamics_SIR(x,u,alpha,beta_fun);

% Control objective and cost function
C_d = 0.9*ICU_max; % ICU Capacity
q = 10; % cost on output error 
R = 10*eye(nu); % cost on control
q_T = 10; % for terminal cost
% Objective function
stage_cost = @(x,u) q*(pop_size*K*x(2) - C_d)^2 + u'*R*u;
term_cost = @(x) q_T*(pop_size*K*x(2) - C_d)^2;

% Initial conditions
I_0 = 1000; % num persons
p_I_0 = I_0/pop_size;
p_R_0 = 0;
x_0 = [p_R_0*ones(A,1); p_I_0*ones(A,1)];
u_0 = 1.0;

% Simulation parameters
horizon  = 120;  % [days] time horizon
dt_u = 10;   % [days] sample time for discretization
% At the moment horizon/dt_u need to be integer..
RK4_steps = 8;

% In addition to x and u, plot the following:
% (function of x and u)
plot_list = {{@(x,u) 1-x(1:A,:)-x(A+1:2*A,:)}, {@(x,u) pop_size*K*x(A+1:2*A,:), @(x,u) C_d*ones(1,1+horizon/dt_u)}};
plot_list_names = {'p^S','ICU'};
plot_list_use_legends = [1, 0];

%% Solve optimal control problem
[u_opt,x_opt,t] = optimal_control(dyn_fun,stage_cost,term_cost,horizon,dt_u,RK4_steps,x_0,u_0,nx,nu,constraints,only_decrease,integer);

%% Plot Results

% States
L = nx/A;
figure
for i = 1:L
    subplot(L,1,i)
    plot(t,x_opt((i-1)*A+1:i*A,:))
    if(i==1)
        title('x_{opt}')
    end
    if(A > 1)
        legend(legends)
    end
    ylabel(state_names(i))
end
xlabel(['t [' timeUnit ']'])
filename = ['figures/',prefix,'_xopt_',time];
print(gcf,filename,'-dpng')

beta = beta_fun(u_opt); 

figure
stairs(t,beta')
title('u_{opt}')
xlabel(['t [' timeUnit ']'])
filename = ['figures/',prefix,'_uopt_',time];
print(gcf,filename,'-dpng')

% Additional plots
for i=1:length(plot_list)
   temp = plot_list{i};
   figure; hold on
   for j=1:length(temp)
      handle = temp{j};
      plot(t,handle(x_opt,u_opt)) 
   end
   hold off;
   xlabel(['t [' timeUnit ']'])
   title(plot_list_names(i))
   if(A> 1 && plot_list_use_legends(i))
       legend(legends)
   end
   filename = ['figures/',prefix,'_addplot',int2str(i),'_',time];
   print(gcf,filename,'-dpng')
end

%% Now sim system
x0 = x_0;
t = [];
x = [];
for i=1:length(u_opt)
    x_dot = @(t,x) dyn_fun(x,u_opt(i));
    [t_part,x_part] = ode45(x_dot,[(i-1)*dt_u,i*dt_u],x0);
    t = [t; t_part];
    x = [x; x_part];
    x0 = x(end,:);
end

figure
plot(t,x)

