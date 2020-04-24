function [u,info] = step_nmpc(x,u_prev,dt_u,model,objective,opt)

dyn_fun = model.dyn_fun;
nx      = model.nx;
nu      = model.nu;

stage_cost  = objective.stage_cost;
term_cost   = objective.term_cost;
constraints = objective.constraints;

horizon       = opt.horizon;
RK4_steps     = opt.RK4_steps;
only_decrease = opt.only_decrease;
integer       = opt.integer;

x_0 = x;
u_0 = u_prev;

[u_opt,x_opt,t] = optimal_control(dyn_fun,stage_cost,term_cost,horizon,dt_u,RK4_steps,x_0,u_0,nx,nu,constraints,only_decrease,integer);

u = u_opt(:,1);
info.x_opt = x_opt;
info.u_opt = u_opt;
info.t = t;

info.t_pred = [];
info.x_pred = [];

% Simulate forward from x0 (until t0 + T) using calculated control sequence
% to generate x_pred with higher resolution
for i=1:length(u_opt)-1
    x_dot = @(t,x) dyn_fun(x,u_opt(i));
    [t_part,x_part] = ode45(x_dot,[(i-1)*dt_u,i*dt_u],x_0);

    info.t_pred = [info.t_pred, t_part'];
    info.x_pred = [info.x_pred, x_part'];
    
    x_0 = x_part(end,:)';
end
end


