import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SFG Data Processing")
        self.setGeometry(100, 100, 600, 400)
        
        # 主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 文件选择部分
        # File selection buttons
        self.create_file_selection(main_layout, "Select Quartz", "quartz_file")
        self.create_file_selection(main_layout, "Select Quartz BG", "quartz_bg_file")
        self.create_file_selection(main_layout, "Select Signal", "signal_file")
        self.create_file_selection(main_layout, "Select Signal BG", "signal_bg_file")
        
        # 参数输入部分 - 曝光时间在同一行
        exposure_layout = QHBoxLayout()
        # Exposure time inputs
        self.create_input_field(exposure_layout, "Quartz Exposure (s):", "quartz_exposure")
        self.create_input_field(exposure_layout, "Signal Exposure (s):", "signal_exposure")
        main_layout.addLayout(exposure_layout)
        
        # 可见波长和保存文件名在同一行
        bottom_row = QHBoxLayout()
        # Wavelength and output filename
        self.create_input_field(bottom_row, "Visible Wavelength (nm):", "visible_wavelength")
        self.create_input_field(bottom_row, "Output Filename:", "output_filename")
        main_layout.addLayout(bottom_row)
        
        # 处理按钮单独一行
        # Process button
        process_btn = QPushButton("Process Data")
        process_btn.clicked.connect(self.process_data)
        main_layout.addWidget(process_btn)
        
    def create_file_selection(self, layout, btn_text, file_type):
        """创建文件选择控件组"""
        group_layout = QVBoxLayout()
        
        # 按钮
        btn = QPushButton(btn_text)
        btn.clicked.connect(lambda: self.select_file(file_type))
        group_layout.addWidget(btn)
        
        # 文件路径显示
        label = QLabel("No file selected")
        label.setWordWrap(True)
        setattr(self, f"{file_type}_label", label)
        group_layout.addWidget(label)
        
        layout.addLayout(group_layout)
    
    def create_input_field(self, layout, label_text, field_name):
        """创建参数输入控件组"""
        label = QLabel(label_text)
        layout.addWidget(label)
        
        line_edit = QLineEdit()
        setattr(self, f"{field_name}_input", line_edit)
        layout.addWidget(line_edit)
    
    def select_file(self, file_type):
        """文件选择对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select {file_type.replace('_', ' ')} file", 
            "", "Data Files (*.csv *.asc);;CSV Files (*.csv);;ASC Files (*.asc);;All Files (*)"
        )
        
        if file_path:
            label = getattr(self, f"{file_type}_label")
            label.setText(file_path)
            setattr(self, f"{file_type}_path", file_path)
    
    def process_data(self):
        """处理数据按钮点击事件"""
        try:
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            import os
            
            # 获取输入参数
            quartz_path = getattr(self, 'quartz_file_path', None)
            quartz_bg_path = getattr(self, 'quartz_bg_file_path', None)
            signal_path = getattr(self, 'signal_file_path', None)
            signal_bg_path = getattr(self, 'signal_bg_file_path', None)
            
            if not all([quartz_path, quartz_bg_path, signal_path, signal_bg_path]):
                raise ValueError("Please select all required files")
                
            Tq = float(getattr(self, 'quartz_exposure_input').text())
            Ts = float(getattr(self, 'signal_exposure_input').text())
            visible_wavelength = float(getattr(self, 'visible_wavelength_input').text())
            output_filename = getattr(self, 'output_filename_input').text()
            
            if not output_filename:
                raise ValueError("Please enter output filename")
            
            # 读取数据文件
            def read_data(file_path):
                # 尝试读取前几行检测是否有表头
                with open(file_path, 'r') as f:
                    first_line = f.readline()
                    second_line = f.readline()
                
                # Check file extension and read accordingly
                if file_path.lower().endswith('.csv'):
                    # For CSV files, check if first line is header
                    has_header = not all(c.isdigit() or c in '.-+eE \t\n' for c in first_line.split(',')[0])
                    df = pd.read_csv(file_path, header=0 if has_header else None)
                elif file_path.lower().endswith('.asc'):
                    # For ASC files, try reading with space delimiter first
                    try:
                        df = pd.read_csv(file_path, delim_whitespace=True, header=None)
                        # If only one column, try comma delimiter
                        if len(df.columns) == 1:
                            df = pd.read_csv(file_path, header=None)
                    except:
                        # Fallback to standard CSV reader if space delimiter fails
                        df = pd.read_csv(file_path, header=None)
                return df.iloc[:, 0].values, df.iloc[:, 1].values
                
            # 读取并验证数据长度
            quartz_wl, quartz = read_data(quartz_path)
            quartz_bg_wl, quartz_bg = read_data(quartz_bg_path)
            signal_wl, signal = read_data(signal_path)
            signal_bg_wl, signal_bg = read_data(signal_bg_path)
            
            # 检查所有数据长度是否一致
            lengths = {
                '石英': len(quartz_wl),
                '石英背景': len(quartz_bg),
                '信号': len(signal),
                '信号背景': len(signal_bg)
            }
            
            if len(set(lengths.values())) > 1:
                error_msg = "Data length mismatch:\n"
                for name, length in lengths.items():
                    error_msg += f"{name}: {length} rows\n"
                raise ValueError(error_msg)
            
            # 计算波数 (cm^-1)
            wavenumber = (1/quartz_wl - 1/visible_wavelength) * 1e7
            
            # 计算SFG强度
            sfg_intensity = (signal - signal_bg)/Ts / ((quartz - quartz_bg)/Tq)
            
            # 获取信号文件所在目录
            output_dir = os.path.dirname(signal_path)
            
            # 保存结果为CSV
            output_df = pd.DataFrame({
                'Wavenumber(cm-1)': wavenumber,
                output_filename: sfg_intensity  # 使用保存的文件名作为列名
            })
            csv_path = os.path.join(output_dir, f"{output_filename}.csv")
            output_df.to_csv(csv_path, index=False)
            
            # 绘制图表并保存
            plt.figure(figsize=(10, 6))
            plt.plot(wavenumber, sfg_intensity)
            plt.xlabel('Wavenumber (cm$^{-1}$)')
            plt.ylabel(output_filename)  # 使用保存的文件名作为Y轴标签
            plt.title('SFG Spectrum')
            plt.grid(True)
            
            jpg_path = os.path.join(output_dir, f"{output_filename}.jpg")
            plt.savefig(jpg_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 显示完成弹窗
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Processing Complete")
            msg.setText(f"Data processed successfully! Results saved as:\n{csv_path}\n{jpg_path}")
            msg.exec()
            
            # 清空文件选择和保存文件名
            # Reset file selection labels
            for file_type in ['quartz_file', 'quartz_bg_file', 'signal_file', 'signal_bg_file']:
                label = getattr(self, f"{file_type}_label")
                label.setText("No file selected")
                setattr(self, f"{file_type}_path", None)
            
            getattr(self, 'output_filename_input').clear()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Processing Error", f"Error processing data: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
