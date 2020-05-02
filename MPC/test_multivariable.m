clear

load('I_H_ICU_tfs')
load('MI_LFM')
%%

ages = [0,5,9,15,20];
x_val = 0:1:length(ages)-1;
y_val = ages;
p = polyfit(x_val,y_val,length(x_val)-1);
opt.integer = 0;
if(opt.integer)
    model.school_fun = @(u) [polyval(p',u(1));u(2);u(3)];
else
    model.school_fun = @(u) u';
end
%figure, plot(x_val,polyval(p',x_val))

%%

params.alpha = alpha;
params.p = beta_params';
params.a = -16.263;
params.b = 8.0517;

params.a_H1 = sys_I2H.Denominator{:}(end);
params.a_H2 = sys_I2H.Denominator{:}(end-1);
params.a_ICU1 = sys_H2ICU.Denominator{:}(end);
params.a_ICU2 = sys_H2ICU.Denominator{:}(end-1);
params.b_H = sys_I2H.Numerator{:}(end);
params.b_ICU = sys_H2ICU.Numerator{:}(end);

u = [20;1;3]; % should be uncontrolled response
x_dot = @(t,x) dynamics_SIRHICU(x,u',params,model.school_fun);

N = 213999;



x0 = [(N-20)/N; 20/N; 0; 0; 0; 0];
simTime = 200; % sec
[t,x] = ode45(x_dot,[0 simTime],x0);

% figure
% plot(t,x(:,3:4))

%%
H_max   = 300;
ICU_max = 100;
safety_factor = 1.0;

%opt.integer = 1; % set to one to use mixed integer optimization
model.dyn_fun = @(x,u) dynamics_SIRHICU(x,u',params,model.school_fun);
model.nx = 6;
model.nu = 3;

% Objective
C_d = safety_factor*0.9*ICU_max; % ICU Capacity [num individuals]
q = 100;            % (Stage) output error weight
r = 10;    % (Stage) control weight
q_T = 10;          % Terminal output error weight


H = diag([1/20,1,1/3]); % Normalizing
if(opt.integer)
    H = diag([1/(length(ages)-1),1,1/3]); % Normalizing
end


R = diag([10,1,1]);

objective.stage_cost = @(x,u) (1-H*u)'*R*(1-H*u);
objective.term_cost = @(x) 0;
%objective.stage_cost = @(x,u) q*(N*ICU_state(x(3:3+n_pade-1),x(2)*(params.c*x(2) + params.d)) - C_d)^2 + r*(n_control-1-u)^2;
%objective.term_cost = @(x) q_T*(N*ICU_state(x(3:3+n_pade-1),x(2)*(params.c*x(2) + params.d)) - C_d)^2;
% Constraints
objective.constraints.u_max = [20; 1; 3];
if(opt.integer)
    objective.constraints.u_max = [length(ages)-1; 1; 3];
end
objective.constraints.u_min = [0; 0; 0];

objective.constraints.x_max = [1;1;0.9*H_max*safety_factor/N;0.9*ICU_max*safety_factor/N;Inf;Inf];
objective.constraints.x_min = [0;0;-0.1;-0.1;-Inf;-Inf];

%objective.constraints.du_max = 1;
%objective.constraints.du_min = -1;

% Simulation parameters
opt.horizon  = 308;  % [days] time horizon
% At the moment horizon/dt_u need to be integer..
opt.RK4_steps = 2;

opt.only_decrease = 0; % setting this to one limits change in u to decrease only
dt_u = 14;
u_0 = [0;0;0];

[u_opt,x_opt,t_opt] = optimal_control(model.dyn_fun,objective.stage_cost,objective.term_cost,opt.horizon,dt_u,opt.RK4_steps,x0,u_0,model.nx,model.nu,objective.constraints,opt.only_decrease,opt.integer);


figure
subplot(2,1,1)
plot(t_opt,x_opt(3,:)*N); hold on
plot([0,max(t_opt)],[H_max,H_max]); hold off
subplot(2,1,2)
plot(t_opt,x_opt(4,:)*N); hold on
plot([0,max(t_opt)],[ICU_max,ICU_max]); hold off
%%
figure
subplot(3,1,1)
if(opt.integer)
    stairs(t_opt,polyval(p',u_opt(1,:)))
else
    stairs(t_opt,u_opt(1,:))
end
subplot(3,1,2)
stairs(t_opt,u_opt(2,:))
subplot(3,1,3)
stairs(t_opt,u_opt(3,:))


