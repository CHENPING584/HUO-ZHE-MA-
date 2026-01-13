@echo off
echo ========================================================
echo                 huo-zhe-ma 手机启动脚本
echo ========================================================
echo.
echo 正在获取局域网IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set IP=%%a
)
set IP=%IP: =%

echo.
echo 请确保手机和电脑连接同一个Wi-Fi！
echo.
echo 手机浏览器访问地址: http://%IP%:5000
echo.
echo ========================================================
echo 按任意键启动服务器...
pause > nul

py webapp.py
pause