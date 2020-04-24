function x_dot = dynamics_SIR_ICU_d_1(x,u,dist,params,beta_fun,n_pade)
p_S = x(1);
p_I = x(2);
z   = x(3:3+n_pade-1);

beta = beta_fun(u) + dist;

a = params.a;
b = params.b;
c = params.c;
d = params.d;
alpha = params.alpha;
A = params.A;
B = params.B;

% Dynamics
p_S_dot = -beta*p_I*p_S^(a*beta + b);
p_I_dot =  beta*p_I*p_S^(a*beta + b) - alpha*p_I;
z_dot   =  A*z + B*p_I*(c*p_I + d);

x_dot = [p_S_dot; p_I_dot; z_dot];
end
