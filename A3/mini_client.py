
import socket
import threading

# 创建 TCP 客户端
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接服务器
client.connect(("127.0.0.1", 5000))

# 用户自己输入昵称
name = input("请输入用户名：").strip()

# 把昵称发送给服务器
client.sendall((name + "\n").encode("utf-8"))#分隔符法解决沾包拆包
reader = client.makefile("r", encoding="utf-8")

# 等待服务器确认昵称
result = reader.readline().strip()

if result != "登录成功":
    print("登录失败：", result)
    client.close()


print(f"登录成功！欢迎 {name} 加入聊天室")
print("可以开始聊天，输入 ‘退出’ 退出")


#专门负责接收服务器消息
def receiveMessages():
    while True:
        message = reader.readline()
        print("\n" + message.rstrip("\r\n"))


#创建接收消息的线程
t = threading.Thread(
    target=receiveMessages,
    daemon=True
)
t.start()


#发送消息
while True:
    message = input()

    client.sendall(
        (message + "\n").encode("utf-8")
    )

    if message == "退出":
        break

client.close()












