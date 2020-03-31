function x_dot = dynamics_SIR(x,u,alpha,beta_fun)
% alpha:  Recovery rate [1/time]
% beta_fun: Function handle to calculate beta from u
p_R = x(1);         % R/N, fraction of total population that has recovered.
p_I = x(2);         % I/N, fraction of total population that is infected (and infections).
p_S = 1- p_I - p_R; % S/N, fraction of total population that is susceptible.

beta = beta_fun(u);

% Dynamics
p_I_dot = beta*p_I*p_S - alpha*p_I;
p_R_dot = alpha*p_I;

x_dot = [p_R_dot; p_I_dot];
end

