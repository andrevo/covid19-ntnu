%%
clear
close all

% x = [p^E p^I p^R]^T

alpha = 0.1;
gamma = 0.2;

c = 0.1;
ICU_max = 100;

N = 100000;
I_0 = 100;
p_I_0 = I_0/N;
p_R_0 = 0;
p_E_0 = 0.01;

y_d = 0.9*ICU_max/N;

x_0 = [p_E_0; p_I_0; p_R_0];

% I/O Feedback linearization
k = .001;
control = @(x) alpha*y_d./(c*x(2).*(1-sum(x))) - k*(c*x(2)-y_d)/(gamma*c*x(2).*(1-sum(x)));

dyn = @(t,x) [control(x)*x(2)*(1-sum(x)) - gamma*x(1); -alpha*x(2) + gamma*x(1); alpha*x(2)];

tspan = [0 200];

[t,y] = ode45(dyn,tspan,x_0);
%%
p_E = y(:,1);
p_I = y(:,2);
p_R = y(:,3);
p_S = 1 - p_E - p_I - p_R;

beta = zeros(size(p_E));
for i=1:length(p_E)
   beta(i) = control(y(i,:));
end

figure
subplot(4,1,1)
plot(t,p_S)
subplot(4,1,2)
plot(t,p_E)
subplot(4,1,3)
plot(t,p_I)
subplot(4,1,4)
plot(t,p_R)

figure
subplot(2,1,1)
plot(t,c*p_I*N); hold on
plot(t,ICU_max*ones(size(t))); hold off
subplot(2,1,2)
plot(t,beta)



