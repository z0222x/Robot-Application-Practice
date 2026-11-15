# 演示
A1演示.mp4

# 实现
浏览器中通过 Three.js 绘制 3D 场景与蓝色方块
C++ 控制程序发送目标位置、速度及多个路径点
C++ WebSocket 服务端转发 JSON 指令到浏览器
页面按照速度（单位/秒）到达目标


# 环境准备（Windows 11 + VS2022 + CMake）

VS2022 的C++桌面开发
Boost 头文件（vcpkg安装）


# Windows 编译

在PowerShell中执行camk命令

cmake -S . -B build -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=D:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release


即可生成对应.exe运行文件：
relay_server.exe
controller.exe`

