function x_dot = sir_dynamics(x,u,alpha,beta_1,beta_2)
p_I = x(1);
p_R = x(2);
p_S = 1- p_I - p_R;
x_dot = [(beta_2*u + beta_1*(1-u))*p_I*p_S - alpha*p_I; alpha*p_I];
end

