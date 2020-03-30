function p_R_dot = diff_p_R(x)
    p_C = x(1);
    p_E = x(2);
    p_I = x(3);
    p_H = x(4);
    
    p_R_dot = alpha_E*p_E + alpha_I*p_I + gamma_R*p_H + rho*p_C;
end