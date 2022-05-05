clc; close all; clear all;

BrakeTest = readmatrix('BrakingTest.txt');
AccelTest = readmatrix('SecondAccelTest.txt');
TurnTest = readmatrix('LeftTurnFollowedByRightTurn.txt');


figure(1)
plot(BrakeTest(:,1))
xlabel('Indicies')
ylabel('Acceleration in X direction')
title('Braking Test')

figure(2)
plot(AccelTest(:,3))
xlabel('Indicies')
ylabel('Acceleration in X direction')
title('Accel Test')

figure(3)
plot(TurnTest(:,3),TurnTest(:,1))
hold on 

xlabel('Indicies')
ylabel('Acceleration in Z direction')
title('Turn Test')
legend('Forward and Back', 'Left to Right')
