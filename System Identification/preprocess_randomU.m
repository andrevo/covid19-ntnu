clear;

data = {};

index = 1;

for i=0:5.
   for j=0:29
       filename = ['results/u',num2str(i),'_run',num2str(j)];
       load(filename);
       data.u{index} = u;
       data.S{index} = S;
       data.Ia{index} = Ia;
       data.Ip{index} = Ip;
       data.Is{index} = Is;
       data.H{index} = H;
       data.ICU{index} = ICU;
       data.D{index} = D;
       data.R{index} = R;
       data.W{index} = W;
       data.NH{index} = NH;
       data.HH{index} = HH;
       data.BH{index} = BH;
       data.BS{index} = BS;
       data.US{index} = US;
       data.VS{index} = VS;
       data.Rp{index} = Rp;
       
       index = index + 1;
   end
end
save('Trondheim_randomU_180replicates','data')

%%

clear

load('Trondheim_randomU_180replicates')

for i=1:10
    figure(2)
    subplot(2,1,1)
    stairs(data.u{i})
    subplot(2,1,2)
    plot(data.ICU{i})
    pause
end

%% Current
clear
N = 214004;
load('Trondheim_randomU_180replicates')

% sample time in days
start_sample = 1;%9;
Ts = 1;

S_in = [];
I_in = [];
U_in = [];
S_diff_out = [];

for i=1:150
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    
    S = double(data.S{i}(indices))/N;
    S_diff = diff(S);
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    U = double(data.u{i}(indices));
    
    S_in = [S_in, S(1:end-1)];
    I_in = [I_in, I(1:end-1)];
    U_in = [U_in, U(1:end-1)];
    
    S_diff_out = [S_diff_out, S_diff];
end

input = [S_in; I_in; U_in];
output = S_diff_out;


%%
a_vec = zeros(1,6);

for i = 0:5
   indices = find(U_in == i);  
   S_sel = S_in(indices);
   I_sel = I_in(indices);
   S_diff_sel = S_diff_out(indices);
   force = S_diff_sel./S_sel;
   
   a = I_sel'\force';
   a_vec(i+1) = a;
   I_vals = 0:0.01:0.35;
   y  = a*I_vals;
   
   y2 = a*I_sel;
   res = force - y2;
   
   figure(1)
   subplot(3,1,1)
   scatter(S_sel,I_sel)
   xlabel('S')
   ylabel('I')
   subplot(3,1,2)
   scatter(I_sel,force); hold on
   plot(I_vals,y); hold off
   xlabel('I')
   ylabel('force of infection')
   subplot(3,1,3)
   scatter(I_sel,res) 
   ylabel('residuals')
   xlabel('I')
   pause
end
-a_vec
%%
x = 0:5;
x_vals = 0:0.1:5;
y = -a_vec; 

p5 = polyfit(x,y,5);
y_eval = polyval(p5,x_vals);

figure
plot(x,y); hold on
plot(x_vals,y_eval); hold off

%% Validate using validation data
S_in = [];
I_in = [];
U_in = [];
S_diff_out = [];

for i=151:180
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    
    S = double(data.S{i}(indices))/N;
    S_diff = diff(S);
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    U = double(data.u{i}(indices));
    
    S_in = [S_in, S(1:end-1)];
    I_in = [I_in, I(1:end-1)];
    U_in = [U_in, U(1:end-1)];
    
    S_diff_out = [S_diff_out, S_diff];
end

input2 = [S_in; I_in; U_in];
output2 = S_diff_out;
%%

S_diff_fun = @(u,S,I) -polyval(p5,u).*I.*S;

S_diff_eval = S_diff_fun(U_in,S_in,I_in);

S_diff_res = S_diff_out - S_diff_eval;

figure
subplot(2,1,1)
plot(S_diff_out); hold on
plot(S_diff_eval); hold off
subplot(2,1,2)
plot(S_diff_res)
%%
figure
scatter(I_in,S_diff_res)

%% Simulate and compare
load('estimated_r_diff')
load('estimated_ICU_model')
%load('estimated_r_diff_crude')
%load('estimated_ICU_model_crude')

S_diff_fun = @(u,S,I) -polyval(p5,u).*I.*S;
R_diff_fun = @(I_delay_3) 0.1336*I_delay_3;
I_diff_fun = @(u,S,I,I_delay_3) -S_diff_fun(u,S,I) - R_diff_fun(I_delay_3);
ICU_diff_fun = @(ICU,I_delay_14) -0.1287*ICU + 0.00254*I_delay_14;

%x_{k+1} = f(x_k,u_k)
dyn_fun = @(x,u) [x(1) + S_diff_fun(u,x(1),x(2)); 
                x(2) + I_diff_fun(u,x(1),x(2),x(6));
                x(3) + ICU_diff_fun(x(3),x(17));
                x(2);
                x(4);
                x(5);
                x(6);
                x(7);
                x(8);
                x(9);
                x(10);
                x(11);
                x(12);
                x(13);
                x(14);
                x(15);
                x(16)];

%S_diff_fun = @(u,S,I) -polyval(p5,u).*I.*S;
%R_diff_fun = @(I) 1.308*I;
%I_diff_fun = @(u,S,I) -S_diff_fun(u,S,I) - R_diff_fun(I);
%ICU_diff_fun = @(ICU,I_delay_1) -0.8452*ICU + 0.016*I_delay_1;

% x_{k+1} = f(x_k,u_k)
% dyn_fun = @(x,u) [x(1) + S_diff_fun(u,x(1),x(2));                  % S 
%                   x(2) + I_diff_fun(u,x(1),x(2));   % I
%                   x(3) + ICU_diff_fun(x(3),x(4));                  % ICU
%                   x(2);                                            % I_delay_1
%                   ];
% 4 states!

% Evaluate R_diff and ICU models based on real data:
for i=151:180
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    S = double(data.S{i}(indices))/N;
    S_diff = diff(S);
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    U = double(data.u{i}(indices));
    ICU = double(data.ICU{i}(indices))/N;
    Rem = double(data.Is{i}(indices) + data.H{i}(indices) + data.ICU{i}(indices) + data.D{i}(indices) + data.R{i}(indices))/N;
    Rem_diff = diff(Rem);
    
    % Calculate ICU with model, using real input, and compare
    ICU_0 = ICU(1);
    ICU_pred = zeros(size(ICU));
    ICU_pred(1) = ICU_0;
    for j =1:length(ICU)-1
        I_delay_1 = 0;
        if(j>1)
            I_delay_1 = I(j-1);
        end
        ICU_pred(j+1) = ICU_pred(j) + ICU_diff_fun(ICU_pred(j),I_delay_1);
    end
    % Calculate R_diff with model, using real input, and compare
    R_diff_0 = Rem_diff(1);
    R_diff_pred = R_diff_fun(I);
    figure
    subplot(2,1,1)
    plot(ICU_pred); hold on
    plot(ICU); hold off
    subplot(2,1,2)
    plot(R_diff_pred); hold on
    plot(Rem_diff); hold off
    pause
    
    
end

%%

              
              
for i=151:180
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    
    S = double(data.S{i}(indices))/N;
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    U = double(data.u{i}(indices));
    ICU = double(data.ICU{i}(indices))/N;
    Rem = double(data.Is{i}(indices) + data.H{i}(indices) + data.ICU{i}(indices) + data.D{i}(indices) + data.R{i}(indices))/N;
    
    
    % Simulate
    % 9,19,29,39,49,59,69,79,89,99,109,119,129,139,149..etc
    start_index = 8;  % Ts = 1: e.g. 80,    Ts= 10: use e.g 8
    end_index = length(S);
    
    if(end_index > length(S))
        end_index = length(S);
    end
    l = end_index - start_index + 1;
    S_sim = zeros(1,l);
    I_sim = zeros(1,l);
    ICU_sim = zeros(1,l);
    Rem_sim = zeros(1,l);
    
    S_sim(1) = S(start_index);
    I_sim(1) = I(start_index);
    Rem_sim(1) = Rem(start_index);
    ICU_sim(1) = ICU(start_index);
    
    S_0 = S(start_index);
    I_0 = I(start_index);
    ICU_0 = ICU(start_index);
    %x_0 = [S_0, I_0, ICU_0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]';
    x_0 = [S_0, I_0, ICU_0, 0]';
    k = 1;
    for j=start_index-1:-1:max(1,start_index-1)%14)
        x_0(3+k) = I(j);
        k = k + 1;
    end
    
    x = zeros(l,length(x_0));
    x(1,:) = x_0;
    
    for j=1:l-1
        x(j+1,:) = dyn_fun(x(j,:),U(start_index + j - 1));
        
%         S_diff_sim = S_diff_fun(U(start_index + j - 1),S_sim(j),I_sim(j));
%         S_sim(j+1) = S_sim(j) + S_diff_sim;
%         
%         I_delay_3 = 0;
%         if(j >= 4)
%            I_delay_3 = I_sim(j-3);
%         elseif((start_index + j - 1 - 3) >= 1)
%            I_delay_3 = I(start_index + j - 1 - 3);
%         end
%         R_diff = 0.1336*I_delay_3;
%         I_sim(j+1) = I_sim(j) - S_diff_sim - R_diff;
%         Rem_sim(j+1) = Rem_sim(j) + R_diff;
%         
%         I_delay_14 = 0;
%         if(j >= 15)
%            I_delay_14 = I_sim(j-14);
%         elseif((start_index + j - 1 - 14) >= 1)
%            I_delay_14 = I(start_index + j - 1 - 14);
%         end
%         ICU_sim(j+1) = ICU_sim(j) - 0.1287*ICU_sim(j) + 0.00254*I_delay_14;
    end
    
    S_sim = x(:,1);
    I_sim = x(:,2);
    ICU_sim = x(:,3);
    Rem_sim = Rem(start_index) + cumsum(R_diff_fun(I_sim)) - R_diff_fun(I_sim(1));
    
    % Use full states histories for comparison, even when using Ts > 1..
    S = double(data.S{i})/N;
    I = double(data.Ia{i} + data.Ip{i})/N;
    ICU = double(data.ICU{i})/N;
    Rem = double(data.Is{i} + data.H{i} + data.ICU{i} + data.D{i} + data.R{i})/N;
    
    start_index = indices(start_index);
    end_index = indices(end_index);
    
    t_ = 0:Ts:Ts*(length(S_sim)-1);
    t  = 0:end_index - start_index;
    
    % Compare
    figure(1)
    subplot(4,1,1)
    plot(t_,S_sim); hold on
    plot(t,S(start_index:end_index)); hold off
    legend('sim','real')
    ylabel('S')
    subplot(4,1,2)
    plot(t_,I_sim); hold on
    plot(t,I(start_index:end_index)); hold off
    legend('sim','real')
    ylabel('I')
    subplot(4,1,3)
    plot(t_,Rem_sim); hold on
    plot(t,Rem(start_index:end_index)); hold off
    legend('sim','real')
    ylabel('R')
    subplot(4,1,4)
    plot(t_,ICU_sim); hold on
    plot(t,ICU(start_index:end_index)); hold off
    legend('sim','real')
    ylabel('ICU')
    pause
end

%% Repeat for continuous-time model?

%%

for i=21:180
    S = double(data.S{i});
    S_diff = diff(S);
    I = double(data.Ia{i} + data.Ip{i});
    U = double(data.u{i});
    
    S_in = S(1:end-1);
    I_in = I(1:end-1);
    U_in = U(1:end-1);
    input = [S_in; I_in; U_in];
    out = net(input);
    
    figure
    subplot(2,1,1)
    plot(S_diff); hold on
    plot(out); hold off
    legend('true','nn')
    subplot(2,1,2)
    plot(S); hold on
    plot(S(1) + cumsum(out)); hold off
    legend('true','nn')
    pause
end

%%
for i=1:180
    S = double(data.S{i});
    S_diff = diff(S);
    I = double(data.Ia{i} + data.Ip{i});
    I_diff = diff(I);
    U = double(data.u{i});
    
    S_in = S(1:end-1);
    I_in = I(1:end-1);
    U_in = U(1:end-1);
    input = [S_in; I_in; U_in];
    out = net(input);
    
    y = I_diff + out;
    
    figure
    plot(y); hold on
    plot(-0.1*circshift(I,4)); hold off
    legend('y','I')
    pause
end

%%

clear

load('Trondheim_randomU_180replicates')
N = 214004;
dats_diff = {};
dats_out  = {};
dats_ICU  = {};
% sample time in days
start_sample = 9;
Ts = 10;


for i=1:20
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    Rem = double(data.Is{i}(indices) + data.H{i}(indices) + data.ICU{i}(indices) + data.D{i}(indices) + data.R{i}(indices))/N;
    
    Rem_diff = diff(Rem);
    
    id_data = iddata(Rem_diff',I(1:end-1)',1);
    dats_diff{i} = id_data;
    id_data = iddata(Rem',I',1);
    dats_out{i} = id_data;
    
%     figure(1)
%     subplot(2,1,1)
%     scatter(I,Rem)
%     subplot(2,1,2)
%     scatter(I(1:end-1),Rem_diff)
%     pause

    % ICU data
    ICU = double(data.ICU{i}(indices))/N;
    id_data = iddata(ICU',I',1);
    dats_ICU{i} = id_data;
end
merged_diff_1 = merge(dats_diff{:});
merged_out_1 = merge(dats_out{:});
merged_ICU_1 = merge(dats_ICU{:});

% Create validation data
dats_diff = {};
dats_out  = {};
dats_ICU = {};
for i=31:40
    len = length(data.S{i});
    indices = start_sample:Ts:len;
    I = double(data.Ia{i}(indices) + data.Ip{i}(indices))/N;
    Rem = double(data.Is{i}(indices) + data.H{i}(indices) + data.ICU{i}(indices) + data.D{i}(indices) + data.R{i}(indices))/N;
    
    Rem_diff = diff(Rem);
    
    id_data = iddata(Rem_diff',I(1:end-1)',1);
    dats_diff{i-30} = id_data;
    id_data = iddata(Rem',I',1);
    dats_out{i-30} = id_data;
    
    % ICU data
    ICU = double(data.ICU{i}(indices))/N;
    id_data = iddata(ICU',I',1);
    dats_ICU{i-30} = id_data;
end

merged_diff_2 = merge(dats_diff{:});
merged_out_2 = merge(dats_out{:});
merged_ICU_2 = merge(dats_ICU{:});

%%
%%
clear

load('Trondheim_randomU_180replicates')

S_in = [];
I_in = [];
U_in = [];
y_out = [];

for i=1:30
    S = double(data.S{i});
    I = double(data.Ia{i} + data.Ip{i});
    U = double(data.u{i});
    
    I_diff = diff(I);
    
    S_in = [S_in, S(1:end-1)];
    I_in = [I_in, I(1:end-1)];
    U_in = [U_in, U(1:end-1)];
    
    
    I_prev = zeros(size(I_diff));
    for i=1:length(I_prev)
       
        if i >= 4
            I_prev(i) = I(i-3);
        end
        
    end
    
    y = I_diff + 0.1337*I_prev;
    
    y_out = [y_out, y];
end

input = [S_in; I_in; U_in];
output = y_out;

S_in = [];
I_in = [];
U_in = [];
y_out = [];

for i=151:180
    S = double(data.S{i});
    I = double(data.Ia{i} + data.Ip{i});
    U = double(data.u{i});
    
    I_diff = diff(I);
    
    S_in = [S_in, S(1:end-1)];
    I_in = [I_in, I(1:end-1)];
    U_in = [U_in, U(1:end-1)];
    
    
    I_prev = zeros(size(I_diff));
    for i=1:length(I_prev)
       
        if i >= 4
            I_prev(i) = I(i-3);
        end
        
    end
    
    y = I_diff + 0.1337*I_prev;
    
    y_out = [y_out, y];
end

input2 = [S_in; I_in; U_in];
output2 = y_out;

%%

for i=1:180
    S = double(data.S{i});
    I = double(data.Ia{i} + data.Ip{i});
    U = double(data.u{i});
    ICU = double(data.ICU{i});
    
    I_diff = diff(I);
    
    
    I_prev = zeros(size(I_diff));
    for i=1:length(I_prev)
        if i >= 4
            I_prev(i) = I(i-3);
        end
    end
    y = I_diff + 0.1337*I_prev;
    S_in = S(1:end-1);
    I_in = I(1:end-1);
    U_in = U(1:end-1);
    input = [S_in; I_in; U_in];
    out = myNeuralNetworkFunction2(input);
    I_pred = I(1) + cumsum(out - 0.1337*I_prev)
    
    I_11 = zeros(size(ICU));
    I_12 = zeros(size(ICU));
    I_13 = zeros(size(ICU));
    for i=1:length(I_prev)
        if i >= 12
            I_11(i) = I_pred(i-11);
        end
        if i >= 13
            I_12(i) = I_pred(i-12);
        end
        if i >= 14
            I_13(i) = I_pred(i-13);
        end
    end
    ICU_pred = zeros(size(ICU));
    ICU_pred(1) = ICU(1);
    for k = 1:length(ICU)-1
       ICU_pred(k+1) = 0.8805*ICU_pred(k) + 0.002799*I_11(k) - 0.007905*I_12(k) + 0.007484*I_13(k); 
        
    end
    
 
    
    figure
    subplot(4,1,1)
    plot(y); hold on
    plot(out); hold off
    legend('true','nn')
    subplot(4,1,2)
    plot(S); hold on
    plot(S(1) + cumsum(-out)); hold off
    legend('true','nn')
    subplot(4,1,3)
    plot(I); hold on
    plot(I_pred); hold off
    legend('true','nn')
        subplot(4,1,4)
    plot(ICU); hold on
    plot(ICU_pred); hold off
    legend('true','nn')
    pause
end
%%
clear

load('Trondheim_randomU_180replicates')

dats = {};

for i=1:10
    I = double(data.Ia{i} + data.Ip{i});
    ICU = double(data.ICU{i});
    
    ICU_diff = diff(ICU);
    
    id_data = iddata(ICU',I(1:end)',1);
    dats{i} = id_data;
end

merged1 = merge(dats{:});

dats = {};
for i=11:20
    I = double(data.Ia{i} + data.Ip{i});
    ICU = double(data.ICU{i});
    
    ICU_diff = diff(ICU);
    
    id_data = iddata(ICU',I(1:end)',1);
    dats{i-10} = id_data;
end

merged2 = merge(dats{:});

%%


y_fun = @(u) net(u);
y_fun([1;2;3])


