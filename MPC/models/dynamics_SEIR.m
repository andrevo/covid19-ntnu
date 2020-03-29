function x_dot = dynamics_SEIR(x,u,alpha,gamma,beta_1,beta_2)
% alpha:  Recovery rate [1/time]
% gamma:  Rate of becoming infectious
% beta_1: Uncontrolled transmission rate (when u = 0)
% beta_2: Transmission rate for maximum control (when u = 1)
% beta_2 < beta_1
p_E = x(1);
p_I = x(2);         % I/N, fraction of total population that is infected (and infections).
p_R = x(3);         % R/N, fraction of total population that has recovered.
p_S = 1- p_E - p_I - p_R; % S/N, fraction of total population that is susceptible.

% Dynamics
p_E_dot = (beta_2*u + beta_1*(1-u))*p_I*p_S - gamma*p_E;
p_I_dot = gamma*p_E - alpha*p_I;
p_R_dot = alpha*p_I;

x_dot = [p_E_dot; p_I_dot; p_R_dot];
end

