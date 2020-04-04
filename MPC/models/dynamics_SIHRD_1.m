function x_dot = dynamics_SIHRD_1(x,u,param,beta_fun)
% alpha:  Recovery rate [1/time]
% beta_fun: Function handle to calculate beta from u
p_I = x(1);         % I/N, fraction of total population that is infected (and infections).
p_H = x(2);         % H/N, fraction of total population that is hospitalized
p_R = x(3);         % R/N  fraction of total population that has recovered.
p_D = x(4);         % D/N  fraction of total population that has died.

p_S = 1- p_I - p_H - p_R - p_D; % S/N, fraction of total population that is susceptible.

beta = beta_fun(u);

% Dynamics
p_I_dot = beta*p_I*p_S - (param.alpha_I + param.xi)*p_I;
p_H_dot = param.xi*p_I - (param.mu + param.alpha_H)*p_H;
p_R_dot = param.alpha_I*p_I + param.alpha_H*p_H;
p_D_dot = param.mu*p_H;

x_dot = [p_I_dot; p_H_dot; p_R_dot; p_D_dot];
end

