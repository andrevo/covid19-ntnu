clear

safety = 0.9; % 0.45
folder = 'new_model_090/'; %_045

ICU_mat = zeros(10,200);

figure; hold on
for i=0:9
    filename = sprintf('%sclosedLoop_test_run%d',folder,i);
    load(filename)
    ICU_mat(i+1,:) = ICU;
    
    plot(ICU)
end
plot([0 200],[safety*74 safety*74]) % 0.45*74
plot([0 200],[74, 74]); 
plot(median(ICU_mat),'*')
hold off

figure; hold on
for i=0:9
    if i==3
        continue;
    end
    filename = sprintf('%sclosedLoop_test_run%d',folder,i);
    load(filename)
    
    plot(ICU)
end
plot([0 200],[safety*74 safety*74]) % 0.45*74
plot([0 200],[74, 74]); 
hold off

%%
safety = 0.45; % 0.45
folder = 'new_model_045/'; %_045

figure; hold on
for i=0:9
    filename = sprintf('%sclosedLoop_test_run%d',folder,i);
    load(filename)
    
    plot(ICU)
end
plot([0 200],[safety*74 safety*74]) % 0.45*74
plot([0 200],[74, 74]); 
hold off

%%

%%
clear

% 6 strats
strats = [0,  0,   0;
          9,  0,   0;
          9,  0.4, 1;
          20, 0.4, 1;
          20, 0.8, 2;
          20, 1.0, 3];

safety = 0.9; % 0.45
folder = 'new_model_090/'; %_045

for i = 0:9
    filename = sprintf('%sclosedLoop_test_run%d',folder,i);
    load(filename)
N_pop = 214004;

figure(3)
index = 1;

u = squeeze(u_preds(:,:,1));
for j = 2:7:length(ICU)
    x_pred = squeeze(x_preds(index,:,:));
    ICU_pred = x_pred(3,:)*N_pop;
    I_pred = x_pred(2,:)*N_pop;
    t_pred = j-1:7:7*(length(ICU_pred)-1)+j-1;
    I_max = max(I_pred);
    
    subplot(3,1,1)
    plot(Ia + Ip); hold on
    plot(t_pred,I_pred); hold off
    axis([0 length(ICU) 0 I_max])
    
    subplot(3,1,2)
    plot(ICU); hold on
    plot([0 200],[safety*74 safety*74]) % 0.45*74
    plot([0 200],[74, 74]); 
    plot(t_pred,ICU_pred); hold off
    
    axis([0 length(ICU) 0 100])
    
    u_pred = squeeze(u_preds(index,:,:));
    t_u = 1:7:200;
    
    
    subplot(3,1,3)
    stairs(t_u,u); hold on
    stairs(t_pred,u_pred); hold off
    axis([0 length(ICU) -0.2 5.2])
    
    pause(0.2)
    index = index + 1;
end

strat = zeros(length(u),3);
for k = 1:length(u)
    strat(k,:) = strats(u(k)+1,:);
end

% figure
% subplot(3,1,1)
% stairs(strat(:,1))
% ylabel('S')
% subplot(3,1,2)
% stairs(strat(:,2))
% ylabel('W')
% subplot(3,1,3)
% stairs(strat(:,3))
% ylabel('R')
% pause
end







