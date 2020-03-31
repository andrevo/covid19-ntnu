param.alpha_E = 0.03;
param.alpha_I = 0.03;

param.beta_E = 0.2;
param.beta_I = 0.1;
param.beta_H = 0.01;
param.beta_C = 0.002;

param.delta_S = 0.001;
param.delta_E = 0.01;
param.delta_I = 0.5;

param.eta = 0.01;

param.gamma_S = 0.01;
param.gamma_E = 0.0001;
param.gamma_I = 0.0001;
param.gamma_R = 0.001;
param.gamma_C = 0.0001;

param.mu = 0.01;

param.N = 200000;
param.E_0 = 100;

param.rho = 0.05;

param.xi = 0.003;
unpackStruct(param)

sim('Model_1_0_simple_wo_constraint', 500)
