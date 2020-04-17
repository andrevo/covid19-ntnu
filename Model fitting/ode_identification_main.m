clear
close all

dataVec = {'data_4','data_3','data_2','data_1','data_0'};
N = 200000;
modelType = 'SIR';

paramsMat = [];

for i = 1:length(dataVec)
    fileString = dataVec{i};
    data = prepare_data(fileString);
    titleText = fileString;
    plot_data(data,titleText);
    [params,modelFit,id_data] = param_identification(data,modelType,N);
    
    paramsMat(i,:) = params';
    % Compare fit to data
    figure
    compare(id_data,modelFit)
    title([fileString,', ',num2str(params')]); 
end

paramsMat



