import os
from pathlib import Path
from PIL import Image
from PIL import ImageFont, ImageDraw
from typing import NewType, Union, Tuple

Picture = NewType("Picture", Image)

ascii_char = list('''$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ''')


def get_char(r, g, b, alpha=256):
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)  # BT.709 标准

    unit = (256.0 + 1)/length
    return ascii_char[int(gray/unit)]


def draw_text(text: str,
              text_color: Union[str, tuple],
              text_size: int,
              picture: Picture,
              location: tuple, font: str = "w6.ttf"):
    font = ImageFont.truetype(font, text_size)
    draw = ImageDraw.Draw(picture)
    draw.text(location, text, fill=text_color, font=font)


def pixelate_image_info(picture: Picture, block_size: int) -> Tuple[Picture, list]:
    # 确保块大小是整数且大于0
    block_size = int(block_size)
    if block_size <= 0:
        raise ValueError("block_size must be a positive integer")

    # 调整图片大小，使其成为块的整数倍
    width, height = picture.size
    new_width = int(width / block_size) * block_size
    new_height = int(height / block_size) * block_size
    picture = picture.resize((new_width, new_height))

    # 将图片分割成块
    coordinate_colors = list()
    pixels = picture.load()
    for i in range(0, new_width, block_size):
        for j in range(0, new_height, block_size):
            block = picture.crop((i, j, i + block_size, j + block_size))

            # 计算块的平均颜色
            avg_color = block.resize((1, 1)).getpixel((0, 0))
            # # (color, x, y)
            coordinate_colors.append((avg_color, i, j))

            # # 用平均颜色填充整个块
            for x in range(i, i + block_size):
                for y in range(j, j + block_size):
                    pixels[x, y] = avg_color

    return picture, coordinate_colors


def transfer_to_text(picture: str,
                     out_picture: str,
                     block_size: int = 10,
                     bg_color: str = "white",
                     text_color: str = "black",
                     width: int = 0,
                     height: int = 0,
                     mosaic: bool = False,
                     text_size: int = 5) -> None:

    im = Image.open(picture)

    pixelate_image = pixelate_image_info(im, block_size)[0] if mosaic else im

    original_width = pixelate_image.width
    original_height = pixelate_image.height
    default_resized_width = 100

    actual_resized_width = default_resized_width if 0 in (width, height) else width
    actual_resized_height = int(default_resized_width * original_height / original_width) if 0 in (width, height) else height

    pixelate_image = pixelate_image.resize((actual_resized_width, actual_resized_height), Image.NEAREST)
    new_width, new_height = pixelate_image.width, pixelate_image.height

    infos = list()
    for i in range(actual_resized_height):
        for j in range(actual_resized_width):
            text = get_char(*pixelate_image.getpixel((j, i)))
            infos.append(((i, j), text))

    new_image = Image.new("RGB", (new_width * text_size, new_height * text_size), color=bg_color)
    for info in infos:
        coordinate, text = info
        draw_text(text, text_color, text_size, picture=new_image, location=(coordinate[1] * text_size, coordinate[0] * text_size))
    new_image.save(f"{out_picture}")


if __name__ in "__main__":
    VIDEO = "test.MP4"

    installed_at = Path(__file__).resolve().parent
    tmp_frames_folder = f"{installed_at}/tmp_frames"
    out_frames_folder = f"{installed_at}/out_frames"

    os.system(f"ffmpeg -i {VIDEO} -qscale:v 1 -qmin 1 -qmax 1 -vsync 0 {installed_at}/tmp_frames/frame%08d.jpg")

    tmp_frames_uri = sorted([file for file in os.listdir(tmp_frames_folder) if file.endswith("jpg")])
    # print(tmp_frames_uri)
    for frame in tmp_frames_uri:
        transfer_to_text(picture=f"{tmp_frames_folder}/{frame}", out_picture=f"{out_frames_folder}/out_{frame}", text_size=10, block_size=20, mosaic=False)
        print(f"{frame} 处理完成！")

    os.system(f"ffmpeg -i {installed_at}/out_frames/out_frame%08d.jpg -i {VIDEO} -map 0:v:0 -map 1:a:0 -c:a copy -c:v libx264 -r 23.98 -pix_fmt yuv420p output_{VIDEO}")
