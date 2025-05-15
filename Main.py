import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                            QVBoxLayout, QGridLayout, QLabel, QLineEdit, QFrame,
                            QPushButton)
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
        self.fresnel_tab = QWidget()
        
        self.tabs.addTab(self.quartz_tab, "石英计算")
        self.tabs.addTab(self.focus_tab, "聚焦计算")
        self.tabs.addTab(self.fresnel_tab, "Fresnel计算")
        
        # Set up basic layouts for each tab
        self.setup_quartz_tab()
        self.setup_focus_tab()
        self.setup_fresnel_tab()
        
        # Initialize with default values after all widgets are created
        self.calculate_focus()
        self.update_sfg_results()
        self.calculate_fresnel_factors()

    def calculate_refraction_angle(self, incident_angle, n1, n2):
        """计算折射角度"""
        return math.degrees(math.asin(n1 * math.sin(math.radians(incident_angle)) / n2))
        
    def calculate_fresnel(self, n1, n2, theta1, theta2, polarization):
        """计算菲涅耳因子"""
        theta1_rad = math.radians(theta1)
        theta2_rad = math.radians(theta2)
        
        cos_theta1 = math.cos(theta1_rad)
        cos_theta2 = math.cos(theta2_rad)
        
        # 计算n_prime
        n_prime = math.sqrt((n2**2 * (n2**2 + 5)) / (4 * n2**2 + 2))
        
        if polarization == 'xx':
            # Lxx = (2 * n1 * cosθ2) / (n1 * cosθ2 + n2 * cosθ1)
            numerator = 2 * n1 * cos_theta2
            denominator = n1 * cos_theta2 + n2 * cos_theta1
            return numerator / denominator
        elif polarization == 'yy':
            # Lyy = (2 * n1 * cosθ1) / (n1 * cosθ1 + n2 * cosθ2)
            numerator = 2 * n1 * cos_theta1
            denominator = n1 * cos_theta1 + n2 * cos_theta2
            return numerator / denominator
        elif polarization == 'zz':
            # Lzz = (2 * n2 * cosθ1) / (n1 * cosθ2 + n2 * cosθ1) * (n1/n')^2
            numerator = 2 * n2 * cos_theta1
            denominator = n1 * cos_theta2 + n2 * cos_theta1
            return (numerator / denominator) * (n1 / n_prime)**2
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
            # 获取输入值
            vis_angle_text = self.quartz_vis_angle_input.text()
            ir_angle_text = self.quartz_ir_angle_input.text()
            vis_wavelength_text = self.quartz_vis_wavelength_input.text()
            ir_wavenumber_text = self.quartz_ir_wavenumber_input.text()
            
            # 检查输入是否为空
            if not vis_angle_text or not ir_angle_text or not vis_wavelength_text or not ir_wavenumber_text:
                raise ValueError("请输入所有参数")
                
            # 转换为数值并验证
            vis_angle = float(vis_angle_text)
            ir_angle = float(ir_angle_text)
            vis_wavelength = float(vis_wavelength_text)
            ir_wavenumber = float(ir_wavenumber_text)
            
            # 验证输入值范围
            if not (0 <= vis_angle <= 90) or not (0 <= ir_angle <= 90):
                raise ValueError("入射角度必须在0到90度之间")
            if vis_wavelength <= 0 or ir_wavenumber <= 0:
                raise ValueError("波长和波数必须大于0")
            
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
            self.sfg_wavelength_output.setText(f"{sfg_wavelength:.2f}")
            self.sfg_angle_output.setText(f"{sfg_angle:.2f}")
            
            # 计算并更新红外波长
            ir_wavelength = 1e7 / ir_wavenumber
            self.ir_wavelength_output.setText(f"{ir_wavelength:.2f}")
            
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
            
            # 使用用户提供的新公式计算相干长度，单位为nm
            coherence_length = 1 / (2 * math.pi * (sfg_term + vis_term) + ir_term)
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
            # 输入无效时清空所有输出
            self.sfg_wavelength_output.clear()
            self.sfg_angle_output.clear()
            self.ir_wavelength_output.clear()
            self.vis_refractive_index_output.clear()
            self.ir_refractive_index_output.clear()
            self.sfg_refractive_index_output.clear()
            self.vis_refraction_angle_output.clear()
            self.ir_refraction_angle_output.clear()
            self.sfg_refraction_angle_output.clear()
            self.coherence_length_output.clear()
            self.fresnel_xx_sfg.clear()
            self.fresnel_yy_sfg.clear()
            self.fresnel_xx_vis.clear()
            self.fresnel_yy_vis.clear()
            self.fresnel_xx_ir.clear()
            self.fresnel_yy_ir.clear()
            self.chi2_ssp_output.clear()
            self.chi2_sps_output.clear()
            self.chi2_pss_output.clear()
            self.chi2_ppp_output.clear()
            self.chi2_ssp_sq_output.clear()
            self.chi2_sps_sq_output.clear()
            self.chi2_pss_sq_output.clear()
            self.chi2_ppp_sq_output.clear()
        
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

    def setup_fresnel_tab(self):
        """设置Fresnel计算选项卡"""
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 添加输入控件 - 第一行: 折射率
        input_layout.addWidget(QLabel("SFG折射率:"), 0, 0)
        self.sfg_n_input = QLineEdit()
        self.sfg_n_input.setText("1.4727")
        self.sfg_n_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.sfg_n_input, 0, 1)

        input_layout.addWidget(QLabel("可见光折射率:"), 0, 2)
        self.vis_n_input = QLineEdit()
        self.vis_n_input.setText("1.4727")
        self.vis_n_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.vis_n_input, 0, 3)

        input_layout.addWidget(QLabel("红外折射率:"), 0, 4)
        self.ir_n_input = QLineEdit()
        self.ir_n_input.setText("1.47")
        self.ir_n_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.ir_n_input, 0, 5)

        # 第二行: 入射角度
        input_layout.addWidget(QLabel("可见光入射角(°):"), 1, 0)
        self.vis_angle_input = QLineEdit()
        self.vis_angle_input.setText("45")
        self.vis_angle_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.vis_angle_input, 1, 1)

        input_layout.addWidget(QLabel("红外入射角(°):"), 1, 2)
        self.ir_angle_input = QLineEdit()
        self.ir_angle_input.setText("55")
        self.ir_angle_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.ir_angle_input, 1, 3)

        # 第三行: 波长/波数
        input_layout.addWidget(QLabel("可见光波长(nm):"), 2, 0)
        self.vis_wavelength_input = QLineEdit()
        self.vis_wavelength_input.setText("532.1")
        self.vis_wavelength_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.vis_wavelength_input, 2, 1)

        input_layout.addWidget(QLabel("红外波数(cm⁻¹):"), 2, 2)
        self.ir_wavenumber_input = QLineEdit()
        self.ir_wavenumber_input.setText("2900")
        self.ir_wavenumber_input.textChanged.connect(self.calculate_fresnel_factors)
        input_layout.addWidget(self.ir_wavenumber_input, 2, 3)

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
        
        # 添加输出控件 - 第一行: 相干长度
        output_layout.addWidget(QLabel("相干长度 (nm):"), 0, 0)
        self.fresnel_coherence_length_output = QLineEdit()
        self.fresnel_coherence_length_output.setReadOnly(True)
        output_layout.addWidget(self.fresnel_coherence_length_output, 0, 1, 1, 5)
        
        # 第二行: SFG
        output_layout.addWidget(QLabel("SFG Lxx:"), 1, 0)
        self.sfg_lxx_output = QLineEdit()
        self.sfg_lxx_output.setReadOnly(True)
        output_layout.addWidget(self.sfg_lxx_output, 1, 1)

        output_layout.addWidget(QLabel("SFG Lyy:"), 1, 2)
        self.sfg_lyy_output = QLineEdit()
        self.sfg_lyy_output.setReadOnly(True)
        output_layout.addWidget(self.sfg_lyy_output, 1, 3)

        output_layout.addWidget(QLabel("SFG Lzz:"), 1, 4)
        self.sfg_lzz_output = QLineEdit()
        self.sfg_lzz_output.setReadOnly(True)
        output_layout.addWidget(self.sfg_lzz_output, 1, 5)

        # 第三行: VIS
        output_layout.addWidget(QLabel("VIS Lxx:"), 2, 0)
        self.vis_lxx_output = QLineEdit()
        self.vis_lxx_output.setReadOnly(True)
        output_layout.addWidget(self.vis_lxx_output, 2, 1)

        output_layout.addWidget(QLabel("VIS Lyy:"), 2, 2)
        self.vis_lyy_output = QLineEdit()
        self.vis_lyy_output.setReadOnly(True)
        output_layout.addWidget(self.vis_lyy_output, 2, 3)

        output_layout.addWidget(QLabel("VIS Lzz:"), 2, 4)
        self.vis_lzz_output = QLineEdit()
        self.vis_lzz_output.setReadOnly(True)
        output_layout.addWidget(self.vis_lzz_output, 2, 5)

        # 第四行: IR
        output_layout.addWidget(QLabel("IR Lxx:"), 3, 0)
        self.ir_lxx_output = QLineEdit()
        self.ir_lxx_output.setReadOnly(True)
        output_layout.addWidget(self.ir_lxx_output, 3, 1)

        output_layout.addWidget(QLabel("IR Lyy:"), 3, 2)
        self.ir_lyy_output = QLineEdit()
        self.ir_lyy_output.setReadOnly(True)
        output_layout.addWidget(self.ir_lyy_output, 3, 3)

        output_layout.addWidget(QLabel("IR Lzz:"), 3, 4)
        self.ir_lzz_output = QLineEdit()
        self.ir_lzz_output.setReadOnly(True)
        output_layout.addWidget(self.ir_lzz_output, 3, 5)

        # 添加分割线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("color: #95a5a6;")
        separator2.setFixedHeight(2)
        output_layout.addWidget(separator2, 4, 0, 1, 6)

        # 非手性项
        output_layout.addWidget(QLabel("非手性项:"), 5, 0)
        output_layout.addWidget(QLabel("SSP YYZ:"), 6, 0)
        self.ssp_yyz_output = QLineEdit()
        self.ssp_yyz_output.setReadOnly(True)
        output_layout.addWidget(self.ssp_yyz_output, 6, 1)

        output_layout.addWidget(QLabel("SPS YZY:"), 7, 0)
        self.sps_yzy_output = QLineEdit()
        self.sps_yzy_output.setReadOnly(True)
        output_layout.addWidget(self.sps_yzy_output, 7, 1)

        output_layout.addWidget(QLabel("PSS ZYY:"), 8, 0)
        self.pss_zyy_output = QLineEdit()
        self.pss_zyy_output.setReadOnly(True)
        output_layout.addWidget(self.pss_zyy_output, 8, 1)

        output_layout.addWidget(QLabel("PPP ZXX:"), 9, 0)
        self.ppp_zxx_output = QLineEdit()
        self.ppp_zxx_output.setReadOnly(True)
        output_layout.addWidget(self.ppp_zxx_output, 9, 1)

        output_layout.addWidget(QLabel("PPP XXZ:"), 10, 0)
        self.ppp_xxz_output = QLineEdit()
        self.ppp_xxz_output.setReadOnly(True)
        output_layout.addWidget(self.ppp_xxz_output, 10, 1)

        output_layout.addWidget(QLabel("PPP XZX:"), 11, 0)
        self.ppp_xzx_output = QLineEdit()
        self.ppp_xzx_output.setReadOnly(True)
        output_layout.addWidget(self.ppp_xzx_output, 11, 1)

        output_layout.addWidget(QLabel("PPP ZZZ:"), 12, 0)
        self.ppp_zzz_output = QLineEdit()
        self.ppp_zzz_output.setReadOnly(True)
        output_layout.addWidget(self.ppp_zzz_output, 12, 1)

        # 手性项
        output_layout.addWidget(QLabel("手性项:"), 5, 2)
        output_layout.addWidget(QLabel("PSP ZYX:"), 6, 2)
        self.psp_zyx_output = QLineEdit()
        self.psp_zyx_output.setReadOnly(True)
        output_layout.addWidget(self.psp_zyx_output, 6, 3)

        output_layout.addWidget(QLabel("PSP XYZ:"), 7, 2)
        self.psp_xyz_output = QLineEdit()
        self.psp_xyz_output.setReadOnly(True)
        output_layout.addWidget(self.psp_xyz_output, 7, 3)

        output_layout.addWidget(QLabel("SPP YZX:"), 8, 2)
        self.spp_yzx_output = QLineEdit()
        self.spp_yzx_output.setReadOnly(True)
        output_layout.addWidget(self.spp_yzx_output, 8, 3)

        output_layout.addWidget(QLabel("SPP YXZ:"), 9, 2)
        self.spp_yxz_output = QLineEdit()
        self.spp_yxz_output.setReadOnly(True)
        output_layout.addWidget(self.spp_yxz_output, 9, 3)

        output_layout.addWidget(QLabel("PPS ZXY:"), 10, 2)
        self.pps_zxy_output = QLineEdit()
        self.pps_zxy_output.setReadOnly(True)
        output_layout.addWidget(self.pps_zxy_output, 10, 3)

        output_layout.addWidget(QLabel("PPS XZY:"), 11, 2)
        self.pps_xzy_output = QLineEdit()
        self.pps_xzy_output.setReadOnly(True)
        output_layout.addWidget(self.pps_xzy_output, 11, 3)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # 调整布局间距
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setVerticalSpacing(15)
        output_layout.setVerticalSpacing(15)
        
        # 设置输入框样式并连接信号
        for widget in input_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px;")
            widget.textChanged.connect(self.calculate_fresnel_factors)
            
        # 设置输出框样式
        for widget in output_group.findChildren(QLineEdit):
            widget.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 3px; background-color: #ecf0f1;")
        
        self.fresnel_tab.setLayout(main_layout)

    def calculate_fresnel_factors(self):
        """计算菲涅耳因子"""
        try:
            # 获取输入参数
            n_sfg = float(self.sfg_n_input.text())
            n_vis = float(self.vis_n_input.text())
            n_ir = float(self.ir_n_input.text())
            vis_angle = float(self.vis_angle_input.text())
            ir_angle = float(self.ir_angle_input.text())
            vis_wavelength = float(self.vis_wavelength_input.text())
            ir_wavenumber = float(self.ir_wavenumber_input.text())
            
            # 计算相干长度(使用选项卡3的参数但保持与选项卡1相同的计算逻辑)
            ir_wavelength_fresnel = 1e7 / ir_wavenumber
            sfg_wavelength_fresnel = 1/(1/vis_wavelength + 1/ir_wavelength_fresnel)
            
            sfg_angle_fresnel = math.degrees(math.asin(
                sfg_wavelength_fresnel * (math.sin(math.radians(vis_angle))/vis_wavelength + 
                                        math.sin(math.radians(ir_angle))/ir_wavelength_fresnel)
            ))
            
            sfg_angle_rad_fresnel = math.radians(sfg_angle_fresnel)
            vis_angle_rad_fresnel = math.radians(vis_angle)
            ir_angle_rad_fresnel = math.radians(ir_angle)
            
            sfg_term_fresnel = math.sqrt(n_sfg**2 - math.sin(sfg_angle_rad_fresnel)**2) / sfg_wavelength_fresnel
            vis_term_fresnel = math.sqrt(n_vis**2 - math.sin(vis_angle_rad_fresnel)**2) / vis_wavelength
            ir_term_fresnel = math.sqrt(n_ir**2 - math.sin(ir_angle_rad_fresnel)**2) / ir_wavelength_fresnel
            
            coherence_length_fresnel = 1 / (2 * math.pi * (sfg_term_fresnel + vis_term_fresnel) + ir_term_fresnel)
            self.fresnel_coherence_length_output.setText(f"{coherence_length_fresnel:.2f}")
            
            # 计算波长
            ir_wavelength = 1e7 / ir_wavenumber
            sfg_wavelength = 1/(1/vis_wavelength + 1/ir_wavelength)
            
            # 计算折射率
            n_air = 1.0
            n_quartz_vis = self.calculate_quartz_refractive_index(vis_wavelength)
            n_quartz_ir = self.calculate_quartz_refractive_index(ir_wavelength)
            n_quartz_sfg = self.calculate_quartz_refractive_index(sfg_wavelength)
            
            # 计算折射角度
            vis_ref_angle = self.calculate_refraction_angle(vis_angle, n_air, n_quartz_vis)
            ir_ref_angle = self.calculate_refraction_angle(ir_angle, n_air, n_quartz_ir)
            sfg_angle = math.degrees(math.asin(
                sfg_wavelength * (math.sin(math.radians(vis_angle))/vis_wavelength + 
                                math.sin(math.radians(ir_angle))/ir_wavelength)
            ))
            sfg_ref_angle = self.calculate_refraction_angle(sfg_angle, n_air, n_quartz_sfg)
            
            # 计算菲涅耳因子
            sfg_lxx = self.calculate_fresnel(n_air, n_sfg, sfg_angle, sfg_ref_angle, 'xx')
            sfg_lyy = self.calculate_fresnel(n_air, n_sfg, sfg_angle, sfg_ref_angle, 'yy')
            sfg_lzz = self.calculate_fresnel(n_air, n_sfg, sfg_angle, sfg_ref_angle, 'zz')
            vis_lxx = self.calculate_fresnel(n_air, n_vis, vis_angle, vis_ref_angle, 'xx')
            vis_lyy = self.calculate_fresnel(n_air, n_vis, vis_angle, vis_ref_angle, 'yy')
            vis_lzz = self.calculate_fresnel(n_air, n_vis, vis_angle, vis_ref_angle, 'zz')
            ir_lxx = self.calculate_fresnel(n_air, n_ir, ir_angle, ir_ref_angle, 'xx')
            ir_lyy = self.calculate_fresnel(n_air, n_ir, ir_angle, ir_ref_angle, 'yy')
            ir_lzz = self.calculate_fresnel(n_air, n_ir, ir_angle, ir_ref_angle, 'zz')
            
            # 计算组合因子
            ssp_yyz = sfg_lyy * vis_lyy * ir_lzz * math.sin(math.radians(ir_angle))
            psp_zyx = sfg_lzz * vis_lyy * ir_lxx * math.sin(math.radians(sfg_angle)) * math.cos(math.radians(ir_angle))
            psp_xyz = sfg_lxx * vis_lyy * ir_lzz * math.cos(math.radians(sfg_angle)) * math.sin(math.radians(ir_angle))
            
            # 新增PPP组合因子
            ppp_zxx = sfg_lzz * vis_lxx * ir_lxx * math.sin(math.radians(sfg_angle)) * math.cos(math.radians(vis_angle)) * math.cos(math.radians(ir_angle))
            ppp_xxz = sfg_lxx * vis_lxx * ir_lzz * math.cos(math.radians(sfg_angle)) * math.cos(math.radians(vis_angle)) * math.sin(math.radians(ir_angle))
            ppp_xzx = sfg_lxx * vis_lzz * ir_lxx * math.cos(math.radians(sfg_angle)) * math.sin(math.radians(vis_angle)) * math.cos(math.radians(ir_angle))
            ppp_zzz = sfg_lzz * vis_lzz * ir_lzz * math.sin(math.radians(sfg_angle)) * math.sin(math.radians(vis_angle)) * math.sin(math.radians(ir_angle))
            
            # 新增SPS组合因子
            sps_yzy = sfg_lyy * vis_lzz * ir_lyy * math.sin(math.radians(vis_angle))
            
            # 新增PSS组合因子
            pss_zyy = sfg_lzz * vis_lyy * ir_lyy * math.sin(math.radians(sfg_angle))
            
            # 新增SPP组合因子
            spp_yzx = sfg_lyy * vis_lzz * ir_lxx * math.sin(math.radians(vis_angle)) * math.cos(math.radians(ir_angle))
            spp_yxz = sfg_lyy * vis_lxx * ir_lzz * math.cos(math.radians(vis_angle)) * math.sin(math.radians(ir_angle))
            
            # 新增PPS组合因子
            pps_zxy = sfg_lzz * vis_lxx * ir_lyy * math.sin(math.radians(sfg_angle)) * math.cos(math.radians(vis_angle))
            pps_xzy = sfg_lxx * vis_lzz * ir_lyy * math.cos(math.radians(sfg_angle)) * math.sin(math.radians(vis_angle))
            
            # 更新输出
            self.sfg_lxx_output.setText(f"{sfg_lxx:.4f}")
            self.sfg_lyy_output.setText(f"{sfg_lyy:.4f}")
            self.sfg_lzz_output.setText(f"{sfg_lzz:.4f}")
            self.vis_lxx_output.setText(f"{vis_lxx:.4f}")
            self.vis_lyy_output.setText(f"{vis_lyy:.4f}")
            self.vis_lzz_output.setText(f"{vis_lzz:.4f}")
            self.ir_lxx_output.setText(f"{ir_lxx:.4f}")
            self.ir_lyy_output.setText(f"{ir_lyy:.4f}")
            self.ir_lzz_output.setText(f"{ir_lzz:.4f}")
            self.ssp_yyz_output.setText(f"{ssp_yyz:.4f}")
            self.psp_zyx_output.setText(f"{psp_zyx:.4f}")
            self.psp_xyz_output.setText(f"{psp_xyz:.4f}")
            self.ppp_zxx_output.setText(f"{ppp_zxx:.4f}")
            self.ppp_xxz_output.setText(f"{ppp_xxz:.4f}")
            self.ppp_xzx_output.setText(f"{ppp_xzx:.4f}")
            self.ppp_zzz_output.setText(f"{ppp_zzz:.4f}")
            self.sps_yzy_output.setText(f"{sps_yzy:.4f}")
            self.pss_zyy_output.setText(f"{pss_zyy:.4f}")
            self.spp_yzx_output.setText(f"{spp_yzx:.4f}")
            self.spp_yxz_output.setText(f"{spp_yxz:.4f}")
            self.pps_zxy_output.setText(f"{pps_zxy:.4f}")
            self.pps_xzy_output.setText(f"{pps_xzy:.4f}")
            
        except ValueError:
            # 输入无效时清空输出
            self.sfg_lxx_output.clear()
            self.sfg_lyy_output.clear()
            self.sfg_lzz_output.clear()
            self.vis_lxx_output.clear()
            self.vis_lyy_output.clear()
            self.vis_lzz_output.clear()
            self.ir_lxx_output.clear()
            self.ir_lyy_output.clear()
            self.ir_lzz_output.clear()
            self.ssp_yyz_output.clear()
            self.psp_zyx_output.clear()
            self.psp_xyz_output.clear()

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


    def setup_quartz_tab(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 输入角度
        input_layout.addWidget(QLabel("可见光入射角度 (°):"), 0, 0)
        self.quartz_vis_angle_input = QLineEdit()
        self.quartz_vis_angle_input.setText("45")
        self.quartz_vis_angle_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.quartz_vis_angle_input, 0, 1)
        
        input_layout.addWidget(QLabel("红外光入射角度 (°):"), 0, 2)
        self.quartz_ir_angle_input = QLineEdit()
        self.quartz_ir_angle_input.setText("55")
        self.quartz_ir_angle_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.quartz_ir_angle_input, 0, 3)
        
        # 输入波长/波数
        input_layout.addWidget(QLabel("可见光波长 (nm):"), 1, 0)
        self.quartz_vis_wavelength_input = QLineEdit()
        self.quartz_vis_wavelength_input.setText("532")
        self.quartz_vis_wavelength_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.quartz_vis_wavelength_input, 1, 1)
        
        input_layout.addWidget(QLabel("红外光波数 (cm⁻¹):"), 1, 2)
        self.quartz_ir_wavenumber_input = QLineEdit()
        self.quartz_ir_wavenumber_input.setText("3000")
        self.quartz_ir_wavenumber_input.textChanged.connect(self.update_sfg_results)
        input_layout.addWidget(self.quartz_ir_wavenumber_input, 1, 3)

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
        
        # SFG反射角度
        output1_layout.addWidget(QLabel("SFG反射角度:"), 0, 0)
        self.sfg_angle_output = QLineEdit()
        self.sfg_angle_output.setReadOnly(True)
        output1_layout.addWidget(self.sfg_angle_output, 0, 1)
        
        # SFG波长
        output1_layout.addWidget(QLabel("SFG波长 (nm):"), 0, 2)
        self.sfg_wavelength_output = QLineEdit()
        self.sfg_wavelength_output.setReadOnly(True)
        output1_layout.addWidget(self.sfg_wavelength_output, 0, 3)

        # 红外波长
        output1_layout.addWidget(QLabel("红外波长 (nm):"), 1, 0)
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
