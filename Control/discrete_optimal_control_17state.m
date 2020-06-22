clear;
addpath('C:\Users\emcoates\CasADi\casadi-windows-matlabR2016a-v3.4.5')

% Dependencies:
% problemDef
% defineModel
% initNLP, solveNLP, plotResults

% TODO:
% - continuous model
% - warm starting
% - automate defineModel function from sys. id. scripts

problemDef;

% Initial condition
I_0 = 20/N_pop;
x_0 = [1-I_0, I_0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]';
u_0 = 0; % start with full lockdown
% x_0 is used as first elements in lbw, ubw and w0, and used to generate
% x_start
% u_0 is used in u_start (which enters w0 and generates x_start) and 
% first delta_u cost and constraint
% NB: u_0 enters cost function J (through first delta_u cost term)
%     therefore init_NLP needs to be called every time...

% NB: need to update x_0 and u_0 before calls to solveNLP


problem = initNLP(model,cost,constraints,options,x_0,u_0);
[x_opt,u_opt,s_opt,t] = solveNLP(problem);
plotResults;

%% Now, test MPC
n_intervals = 1; % number of control intervals
simTime = n_intervals*options.dt;

x = zeros(model.nx, simTime);
x(:,1) = x_0;
u = zeros(model.nu, simTime-1);
u_prev = u_0; % This is not actually used. Just to initialize..
t = 0:1:simTime-1;

% To store MPC outputs at each iteration
x_opts = {};
u_opts = {};
s_opts = {};
t_opts = {};

MPC_iter = 1;

problemDef;


for i=1:simTime-1
    
    if(mod(i,options.dt)==1)
        problem = initNLP(model,cost,constraints,options,x(:,i),u_prev);
        [x_opt,u_opt,s_opt,t_opt] = solveNLP(problem);
        
        x_opts{MPC_iter} = x_opt;
        u_opts{MPC_iter} = u_opt;
        s_opts{MPC_iter} = s_opt;
        t_opts{MPC_iter} = t_opt;
        
        MPC_iter = MPC_iter + 1;
        
        u(:,i) = u_opt(:,1); % Only use first control
        
        figure(7)
        subplot(2,1,1)
        plot(t(1:i),x(3,1:i)); hold on
        plot(t(i)+t_opt,x_opt(3,:)); 
        plot(t,ones(size(t))*safety*ICU_max/N_pop); hold off
        axis([0 simTime + options.T 0 1.3*safety*ICU_max/N_pop])
        subplot(2,1,2)
        plot(t(1:i),u(:,1:i)); hold on
        plot(t(i)+t_opt,u_opt(:,:)); hold off
        axis([0 simTime + options.T -0.1 5.2])
        %pause
    else
        u(:,i) = u_prev;
    end
    u_prev = u(:,i);
    
    x(:,i+1) = model.dyn_fun(x(:,i),u(:,i));
    
    
end

%% Plot MPC results
figure
subplot(4,1,1)
plot(t,x(1,:))
ylabel('S')
subplot(4,1,2)
plot(t,x(2,:))
ylabel('I')
subplot(4,1,3)
plot(t,x(3,:)); hold on
plot(t,ones(size(t))*safety*ICU_max/N_pop); hold off
ylabel('ICU')
subplot(4,1,4)
stairs(t(1:end-1),u(1,:))
ylabel('u')
xlabel('t [days]')

