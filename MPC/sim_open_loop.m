function [x_out,t_out] = sim_open_loop(x_0,u,dt_u,model)

x = [];
t = [];

x0 = x_0;

for i=1:length(u)
    x_dot = @(t,x) model.dyn_fun(x,u(i));
    [t_part,x_part] = ode45(x_dot,[(i-1)*dt_u,i*dt_u],x0);
    t = [t; t_part];
    x = [x; x_part];
    x0 = x(end,:);
end

t_out = t;
x_out = x;

end