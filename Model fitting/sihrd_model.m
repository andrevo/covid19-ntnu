function [dx,y] = sihrd_model(t,x,u,alpha_I,alpha_H,xi,a,beta,varargin)

% Output equation.
y = x; 

% State equations.
dx = [-beta*x(1)*x(2);                      ... % S
      beta*x(1)*x(2) - (alpha_I+xi)*x(2);   ... % I
      xi*x(2) - alpha_H*x(3);               ... % H
      alpha_I*x(2) + a*alpha_H*x(3);        ... % R
      (1-a)*alpha_H*x(3)                    ... % D
     ];
end