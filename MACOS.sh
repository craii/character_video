#!/bin/bash

# 获取当前脚本的目录
SCRIPT_DIR=$(dirname $0)

# 调用Python脚本并传递目录参数
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

$VENV_PYTHON "$SCRIPT_DIR/App_Ps6.py"