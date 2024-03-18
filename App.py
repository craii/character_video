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
    return os.system(f"/Users/eliascheung/Documents/pythonscripts/pic_2_char/venv/bin/python /Users/eliascheung/Documents/pythonscripts/pic_2_char/video_to_char.py --VIDEO {VIDEO} --TEXT_COLOR '{TEXT_COLOR}' --BG_COLOR '{BG_COLOR}' --MOSAIC {MOSAIC} --PROCESS_NUM {PROCESS_NUM} --DELETE_FRAMES_AFTER_PROCESSED {DELETE_FRAMES_AFTER_PROCESSED}")



layout = [
    [sg.Text('选择：'), sg.InputText(key='VIDEO_OR_IMAGE', enable_events=True), sg.FilesBrowse(button_text='选择文件')],
    [sg.Text('文字颜色：'), sg.InputText(key='TEXT_COLOR', size=(10,1)), sg.ColorChooserButton('选择颜色')],
    [sg.Text('背景颜色：'), sg.InputText(key='BG_COLOR', size=(10,1)), sg.ColorChooserButton('选择颜色')],
    [sg.Checkbox('使用马', key='MOSAIC')],
    [sg.Text('进程数：'), sg.InputText(key='PROCESS_NUM')],
    [sg.Checkbox('处理后删除帧', key='DELETE_FRAMES_AFTER_PROCESSED')],
    [sg.Button('开始', key='START')]
]

window = sg.Window('数据分析，清洗表格', layout)

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
