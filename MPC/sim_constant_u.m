function [x_out,t_out] = sim_constant_u(x_0,u,dt_u,simTime,model)

x_dot = @(t,x) model.dyn_fun(x,u);

x = [];
t = [];

[t,x] = ode45(x_dot,[0,simTime],x_0);

t_out = t;
x_out = x;

end


