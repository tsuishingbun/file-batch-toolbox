@echo off
chcp 65001 >nul
title FileBatchToolbox - 文件批量处理工具箱
echo ==========================================
echo   FileBatchToolbox v1.0.0
echo   批量文件处理工具箱
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Pillow是否安装
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo [!] 正在安装依赖...
    pip install Pillow
    if errorlevel 1 (
        echo [错误] 安装依赖失败，请手动运行: pip install Pillow
        pause
        exit /b 1
    )
)

echo [OK] 环境检查通过
echo.
echo 开始运行工具...
echo.

REM 运行工具
python "%~dp0file_batch_toolbox.py"

pause
