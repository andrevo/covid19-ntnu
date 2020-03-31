clear
clf

param.alpha_E = 0.03;
param.alpha_I = 0.03;
param.alpha_C = 0.05;

param.beta_E = 0.1;
param.beta_I = 0.05;
param.beta_C = 0.01;

param.delta = 0.01;

param.eta = 0.025;

param.gamma = 0.2;

param.mu_u = 0.01;
param.mu_t = 0.002;

param.C_C = 1000;
param.N = 5400000;
param.E_0 = 100;

param.P = 1;
param.e_0 = 1/param.N;
param.rho = 0.0005;
param.c_C = param.C_C/param.N;

param.r = 0.002;

unpackStruct(param)

simout = sim('Model_1_1', 4000);
time = simout.simout.time;
data = simout.simout.data;

figure(1)
subplot(2,3,1)
plot(time,data(:,3), 'r-')
legend('Infected')
subplot(2,3,2)
plot(time,data(:,5), 'b-')
legend('Susceptible')
subplot(2,3,3)
plot(time,data(:,2), 'b-')
legend('Recovered')
subplot(2,3,4)
plot(time,data(:,7), 'k-')
legend('Asymptomatic')
subplot(2,3,5)
plot(time,data(:,6), 'r-')
legend('Death')
subplot(2,3,6)
plot(time,data(:,1), 'k-')
legend('Quarantines')

figure(2)
plot(time,data(:,4), 'r-')
hold on
plot(time,C_C*ones(1,length(time)), 'k-')
hold off
legend('ICU Patients', 'ICU Capacity')
