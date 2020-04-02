function u = step_nmpc(x,u_prev,dt_u,model,objective,opt)

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

[u_opt,~,~] = optimal_control(dyn_fun,stage_cost,term_cost,horizon,dt_u,RK4_steps,x_0,u_0,nx,nu,constraints,only_decrease,integer);

u = u_opt(:,1);

end


