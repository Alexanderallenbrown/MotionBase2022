clc; close all; clear all;

IMUdata = load('IMUDataDirectPowerandEnabledMotors.txt');
IMUdata1 = load('IMUDataDirectWithNoPowerToMotor.txt');
IMUdata2 = load('IMUDataDirectWithPowerToMotors.txt');
%washData = readtable('washFileValidationFullSize.txt');

%organize IMU data from python
xAccel = [IMUdata(1:length(IMUdata2),1),IMUdata1(1:length(IMUdata2),1),IMUdata2(:,1)];
yAccel = [IMUdata(1:length(IMUdata2),2),IMUdata1(1:length(IMUdata2),2),IMUdata2(:,2)];
zAccel = [IMUdata(1:length(IMUdata2),3),IMUdata1(1:length(IMUdata2),3),IMUdata2(:,3)];

% xGyro = table2array(IMUdata(:,4));
% yGyro = table2array(IMUdata(:,5));
% zGyro = table2array(IMUdata(:,6));

timeArduino = [IMUdata(1:length(IMUdata2),7),IMUdata1(1:length(IMUdata2),7),IMUdata2(:,7)];

figure(1)
plot(xAccel(:,1),'g')
hold on
plot(xAccel(:,2),'b')
plot(xAccel(:,3),'k')
legend('Power and Motors Enabled','No Power to Motors','Power to motors not enabled')
xlabel('Indexing')
ylabel('X Acceleration From IMU')
title('X accleration Testing for EMI Interferance')

figure(2)
plot(yAccel(:,1),'g')
hold on
plot(yAccel(:,2),'b')
plot(yAccel(:,3),'k')
legend('Power and Motors Enabled','No Power to Motors','Power to motors not enabled')
xlabel('Indexing')
ylabel('Y Acceleration From IMU')
title('Y accleration Testing for EMI Interferance')
