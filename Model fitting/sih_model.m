function [dx,y] = sih_model(t,x,u,alpha_I,alpha_H,xi,beta,c,varargin)

% Output equation.
y = x; 

% State equations.
dx = [-beta*x(1)*x(2)/(1+c*x(2));                      ... % S
      beta*x(1)*x(2)/(1+c*x(2)) - (alpha_I+xi)*x(2);   ... % I
      xi*x(2) - alpha_H*x(3)                ... % H
     ];
end
