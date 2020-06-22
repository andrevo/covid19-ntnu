figure(3)
subplot(5,1,1)
plot(t,x_opt(1,:)')
subplot(5,1,2)
plot(t,x_opt(2,:)')
subplot(5,1,3)
plot(t,x_opt(3,:)'*N_pop); hold on
plot([0 t(end)],[ICU_max*safety, ICU_max*safety]); hold off
subplot(5,1,4)
plot(t,u_opt')
subplot(5,1,5)
plot(t,s_opt')