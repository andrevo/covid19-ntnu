function p_S = eq_p_S(x)
    p_D = x(1);
    p_E = x(2);
    p_H = x(3);
    p_I = x(4);
    p_C = x(5);
    
    
    p_S = 1 - p_D - p_E - p_H - p_I- p_C;
end