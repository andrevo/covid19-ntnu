function p_H_dot = diff_p_H(x)
    p_H = x(1);
    p_E = x(2);
    p_S = x(3);
    p_I = x(4);
    
    p_H_dot = delta_S*p_S + delta_E*p_E + delta_I*p_I - ...
              (gamma_S + gamma_E + gamma_I + gamma_R + gamma_C) * p_H;
end