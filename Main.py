import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QGridLayout, QLabel, QLineEdit, QFrame)
import pyqtgraph as pg

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
        
    def setup_quartz_tab(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建输入区域
        input_group = QWidget()
        input_layout = QGridLayout()
        
        # 输入角度
        input_layout.addWidget(QLabel("可见光入射角度 (°):"), 0, 0)
        self.vis_angle_input = QLineEdit()
        input_layout.addWidget(self.vis_angle_input, 0, 1)
        
        input_layout.addWidget(QLabel("红外光入射角度 (°):"), 0, 2)
        self.ir_angle_input = QLineEdit()
        input_layout.addWidget(self.ir_angle_input, 0, 3)
        
        # 输入波长/波数
        input_layout.addWidget(QLabel("可见光波长 (nm):"), 1, 0)
        self.vis_wavelength_input = QLineEdit()
        input_layout.addWidget(self.vis_wavelength_input, 1, 1)
        
        input_layout.addWidget(QLabel("红外光波数 (cm⁻¹):"), 1, 2)
        self.ir_wavenumber_input = QLineEdit()
        input_layout.addWidget(self.ir_wavenumber_input, 1, 3)
        
        input_group.setLayout(input_layout)
        
        # 添加输入标题
        input_title = QLabel("输入参数")
        input_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(input_title)
        main_layout.addWidget(input_group)
        
        # 添加分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # 添加输出标题
        output_title = QLabel("输出结果") 
        output_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(output_title)
        
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
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.quartz_tab.setLayout(main_layout)
        
    def setup_focus_tab(self):
        layout = QVBoxLayout()
        self.focus_tab.setLayout(layout)
        
    def setup_intensity_tab(self):
        layout = QVBoxLayout()
        self.intensity_tab.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SFGCalculator()
    window.show()
    sys.exit(app.exec())
