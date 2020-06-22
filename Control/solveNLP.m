function [x_opt,u_opt,s_opt,t] = solveNLP(nlp)
nx = nlp.model.nx;
nu = nlp.model.nu;
ns = nlp.constraints.ns;

dt = nlp.options.dt;
T  = nlp.options.T;

% Solve the NLP
sol = nlp.solver('x0', nlp.w0, 'lbx', nlp.lbw, 'ubx', nlp.ubw,...
            'lbg', nlp.lbg, 'ubg', nlp.ubg);

% Extract solution
w_opt = full(sol.x);
w_opt = [w_opt; nan(nu,1); nan(ns,1)];
w_opt = reshape(w_opt,[nx+nu+ns,nlp.N+1]);

x_opt = w_opt(1:nx,:);
u_opt = w_opt(nx+1:nx+nu,:);
s_opt = w_opt(nx+nu+1:end,:);
t = 0:dt:T;
end

