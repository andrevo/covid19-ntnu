function data = prepare_data(datafile)
% Prepare data
load(datafile);
M = max(indices);
n = length(indices);

data.S_mat = zeros(n,M);
data.I_mat = zeros(n,M);
data.H_mat = zeros(n,M);
data.R_mat = zeros(n,M);
data.D_mat = zeros(n,M);

j = 1;
for i=1:n
    % Start index
    start_index = sum(indices(1:i-1)) + 1;
    % End index
    end_index = sum(indices(1:i));
    
    data.S_mat(i,1:indices(i)) = S(start_index:end_index);
    data.S_mat(i,indices(i)+1:end) = double(S(end_index))*ones(1,length(indices(i)+1:M));
    
    data.I_mat(i,1:indices(i)) = I(start_index:end_index);
    data.I_mat(i,indices(i)+1:end) = double(I(end_index))*ones(1,length(indices(i)+1:M));
    
    data.H_mat(i,1:indices(i)) = H(start_index:end_index);
    data.H_mat(i,indices(i)+1:end) = double(H(end_index))*ones(1,length(indices(i)+1:M));
    
    data.R_mat(i,1:indices(i)) = R(start_index:end_index);
    data.R_mat(i,indices(i)+1:end) = double(R(end_index))*ones(1,length(indices(i)+1:M));
    
    data.D_mat(i,1:indices(i)) = D(start_index:end_index);
    data.D_mat(i,indices(i)+1:end) = double(D(end_index))*ones(1,length(indices(i)+1:M));
end

% Then add mean trajectories
data.S_mean = mean(data.S_mat);
data.I_mean = mean(data.I_mat);
data.H_mean = mean(data.H_mat);
data.R_mean = mean(data.R_mat);
data.D_mean = mean(data.D_mat);
end

