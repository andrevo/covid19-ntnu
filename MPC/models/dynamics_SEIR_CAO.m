function x_dot = dynamics_SEIR_CAO(x,u,alpha,gamma,B,beta)
% x,u,alpha,gamma vectors, B matrix

x_1 = x(1:3); % p^R
x_2 = x(4:6); % p^I
x_3 = x(7:9); % p^E
x_S = 1-x_1-x_2-x_3; % p^S

beta_2 = B(1,1);
beta_1 = beta;

u_ = beta_2*u + beta_1*(1-u);

A = diag(alpha);
Gamma = diag(gamma);
x_1_dot = A*x_2;
x_2_dot = -A*x_2 + Gamma*x_3;
x_3_dot = - Gamma*x_3 + diag(x_S)*B*x_2;

x_3_dot(1) = -gamma(1)*x_3(1) + x_S(1)*(u_*x_2(1) + B(1,2)*x_2(2) + B(1,3)*x_2(3));

x_dot = [x_1_dot; x_2_dot; x_3_dot];
end

