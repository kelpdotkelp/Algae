clear all
close all
clc

WRITE_TO_CSV = true;
pos_range = [1, 10] %[inclusive, inclusive]

%Output directory for .csv file
outputDir = "C:\Users\Noah\Desktop\";
%Name of .csv file - don't include extension
outputName = "dielectric_1.5_inch_0.012_step";

%Antenna Radius (the tip)
antRad = 12e-2;
%The safetyMargin we are going to use to make sure the target doesn't hit
%the antennas. 
safetyMargin = 2e-2;

%maximum radius of the target.
targetRad = 0.020; %smallest dielectric

%What step size you want to use. 
stepSize = 1.2e-2;

%Calculate the diagonal distance at the corner. 
diagonalDist = antRad-safetyMargin-targetRad;
%and calculate the x/y max/min distance.
halfEdgeLength = diagonalDist/sqrt(2);

x = -halfEdgeLength:stepSize:halfEdgeLength;
y = x;
[X, Y] = meshgrid(x,y);

positionGrid = ones(size(X));
%positionGrid(sqrt(X.^2 + Y.^2)>=diagonalDist) = 0;

%create a figure that scatter plots the important parameters. 
figure
scatter(X,Y);
title('Position Grid');
dTheta = 2*pi/24;
theta = 0:dTheta:(2*pi-dTheta);
txPos = [antRad*cos(theta); antRad*sin(theta)];
hold on
scatter(txPos(1,:),txPos(2,:),60,'rx')

%draw a circle of the larget target at the closest point to the antennas.
testTheta = 0:0.1:(2*pi-0.11);
targetCircle = [targetRad*cos(testTheta); targetRad*sin(testTheta)];
funnyCircle = targetCircle + [max(x) ;max(y)];
scatter(funnyCircle(1,:),funnyCircle(2,:),60,'kx');
legend('Positions','Antenna Positions','Approximate outline of max targ. pos.')

numTotalPositions = sum(sum(positionGrid))

%Save positions to a .csv
if WRITE_TO_CSV
    file = fopen(outputDir + outputName + ".csv", "w");
    pos_list = zeros(numTotalPositions, 2);
    pos_index = 1;
    
    for i=1:size(X, 1)
        for j=1:size(X,1)
            pos_list(pos_index,:) = [X(i, j) Y(i, j)];
            pos_index = pos_index + 1;
        end
    end

    %Convert to millimeters
    pos_list = pos_list * 1000;

    for i=pos_range(1):pos_range(2)
        fprintf(file, pos_list(i,1) + "," + Y(1,2) + "\n");
    end

    fclose(file);
end