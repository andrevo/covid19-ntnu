function x_dot = dynamics_SIRHICU(x,u,params,school_fun)
p_S   = x(1);
p_I   = x(2);
p_H   = x(3);
p_ICU = x(4);
z_H   = x(5);
z_ICU = x(6);

beta_fun = @(b,x)  b(1) + b(2)*x(1) + b(3)*x(2) + b(4)*x(3) + b(5)*x(2)^2 + b(6)*x(3)^2 + b(7)*x(1)*x(:,2) + b(8)*x(1)*x(3) + b(9)*x(2)*x(3);

beta = beta_fun(params.p,school_fun(u)');

a = params.a;
b = params.b;
alpha = params.alpha;
a_H1 = params.a_H1;
a_H2 = params.a_H2;
a_ICU1 = params.a_ICU1;
a_ICU2 = params.a_ICU2;
b_H = params.b_H;
b_ICU = params.b_ICU;

% Dynamics
p_S_dot   = -beta*p_I*p_S^(a*beta + b);
p_I_dot   =  beta*p_I*p_S^(a*beta + b) - alpha*p_I;
p_H_dot   =  z_H;
p_ICU_dot =  z_ICU;
z_H_dot   = -a_H1*p_H - a_H2*z_H + b_H*p_I;
z_ICU_dot = -a_ICU1*p_ICU - a_ICU2*z_ICU + b_ICU*p_H;

x_dot = [p_S_dot; p_I_dot; p_H_dot; p_ICU_dot; z_H_dot; z_ICU_dot];
end

