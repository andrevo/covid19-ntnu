function p_I_dot = diff_p_I(x)
    p_I = x(1);
    p_E = x(2);
    p_H = x(3);

    p_I_dot = eta*p_E - (alpha_I + xi + delta_I)*p_I + gamma_I*p_H;
end