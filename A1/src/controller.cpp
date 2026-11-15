#include <boost/asio.hpp>//网络通信 提供tcp IP地址解析等
#include <boost/beast/core.hpp>//
#include <boost/beast/websocket.hpp>//webSocket通信

#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <windows.h>

//方便
namespace net = boost::asio;
namespace beast = boost::beast;
namespace websocket = beast::websocket;
using tcp = net::ip::tcp;

struct Waypoint {//方块运动目标点  x y z speed
    double x, y, z, speed;
};


//提取控制台输入参数 raw接收原始字符串  result存放提取出来的坐标和速度
bool parse_waypoint(const std::string& raw, Waypoint& result) {
    std::istringstream in(raw);//输入流
    std::string extra;//判断用户是否输入多余内容
    if (!(in >> result.x >> result.y >> result.z >> result.speed) || (in >> extra)) return false;
    return std::isfinite(result.x) && std::isfinite(result.y) &&
           std::isfinite(result.z) && std::isfinite(result.speed) &&
           std::abs(result.x) <= 20 && std::abs(result.y) <= 20 &&
           std::abs(result.z) <= 20 && result.speed > 0 && result.speed <= 10;
}


//生成json数据
std::string waypoint_json(const Waypoint& p) {
    std::ostringstream out;//输出流
    //拼接json格式数据
    out << std::setprecision(10) << "{\"x\":" << p.x
        << ",\"y\":" << p.y << ",\"z\":" << p.z
        << ",\"speed\":" << p.speed << '}';
    return out.str();
}

void help() {
    std::cout << "\n命令:\n";
    std::cout << "  move 4 0 2 2         让方块移动(4,0,2) 速度为2单位每秒\n";
    std::cout << "  path 2 0 0 2;2 0 3 1;0 0 3 2  让方块依次经过多个目标点\n";
    std::cout << "  帮助                 显示帮助\n";
    std::cout << "  退出                 退出程序\n";
}

int main() {
    
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);


    net::io_context io;//网络管理I/O操作过程对象
    tcp::resolver resolver(io);//创建一个 TCP 地址解析器 将主机名和服务名转换成可以连接的 TCP 端点
    websocket::stream<tcp::socket> ws(io);//基于TCP的流对象 建立可靠的双向通信（应用层）
    net::connect(ws.next_layer(), resolver.resolve("127.0.0.1", "9002"));//建立TCP连接  ws.next_layer() ws为应层 此函数是调用传输层TCP对象
    ws.handshake("127.0.0.1:9002", "/");//建立底层 TCP 连接后，还需要进行协议握手，才能进行ws消息收发（同步）
    std::cout << "连接成功\n";
    help();

    std::string line;
    while (std::cout << "\ncmd> " && std::getline(std::cin, line)) {//读取整行并保存到line
        if (line == "退出" || line == "exit") break;
        if (line == "帮助") { help(); continue; }

        std::string json;
        if (line.rfind("move ", 0) == 0) {//是否以move开头
            Waypoint point{};
            if (!parse_waypoint(line.substr(5), point)) {
                std::cout << "格式或者范围错误\n";
                continue;
            }
            json = "{\"type\":\"move\",\"target\":" + waypoint_json(point) + "}";
        }
        else if (line.rfind("path ", 0) == 0) {
            std::vector<Waypoint> points;
            
            const std::string body = line.substr(5);
            std::istringstream parts(body);
            std::string item;
            bool valid = true;
            while (std::getline(parts, item, ';')) {
                Waypoint point{};
                if (!parse_waypoint(item, point)) { valid = false; break; }
                points.push_back(point);
                if (points.size() > 20) { valid = false; break; }
            }
            if (!valid || points.empty()) {
                std::cout << "路径无效\n";
                continue;
            }
            std::ostringstream out;
            out << "{\"type\":\"path\",\"waypoints\":[";
            for (std::size_t i = 0; i < points.size(); ++i) {
                if (i) out << ',';
                out << waypoint_json(points[i]);
            }
            out << "]}";
            json = out.str();
        }
        else {
            std::cout << "无此命令\n";
            continue;
        }

        ws.write(net::buffer(json));//发送消息  buffer其目的是为了显示此数据地址 多长
    }
    ws.close(websocket::close_code::normal);


       
}
