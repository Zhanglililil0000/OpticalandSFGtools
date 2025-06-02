import os
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QPushButton, QListWidget, QFileDialog,
                            QHBoxLayout, QLabel, QSpinBox)
from PyQt6.QtCore import Qt

class SparkRemoveUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_paths = []

    def initUI(self):
        self.setWindowTitle('Spark Removal Tool')
        self.setGeometry(300, 300, 400, 400)
        
        # Create file list container
        self.file_list = QListWidget()
        
        # Create parameter controls
        param_layout = QHBoxLayout()
        
        # Window size control
        window_label = QLabel('Window Size:')
        self.window_spin = QSpinBox()
        self.window_spin.setRange(5, 100)
        self.window_spin.setValue(15)
        
        # Threshold multiplier control
        threshold_label = QLabel('Threshold Multiplier:')
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 10)
        self.threshold_spin.setValue(3)
        
        param_layout.addWidget(window_label)
        param_layout.addWidget(self.window_spin)
        param_layout.addWidget(threshold_label)
        param_layout.addWidget(self.threshold_spin)
        
        # Create button area
        btn_layout = QHBoxLayout()
        
        # Create select files button
        self.select_btn = QPushButton('Select Files')
        self.select_btn.clicked.connect(self.select_files)
        
        # Create clear list button
        self.clear_btn = QPushButton('Clear List')
        self.clear_btn.clicked.connect(self.clear_files)
        
        # Create process files button
        self.process_btn = QPushButton('Process Files')
        self.process_btn.clicked.connect(self.process_files)
        
        # Add buttons to layout
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.process_btn)
        
        # Set main layout
        layout = QVBoxLayout()
        layout.addWidget(self.file_list)
        layout.addLayout(param_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 'Select Data Files', '', 'Data Files (*.csv *.asc);;CSV Files (*.csv);;ASC Files (*.asc)')
        if files:
            self.file_paths = files
            self.file_list.clear()
            for file in files:
                self.file_list.addItem(file)
    
    def clear_files(self):
        self.file_paths = []
        self.file_list.clear()
    
    def process_files(self):
        for file_path in self.file_paths:
            try:
                # 读取并保存原始数据
                try:
                    if file_path.lower().endswith('.asc'):
                        # 读取ASC文件
                        original_data = pd.read_csv(file_path, sep='\s+', header=None, engine='python')
                    else:
                        # 读取CSV文件
                        original_data = pd.read_csv(file_path, header=None)
                    
                    if len(original_data.columns) < 2:
                        raise ValueError("File must have at least 2 columns")
                    
                    # 检查是否有表头行
                    try:
                        wavelength = original_data.iloc[:, 0].astype(float).values
                        intensity = original_data.iloc[:, 1].astype(float).values
                    except ValueError:
                        # 如果有表头，跳过第一行
                        original_data = pd.read_csv(file_path, header=0)
                        wavelength = original_data.iloc[:, 0].astype(float).values
                        intensity = original_data.iloc[:, 1].astype(float).values
                except Exception as e:
                    raise ValueError(f"Failed to read file: {str(e)}")
                
                # 处理异常值 - 使用滑动窗口检测局部异常
                window_size = self.window_spin.value()
                threshold_mult = self.threshold_spin.value()
                n = len(intensity)
                is_outlier = np.zeros(n, dtype=bool)
                
                for i in range(n):
                    # 计算窗口边界
                    start = max(0, i - window_size//2)
                    end = min(n, i + window_size//2 + 1)
                    
                    # 获取窗口内数据(排除当前点)
                    window_data = np.concatenate([intensity[start:i], intensity[i+1:end]])
                    
                    if len(window_data) > 0:
                        # 计算窗口内中位数和MAD
                        window_median = np.median(window_data)
                        window_mad = np.median(np.abs(window_data - window_median))
                        
                        # 计算阈值并检测异常
                        threshold = window_median + threshold_mult * 1.4826 * window_mad
                        if intensity[i] > threshold:
                            is_outlier[i] = True
                
                x = np.arange(len(intensity))
                f = interp1d(x[~is_outlier], intensity[~is_outlier], 
                            kind='linear', fill_value='extrapolate')
                intensity[is_outlier] = f(x[is_outlier])
                
                # 保存处理结果
                dir_path, file_name = os.path.split(file_path)
                base_name = file_name.replace('.csv', '')
                output_file = os.path.join(
                    dir_path, 
                    f"{base_name}-sparkremoved.csv"
                )
                
                # 保存CSV
                pd.DataFrame({
                    'Wavelength': wavelength,
                    'Intensity': intensity
                }).to_csv(output_file, index=False, header=False)
                
                # 绘制对比图
                if hasattr(original_data, 'iloc'):
                    original_wavelength = original_data.iloc[:, 0].values
                    original_intensity = original_data.iloc[:, 1].values
                    
                    # 尝试多种中文字体
                    try:
                        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']  # 设置中文字体
                        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                    except:
                        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 回退字体
                    
                    plt.figure(figsize=(10, 6))
                    plt.plot(original_wavelength, original_intensity, 'r-', label='Original Data')
                    plt.plot(wavelength, intensity, 'b-', label='Processed Data')
                    plt.xlabel('Wavelength')
                    plt.ylabel('Intensity')
                    plt.title(f'{base_name} Data Processing Comparison')
                    plt.legend()
                    plt.grid(True)
                    
                    # 保存图片
                    image_file = os.path.join(dir_path, f"{base_name}-comparison.jpg")
                    plt.savefig(image_file, dpi=300, bbox_inches='tight')
                    plt.close()
                
                self.file_list.addItem(f"Processing complete: {output_file} (with comparison chart)")
                
            except Exception as e:
                error_msg = f"Processing failed {file_path}: {str(e)}"
                print(error_msg)  # 输出到控制台
                self.file_list.addItem(error_msg)

def main():
    app = QApplication(sys.argv)
    ex = SparkRemoveUI()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
