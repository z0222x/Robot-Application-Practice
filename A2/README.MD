
# Linux选择

这个题通过VMware创建 Ubuntu 虚拟机 并将项目部署在虚拟机中

# 网络模式选择

采用 桥接网络

原因：
虚拟机可以通过桥接网络获取局域网内的独立 IP 地址
Windows 主机可以直接通过虚拟机 IP 访问部署的网站
无需额外配置 NAT 端口转发，便于主机与虚拟机之间进行网络通信


# Docker部署

# 项目文件传输

在 Ubuntu 虚拟机中安装共享文件夹：
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop


挂载共享目录：
sudo mkdir -p /mnt/hgfs
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other


将共享目录中的项目复制到 Ubuntu 用户目录：
cp -a /mnt/hgfs/cpp_threejs_control ~/cpp_threejs_control

# Docker环境

在 Ubuntu 虚拟机中安装 Docker 及 Docker Compose：
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker


# Docker 容器部署

进入传输完成的项目目录：
cd ~/cpp_threejs_control


通过 Docker Compose自动构建镜像并启动服务：
sudo docker compose up -d --build


# 主机访问虚拟机网站

在 Windows 主机浏览器中输入对应ip地址, 能够正常打开网页，项目成功部署到 Ubuntu Linux 虚拟机，并实现了 Windows 主机对虚拟机网站的访问







