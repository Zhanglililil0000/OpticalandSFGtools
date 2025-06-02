import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QSlider, QDoubleSpinBox, QGroupBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from voigt import voigt

class VoigtSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.controls = []  # 初始化控件列表
        self.initUI()
        
    def initUI(self):
        # 创建图形窗口
        self.plot = pg.PlotWidget()
        
        # 创建结果显示区域
        self.info_group = QGroupBox("Peak Analysis")
        self.info_layout = QHBoxLayout()
        
        # 创建两个独立的标签用于显示峰信息
        self.info_label1 = QLabel()
        self.info_label1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.info_label2 = QLabel()
        self.info_label2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.info_layout.addWidget(self.info_label1)
        self.info_layout.addWidget(self.info_label2)
        self.info_group.setLayout(self.info_layout)
        self.plot.setLabel('left', 'Intensity')
        self.plot.setLabel('bottom', 'Wavenumber (cm-1)')
        
        # 设置绘图风格
        self.plot.setBackground('w')
        for axis in ['left', 'bottom']:
            self.plot.getAxis(axis).setPen(pg.mkPen('k'))
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        
        # 创建范围设置控件
        range_group = QGroupBox("Plot Range")
        range_layout = QHBoxLayout()
        
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(1000, 4000)
        self.min_spin.setValue(3600)
        self.min_spin.setSingleStep(10)
        
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setRange(1000, 4000)
        self.max_spin.setValue(3800)
        self.max_spin.setSingleStep(10)
        
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.min_spin)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.max_spin)
        range_group.setLayout(range_layout)
        
        # 创建峰参数控件
        control_layout = QHBoxLayout()
        for i in range(2):  # 两个峰
            layout = self.create_peak_controls(i+1)
            control_layout.addLayout(layout)
        
        # 非共振项输入
        nonres_group = QGroupBox("Nonresonance Term")
        nonres_layout = QHBoxLayout()
        
        # 实部
        real_label = QLabel("Real Part:")
        self.real_spin = QDoubleSpinBox()
        self.real_spin.setRange(-100, 100)
        self.real_spin.setValue(0.1)
        self.real_spin.setSingleStep(0.01)
        
        # 虚部
        imag_label = QLabel("Imaginary Part:")
        self.imag_spin = QDoubleSpinBox()
        self.imag_spin.setRange(-100, 100)
        self.imag_spin.setValue(0.0)
        self.imag_spin.setSingleStep(0.01)
        
        nonres_layout.addWidget(real_label)
        nonres_layout.addWidget(self.real_spin)
        nonres_layout.addWidget(imag_label)
        nonres_layout.addWidget(self.imag_spin)
        nonres_group.setLayout(nonres_layout)
        
        # 布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(range_group)
        main_layout.addWidget(nonres_group)
        main_layout.addWidget(self.info_group)
        main_layout.addWidget(self.plot)
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle('Spectra Line Shape Simulator')
        
        # 连接信号
        self.min_spin.valueChanged.connect(self.update_range)
        self.max_spin.valueChanged.connect(self.update_range)
        self.update_plot()
        
    def create_peak_controls(self, peak_num):
        layout = QVBoxLayout()
        
        # 中心位置
        pos_group = QGroupBox(f'Peak {peak_num} Position')
        pos_layout = QVBoxLayout()
        
        pos_spin = QDoubleSpinBox()
        pos_spin.setRange(3600, 3800)
        pos_spin.setValue(3700)
        pos_spin.setSingleStep(0.1)
        
        pos_slider = QSlider()
        pos_slider.setOrientation(Qt.Orientation.Horizontal)  # 垂直滑块
        pos_slider.setRange(3600, 3800)
        pos_slider.setValue(3700)
        
        # 同步滑块和输入框
        pos_spin.valueChanged.connect(lambda val: pos_slider.setValue(int(val)))
        pos_slider.valueChanged.connect(pos_spin.setValue)
        pos_spin.valueChanged.connect(self.update_plot)
        
        pos_layout.addWidget(pos_spin)
        pos_layout.addWidget(pos_slider)
        pos_group.setLayout(pos_layout)
        
        # 强度
        int_label = QLabel(f'Peak {peak_num} Intensity:')
        int_spin = QDoubleSpinBox()
        int_spin.setRange(-10, 10)
        int_spin.setValue(0.5)
        int_spin.setSingleStep(0.01)
        int_spin.valueChanged.connect(self.update_plot)
        
        # 洛伦兹宽度
        lw_label = QLabel(f'Peak {peak_num} Lorentzian FWHM:')
        lw_spin = QDoubleSpinBox()
        lw_spin.setRange(0, 1000)
        lw_spin.setValue(10.0)
        lw_spin.setSingleStep(0.1)
        lw_spin.valueChanged.connect(self.update_plot)
        
        # 高斯宽度
        gw_label = QLabel(f'Peak {peak_num} Gaussian FWHM:')
        gw_spin = QDoubleSpinBox()
        gw_spin.setRange(0, 1000)
        gw_spin.setValue(0.0)
        gw_spin.setSingleStep(0.1)
        gw_spin.valueChanged.connect(self.update_plot)
        
        # 添加到布局
        layout.addWidget(pos_group)
        layout.addWidget(int_label)
        layout.addWidget(int_spin)
        layout.addWidget(lw_label)
        layout.addWidget(lw_spin)
        layout.addWidget(gw_label)
        layout.addWidget(gw_spin)
        
        # 保存控件引用
        self.controls.append({
            'position': pos_spin,
            'intensity': int_spin,
            'lorentz_width': lw_spin,
            'gauss_width': gw_spin,
            'slider': pos_slider
        })
        
        return layout
        
    def update_range(self):
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        
        # 更新滑块范围
        for controls in self.controls:
            controls['position'].setRange(min_val, max_val)
            controls['slider'].setRange(int(min_val), int(max_val))
        
        self.update_plot()
        
    def analyze_peaks(self, x, y):
        """分析光谱峰，返回峰位置和FWHM"""
        from scipy.signal import find_peaks
        from scipy.interpolate import interp1d
        
        # 找峰
        peaks, _ = find_peaks(y, height=0.1*max(y))
        peak_info = []
        
        for peak in peaks:
            # 计算半高全宽
            half_max = y[peak]/2
            
            # 找到左交叉点的索引
            left_cross = np.where(y[:peak] <= half_max)[0]
            if len(left_cross) == 0:
                x_left = x[peak] - 10  # 默认10cm-1宽度
            else:
                left_idx = left_cross[-1]
                # 使用线性插值找到精确的左交叉点
                x_left = x[left_idx] + (half_max - y[left_idx]) * (x[left_idx+1] - x[left_idx]) / (y[left_idx+1] - y[left_idx])
            
            # 找到右交叉点的索引
            right_cross = np.where(y[peak:] <= half_max)[0]
            if len(right_cross) == 0:
                x_right = x[peak] + 10  # 默认10cm-1宽度
            else:
                right_idx = right_cross[0] + peak
                # 使用线性插值找到精确的右交叉点
                x_right = x[right_idx-1] + (half_max - y[right_idx-1]) * (x[right_idx] - x[right_idx-1]) / (y[right_idx] - y[right_idx-1])
            
            fwhm = x_right - x_left
            
            peak_info.append({
                'position': x[peak],
                'fwhm': fwhm,
                'intensity': y[peak]
            })
            
        return peak_info
        
    def update_peak_info(self, peak_info):
        """更新峰信息显示"""
        if not hasattr(self, 'info_label1'):
            return
            
            
        # 更新显示内容
        text1 = ""
        text2 = ""
        for i, info in enumerate(peak_info):
            if i == 0:
                text1 += f"Peak {i+1}:\n"
                text1 += f"  Position: {info['position']:.2f} cm-1\n"
                text1 += f"  FWHM: {info['fwhm']:.2f} cm-1\n"
                text1 += f"  Intensity: {info['intensity']:.4f}\n\n"
            elif i == 1:
                text2 += f"Peak {i+1}:\n"
                text2 += f"  Position: {info['position']:.2f} cm-1\n"
                text2 += f"  FWHM: {info['fwhm']:.2f} cm-1\n"
                text2 += f"  Intensity: {info['intensity']:.4f}\n\n"
        
        self.info_label1.setText(text1)
        self.info_label2.setText(text2)
        
    def update_plot(self):
        min_val = self.min_spin.value()
        max_val = self.max_spin.value()
        x = np.linspace(min_val, max_val, 1000)
        y = np.zeros_like(x, dtype=complex)  # 使用复数数组
        
        for controls in self.controls:
            pos = controls['position'].value()
            intensity = controls['intensity'].value()
            lw = controls['lorentz_width'].value()
            gw = controls['gauss_width'].value()
            
            if gw == 0:
                # 复数形式的洛伦兹线型
                y += intensity * (lw/2) / (x - pos + 1j*(lw/2))
            else:
                y += voigt(x, pos, intensity, lw, gw)
        
        # 加入非共振项
        nonres = self.real_spin.value() + 1j * self.imag_spin.value()
        y += nonres
        
        # 对复数结果取模平方
        y = np.abs(y)**2
        
        self.plot.clear()
        self.plot.plot(x, y, pen='k')
        
        # 连接非共振项的信号
        if not hasattr(self, '_nonres_connected'):
            self.real_spin.valueChanged.connect(self.update_plot)
            self.imag_spin.valueChanged.connect(self.update_plot)
            self._nonres_connected = True
        
        # 峰识别和计算
        peak_info = self.analyze_peaks(x, y)
        self.update_peak_info(peak_info)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VoigtSimulator()
    window.show()
    sys.exit(app.exec())
