function model = defineModel

% This script defines the predictive model.
% Should define the following:
% model.dyn_fun, model.nx and model.nu
p5 = [-0.0015, 0.0195, -0.0882, 0.1649, -0.0900, 0.0987]';
S_diff_fun = @(u,S,I) -polyval(p5,u).*I.*S;
R_diff_fun = @(I_delay_3) 0.1336*I_delay_3;
I_diff_fun = @(u,S,I,I_delay_3) -S_diff_fun(u,S,I) - R_diff_fun(I_delay_3);
ICU_diff_fun = @(ICU,I_delay_14) -0.1287*ICU + 0.00254*I_delay_14;

% All states normalized by population size N
% x = [S, I, ICU, I_delay_1, I_delay_2, I_delay_3, I_delay_4, I_delay_5,
%      I_delay_6, I_delay_7, I_delay_8, I_delay_9, I_delay_10, I_delay_11,
%      I_delay_12, I_delay_13, I_delay_14]

% 17 state variables, 1 control variable
model.nx = 17; 
model.nu = 1;
% and I_delay_i = x_{i+3}

% x_{k+1} = f(x_k,u_k)
model.dyn_fun = @(x,u) [x(1) + S_diff_fun(u,x(1),x(2)); 
                x(2) + I_diff_fun(u,x(1),x(2),x(6));
                x(3) + ICU_diff_fun(x(3),x(17));
                x(2);
                x(4);
                x(5);
                x(6);
                x(7);
                x(8);
                x(9);
                x(10);
                x(11);
                x(12);
                x(13);
                x(14);
                x(15);
                x(16)];
end