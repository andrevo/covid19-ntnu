function x_dot = dynamics_SIH_1(x,u,param,beta_fun)
% alpha:  Recovery rate [1/time]
% beta_fun: Function handle to calculate beta from u
p_S = x(1);         % S/N, fraction of total population that is susceptible
p_I = x(2);         % I/N, fraction of total population that is infected (and infections).
p_H = x(3);         % H/N, fraction of total population that is hospitalized

beta = beta_fun(u);

% Dynamics
p_S_dot = -beta*p_S*p_I;
p_I_dot = beta*p_I*p_S - (param.alpha_I + param.xi)*p_I;
p_H_dot = param.xi*p_I - param.alpha_H*p_H;

x_dot = [p_S_dot; p_I_dot; p_H_dot];
end

