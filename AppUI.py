import os
import psutil
from pathlib import Path
import PySimpleGUI as sg


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



layout = [
    [sg.Text('选择视频：'), sg.InputText(key='VIDEO_OR_IMAGE', enable_events=True), sg.FilesBrowse(button_text='选择文件')],
    [sg.Text('文字颜色：'), sg.InputText(key='TEXT_COLOR', default_text="auto", size=(10,1)), sg.ColorChooserButton('选择颜色', key='SELECT_T_COLOR')],
    [sg.Text('背景颜色：'), sg.InputText(key='BG_COLOR', default_text="white", size=(10,1)), sg.ColorChooserButton('选择颜色', key='SELECT_B_COLOR')],
    [sg.Text('进程数：'), sg.InputText(default_text="10", key='PROCESS_NUM')],
    [sg.Checkbox('转换后删除帧', default=True, key='DELETE_FRAMES_AFTER_PROCESSED'), sg.Checkbox('马赛克化', key='MOSAIC')],
    [sg.Button('开始', key='START')]
]

window = sg.Window('视频转字符画', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WINDOW_CLOSED:
        kill_python_processes()
        break
    elif event == 'START':
        video_or_image = values['VIDEO_OR_IMAGE']
        text_color = values['TEXT_COLOR']
        bg_color = values['BG_COLOR']
        mosaic = "yes" if values['MOSAIC'] else "no"
        process_num = int(values['PROCESS_NUM']) if values['PROCESS_NUM'].isdigit() else 6
        delete_frames_after_processed = "yes" if values['DELETE_FRAMES_AFTER_PROCESSED'] else "no"
        print(f"\n\n视频：{video_or_image}\n"
              f"字色：{text_color}\n"
              f"背景：{bg_color}\n"
              f"马赛克：{mosaic}，{type(mosaic)}\n"
              f"进程：{process_num}\n"
              f"后续：{delete_frames_after_processed}, {type(delete_frames_after_processed)}\n"
              )
        #window.perform_long_operation(lambda : long_perform(VIDEO=video_or_image, TEXT_COLOR=text_color, BG_COLOR=bg_color, MOSAIC=mosaic, PROCESS_NUM=process_num, DELETE_FRAMES_AFTER_PROCESSED=delete_frames_after_processed), end_key="perform_finished")
        window.start_thread(lambda: long_perform(VIDEO=video_or_image, TEXT_COLOR=text_color, BG_COLOR=bg_color, MOSAIC=mosaic, PROCESS_NUM=process_num, DELETE_FRAMES_AFTER_PROCESSED=delete_frames_after_processed), end_key="perform_finished")

        # 禁用所有组件
        for key in values:
            window[key].update(disabled=True)
        window['START'].update(disabled=True)
    elif event == "perform_finished":
        for key in values:
            if key != "perform_finished":
                window[key].update(disabled=False)
        window['START'].update(disabled=False)

kill_python_processes()
window.close()
