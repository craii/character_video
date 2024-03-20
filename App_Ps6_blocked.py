from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QColorDialog, QCheckBox
import os
import sys
import psutil
from pathlib import Path


def kill_python_processes():
    # 获取系统中所有进程
    for proc in psutil.process_iter():
        try:
            # 获取进程的名称
            proc_name = proc.name()

            # 如果进程名称包含"python"，则杀死该进程
            if 'python' in proc_name.lower():
                proc.kill()
                print(f"Killed process: {proc_name}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def long_perform(VIDEO, TEXT_COLOR, BG_COLOR, MOSAIC, PROCESS_NUM, DELETE_FRAMES_AFTER_PROCESSED):
    '''
    VIDEO = args.VIDEO
    TEXT_COLOR = args.TEXT_COLOR  # 如果是auto，则自动计算颜色，提取自原视频
    BG_COLOR = args.BG_COLOR
    MOSAIC = args.MOSAIC
    PROCESS_NUM = args.PROCESS_NUM
    DELETE_FRAMES_AFTER_PROCESSED = args.DELETE_FRAMES_AFTER_PROCESSED
    :return:
    '''
    installed_path = Path(__file__).resolve().parent
    command_win = f"{installed_path}/venv/Scripts/python.exe {installed_path}/video_to_char.py --VIDEO {VIDEO} --TEXT_COLOR {TEXT_COLOR} --BG_COLOR {BG_COLOR} --MOSAIC {MOSAIC} --PROCESS_NUM {PROCESS_NUM} --DELETE_FRAMES_AFTER_PROCESSED {DELETE_FRAMES_AFTER_PROCESSED}"
    command_mac = f"{installed_path}/venv/bin/python {installed_path}/video_to_char.py --VIDEO {VIDEO} --TEXT_COLOR '{TEXT_COLOR}' --BG_COLOR '{BG_COLOR}' --MOSAIC {MOSAIC} --PROCESS_NUM {PROCESS_NUM} --DELETE_FRAMES_AFTER_PROCESSED {DELETE_FRAMES_AFTER_PROCESSED}"
    command = command_win if psutil.WINDOWS else command_mac
    return os.system(command)

class VideoToASCIIConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('视频转字符画')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        self.video_input_layout = QHBoxLayout()
        self.video_label = QLabel('选择视频：')
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText('视频路径')
        self.video_browse_button = QPushButton('选择文件')
        self.video_browse_button.clicked.connect(self.select_video_file)
        self.video_input_layout.addWidget(self.video_label)
        self.video_input_layout.addWidget(self.video_input)
        self.video_input_layout.addWidget(self.video_browse_button)

        self.text_color_layout = QHBoxLayout()
        self.text_color_label = QLabel('文字颜色：')
        self.text_color_input = QLineEdit('auto')
        self.text_color_input.setFixedWidth(100)
        self.select_text_color_button = QPushButton('选择颜色')
        self.select_text_color_button.clicked.connect(self.select_text_color)
        self.text_color_layout.addWidget(self.text_color_label)
        self.text_color_layout.addWidget(self.text_color_input)
        self.text_color_layout.addWidget(self.select_text_color_button)

        self.bg_color_layout = QHBoxLayout()
        self.bg_color_label = QLabel('背景颜色：')
        self.bg_color_input = QLineEdit('white')
        self.bg_color_input.setFixedWidth(100)
        self.select_bg_color_button = QPushButton('选择颜色')
        self.select_bg_color_button.clicked.connect(self.select_bg_color)
        self.bg_color_layout.addWidget(self.bg_color_label)
        self.bg_color_layout.addWidget(self.bg_color_input)
        self.bg_color_layout.addWidget(self.select_bg_color_button)

        self.process_num_layout = QHBoxLayout()
        self.process_num_label = QLabel('进程数：')
        self.process_num_input = QLineEdit('10')
        self.process_num_input.setFixedWidth(100)
        self.process_num_layout.addWidget(self.process_num_label)
        self.process_num_layout.addWidget(self.process_num_input)

        self.options_layout = QHBoxLayout()
        self.delete_frames_checkbox = QCheckBox('转换后删除帧')
        self.delete_frames_checkbox.setChecked(True)
        self.mosaic_checkbox = QCheckBox('马赛克化')
        self.options_layout.addWidget(self.delete_frames_checkbox)
        self.options_layout.addWidget(self.mosaic_checkbox)

        self.start_button = QPushButton('开始')
        self.start_button.clicked.connect(self.start_conversion)

        self.layout.addLayout(self.video_input_layout)
        self.layout.addLayout(self.text_color_layout)
        self.layout.addLayout(self.bg_color_layout)
        self.layout.addLayout(self.process_num_layout)
        self.layout.addLayout(self.options_layout)
        self.layout.addWidget(self.start_button)

    def select_video_file(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, '选择视频文件', '.', '视频文件 (*.mp4 *.avi *.mov)')
        if filename:
            self.video_input.setText(filename)

    def select_text_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.text_color_input.setText(color.name())

    def select_bg_color(self):
        color_dialog = QColorDialog()
        color = color_dialog.getColor()
        if color.isValid():
            self.bg_color_input.setText(color.name())

    def start_conversion(self):
        video_or_image = self.video_input.text()
        text_color = self.text_color_input.text()
        bg_color = self.bg_color_input.text()
        mosaic = "yes" if self.mosaic_checkbox.isChecked() else "no"
        process_num = int(self.process_num_input.text()) if self.process_num_input.text().isdigit() else 6
        delete_frames_after_processed = "yes" if self.delete_frames_checkbox.isChecked() else "no"
        print("\n\n视频：{}\n"
              "字色：{}\n"
              "背景：{}\n"
              "马赛克：{}，{}\n"
              "进程：{}\n"
              "后续：{}, {}\n".format(video_or_image, text_color, bg_color, mosaic, type(mosaic), process_num, delete_frames_after_processed, type(delete_frames_after_processed)))
        # Perform the conversion here
        # Call your conversion function with the parameters
        long_perform(VIDEO=video_or_image, TEXT_COLOR=text_color, BG_COLOR=bg_color, MOSAIC=mosaic,
                     PROCESS_NUM=process_num, DELETE_FRAMES_AFTER_PROCESSED=delete_frames_after_processed)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter_window = VideoToASCIIConverter()
    converter_window.show()
    sys.exit(app.exec())
