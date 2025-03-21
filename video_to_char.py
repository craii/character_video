import os
import argparse
import subprocess
import multiprocessing
from pathlib import Path

import psutil
from PIL import Image
from PIL import ImageFont, ImageDraw
from typing import NewType, Union, Tuple, List

FRAME = NewType("FRAME", Image)

ascii_char = list('''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ''')


def get_char(r, g, b, alpha=256) -> str:
    """
    BT.709 标准 https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf 
    page 4, item 3.2

    """
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)  

    unit = (256.0 + 1)/length
    return ascii_char[int(gray/unit)]


def draw_text(text: str,
              text_color: Union[str, tuple],
              text_size: int,
              frame: FRAME,
              location: tuple, font: str = "w6.ttf") -> None:
    font = ImageFont.truetype(font, text_size)
    draw = ImageDraw.Draw(frame)
    draw.text(location, text, fill=text_color, font=font)


def pixelate_image_info(frame: FRAME, block_size: int) -> Tuple[FRAME, list]:
    # 确保块大小是整数且大于0
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be a positive integer")

    # 调整图片大小，使其成为块的整数倍
    width, height = frame.size
    new_width = int(width / block_size) * block_size
    new_height = int(height / block_size) * block_size
    frame = frame.resize((new_width, new_height))

    # 将图片分割成块
    coordinate_colors = list()
    pixels = frame.load()
    for i in range(0, new_width, block_size):
        for j in range(0, new_height, block_size):
            block = frame.crop((i, j, i + block_size, j + block_size))

            # 计算块的平均颜色
            avg_color = block.resize((1, 1)).getpixel((0, 0))
            # # (color, x, y)
            coordinate_colors.append((avg_color, i, j))

            # # 用平均颜色填充整个块
            for x in range(i, i + block_size):
                for y in range(j, j + block_size):
                    pixels[x, y] = avg_color

    return frame, coordinate_colors


def transfer_to_text(frame_src: str,
                     out_picture: str,
                     block_size: int = 10,
                     bg_color: str = "white",
                     text_color: str = "auto",
                     width: int = 0,
                     height: int = 0,
                     mosaic: bool = False,
                     text_size: int = 5) -> None:

    im = Image.open(frame_src)

    pixelate_image = pixelate_image_info(im, block_size)[0] if mosaic else im

    original_width = pixelate_image.width
    original_height = pixelate_image.height
    default_resized_width = 100

    actual_resized_width = default_resized_width if 0 in (width, height) else width
    actual_resized_height = int(default_resized_width * original_height / original_width) if 0 in (width, height) else height

    pixelate_image = pixelate_image.resize((actual_resized_width, actual_resized_height), Image.NEAREST)
    new_width, new_height = pixelate_image.width, pixelate_image.height

    # pixelate_image = np.array(pixelate_image)
    infos = list()
    for i in range(actual_resized_height):
        for j in range(actual_resized_width):
            pixel_color = pixelate_image.getpixel((j, i))
            text = get_char(*pixel_color)
            # text = get_char(*pixelate_image[j, i])
            infos.append(((i, j), text, pixel_color))

    new_image = Image.new("RGB", (new_width * text_size, new_height * text_size), color=bg_color)
    for info in infos:
        coordinate, text, color = info
        _color = color if text_color == "auto" else text_color
        draw_text(text=text, text_color=_color, text_size=text_size, frame=new_image, location=(coordinate[1] * text_size, coordinate[0] * text_size))
    new_image.save(f"{out_picture}")


class WorkerProcess(multiprocessing.Process):

    def __init__(self,
                 image_queue: multiprocessing.Queue,
                 input_folder: str,
                 output_folder: str,
                 text_color: str = "auto",
                 bg_color: str="white",
                 mosaic: bool = False):

        super().__init__()
        self.image_queue = image_queue
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.text_color = text_color
        self.mosaic = mosaic
        self.bg_color = bg_color

    def run(self):
        while True:
            # 从队列中获取图片路径
            image_path = self.image_queue.get()
            # 如果队列为空，则结束循环
            if image_path is None:
                break
            # 处理图片
            transfer_to_text(frame_src=f"{self.input_folder}/{image_path}",
                             out_picture=f"{self.output_folder}/out_{image_path}",
                             text_size=10,
                             block_size=20,
                             text_color=self.text_color,
                             bg_color=self.bg_color,
                             mosaic=self.mosaic)
            print(f"{self.input_folder}/{image_path} 处理完成！ -----> {self.output_folder}/out_{image_path}")


def frame_transfer_multiprocessor(input_folder: str,
                                  output_folder: str,
                                  process_num: int = 10,
                                  text_color: str = "auto",
                                  bg_color="white",
                                  mosaic: bool = False) -> List[multiprocessing.Process]:
    # 创建一个队列
    image_queue = multiprocessing.Queue()
    for frame in sorted([file for file in os.listdir(input_folder) if file.endswith("jpg")]):
        image_queue.put(frame)

    # 创建并启动进程
    num_worker_processes = process_num
    transfer_processes = []
    for i in range(num_worker_processes):
        _process = WorkerProcess(image_queue, input_folder, output_folder, text_color=text_color, bg_color=bg_color, mosaic=mosaic)
        _process.start()
        transfer_processes.append(_process)

    for i in range(num_worker_processes):
        image_queue.put(None)

    for _process in transfer_processes:
        _process.join()

    print("All images have been processed.")
    return transfer_processes


if __name__ in "__main__":
    parser = argparse.ArgumentParser(description="Transfer a normal video into ASCII one")

    parser.add_argument("--VIDEO", type=str, help="Path to the video file")
    parser.add_argument("--TEXT_COLOR", type=str, default="auto",
                        help="Color of the text overlay. If 'auto', it will be automatically calculated.")
    parser.add_argument("--BG_COLOR", type=str, default="white",
                        help="Background color")
    parser.add_argument("--MOSAIC", type=str, help="Whether to apply mosaic effect", default="no")
    parser.add_argument("--PROCESS_NUM", type=int, default=10, help="Number of processes to use")
    parser.add_argument("--DELETE_FRAMES_AFTER_PROCESSED", type=str, default="no",
                        help="Whether to delete frames after processing")

    # parse args
    args = parser.parse_args()
    video_path = Path(args.VIDEO).resolve()
    VIDEO = f"{video_path}"
    TEXT_COLOR = args.TEXT_COLOR  # 如果是auto，则自动计算颜色，提取自原视频
    BG_COLOR = args.BG_COLOR
    MOSAIC = True if args.MOSAIC == "yes" else False
    PROCESS_NUM = args.PROCESS_NUM
    DELETE_FRAMES_AFTER_PROCESSED = True if args.DELETE_FRAMES_AFTER_PROCESSED == "yes" else False



    installed_at = Path(__file__).resolve().parent
    print(f"install {installed_at}-------------------{VIDEO}-----------------{psutil.WINDOWS}")

    # 预设原视频帧文件夹/处理帧文件夹
    tmp_frames_folder = f"{installed_at}/tmp_frames"
    out_frames_folder = f"{installed_at}/out_frames"
    if not os.path.exists(tmp_frames_folder):
        os.mkdir(tmp_frames_folder)
    if not os.path.exists(out_frames_folder):
        os.mkdir(out_frames_folder)


    # 获取视频帧率
    ffprobe_path = f"{installed_at}/ffprobe.exe" if psutil.WINDOWS else f"{installed_at}/ffprobe"
    command_get_rate = f"{ffprobe_path} -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 {VIDEO}"

    process = subprocess.Popen(command_get_rate, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    rate, sec = output.decode('utf-8').split("/")
    VIDEO_RATE = int(int(rate) / int(sec))
    print(VIDEO_RATE, psutil.WINDOWS)


    #视频处理
    ffmpeg_path = f"{installed_at}/ffmpeg.exe" if psutil.WINDOWS else f"{installed_at}/ffmpeg"

    os.system(f"{ffmpeg_path} -i {VIDEO} -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 {installed_at}/tmp_frames/frame%08d.jpg")
    processors = frame_transfer_multiprocessor(input_folder=tmp_frames_folder,
                                               output_folder=out_frames_folder,
                                               process_num=PROCESS_NUM,
                                               text_color=TEXT_COLOR,
                                               bg_color=BG_COLOR,
                                               mosaic=MOSAIC)


    command_rebuild_video = f"{ffmpeg_path} -r {VIDEO_RATE} -i {installed_at}/out_frames/out_frame%08d.jpg -i {VIDEO} -map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -pix_fmt yuv420p {video_path.parent}/out_{'mosaic' if MOSAIC else ''}_{video_path.name}"
    # os.system()
    rebuild_process = subprocess.Popen(command_rebuild_video, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = rebuild_process.communicate()
    print(f"Process Finished... result:{output}, err: {error}")
    if DELETE_FRAMES_AFTER_PROCESSED:
        for tmp_frame in [f"{tmp_frames_folder}/{file}" for file in os.listdir(tmp_frames_folder)]:
            os.remove(tmp_frame)

        for out_frame in [f"{out_frames_folder}/{file}" for file in os.listdir(out_frames_folder)]:
            os.remove(out_frame)
