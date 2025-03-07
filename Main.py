import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                            QVBoxLayout, QGridLayout, QLabel, QLineEdit, QFrame)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import math

class SFGCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle('SFG Calculation Tool')
        self.setGeometry(100, 100, 800, 600)
        
        # Create main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create and add tabs
        self.quartz_tab = QWidget()
        self.focus_tab = QWidget() 
        self.intensity_tab = QWidget()
        
        self.tabs.addTab(self.quartz_tab, "石英计算")
        self.tabs.addTab(self.focus_tab, "聚焦计算")
        self.tabs.addTab(self.intensity_tab, "强度与信噪比计算")
        
        # Set up basic layouts for each tab
        self.setup_quartz_tab()
        self.setup_focus_tab()
        self.setup_intensity_tab()
        
    def calculate_sfg_angle(self):
        """计算SFG反射角度"""
        # TODO: 实现具体计算逻辑
        pass
        
    def calculate_sfg_wavelength(self):
        """计算SFG波长"""
        # TODO: 实现具体计算逻辑
        pass
        
    def calculate_refraction_angle(self, incident_angle, n1, n2):
        """计算折射角度"""
        return math.degrees(math.asin(n1 * math.sin(math.radians(incident_angle)) / n2))
        
    def calculate_fresnel(self, n1, n2, theta1, theta2, polarization):
        """计算菲涅耳因子"""
        theta1_rad = math.radians(theta1)
        theta2_rad = math.radians(theta2)
        
        if polarization == 'xx':
            # Lxx = (2 * n1 * cosθ2) / (n2 * cosθ1 + n1 * cosθ2)
            numerator = 2 * n1 * math.cos(theta2_rad)
            denominator = n2 * math.cos(theta1_rad) + n1 * math.cos(theta2_rad)
            return numerator / denominator
        elif polarization == 'yy':
            # Lyy = (2 * n1 * cosθ1) / (n1 * cosθ2 + n2 * cosθ1)
            numerator = 2 * n1 * math.cos(theta1_rad)
            denominator = n1 * math.cos(theta2_rad) + n2 * math.cos(theta1_rad)
            return numerator / denominator
        else:
            return 0.0
        
    def update_sfg_results(self):
        """当输入值变化时更新计算结果"""
        try:
            # 获取并验证输入值
            vis_angle = float(self.vis_angle_input.text())
            ir_angle = float(self.ir_angle_input.text())
            vis_wavelength = float(self.vis_wavelength_input.text())
            ir_wavenumber = float(self.ir_wavenumber_input.text())
            
            # 验证角度范围
            if not (0 <= vis_angle <= 90) or not (0 <= ir_angle <= 90):
                raise ValueError("入射角度必须在0到90度之间")
                
            # 计算SFG波长
            sfg_wavelength = 1e7 / (1e7/vis_wavelength - ir_wavenumber)
            
            # 计算SFG反射角度（使用更精确的公式）
            n_air = 1.0  # 空气折射率
            n_quartz = 1.55  # 石英折射率（近似值）
            
            # 计算可见光和红外光的折射角度
            vis_ref_angle = self.calculate_refraction_angle(vis_angle, n_air, n_quartz)
            ir_ref_angle = self.calculate_refraction_angle(ir_angle, n_air, n_quartz)
            
            # 计算SFG反射角度
            sfg_angle = (vis_ref_angle + ir_ref_angle) / 2
            
            # 更新输出框
            self.sfg_wavelength_output.setText(f"{sfg_wavelength:.2f} nm")
            self.sfg_angle_output.setText(f"{sfg_angle:.2f} °")
            
            # 计算并更新红外波长
            ir_wavelength = 1e7 / ir_wavenumber
            self.ir_wavelength_output.setText(f"{ir_wavelength:.2f} nm")
            
            # 更新折射率和折射角度
            self.vis_refractive_index_output.setText(f"{n_quartz:.3f}")
            self.ir_refractive_index_output.setText(f"{n_quartz:.3f}")
            self.sfg_refractive_index_output.setText(f"{n_quartz:.3f}")
            
            self.vis_refraction_angle_output.setText(f"{vis_ref_angle:.2f} °")
            self.ir_refraction_angle_output.setText(f"{ir_ref_angle:.2f} °")
            self.sfg_refraction_angle_output.setText(f"{sfg_angle:.2f} °")
            
            # 计算并更新相干长度
            delta_n = abs(n_quartz - n_air)
            coherence_length = (sfg_wavelength * 1e-3) / (2 * delta_n)  # 转换为μm
            self.coherence_length_output.setText(f"{coherence_length:.2f}")
            
            # 计算并更新菲涅耳因子
            # SFG
            self.fresnel_xx_sfg.setText(f"{self.calculate_fresnel(n_air, n_quartz, sfg_angle, sfg_angle, 'xx'):.3f}")
            self.fresnel_yy_sfg.setText(f"{self.calculate_fresnel(n_air, n_quartz, sfg_angle, sfg_angle, 'yy'):.3f}")
            
            # VIS
            self.fresnel_xx_vis.setText(f"{self.calculate_fresnel(n_air, n_quartz, vis_angle, vis_ref_angle, 'xx'):.3f}")
            self.fresnel_yy_vis.setText(f"{self.calculate_fresnel(n_air, n_quartz, vis_angle, vis_ref_angle, 'yy'):.3f}")
            
            # IR
            self.fresnel_xx_ir.setText(f"{self.calculate_fresnel(n_air, n_quartz, ir_angle, ir_ref_angle, 'xx'):.3f}")
            self.fresnel_yy_ir.setText(f"{self.calculate_fresnel(n_air, n_quartz, ir_angle, ir_ref_angle, 'yy'):.3f}")
            
        except ValueError:
            # 输入无效时清空输出
            self.sfg_wavelength_output.clear()
            self.sfg_angle_output.clear()
            self.ir_wavelength_output.clear()
        
    def calculate_focus(self):
        """计算光束直径和瑞利长度"""
        try:
            # 获取输入值
            wavelength = float(self.laser_wavelength_input.text())  # nm
            focal_length = float(self.lens_focal_input.text())  # mm
            
            # 假设光束质量因子M²=1，初始光束直径1mm
            M2 = 1.0
            initial_beam_diameter = 1.0  # mm
            
            # 计算光束直径
            beam_diameter = (4 * M2 * wavelength * 1e-6 * focal_length) / \
                           (math.pi * initial_beam_diameter)
            
            # 计算瑞利长度
            rayleigh_length = (math.pi * (beam_diameter/2)**2) / (wavelength * 1e-6)
            
            # 更新输出框
            self.beam_diameter_output.setText(f"{beam_diameter:.2f}")
            self.rayleigh_length_output.setText(f"{rayleigh_length:.2f}")
            
        except ValueError:
            # 输入无效时清空输出
            self.beam_diameter_output.clear()
            self.rayleigh_length_output.clear()

    def setup_focus_tab(self):
        """设置聚焦计算选项卡"""
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 添加输入控件
        input_layout.addWidget(QLabel("激光波长 (nm):"), 0, 0)
        self.laser_wavelength_input = QLineEdit()
        self.laser_wavelength_input.setText("532")
        self.laser_wavelength_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.laser_wavelength_input, 0, 1)
        
        input_layout.addWidget(QLabel("透镜焦距 (mm):"), 1, 0)
        self.lens_focal_input = QLineEdit()
        self.lens_focal_input.setText("100")
        self.lens_focal_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.lens_focal_input, 1, 1)
        
        input_group.setLayout(input_layout)
        
        # 添加输入标题
        input_title = QLabel("输入参数")
        input_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(input_title)
        main_layout.addSpacing(10)
        main_layout.addWidget(input_group)
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #95a5a6;")
        separator.setFixedHeight(2)
        main_layout.addSpacing(15)
        main_layout.addWidget(separator)
        main_layout.addSpacing(15)
        
        # 添加输出标题
        output_title = QLabel("输出结果")
        output_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(output_title)
        main_layout.addSpacing(10)
        
        # 创建输出区域
        output_group = QWidget()
        output_layout = QGridLayout()
        
        # 添加输出控件
        output_layout.addWidget(QLabel("光束直径 (mm):"), 0, 0)
        self.beam_diameter_output = QLineEdit()
        self.beam_diameter_output.setReadOnly(True)
        output_layout.addWidget(self.beam_diameter_output, 0, 1)
        
        output_layout.addWidget(QLabel("瑞利长度 (mm):"), 1, 0)
        self.rayleigh_length_output = QLineEdit()
        self.rayleigh_length_output.setReadOnly(True)
        output_layout.addWidget(self.rayleigh_length_output, 1, 1)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 调整布局间距
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setVerticalSpacing(15)
        output_layout.setVerticalSpacing(15)
        
        # 设置输入框样式
        for widget in input_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
            
        # 设置输出框样式
        for widget in output_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #ecf0f1;")
        
        self.focus_tab.setLayout(main_layout)

    def calculate_intensity(self):
        """计算信号强度、噪声水平和信噪比"""
        try:
            # 获取输入值
            power = float(self.laser_power_input.text())
            gain = float(self.detector_gain_input.text())
            time = float(self.integration_time_input.text())
            
            # 计算信号强度
            signal = power * gain * time
            
            # 计算噪声水平（假设与信号强度的平方根成正比）
            noise = math.sqrt(signal)
            
            # 计算信噪比
            snr = 10 * math.log10(signal / noise) if noise > 0 else 0
            
            # 更新输出框
            self.signal_intensity_output.setText(f"{signal:.2f}")
            self.noise_level_output.setText(f"{noise:.2f}")
            self.snr_output.setText(f"{snr:.2f}")
            
        except ValueError:
            # 输入无效时清空输出
            self.signal_intensity_output.clear()
            self.noise_level_output.clear()
            self.snr_output.clear()

    def setup_intensity_tab(self):
        """设置强度与信噪比计算选项卡"""
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 添加输入控件
        input_layout.addWidget(QLabel("激光功率 (mW):"), 0, 0)
        self.laser_power_input = QLineEdit()
        self.laser_power_input.setText("100")
        self.laser_power_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.laser_power_input, 0, 1)
        
        input_layout.addWidget(QLabel("探测器增益:"), 1, 0)
        self.detector_gain_input = QLineEdit()
        self.detector_gain_input.setText("1.0")
        self.detector_gain_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.detector_gain_input, 1, 1)
        
        input_layout.addWidget(QLabel("积分时间 (s):"), 2, 0)
        self.integration_time_input = QLineEdit()
        self.integration_time_input.setText("1.0")
        self.integration_time_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.integration_time_input, 2, 1)
        
        input_group.setLayout(input_layout)
        
        # 添加输入标题
        input_title = QLabel("输入参数")
        input_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(input_title)
        main_layout.addSpacing(10)
        main_layout.addWidget(input_group)
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #95a5a6;")
        separator.setFixedHeight(2)
        main_layout.addSpacing(15)
        main_layout.addWidget(separator)
        main_layout.addSpacing(15)
        
        # 添加输出标题
        output_title = QLabel("输出结果")
        output_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(output_title)
        main_layout.addSpacing(10)
        
        # 创建输出区域
        output_group = QWidget()
        output_layout = QGridLayout()
        
        # 添加输出控件
        output_layout.addWidget(QLabel("信号强度 (a.u.):"), 0, 0)
        self.signal_intensity_output = QLineEdit()
        self.signal_intensity_output.setReadOnly(True)
        output_layout.addWidget(self.signal_intensity_output, 0, 1)
        
        output_layout.addWidget(QLabel("噪声水平 (a.u.):"), 1, 0)
        self.noise_level_output = QLineEdit()
        self.noise_level_output.setReadOnly(True)
        output_layout.addWidget(self.noise_level_output, 1, 1)
        
        output_layout.addWidget(QLabel("信噪比 (dB):"), 2, 0)
        self.snr_output = QLineEdit()
        self.snr_output.setReadOnly(True)
        output_layout.addWidget(self.snr_output, 2, 1)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 调整布局间距
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setVerticalSpacing(15)
        output_layout.setVerticalSpacing(15)
        
        # 设置输入框样式
        for widget in input_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
            
        # 设置输出框样式
        for widget in output_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #ecf0f1;")
        
        self.intensity_tab.setLayout(main_layout)

    def setup_quartz_tab(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 输入角度
        input_layout.addWidget(QLabel("可见光入射角度 (°):"), 0, 0)
        self.vis_angle_input = QLineEdit()
        self.vis_angle_input.setText("45")
        self.vis_angle_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.vis_angle_input, 0, 1)
        
        input_layout.addWidget(QLabel("红外光入射角度 (°):"), 0, 2)
        self.ir_angle_input = QLineEdit()
        self.ir_angle_input.setText("55")
        self.ir_angle_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.ir_angle_input, 0, 3)
        
        # 输入波长/波数
        input_layout.addWidget(QLabel("可见光波长 (nm):"), 1, 0)
        self.vis_wavelength_input = QLineEdit()
        self.vis_wavelength_input.setText("532")
        self.vis_wavelength_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.vis_wavelength_input, 1, 1)
        
        input_layout.addWidget(QLabel("红外光波数 (cm⁻¹):"), 1, 2)
        self.ir_wavenumber_input = QLineEdit()
        self.ir_wavenumber_input.setText("3000")
        self.ir_wavenumber_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.ir_wavenumber_input, 1, 3)
        
        input_group.setLayout(input_layout)
        
        # 添加输入标题
        input_title = QLabel("输入参数")
        input_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(input_title)
        main_layout.addSpacing(10)
        main_layout.addWidget(input_group)
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #95a5a6;")
        separator.setFixedHeight(2)
        main_layout.addSpacing(15)
        main_layout.addWidget(separator)
        main_layout.addSpacing(15)
        
        # 添加输出标题
        output_title = QLabel("输出结果")
        output_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; padding: 5px;")
        main_layout.addWidget(output_title)
        main_layout.addSpacing(10)
        
        # 创建输出区域
        output_group = QWidget()
        output_layout = QGridLayout()
        
        # 第一部分输出
        output1_group = QWidget()
        output1_layout = QGridLayout()
        output1_layout.addWidget(QLabel("SFG反射角度:"), 0, 0)
        self.sfg_angle_output = QLineEdit()
        self.sfg_angle_output.setReadOnly(True)
        output1_layout.addWidget(self.sfg_angle_output, 0, 1)
        
        output1_layout.addWidget(QLabel("SFG波长:"), 0, 2)
        self.sfg_wavelength_output = QLineEdit()
        self.sfg_wavelength_output.setReadOnly(True)
        output1_layout.addWidget(self.sfg_wavelength_output, 0, 3)

        output1_layout.addWidget(QLabel("红外波长:"), 1, 0)
        self.ir_wavelength_output = QLineEdit()
        self.ir_wavelength_output.setReadOnly(True)
        output1_layout.addWidget(self.ir_wavelength_output, 1, 1)

        output1_group.setLayout(output1_layout)
        output_layout.addWidget(output1_group, 0, 0, 1, 2)
        
        # 第二部分输出
        output2_group = QWidget()
        output2_layout = QGridLayout()

        # 可见光的折射率和折射角度
        output2_layout.addWidget(QLabel("可见光折射率:"), 0, 0)
        self.vis_refractive_index_output = QLineEdit()
        self.vis_refractive_index_output.setReadOnly(True)
        output2_layout.addWidget(self.vis_refractive_index_output, 0, 1)
        
        output2_layout.addWidget(QLabel("可见光折射角度:"), 1, 0)
        self.vis_refraction_angle_output = QLineEdit()
        self.vis_refraction_angle_output.setReadOnly(True)
        output2_layout.addWidget(self.vis_refraction_angle_output, 1, 1)
        
        # 红外光的折射率和折射角度
        output2_layout.addWidget(QLabel("红外光折射率:"), 0, 2)
        self.ir_refractive_index_output = QLineEdit()
        self.ir_refractive_index_output.setReadOnly(True)
        output2_layout.addWidget(self.ir_refractive_index_output, 0, 3)
        
        output2_layout.addWidget(QLabel("红外光折射角度:"), 1, 2)
        self.ir_refraction_angle_output = QLineEdit()
        self.ir_refraction_angle_output.setReadOnly(True)
        output2_layout.addWidget(self.ir_refraction_angle_output, 1, 3)

        # SFG的折射率和折射角度
        output2_layout.addWidget(QLabel("SFG折射率:"), 0, 4)
        self.sfg_refractive_index_output = QLineEdit()
        self.sfg_refractive_index_output.setReadOnly(True)
        output2_layout.addWidget(self.sfg_refractive_index_output, 0, 5)
        
        output2_layout.addWidget(QLabel("SFG折射角度:"), 1, 4)
        self.sfg_refraction_angle_output = QLineEdit()
        self.sfg_refraction_angle_output.setReadOnly(True)
        output2_layout.addWidget(self.sfg_refraction_angle_output, 1, 5)

        output2_group.setLayout(output2_layout)
        output_layout.addWidget(output2_group, 1, 0, 1, 2)
        
        # 第三部分输出:相干长度
        output3_group = QWidget()
        output3_layout = QGridLayout()
        output3_layout.addWidget(QLabel("相干长度 (μm):"), 0, 0)
        self.coherence_length_output = QLineEdit()
        self.coherence_length_output.setReadOnly(True)
        output3_layout.addWidget(self.coherence_length_output, 0, 1)

        output3_group.setLayout(output3_layout)
        output_layout.addWidget(output3_group, 2, 0, 1, 2)
        
        # 第四部分输出:菲涅耳因子
        fresnel_group = QWidget()
        fresnel_layout = QGridLayout()
        
        # SFG
        fresnel_layout.addWidget(QLabel("LxxSFG:"), 0, 0)
        self.fresnel_xx_sfg = QLineEdit()
        self.fresnel_xx_sfg.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_xx_sfg, 0, 1)
        
        fresnel_layout.addWidget(QLabel("LyySFG:"), 1, 0)
        self.fresnel_yy_sfg = QLineEdit()
        self.fresnel_yy_sfg.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_yy_sfg, 1, 1)
        
        # VIS
        fresnel_layout.addWidget(QLabel("LxxVIS:"), 0, 2)
        self.fresnel_xx_vis = QLineEdit()
        self.fresnel_xx_vis.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_xx_vis, 0, 3)
        
        fresnel_layout.addWidget(QLabel("LyyVIS:"), 1, 2)
        self.fresnel_yy_vis = QLineEdit()
        self.fresnel_yy_vis.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_yy_vis, 1, 3)
        
        # IR
        fresnel_layout.addWidget(QLabel("LxxIR:"), 0, 4)
        self.fresnel_xx_ir = QLineEdit()
        self.fresnel_xx_ir.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_xx_ir, 0, 5)
        
        fresnel_layout.addWidget(QLabel("LyyIR:"), 1, 4)
        self.fresnel_yy_ir = QLineEdit()
        self.fresnel_yy_ir.setReadOnly(True)
        fresnel_layout.addWidget(self.fresnel_yy_ir, 1, 5)
        
        fresnel_group.setLayout(fresnel_layout)
        output_layout.addWidget(fresnel_group, 3, 0, 1, 2)
        
        # 第五部分输出:二阶极化率
        output5_group = QWidget()
        output5_layout = QGridLayout()

        output5_layout.addWidget(QLabel("χ²(SSP):"), 0, 0)
        self.chi2_ssp_output = QLineEdit()
        self.chi2_ssp_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_ssp_output, 0, 1)
        
        output5_layout.addWidget(QLabel("χ²(SPS):"), 0, 2)
        self.chi2_sps_output = QLineEdit()
        self.chi2_sps_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_sps_output, 0, 3)
        
        output5_layout.addWidget(QLabel("χ²(PSS):"), 0, 4)
        self.chi2_pss_output = QLineEdit()
        self.chi2_pss_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_pss_output, 0, 5)
        
        output5_layout.addWidget(QLabel("χ²(PPP):"), 0, 6)
        self.chi2_ppp_output = QLineEdit()
        self.chi2_ppp_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_ppp_output, 0, 7)
        
        # 二阶极化率的平方
        output5_layout.addWidget(QLabel("|χ²(SSP)|²:"), 1, 0)
        self.chi2_ssp_sq_output = QLineEdit()
        self.chi2_ssp_sq_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_ssp_sq_output, 1, 1)
        
        output5_layout.addWidget(QLabel("|χ²(SPS)|²:"), 1, 2)
        self.chi2_sps_sq_output = QLineEdit()
        self.chi2_sps_sq_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_sps_sq_output, 1, 3)
        
        output5_layout.addWidget(QLabel("|χ²(PSS)|²:"), 1, 4)
        self.chi2_pss_sq_output = QLineEdit()
        self.chi2_pss_sq_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_pss_sq_output, 1, 5)
        
        output5_layout.addWidget(QLabel("|χ²(PPP)|²:"), 1, 6)
        self.chi2_ppp_sq_output = QLineEdit()
        self.chi2_ppp_sq_output.setReadOnly(True)
        output5_layout.addWidget(self.chi2_ppp_sq_output, 1, 7)
        
        output5_group.setLayout(output5_layout)
        output_layout.addWidget(output5_group, 4, 0, 1, 2)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 调整布局间距
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 增加输入框之间的垂直间距
        input_layout.setVerticalSpacing(15)
        
        # 增加输出框之间的间距
        output1_layout.setVerticalSpacing(10)
        output2_layout.setVerticalSpacing(10)
        output3_layout.setVerticalSpacing(10)
        output5_layout.setVerticalSpacing(10)
        
        # 增加组之间的间距
        main_layout.insertSpacing(2, 20)  # 输入组和分割线之间
        main_layout.insertSpacing(4, 20)  # 分割线和输出组之间
        
        # 设置输入框样式
        for widget in input_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
            
        # 设置输出框样式
        for widget in output_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #ecf0f1;")
        
        self.quartz_tab.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SFGCalculator()
    window.show()
    sys.exit(app.exec())
