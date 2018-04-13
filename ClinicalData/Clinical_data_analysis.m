%% Data extraction

time = load('Time_data2018-03-22 17-14.dat');
stress = load('Stress_data2018-03-22 17-14.dat');
score = load('Score_data2018-03-22 17-14.dat');
righth = load('Right_data2018-03-22 17-14.dat');
lefth = load('Left_data2018-03-22 17-14.dat');
pot = load('Pot_data2018-03-22 17-14.dat');
lives = load('Lives_data2018-03-22 17-14.dat');

%% Data analysis

pot_mean = 709;

score_diff = [0;diff(score)];
lives_diff = [0;diff(lives)];
righth_diff = [0;diff(righth)];
lefth_diff = [0;diff(righth)];
pot_side = 2*(pot>pot_mean)-1;

Performance = score_diff+50*lives_diff;

Preference = sum((Performance).*pot_side);
Performance_cleaned = Performance(Performance~=0,:);
Pot_cleaned = pot(Performance~=0,:);
Stress_cleaned = stress(Performance~=0,:)./(1+lives(Performance~=0,:));

correlation_perf_pot = cov(Performance_cleaned,Pot_cleaned)/sqrt(var(Performance_cleaned)*var(Pot_cleaned));
correlation_perf_stress = cov(Performance_cleaned,Stress_cleaned)/sqrt(var(Performance_cleaned)*var(Stress_cleaned));

regression_perf_pot = pinv(Pot_cleaned)*Performance_cleaned;
regression_perf_stress = pinv(Stress_cleaned)*Performance_cleaned;

Righth_cleaned2 = righth_diff(righth_diff~=0,:);
Lefth_cleaned2 = lefth_diff(lefth_diff~=0,:);
Stress_cleaned2r = stress(righth_diff~=0,:);
Stress_cleaned2l = stress(lefth_diff~=0,:);

correlation_righth_stress = cov(Righth_cleaned2,Stress_cleaned2r)/sqrt(var(Righth_cleaned2)*var(Stress_cleaned2r));
correlation_lefth_stress = cov(Lefth_cleaned2,Stress_cleaned2l)/sqrt(var(Lefth_cleaned2)*var(Stress_cleaned2l));

regression_righth_stress = pinv(Stress_cleaned2r)*Righth_cleaned2;
regression_lefth_stress = pinv(Stress_cleaned2l)*Lefth_cleaned2;


%% Data representation

subplot(2,2,1)
plot(Pot_cleaned,Performance_cleaned,'o',Pot_cleaned,regression_perf_pot*Pot_cleaned)
xlabel('Potentiometer value (°)')
ylabel('Performance')
title('Correlation between potentiometer value and performance')
axis([-inf inf -200 200])
subplot(2,2,2)
plot(Stress_cleaned,Performance_cleaned,'o',Stress_cleaned,regression_perf_stress*Stress_cleaned)
xlabel('Stress value')
ylabel('Performance')
axis([-inf inf -200 200])
title('Correlation between stress value and performance')
subplot(2,2,3)
plot(Stress_cleaned2r,Righth_cleaned2,'o',Stress_cleaned2r,regression_righth_stress*Stress_cleaned2r)
xlabel('Stress value')
ylabel('Propensity to use right hand')
title('Correlation between right hand usage and stress')
axis([-inf inf -2 2])
subplot(2,2,4)
plot(Stress_cleaned2l,Lefth_cleaned2,'o',Stress_cleaned2l,regression_lefth_stress*Stress_cleaned2l)
xlabel('Stress value')
ylabel('Propensity to use left hand')
title('Correlation between left hand usage and stress')
axis([-inf inf -2 2])






