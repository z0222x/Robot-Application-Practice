
import socket
import threading

# 创建字典，保存所有在线用户
clients = {}

# 线程锁 避免共享资源同一时刻被多个用户用
clients_lock = threading.Lock()


# 将消息转发给其他所有在线客户
def broadcast(message):
    with clients_lock:
        for tem1 in clients.values():
                tem1.sendall(
                    (message + "\n").encode("utf-8")
                )



#每个客户端由一个独立线程处理
def getThread(conn, addr):
    name = None
    joined = False#判断客户是否退出
    reader = None

    # 按行读取客户端发送的数据  解决沾包关键 按行读取
    reader = conn.makefile("r", encoding="utf-8")

    # 客户端连接后，首先发送用户名
    name = reader.readline().strip() #strip删除首尾空白

    # 将用户名和连接存入字典
    with clients_lock:
        if not name:
            conn.sendall(
                "昵称为空\n".encode("utf-8")
            )
            return

        conn.sendall("登录成功\n".encode("utf-8"))
        clients[name] = conn
        joined = True

        print("当前在线用户：", list(clients.keys()))

    # 将消息转发给其他所有在线客户
    broadcast(f"[系统] {name} 加入了聊天室")

    # 持续接收这个客户端的消息
    while True:
        data = reader.readline()#等待接收数据

        # 客户端断开连接
        if not data:
            break
        #删除字符串末尾连续出现的 回车\r 和 换行\n 字符
        message = data.rstrip("\r\n")

        # 用户主动退出
        if message == "退出":
            break

        if message.strip():
            print(f"{name} 发送：{message}")

            # 转发给所有在线客户端
            broadcast(f"[{name}] {message}")

    # 客户端退出，删除字典里的记录
    if joined:
        with clients_lock:
            del clients[name] #删除用户
            print("当前在线用户：", list(clients.keys()))

        broadcast(f"[系统] {name} 离开了聊天室")

    #释放资源
    reader.close()
    conn.close()


#创建 TCP 服务器  ipv4地址  TCP字节流
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("127.0.0.1", 5000))

#监听
server.listen()

print("服务器启动，等待客户端连接")


# 接收新客户端
while True:
    conn, addr = server.accept()

    print("新客户端地址：", addr)

    # 为每个客户端创建独立线程
    t = threading.Thread(
        target=getThread,
        args=(conn, addr),
        daemon=True
    )

    t.start()




