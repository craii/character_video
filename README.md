# character_video
 transfer a normal video frames to character ones 

# manual
## step 1
创建虚拟环境：
```python -m venv venv_win``````

启动虚拟环境：
win: ```.\venv_win\Scripts\activate```

macOS: ```source ./venv_win/bin/activate```

## step 2
如果你不需要 UI, 直接运行
```pip install -r requirements.txt```
如果你需要 UI,请额外安装 pyside6
```pip install pyside6```

## step 3 (optional)
install ffmpeg
下载地址 [ffmpeg](https://www.ffmpeg.org/download.html) 下载之后将 ffmpeg.exe, ffprobe.exe (macOS则是：ffmpeg, ffprobe， 或通过homebrew安装)放到本项目根目录下。如果你已经在使用ffmpeg并且已经添加到 path，可跳过此步骤

## step 4
check video_to_char.py, modify the "VIDEO" and run ```python video_to_char.py ```

## result
| original| result |
|----------|----------|
| ![](https://github.com/craii/character_video/blob/main/original.png)|![](https://github.com/craii/character_video/blob/main/result.png) |
