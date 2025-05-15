close all;
clear;

%% 输入折射率
% n_SFG = 1.34;
% n_vis = 1.34;
% n_IR = 1.4;

n_SFG = 1.4727;
n_vis = 1.4727;
n_IR = 1.47;


%% 基本实验参数
vis_angle_degree = 45; % 可见入射角
ir_angle_degree = 55; % 红外入射角
vis_wavelength = 532.1; % 可见波长
ir_wavenumber = 2900; % 红外波数

%% 中间参数
% 红外波长
ir_wavelength = 1e7 ./ ir_wavenumber;
sfg_wavelength = 1./(1./vis_wavelength + 1./ir_wavelength);

% 入射反射角的弧度
vis_angle_rad = deg2rad(vis_angle_degree);
ir_angle_rad = deg2rad(ir_angle_degree);
sfg_angle_rad = asin(sfg_wavelength .* (sin(vis_angle_rad)./vis_wavelength +  sin(ir_angle_rad)./ir_wavelength));

% 折射率
n_air = 1; % 空气折射率
n_quartz_vis = calculate_quartz_refractive_index(vis_wavelength); % 可见光折射率
n_quartz_ir = calculate_quartz_refractive_index(ir_wavelength); % 红外折射率
n_quartz_sfg = calculate_quartz_refractive_index(sfg_wavelength); % SFG折射率

% 折射角
vis_ref_angle_rad = calculate_refraction_angle(vis_angle_rad, n_air, n_quartz_vis); % 可见光折射角
ir_ref_angle_rad = calculate_refraction_angle(ir_angle_rad, n_air, n_quartz_ir); % 红外折射角
sfg_ref_angle_rad = calculate_refraction_angle(sfg_angle_rad, n_air, n_quartz_sfg); % SFG折射角


%% 计算菲涅尔
SFGLxx = fresnel(n_air, n_SFG, sfg_angle_rad, sfg_ref_angle_rad, 'xx');
SFGLyy = fresnel(n_air, n_SFG, sfg_angle_rad, sfg_ref_angle_rad, 'yy');
SFGLzz = fresnel(n_air, n_SFG, sfg_angle_rad, sfg_ref_angle_rad, 'zz');
VISLxx = fresnel(n_air, n_vis, vis_angle_rad, vis_ref_angle_rad, 'xx');
VISLyy = fresnel(n_air, n_vis, vis_angle_rad, vis_ref_angle_rad, 'yy');
VISLzz = fresnel(n_air, n_vis, vis_angle_rad, vis_ref_angle_rad, 'zz');
IRLxx = fresnel(n_air, n_IR, ir_angle_rad, ir_ref_angle_rad, 'xx');
IRLyy = fresnel(n_air, n_IR, ir_angle_rad, ir_ref_angle_rad, 'yy');
IRLzz = fresnel(n_air, n_IR, ir_angle_rad, ir_ref_angle_rad, 'zz');

%% SSP
YYZ_local_factor = SFGLyy .*VISLyy .*IRLzz .*sin(ir_angle_rad)

%% PPP
ZXX_local_factor = SFGLzz .* VISLxx .* IRLxx .* sin(sfg_angle_rad) .* cos(vis_angle_rad) .* cos(ir_angle_rad)
XXZ_local_factor = SFGLxx .* VISLxx .* IRLzz .* cos(sfg_angle_rad) .* cos(vis_angle_rad) .* sin(ir_angle_rad)
XZX_local_factor = SFGLxx .* VISLzz .* IRLxx .* cos(sfg_angle_rad) .* sin(vis_angle_rad) .* cos(ir_angle_rad)
ZZZ_local_factor = SFGLzz .* VISLzz .* IRLzz .* sin(sfg_angle_rad) .* sin(vis_angle_rad) .* sin(ir_angle_rad)

%% SPS
YZY_local_factor = SFGLyy .*VISLzz .*IRLyy .*sin(vis_angle_rad)

%% PSS
ZYY_local_factor = SFGLzz .*VISLyy .*IRLyy .*sin(sfg_angle_rad)

%% PSP
ZYX_local_factor = SFGLzz.*VISLyy.*IRLxx.*sin(sfg_angle_rad).*cos(ir_angle_rad)
XYZ_local_factor = SFGLxx.*VISLyy.*IRLzz.*cos(sfg_angle_rad).*sin(ir_angle_rad)

%% SPP
YZX = SFGLyy.*VISLzz.*IRLxx.*sin(vis_angle_rad).*cos(ir_angle_rad)
YXZ = SFGLyy.*VISLxx.*IRLzz.*vos(vis_angle_rad).*sin(ir_angle_rad)

%% PPS
ZXY = SFGLzz.*VISLxx.*IRLyy.*sin(sfg_angle_rad).*cos(vis_angle_rad)
XZY = SFGLxx.*VISLzz.*IRLyy.*cos(sfg_angle_rad).*sin(vis_angle_rad)

%% 各项计算函数
% 计算折射率的函数
function n = calculate_quartz_refractive_index(wavelength)
    wavelength_um = wavelength ./ 1000;
    n_squared = 1.28604141 + 1.07044083 .* wavelength_um.^2 ./ (wavelength_um.^2 - 0.0100585997) + 1.10202242 .* wavelength_um.^2 ./ (wavelength_um.^2 - 100);
    n = sqrt(n_squared);
end


% 计算折射角的函数
function gamma = calculate_refraction_angle(incident_angle, n1, n2)
    gamma = asin(n1 .* sin(incident_angle) ./ n2);
end

% 界面菲涅耳因子计算
function fresnel_result = fresnel(n1, n2, beta, gamma, polarization)

    % HXH Thesis
    % n_prime = sqrt((n1.^2 + n2.^2 + 4)./(2 .* (n1.^-2 + n2.^-2 + 1))); 
    % Consistency paper
    n_prime = sqrt((n2.^2 .*( n2.^2 + 5))./(4 .* n2.^2 + 2));

    if polarization == 'xx'
        % L_xx = ( 2 * n1 * cos(gamma)) / (n1 * cos(gamma) + n2 * cos(beta))
        numerator = 2 .* n1 .* cos(gamma);
        denominator = n1 .* cos(gamma) + n2 .* cos(beta);
        fresnel_result =  numerator ./ denominator;
    elseif polarization == 'yy'
        % L_yy = ( 2 * n1 * cos(beta)) / (n1 * cos(beta) + n2 * cos(gamma))
        numerator = 2 .* n1 .* cos(beta);
        denominator = n1 .* cos(beta) + n2 .* cos(gamma);
        fresnel_result =  numerator ./ denominator;
    elseif polarization == 'zz'
        % L_xx = ( 2 * n2 * cos(beta)) / (n1 * cos(gamma) + n2 *
        % cos(beta)) * (n1 / n') ^ 2
        numerator = 2 .* n2 .* cos(beta);
        denominator = n1 .* cos(gamma) + n2 .* cos(beta);
        fresnel_result =  numerator ./ denominator .* (n1 ./ n_prime) .^2;
    end

end


