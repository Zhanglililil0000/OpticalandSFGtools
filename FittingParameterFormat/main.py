import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QLineEdit
)
from PyQt6.QtGui import QDoubleValidator

class TextEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("科学数据格式化工具")
        self.setGeometry(100, 100, 1000, 400)
        
        # 创建主部件和主水平布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 创建左侧输入布局
        left_layout = QVBoxLayout()
        input_label = QLabel("输入数据（格式a±b）")
        left_layout.addWidget(input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("在此输入文本...")
        left_layout.addWidget(self.input_text)
        main_layout.addLayout(left_layout, stretch=2)
        
        # 创建中间控制区域
        control_layout = QVBoxLayout()
        control_layout.addStretch()
        
        # 处理按钮
        self.transfer_button = QPushButton("处理文本")
        self.transfer_button.clicked.connect(self.transfer_text)
        control_layout.addWidget(self.transfer_button)
        
        # 倍率输入
        factor_layout = QHBoxLayout()
        factor_label = QLabel("倍率:")
        self.factor_input = QLineEdit("1")
        self.factor_input.setValidator(QDoubleValidator(0.0001, 1000, 4))
        factor_layout.addWidget(factor_label)
        factor_layout.addWidget(self.factor_input)
        control_layout.addLayout(factor_layout)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout, stretch=1)
        
        # 创建中间输出布局
        middle_layout = QVBoxLayout()
        output_label = QLabel("格式化输出")
        middle_layout.addWidget(output_label)
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("格式化输出...")
        self.output_text.setReadOnly(True)
        middle_layout.addWidget(self.output_text)
        main_layout.addLayout(middle_layout, stretch=2)
        
        # 创建右侧输出布局
        right_layout = QVBoxLayout()
        clean_label = QLabel("无误差输出")
        right_layout.addWidget(clean_label)
        self.clean_output = QTextEdit()
        self.clean_output.setPlaceholderText("无误差输出...")
        self.clean_output.setReadOnly(True)
        right_layout.addWidget(self.clean_output)
        
        # 创建误差输出布局
        error_layout = QVBoxLayout()
        error_label = QLabel("误差输出")
        error_layout.addWidget(error_label)
        self.error_output = QTextEdit()
        self.error_output.setPlaceholderText("误差输出...")
        self.error_output.setReadOnly(True)
        error_layout.addWidget(self.error_output)
        
        # 添加右侧和误差布局到主布局
        right_group = QHBoxLayout()
        right_group.addLayout(right_layout)
        right_group.addLayout(error_layout)
        main_layout.addLayout(right_group, stretch=2)

    def transfer_text(self):
        """处理输入文本并格式化输出"""
        import re
        import math
        
        input_lines = self.input_text.toPlainText().split('\n')
        output_lines = []
        clean_lines = []
        error_lines = []
        
        for line in input_lines:
            # 匹配多种数值格式: "数值 +- 误差" 或 "数值 ± 误差" 或科学计数法(e/E)
            # Remove all whitespace from line before matching
            clean_line = re.sub(r'\s+', '', line)
            match = re.match(r'^([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)([\+\-\±]|\+\-)([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)$', clean_line)
            if match:
                # 获取倍率值，默认为1
                try:
                    factor = float(self.factor_input.text() or "1")
                except ValueError:
                    factor = 1.0
                
                value = float(match.group(1)) * factor
                error = float(match.group(3)) * factor  # 修正：从第三组获取误差值
                
                # 计算误差的数量级和有效数字
                if error == 0:
                    error_magnitude = 0
                    rounded_error = 0.0
                else:
                    error_magnitude = int(math.floor(math.log10(abs(error))))
                    first_digit = round(abs(error) / (10 ** error_magnitude), 1)
                    rounded_error = first_digit * (10 ** error_magnitude)
                
                # 根据误差调整数值精度
                rounded_value = round(value, -error_magnitude)
                
                # 格式化输出，避免科学计数法
                if abs(rounded_error) >= 1 or rounded_error == 0:
                    formatted_line = f"{rounded_value} ± {rounded_error:.1f}"
                else:
                    formatted_line = f"{rounded_value} ± {rounded_error:.1g}"
                
                output_lines.append(formatted_line)
                clean_lines.append(f"{rounded_value}")
                # 格式化误差输出，与主输出保持一致
                if abs(rounded_error) >= 1 or rounded_error == 0:
                    error_lines.append(f"{rounded_error:.1f}")
                else:
                    error_lines.append(f"{rounded_error:.1g}")
            else:
                output_lines.append(line)
                clean_lines.append(line)
                error_lines.append(line)
        
        self.output_text.setPlainText('\n'.join(output_lines))
        self.clean_output.setPlainText('\n'.join(clean_lines))
        self.error_output.setPlainText('\n'.join(error_lines))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextEditorApp()
    window.show()
    sys.exit(app.exec())
