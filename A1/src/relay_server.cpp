#include <boost/asio.hpp>
#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>

#include <cstdlib>
#include <deque>
#include <iostream>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <windows.h>

namespace net = boost::asio;
namespace beast = boost::beast;
namespace websocket = beast::websocket;
using tcp = net::ip::tcp;

class Session;


class Room {//管理当前所有客户端
public:
    void join(const std::shared_ptr<Session>& session);//添加客户
    void leave(const std::shared_ptr<Session>& session);//删除客户
    void broadcast(const std::string& json);//给所有客户广播
private:
    std::set<std::shared_ptr<Session>> sessions;//存储当前客户
};

//负责与客户端通信
class Session : public std::enable_shared_from_this<Session> {//在类中可使用session共享指针
public:
    Session(tcp::socket&& s, Room& r)
        : ws(std::move(s)), room(r) {}

    void start() {
        //设置websocket握手的超时配置（握手前期准备工作）
        ws.set_option(websocket::stream_base::timeout::suggested(beast::role_type::server));
        //设置通道读取大小16384 字节
        ws.read_message_max(16 * 1024);
        //应用层握手（异步）
        auto self = shared_from_this();//类中调用指向自己的指针 通过继承enable_shared_from_this<Session>此模板类实现
        ws.async_accept([self](beast::error_code ec) {
            if (ec) {
                std::cerr << "应用层握手失败: " << ec.message() << '\n';
                return;
            }
            self->room.join(self);
            self->read_next();//读取当前客户端发来的下一步信息（异步）
        });
    }

    //向客户发送消息
    void send(const std::string& json) {
        bool busy = outbox.empty();//判断现在队列是否为空
        outbox.push_back(std::make_shared<std::string>(json));
        //在加入此消息前 由于异步操作 要看队列是空 证明没消息发送 这样才能将这条消息发出
        if (busy) write_next();
    }

private:
    websocket::stream<tcp::socket> ws;
    beast::flat_buffer buffer;//缓冲区 保存临时对象
    Room& room;
    std::deque<std::shared_ptr<std::string>> outbox;//保存要等待发送的消息

    //异步接收客户端消息
    void read_next() {
        auto self = shared_from_this();
        ws.async_read(buffer, [self](beast::error_code ec, std::size_t b) {
            if (ec) {
                self->room.leave(self);//当前客户端已经不在 可以移除
                return;
            }
            const std::string json = beast::buffers_to_string(self->buffer.data());//将缓冲区json转化为字符串
            self->buffer.consume(self->buffer.size());
            // Only relay JSON-shaped text frames; browsers also validate fields.
            if (self->ws.got_text() && json.size() < 16000 && !json.empty() && json.front() == '{') {
                self->room.broadcast(json);
            }
            self->read_next();
        });
    }

    void write_next() {
        ws.text(true);//发送模式设置为文本

        auto self = shared_from_this();
        //发送消息
        ws.async_write(net::buffer(*outbox.front()),
            [self](beast::error_code ec, std::size_t b) {
                if (ec) {
                    self->room.leave(self);
                    return;
                }
                self->outbox.pop_front();
                //还有消息 继续发送
                if (!self->outbox.empty()) self->write_next();
            });
    }
};

void Room::join(const std::shared_ptr<Session>& se) {
    sessions.insert(se);
}
void Room::leave(const std::shared_ptr<Session>& se) {
    sessions.erase(se);
}
void Room::broadcast(const std::string& json) {
    for (const auto& session : sessions) session->send(json);
}

int main() {
    
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);



    net::io_context io;
    Room room;//存客户
    tcp::acceptor acceptor(io);//监听TCP连接
    //设置网络通信端点   127.0.0.1仅监听本机
    tcp::endpoint endpoint(net::ip::make_address("127.0.0.1"), 9002);
    //按协议打开Tcp连接  ipv4
    acceptor.open(endpoint.protocol());
    acceptor.set_option(net::socket_base::reuse_address(true));
    acceptor.bind(endpoint);//绑定地址
    acceptor.listen();//开始监听
    std::cout << "服务器开始监听 ws://127.0.0.1:9002\n";
    

    // 异步接收客户端
    std::function<void()> accept_next;//可调用对象包装器
    accept_next = [&]() {
        acceptor.async_accept([&](beast::error_code ec, tcp::socket socket) {//异步tcp连接
            if (!ec) std::make_shared<Session>(std::move(socket), room)->start();//传输层连接后 调用应用层连接
            else std::cerr << "Tcp连接出错: " << ec.message() << '\n';
            accept_next();//继续接收
            });
    };
    accept_next();
    io.run();//异步循环 回调控制操作
   
}
