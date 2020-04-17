function [params,modelFit,id_data] = param_identification(data,modelType,N)
p_S = data.S_mean/N;
p_I = data.I_mean/N;
p_H = data.H_mean/N;
p_R = data.R_mean/N;
p_D = data.D_mean/N;

switch modelType
    case 'SIR'
        y = [p_S; p_I; p_R + p_D + p_H];
        id_data = iddata(y',[],1);
        id_data.Tstart = 0;
        id_data.TimeUnit = 'days';
        id_data.OutputName = {'p^S','p^I','p^R'}
        
        % Initial guess for parameters
        alpha = 0.12;
        beta  = 0.2;
        c = 0;

        % Prepare model
        order          = [3 0 3];      % [ny nu nx].
        parameters     = {alpha,beta,c}; % initial parameters
        initial_states = [(N-20)/N; 20/N; 0];
        Ts             = 0; % Continuous model
        nlgr = idnlgrey('sir_model',order,parameters,initial_states,Ts,'Name','SIR Model','TimeUnit','days');

        % Perform fit
        %nlgr.Parameters(1).Fixed = true; % set fixed alpha
        nlgr.Parameters(3).Fixed = true; % set fixed c
        modelFit = nlgreyest(id_data,nlgr);

        params = getpvec(modelFit);
        return;
    case 'SIH'
        y = [p_S; p_I; p_H];
        id_data = iddata(y',[],1);
        id_data.Tstart = 0;
        id_data.TimeUnit = 'days';
        id_data.OutputName = {'p^S','p^I','p^H'}
        
        % Initial guess for parameters
        alpha_I = 0.12;
        alpha_H = 0.15;
        xi = 0.003;
        beta  = 0.2;
        c = 0;%1.6965;

        % Prepare model
        order          = [3 0 3];      % [ny nu nx].
        parameters     = {alpha_I,alpha_H,xi,beta,c}; % initial parameters
        initial_states = [(N-20)/N; 20/N; 0];
        Ts             = 0; % Continuous model
        nlgr = idnlgrey('sih_model',order,parameters,initial_states,Ts,'Name','SIH Model','TimeUnit','days');

        % Perform fit
        %nlgr.Parameters(1).Fixed = true; % set fixed alpha
        nlgr.Parameters(5).Fixed = true; % Set fixed c
        modelFit = nlgreyest(id_data,nlgr);

        params = getpvec(modelFit);
        return
    case 'SIHRD'
        fprintf('Not implemented yet!\n')
        return
    otherwise
        fprintf('Error, invalid model type provided!\n')
        return
end

% y = [p_S; p_I; p_H; p_R; p_D];
% data = iddata(y',[],1);
% data.Tstart = 0;
% data.TimeUnit = 'days';
% data.OutputName = {'p^S','p^I','p^H','p^R','p^D'};
% 
% % Prepare model   (alpha_H + mu = 0.1094)
% % alpha_I,alpha_H,xi,beta
% alpha_I = 0.1217*param_scale_factors(1);
% alpha_H = 0.1094*param_scale_factors(2);
% xi = 0.0032*param_scale_factors(3);
% a = 0.5*param_scale_factors(4);
% beta  = 0.1908*param_scale_factors(5);
% 
% order          = [5 0 5];      % [ny nu nx].
% parameters     = {alpha_I,alpha_H,xi,a,beta}; % initial parameters
% initial_states = [(1/scale_factors(1))*(N-20)/N; (1/scale_factors(2))*20/N; 0; 0; 0];
% Ts             = 0; % Continuous model
% nlgr = idnlgrey('sihrd_model',order,parameters,initial_states,Ts,'Name','SIHRD Model');
% 
% fix = 0;
% if(fix)
%     nlgr.Parameters(1).Fixed = true;
%     nlgr.Parameters(2).Fixed = true;
%     nlgr.Parameters(3).Fixed = true;
%     %nlgr.Parameters(4).Fixed = true;
%     nlgr.Parameters(5).Fixed = true;
% end
% 
% % Perform fit
% fitted_model = nlgreyest(data,nlgr,'Display','on');
% 
% % Compare fit to data
% figure
% compare(data,fitted_model)
% 
% getpvec(fitted_model)./param_scale_factors'

end

