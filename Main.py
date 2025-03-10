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
        
        # Initialize with default values
        self.update_sfg_results()
        self.calculate_focus()
        self.calculate_intensity()

    def calculate_refraction_angle(self, incident_angle, n1, n2):
        """计算折射角度"""
        return math.degrees(math.asin(n1 * math.sin(math.radians(incident_angle)) / n2))
        
    def calculate_fresnel(self, n1, n2, theta1, theta2, polarization):
        """计算菲涅耳因子"""
        theta1_rad = math.radians(theta1)
        theta2_rad = math.radians(theta2)
        
        cos_theta1 = math.cos(theta1_rad)
        cos_theta2 = math.cos(theta2_rad)
        
        if polarization == 'xx':
            # Lxx = (2 * cosθ2) / (cosθ2 + n2 * cosθ1)
            numerator = 2 * cos_theta2
            denominator = cos_theta2 + n2 * cos_theta1
            return numerator / denominator
        elif polarization == 'yy':
            # Lyy = (2 * cosθ1) / (cosθ1 + n2 * cosθ2)
            numerator = 2 * cos_theta1
            denominator = cos_theta1 + n2 * cos_theta2
            return numerator / denominator
        else:
            return 0.0
        
    def calculate_quartz_refractive_index(self, wavelength):
        """根据波长计算石英折射率"""
        # 将波长转换为微米
        wavelength_um = wavelength / 1000
        # 使用给定的Sellmeier方程计算折射率
        n_squared = 1.28604141 + \
                    1.07044083 * wavelength_um**2 / (wavelength_um**2 - 0.0100585997) + \
                    1.10202242 * wavelength_um**2 / (wavelength_um**2 - 100)
        return math.sqrt(n_squared)

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
            ir_wavelength = 1e7 / ir_wavenumber
            sfg_wavelength = 1/(1/vis_wavelength + 1/ir_wavelength)
            
            # 计算SFG反射角度（使用更精确的公式）
            n_air = 1.0  # 空气折射率
            # 计算各波长对应的石英折射率
            n_quartz_vis = self.calculate_quartz_refractive_index(vis_wavelength)
            n_quartz_ir = self.calculate_quartz_refractive_index(1e7 / ir_wavenumber)
            n_quartz_sfg = self.calculate_quartz_refractive_index(sfg_wavelength)
            
            # 计算可见光和红外光的折射角度
            vis_ref_angle = self.calculate_refraction_angle(vis_angle, n_air, n_quartz_vis)
            ir_ref_angle = self.calculate_refraction_angle(ir_angle, n_air, n_quartz_ir)
            
            # 计算SFG反射角度
            vis_angle_rad = math.radians(vis_angle)
            ir_angle_rad = math.radians(ir_angle)
            sfg_angle = math.degrees(math.asin(
                sfg_wavelength * (math.sin(vis_angle_rad)/vis_wavelength + 
                                math.sin(ir_angle_rad)/ir_wavelength)
            ))
            
            # 计算SFG折射角度
            sfg_ref_angle = self.calculate_refraction_angle(sfg_angle, n_air, n_quartz_sfg)
            
            # 更新输出框
            self.sfg_wavelength_output.setText(f"{sfg_wavelength:.2f} nm")
            self.sfg_angle_output.setText(f"{sfg_angle:.2f} °")
            
            # 计算并更新红外波长
            ir_wavelength = 1e7 / ir_wavenumber
            self.ir_wavelength_output.setText(f"{ir_wavelength:.2f} nm")
            
            # 更新折射率和折射角度
            self.vis_refractive_index_output.setText(f"{n_quartz_vis:.3f}")
            self.ir_refractive_index_output.setText(f"{n_quartz_ir:.3f}")
            self.sfg_refractive_index_output.setText(f"{n_quartz_sfg:.3f}")
            
            self.vis_refraction_angle_output.setText(f"{vis_ref_angle:.2f} °")
            self.ir_refraction_angle_output.setText(f"{ir_ref_angle:.2f} °")
            self.sfg_refraction_angle_output.setText(f"{sfg_ref_angle:.2f} °")
            
            # 计算并更新相干长度
            sfg_angle_rad = math.radians(sfg_angle)
            vis_angle_rad = math.radians(vis_angle)
            ir_angle_rad = math.radians(ir_angle)
            
            sfg_term = math.sqrt(n_quartz_sfg**2 - math.sin(sfg_angle_rad)**2) / sfg_wavelength
            vis_term = math.sqrt(n_quartz_vis**2 - math.sin(vis_angle_rad)**2) / vis_wavelength
            ir_term = math.sqrt(n_quartz_ir**2 - math.sin(ir_angle_rad)**2) / ir_wavelength
            
            coherence_length = 1 /((2 * math.pi * (sfg_term + vis_term) + ir_term))  # 单位为nm
            self.coherence_length_output.setText(f"{coherence_length:.2f}")
            
            # 计算并更新菲涅耳因子
            # SFG
            lxx_sfg = self.calculate_fresnel(n_air, n_quartz_sfg, sfg_angle, sfg_ref_angle, 'xx')
            lyy_sfg = self.calculate_fresnel(n_air, n_quartz_sfg, sfg_angle, sfg_ref_angle, 'yy')
            self.fresnel_xx_sfg.setText(f"{lxx_sfg:.3f}")
            self.fresnel_yy_sfg.setText(f"{lyy_sfg:.3f}")
            
            # VIS
            lxx_vis = self.calculate_fresnel(n_air, n_quartz_vis, vis_angle, vis_ref_angle, 'xx')
            lyy_vis = self.calculate_fresnel(n_air, n_quartz_vis, vis_angle, vis_ref_angle, 'yy')
            self.fresnel_xx_vis.setText(f"{lxx_vis:.3f}")
            self.fresnel_yy_vis.setText(f"{lyy_vis:.3f}")
            
            # IR
            lxx_ir = self.calculate_fresnel(n_air, n_quartz_ir, ir_angle, ir_ref_angle, 'xx')
            lyy_ir = self.calculate_fresnel(n_air, n_quartz_ir, ir_angle, ir_ref_angle, 'yy')
            self.fresnel_xx_ir.setText(f"{lxx_ir:.3f}")
            self.fresnel_yy_ir.setText(f"{lyy_ir:.3f}")

            # 计算二阶极化率
            # 将角度转换为弧度
            sfg_angle_rad = math.radians(sfg_angle)
            vis_angle_rad = math.radians(vis_angle)
            ir_angle_rad = math.radians(ir_angle)

            # SSP
            chi2_ssp = math.cos(ir_angle_rad) * lyy_sfg * lyy_vis * lxx_ir * coherence_length * 1e-9 * 1.6e-12
            self.chi2_ssp_output.setText(f"{chi2_ssp:.3e}")
            self.chi2_ssp_sq_output.setText(f"{abs(chi2_ssp)**2:.3e}")

            # PPP
            chi2_ppp = math.cos(sfg_angle_rad) * math.cos(vis_angle_rad) * math.cos(ir_angle_rad) * \
                      lxx_sfg * lxx_vis * lxx_ir * coherence_length * 1.6e-21
            self.chi2_ppp_output.setText(f"{chi2_ppp:.3e}")
            self.chi2_ppp_sq_output.setText(f"{abs(chi2_ppp)**2:.3e}")

            # SPS
            chi2_sps = math.cos(vis_angle_rad) * lyy_sfg * lxx_vis * lyy_ir * coherence_length * 1.6e-21
            self.chi2_sps_output.setText(f"{chi2_sps:.3e}")
            self.chi2_sps_sq_output.setText(f"{abs(chi2_sps)**2:.3e}")

            # PSS
            chi2_pss = math.cos(ir_angle_rad) * lxx_sfg * lyy_vis * lyy_ir * coherence_length * 1.6e-21
            self.chi2_pss_output.setText(f"{chi2_pss:.3e}")
            self.chi2_pss_sq_output.setText(f"{abs(chi2_pss)**2:.3e}")
            
        except ValueError:
            # 输入无效时清空输出
            self.sfg_wavelength_output.clear()
            self.sfg_angle_output.clear()
            self.ir_wavelength_output.clear()
        
    def calculate_focus(self):
        """计算可见光和红外光的焦点直径"""
        try:
            # 获取输入值并转换为浮点数
            vis_wavelength = float(self.Visible_wavelength_input.text())  # 可见波长 nm
            ir_wavelength = float(self.IR_wavelength_input.text())  # 红外波长 nm
            vis_spot_size = float(self.visible_size_input.text())  # 可见光斑直径 mm
            ir_spot_size = float(self.IR_size_input.text())  # 红外光斑直径 mm
            vis_focal = float(self.Visible_focal_input.text())  # 可见透镜焦距 mm
            ir_focal = float(self.IR_focal_input.text())  # 红外透镜焦距 mm

            # 计算可见光焦点直径 (μm)
            vis_focus_diameter = (4 * vis_focal * vis_wavelength * 1e-3) / (math.pi * vis_spot_size)
            
            # 计算红外光焦点直径 (μm)
            ir_focus_diameter = (4 * ir_focal * ir_wavelength * 1e-3) / (math.pi * ir_spot_size)

            # 计算可见光焦点深度 (mm)
            vis_focus_depth = (2 * math.pi * (vis_focus_diameter * 1e-3 / 2)**2) / (vis_wavelength * 1e-6)
            
            # 计算红外光焦点深度 (mm)
            ir_focus_depth = (2 * math.pi * (ir_focus_diameter * 1e-3 / 2)**2) / (ir_wavelength * 1e-6)

            # 计算可见光斑直径 (μm)
            vis_defocus = float(self.Visible_defocus_input.text())
            vis_spot_diameter = vis_focus_diameter * math.sqrt(1 + (vis_defocus / (vis_focus_depth / 2))**2)
            
            # 计算红外光斑直径 (μm)
            ir_defocus = float(self.IR_defocus_input.text())
            ir_spot_diameter = ir_focus_diameter * math.sqrt(1 + (ir_defocus / (ir_focus_depth / 2))**2)

            # 计算SFG光斑直径 (mm)
            sfg_focal = float(self.SFG_focal_input.text())
            sfg_spot_diameter = vis_spot_size * (sfg_focal / vis_focal)

            # 计算狭缝焦点大小 (μm)
            spectrometer_focal = float(self.Spectrometer_focal_input.text())
            sfg_wavelength = float(self.SFG_wavelength_input.text())
            slit_spot_size = (4 * spectrometer_focal * sfg_wavelength) / (math.pi * sfg_spot_diameter) * 1e-3

            # 更新输出框
            self.Visible_spot_output.setText(f"{vis_focus_diameter:.4f}")
            self.IR_spot_output.setText(f"{ir_focus_diameter:.4f}")
            self.Visible_depth_output.setText(f"{vis_focus_depth:.4f}")
            self.IR_depth_output.setText(f"{ir_focus_depth:.4f}")
            self.Visible_diameter_output.setText(f"{vis_spot_diameter:.4f}")
            self.IR_diameter_output.setText(f"{ir_spot_diameter:.4f}")
            self.SFG_diameter_output.setText(f"{sfg_spot_diameter:.4f}")
            self.Slit_spot_output.setText(f"{slit_spot_size:.4f}")

        except ValueError:
            # 输入无效时清空输出
            self.Visible_spot_output.clear()
            self.IR_spot_output.clear()
            self.Visible_diameter_output.clear()
            self.IR_diameter_output.clear()
            self.SFG_diameter_output.clear()

    def setup_focus_tab(self):
        """设置聚焦计算选项卡"""
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 添加输入控件
        input_layout.addWidget(QLabel("可见波长 (nm):"), 0, 0)
        self.Visible_wavelength_input = QLineEdit()
        self.Visible_wavelength_input.setText("532")
        self.Visible_wavelength_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.Visible_wavelength_input, 0, 1)

        input_layout.addWidget(QLabel("红外波长 (nm):"), 0, 2)
        self.IR_wavelength_input = QLineEdit()
        self.IR_wavelength_input.setText("3300")
        self.IR_wavelength_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.IR_wavelength_input, 0, 3)

        input_layout.addWidget(QLabel("SFG波长 (nm):"), 0, 4)
        self.SFG_wavelength_input = QLineEdit()
        self.SFG_wavelength_input.setText("458")
        self.SFG_wavelength_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.SFG_wavelength_input, 0, 5)

        input_layout.addWidget(QLabel("可见光束直径 (mm):"), 1, 0)
        self.visible_size_input = QLineEdit()
        self.visible_size_input.setText("5")
        self.visible_size_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.visible_size_input, 1, 1)

        input_layout.addWidget(QLabel("红外光束直径 (mm):"), 1, 2)
        self.IR_size_input = QLineEdit()
        self.IR_size_input.setText("5")
        self.IR_size_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.IR_size_input, 1, 3)

        input_layout.addWidget(QLabel("可见透镜焦距 (mm):"), 2, 0)
        self.Visible_focal_input = QLineEdit()
        self.Visible_focal_input.setText("250")
        self.Visible_focal_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.Visible_focal_input, 2, 1)

        input_layout.addWidget(QLabel("红外透镜焦距 (mm):"), 2, 2)
        self.IR_focal_input = QLineEdit()
        self.IR_focal_input.setText("150")
        self.IR_focal_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.IR_focal_input, 2, 3)

        input_layout.addWidget(QLabel("SFG透镜焦距 (mm):"), 2, 4)
        self.SFG_focal_input = QLineEdit()
        self.SFG_focal_input.setText("200")
        self.SFG_focal_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.SFG_focal_input, 2, 5)

        input_layout.addWidget(QLabel("可见焦点距离 (mm):"), 3, 0)
        self.Visible_defocus_input = QLineEdit()
        self.Visible_defocus_input.setText("15")
        self.Visible_defocus_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.Visible_defocus_input, 3, 1)

        input_layout.addWidget(QLabel("红外焦点距离 (mm):"), 3, 2)
        self.IR_defocus_input = QLineEdit()
        self.IR_defocus_input.setText("7")
        self.IR_defocus_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.IR_defocus_input, 3, 3)

        input_layout.addWidget(QLabel("光谱仪透镜焦距 (mm):"), 4, 0)
        self.Spectrometer_focal_input = QLineEdit()
        self.Spectrometer_focal_input.setText("100")
        self.Spectrometer_focal_input.textChanged.connect(self.calculate_focus)
        input_layout.addWidget(self.Spectrometer_focal_input, 4, 1)
        
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
        output_layout.addWidget(QLabel("可见焦点直径 (μm):"), 0, 0)
        self.Visible_spot_output = QLineEdit()
        self.Visible_spot_output.setReadOnly(True)
        output_layout.addWidget(self.Visible_spot_output, 0, 1)

        output_layout.addWidget(QLabel("可见焦点深度 (mm):"), 0, 2)
        self.Visible_depth_output = QLineEdit()
        self.Visible_depth_output.setReadOnly(True)
        output_layout.addWidget(self.Visible_depth_output, 0, 3) 

        output_layout.addWidget(QLabel("可见光斑直径 (μm):"), 0, 4)
        self.Visible_diameter_output = QLineEdit()
        self.Visible_diameter_output.setReadOnly(True)
        output_layout.addWidget(self.Visible_diameter_output, 0, 5)

        output_layout.addWidget(QLabel("红外焦点直径 (μm):"), 1, 0)
        self.IR_spot_output = QLineEdit()
        self.IR_spot_output.setReadOnly(True)
        output_layout.addWidget(self.IR_spot_output, 1, 1)

        output_layout.addWidget(QLabel("红外焦点深度 (mm):"), 1, 2)
        self.IR_depth_output = QLineEdit()
        self.IR_depth_output.setReadOnly(True)
        output_layout.addWidget(self.IR_depth_output, 1, 3)

        output_layout.addWidget(QLabel("红外光斑直径 (μm):"), 1, 4)
        self.IR_diameter_output = QLineEdit()
        self.IR_diameter_output.setReadOnly(True)
        output_layout.addWidget(self.IR_diameter_output, 1, 5)     

        output_layout.addWidget(QLabel("SFG光斑直径 (mm):"), 2, 0)
        self.SFG_diameter_output = QLineEdit()
        self.SFG_diameter_output.setReadOnly(True)
        output_layout.addWidget(self.SFG_diameter_output, 2, 1)    

        output_layout.addWidget(QLabel("狭缝焦点大小 (μm):"), 2, 2)
        self.Slit_spot_output = QLineEdit()
        self.Slit_spot_output.setReadOnly(True)
        output_layout.addWidget(self.Slit_spot_output, 2, 3)
        
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
            # 获取输入参数
            vis_energy = float(self.Visible_pulseenergy_input.text()) * 1e-6  # 转换为J
            vis_width = float(self.Visible_pulsewidth_input.text()) * 1e-12  # 转换为s
            ir_energy = float(self.IR_pulseenergy_input.text()) * 1e-6  # 转换为J
            ir_width = float(self.IR_pulsewidth_input.text()) * 1e-12  # 转换为s
            
            # 从聚焦计算选项卡获取光斑直径
            vis_diameter = float(self.Visible_diameter_output.text()) * 1e-6  # 转换为m
            ir_diameter = float(self.IR_diameter_output.text()) * 1e-6  # 转换为m
            
            # 计算面积 (πr^2)
            vis_area = math.pi * (vis_diameter/2)**2  # m^2
            ir_area = math.pi * (ir_diameter/2)**2  # m^2
            
            # 计算强度 (W/cm^2)
            I_visible = (vis_energy / vis_width) / (vis_area * 1e4)  # 转换为W/cm^2
            I_IR = (ir_energy / ir_width) / (ir_area * 1e4)  # 转换为W/cm^2
            
            # 更新输出
            self.I_visible_output.setText(f"{I_visible:.3e}")
            self.I_IR_output.setText(f"{I_IR:.3e}")

            # 计算SFG信号
            quartz_signal = float(self.quartz_intensity_input.text())
            normalized_intensity = float(self.Normalized_intensity_input.text())
            integration_time = float(self.integration_time_input.text())
            quantum_efficiency = float(self.CCD_QE_input.text()) / 100.0
            
            # SFG每秒信号
            sfg_signal_per_second = quartz_signal * normalized_intensity
            self.SFG_count_output.setText(f"{sfg_signal_per_second:.2f}")
            
            # SFG总信号
            sfg_total_signal = sfg_signal_per_second * integration_time
            self.SFG_totalcount_output.setText(f"{sfg_total_signal:.2f}")
            
            # 计算总噪声
            ccd_dark_current = float(self.CCD_darknoise_input.text())
            ccd_binned_width = float(self.CCD_binned_input.text())
            readout_noise = float(self.CCD_readoutnoise_input.text())
            
            total_noise = (ccd_dark_current * integration_time * ccd_binned_width) + \
                         (readout_noise ** 2)
            self.noise_level_output.setText(f"{total_noise:.2f}")
            
            # 计算信噪比
            snr = sfg_total_signal / total_noise
            self.snr_output.setText(f"{snr:.2f}")
            
        except ValueError:
            # 输入无效时清空输出
            self.I_visible_output.clear()
            self.I_IR_output.clear()
            self.SFG_count_output.clear()
            self.SFG_totalcount_output.clear()
            self.noise_level_output.clear()
            self.snr_output.clear()

    def setup_intensity_tab(self):
        """设置强度与信噪比计算选项卡"""
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 添加输入控件
        input_layout.addWidget(QLabel("可见光单脉冲能量 (uJ/pulse):"), 0, 0)
        self.Visible_pulseenergy_input = QLineEdit()
        self.Visible_pulseenergy_input.setText("400")
        self.Visible_pulseenergy_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.Visible_pulseenergy_input, 0, 1)

        input_layout.addWidget(QLabel("可见光脉冲宽度 (ps):"), 0, 2)
        self.Visible_pulsewidth_input = QLineEdit()
        self.Visible_pulsewidth_input.setText("80")
        self.Visible_pulsewidth_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.Visible_pulsewidth_input, 0, 3)

        input_layout.addWidget(QLabel("红外光单脉冲能量 (uJ/pulse):"), 1, 0)
        self.IR_pulseenergy_input = QLineEdit()
        self.IR_pulseenergy_input.setText("20")
        self.IR_pulseenergy_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.IR_pulseenergy_input, 1, 1)

        input_layout.addWidget(QLabel("红外光脉冲宽度 (ps):"), 1, 2)
        self.IR_pulsewidth_input = QLineEdit()
        self.IR_pulsewidth_input.setText("0.05")
        self.IR_pulsewidth_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.IR_pulsewidth_input, 1, 3)

        input_layout.addWidget(QLabel("CCD暗电流 (e-/pixel/s):"), 2, 0)
        self.CCD_darknoise_input = QLineEdit()
        self.CCD_darknoise_input.setText("2.8e-5")
        self.CCD_darknoise_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.CCD_darknoise_input, 2, 1)

        input_layout.addWidget(QLabel("CCD读出噪声 (e-):"), 2, 2)
        self.CCD_readoutnoise_input = QLineEdit()
        self.CCD_readoutnoise_input.setText("3.5")
        self.CCD_readoutnoise_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.CCD_readoutnoise_input, 2, 3)

        input_layout.addWidget(QLabel("CCD量子效率(%):"), 3, 0)
        self.CCD_QE_input = QLineEdit()
        self.CCD_QE_input.setText("98")
        self.CCD_QE_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.CCD_QE_input, 3, 1)

        input_layout.addWidget(QLabel("CCD Binned 宽度 (pixel):"), 3, 2)
        self.CCD_binned_input = QLineEdit()
        self.CCD_binned_input.setText("20")
        self.CCD_binned_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.CCD_binned_input, 3, 3)

        input_layout.addWidget(QLabel("石英每秒信号(counts/s):"), 4, 0)
        self.quartz_intensity_input = QLineEdit()
        self.quartz_intensity_input.setText("2000")
        self.quartz_intensity_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.quartz_intensity_input, 4, 1)

        input_layout.addWidget(QLabel("对石英归一化强度:"), 4, 2)
        self.Normalized_intensity_input = QLineEdit()
        self.Normalized_intensity_input.setText("0.1")
        self.Normalized_intensity_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.Normalized_intensity_input, 4, 3)

        input_layout.addWidget(QLabel("积分时间 (s):"), 5, 0)
        self.integration_time_input = QLineEdit()
        self.integration_time_input.setText("120")
        self.integration_time_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.integration_time_input, 5, 1)

        input_layout.addWidget(QLabel("激光器重复频率 (/s):"), 5, 2)
        self.laser_repeat_input = QLineEdit()
        self.laser_repeat_input.setText("1000")
        self.laser_repeat_input.textChanged.connect(self.calculate_intensity)
        input_layout.addWidget(self.laser_repeat_input, 5, 3)
        
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
        output_layout.addWidget(QLabel("I_visible (W/cm^2):"), 0, 0)
        self.I_visible_output = QLineEdit()
        self.I_visible_output.setReadOnly(True)
        output_layout.addWidget(self.I_visible_output, 0, 1)

        output_layout.addWidget(QLabel("I_IR (W/cm^2):"), 0, 2)
        self.I_IR_output = QLineEdit()
        self.I_IR_output.setReadOnly(True)
        output_layout.addWidget(self.I_IR_output, 0, 3)

        output_layout.addWidget(QLabel("SFG每秒信号 (counts/s):"), 1, 0)
        self.SFG_count_output = QLineEdit()
        self.SFG_count_output.setReadOnly(True)
        output_layout.addWidget(self.SFG_count_output, 1, 1)

        output_layout.addWidget(QLabel("SFG信号大小 (counts):"), 1, 2)
        self.SFG_totalcount_output = QLineEdit()
        self.SFG_totalcount_output.setReadOnly(True)
        output_layout.addWidget(self.SFG_totalcount_output, 1, 3)
        
        output_layout.addWidget(QLabel("总噪声:"), 2, 0)
        self.noise_level_output = QLineEdit()
        self.noise_level_output.setReadOnly(True)
        output_layout.addWidget(self.noise_level_output, 2, 1)
        
        output_layout.addWidget(QLabel("信噪比 (SNR):"), 2, 2)
        self.snr_output = QLineEdit()
        self.snr_output.setReadOnly(True)
        output_layout.addWidget(self.snr_output, 2, 3)
        
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
        output3_layout.addWidget(QLabel("相干长度 (nm):"), 0, 0)
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
