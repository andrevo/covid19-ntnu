function z_out = sim_z(A,B,u,z0)
    
    dyn_fun = @(x,u) A*x + B*u;

    x_dot = @(t,x) dyn_fun(x,u);
    
    % Simulate one day
    [~,z] = ode45(x_dot,[0, 1],z0);
    z_out = z(end,:)';
end

