% 设置工作目录为脚本所在目录
scriptDir = fileparts(mfilename('fullpath'));
cd(scriptDir);

% 获取用户输入文件名
inputFile = input('请输入要处理的CSV文件名(如testdata.csv): ', 's');

% 检查输入文件是否存在
if ~isfile(inputFile)
    error(['输入文件 ' inputFile ' 不存在']);
end

% 生成输出文件名
[filepath, name, ext] = fileparts(inputFile);
outputFile = [name '-sparkremoved' ext];

% 读取CSV文件
data = readmatrix(inputFile);
wavelength = data(:,1);
intensity = data(:,2);
plot(wavelength,intensity);
hold on;


% 使用中位数绝对偏差(MAD)检测异常值
medianVal = median(intensity);
mad = median(abs(intensity - medianVal));
threshold = medianVal + 3 * 1.4826 * mad; % 3σ阈值

% 标记异常值
isOutlier = intensity > threshold;

% 替换异常值为周围数据的线性插值
x = 1:length(intensity);
intensity(isOutlier) = interp1(x(~isOutlier), intensity(~isOutlier), x(isOutlier), 'linear');

plot(wavelength,intensity);

% 保存处理后的数据
processedData = [wavelength, intensity];
writematrix(processedData, outputFile);

disp(['Successfully processed and saved to: ' outputFile]);
