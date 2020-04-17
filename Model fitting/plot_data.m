function plot_data(data,titleText)
figure
subplot(5,1,1)
plot(data.S_mat','--'); hold on
plot(data.S_mean,'-k'); hold off
title(titleText)
ylabel('S')
subplot(5,1,2)
plot(data.I_mat','--'); hold on
plot(data.I_mean,'-k'); hold off
ylabel('I')
subplot(5,1,3)
plot(data.H_mat','--'); hold on
plot(data.H_mean,'-k'); hold off
ylabel('H')
subplot(5,1,4)
plot(data.R_mat','--'); hold on
plot(data.R_mean,'-k'); hold off
ylabel('R')
subplot(5,1,5)
plot(data.D_mat','--'); hold on
plot(data.D_mean,'-k'); hold off
ylabel('D')
xlabel('time (days)')
end

