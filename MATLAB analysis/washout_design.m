clear all
close all

s = tf('s');


%% SCOOT FILTER 
% the idea is that there are two filters acting on ay
% one is a low-pass filter on accel... then this gets integrated
%twice to end up at an x position... which we ALSO hp filter
%so that it returns to center. This ends up being a 2nd order HP*1/s*
%another HP filter. I design these in two parts, for no good reason.

%scale factor for simulation
scale = 0.25;

z = 1;
wn = 10;
t = 0:.001:4;
%high pass filter for x, y
Ghp = s^2/(s^2+2*z*wn*s+wn^2);
[ayfilt,t]=step(Ghp*scale,t);
figure
plot(t,ayfilt,'r');
ylabel('Filtered ay (gs)')
xlabel('Time (s)')
title('1G step response')

%now integrate that acceleration to see what 
%the x command would be.
[xcommand,t] = lsim(1/s^2,ayfilt,t);

%now leak position back out to zero over a few seconds
aleak = 1/3;
Aleak = 1;
Gleak = Aleak*s/(s+aleak);
[xcommand2,t] = lsim(Gleak,xcommand,t);

%now compute the actual acceleration due to the scoot (just to check it)
vcommand2 = diff(xcommand2)./diff(t);
t2 = t(1:end-1);
%this is the actual acceleration produced during the scoot
acommand2 = diff(vcommand2)./diff(t2);
ta = t2(1:end-1);
%now clean this up with padded zeros. this will be usefuly when computing
%the total acceleration during the simulation from both tilt and scoot.
ascoot = [acommand2;0;0];

figure
plot(t,xcommand,'k',t,xcommand2,'r')
ylabel('platform y command (m)')
xlabel('Time (s)')
title('platform y position for 1g step')
legend('integrated ay','leaked')

figure
plot(ta,acommand2,'r');
ylabel('perceived accel (gs)')
xlabel('Time (s)')
title('1G step response')

%total filter for scoot is the product of these 3 steps:
Gscoot = minreal(Ghp* 1/s^2 * Gleak)
%confirm that this works:
[ycommand_final,tscoot] = step(Gscoot*scale);
figure
plot(tscoot,ycommand_final,'k')
ylabel('platform y command')
xlabel('time (s)')
title('1g acceleration step response in y')


%% TILT FILTER (low pass)

%now simulate the low-pass filter used to develop tilt command
wlp = 100;
zlp = 1;
Glp = wlp^2/(s^2+2*zlp*wlp*s+wlp^2);
[aylp,t]=step(Glp*scale,t);
%now turn this into a tilt angle command. perceived accel is the sin(theta)
tilt = asind(aylp);

figure
plot(t,tilt,'k')
xlabel('time (s)')
ylabel('tilt command (deg)')

%% Total Simulated Acceleration
atot =  aylp+ascoot;
figure
plot(t,aylp,t,ascoot,t,atot)
xlabel('Time (s)')
ylabel('Simulated accel (g)')
title('1g step response')
legend('from tilt','from scoot','total')



