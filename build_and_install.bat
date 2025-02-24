@echo off
REM 设置项目根目录
SET PROJECT_ROOT=%~dp0

REM 设置控制台编码为 UTF-8
chcp 65001
REM 进入项目根目录
cd /d %PROJECT_ROOT%

REM 打包项目
echo 打包项目...
python setup.py sdist bdist_wheel

REM 检查打包是否成功
IF %ERRORLEVEL% NEQ 0 (
    echo 打包失败，请检查错误信息。
    pause
    exit /b %ERRORLEVEL%
)

REM 查找最新的打包文件
FOR /F "delims=" %%i IN ('dir /b /o:-d dist\tuner-*.whl') DO SET LATEST_WHEEL=%%i & GOTO :FOUND
:FOUND

REM 卸载现有的tuner包
echo 卸载现有的tuner包...
pip uninstall -y tuner

REM 检查卸载是否成功
IF %ERRORLEVEL% NEQ 0 (
    echo 卸载失败，请检查错误信息。
    pause
    exit /b %ERRORLEVEL%
)

REM 安装打包文件
echo 安装打包文件 %LATEST_WHEEL%...
pip install --upgrade dist\%LATEST_WHEEL%

REM 检查安装是否成功
IF %ERRORLEVEL% NEQ 0 (
    echo 安装失败，请检查错误信息。
    pause
    exit /b %ERRORLEVEL%
)

echo 打包和安装成功！
pause
exit /b 0