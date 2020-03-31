function p_E_dot = diff_p_E(x)
    p_E = x(1);
    p_C = x(2);
    p_S = x(3);
    p_I = x(4);
    p_H = x(5);
    
    p_E_dot = (beta_E*p_E + beta_H*p_H + beta_I*p_I + beta_C*p_C)*p_S ...
              - eta*p_E - (alpha_E + delta_E)*p_E + gamma_E*p_H;
end