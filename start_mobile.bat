@echo off
chcp 65001 > nul
echo ========================================================
echo                 huo-zhe-ma 手机启动脚本
echo ========================================================
echo.
echo 正在列出本机所有IP地址:
ipconfig | findstr "IPv4"
echo.
echo 请找到形如 192.168.x.x 的地址。
echo 手机浏览器访问: http://[你的IP地址]:5000
echo.
echo 注意：请确保电脑防火墙允许 Python 访问网络 (公用/专用网络都勾选)
echo.
echo ========================================================
echo 按任意键启动服务器...
pause > nul

py webapp.py
pause
