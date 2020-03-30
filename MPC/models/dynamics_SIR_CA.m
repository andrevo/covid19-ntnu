function x_dot = dynamics_SIR_CA(x,u,alpha,B)
% x,u,alpha vectors, B matrix

x_1 = x(1:2); % p^R
x_2 = x(3:4); % p^I
x_S = 1-x_1-x_2; % p^S

A = diag(alpha);
x_1_dot = A*x_2;

x_2_dot = -A*x_2 + diag(x_S)*[(1-u(1))*B(1,1)*x_2(1) + B(1,2)*x_2(2); B(2,1)*x_2(1) + (1-u(2))*B(2,2)*x_2(2)];

x_dot = [x_1_dot; x_2_dot];
end

