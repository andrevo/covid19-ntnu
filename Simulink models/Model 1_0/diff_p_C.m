function p_C_dot = diff_p_C(x)
    p_C = x(1);
    p_I = x(2);
    p_H = x(3);

    p_C_dot = xi*p_I + gamma_C*p_H - (rho + mu)*p_C;
end