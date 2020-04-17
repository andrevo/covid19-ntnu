function [dx,y] = sir_model(t,x,u,alpha,beta,c,varargin)

% Output equation.
y = x; 

% State equations.
dx = [-beta*x(1)*x(2)/(1+c*x(2));               ... % S
      beta*x(1)*x(2)/(1+c*x(2)) - alpha*x(2);   ... % I
      alpha*x(2)                     ... % R
     ];
end