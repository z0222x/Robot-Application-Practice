
import numpy as np
from scipy.spatial.transform import Rotation


# 相机内参
FX = 800.0
FY = 800.0
CX = 640.0
CY = 360.0

# 视觉检测结果
U = 720.0
V = 280.0
Z_CAMERA = 0.400

# 相机在机器人基座坐标系下的位姿
P_BASE_CAMERA = [0.700, -0.200, 1.000]
RPY_BASE_CAMERA = [180, 0, 15]

# 夹爪相对法兰的位姿
P_FLANGE_GRIPPER = [0.000, 0.000, 0.165]
RPY_FLANGE_GRIPPER = [0, 0, 45]

# 圆盘工件姿态  圆盘平放在水平台面上，法向竖直
RPY_BASE_OBJECT = [180, 0, 0]



def pose_to_matrix(position, rpy_deg):

    rotation = Rotation.from_euler(
        'xyz', rpy_deg, degrees=True
    )

    T = np.eye(4)

    T[:3, :3] = rotation.as_matrix()
    T[:3, 3] = position

    return T


def clean(values):

    values = np.array(values, dtype=float).copy()
    values[np.abs(values) < 1e-12] = 0.0
    return values


def max_error(A, B):

    return np.max(np.abs(A - B))




def print_pose(title, T):

    position = clean(T[:3, 3])#拿矩阵前三行第四列

    rotation_matrix = clean(T[:3, :3])#前三行三列

    #旋转对象
    rotation = Rotation.from_matrix(
        T[:3, :3]
    )

    #欧拉角
    rpy = clean(
        rotation.as_euler('xyz', degrees=True)
    )

    #四元函数
    quaternion = clean(
        rotation.as_quat()
    )


    print(title)

    print("\n平移 (m)：")
    print(f"X = {position[0]:.6f}")
    print(f"Y = {position[1]:.6f}")
    print(f"Z = {position[2]:.6f}")

    print("\n旋转矩阵：")
    for row in rotation_matrix:
        print(
            "[" + ", ".join(
                f"{v: .10f}" for v in row
            ) + "]"
        )

    print("\nRPY (deg)：")
    print(f"Rx = {rpy[0]:.6f}")
    print(f"Ry = {rpy[1]:.6f}")
    print(f"Rz = {rpy[2]:.6f}")

    print("\n四元数 (x, y, z, w)：")
    print(
        "(" + ", ".join(
            f"{v:.10f}" for v in quaternion
        ) + ")"
    )


#像素坐标反投影：像素坐标 到 相机坐标

def pixel_to_camera():

    #根据针孔相机模型进行反投影
    #x坐标
    x_camera = (U - CX) * Z_CAMERA / FX
    #y坐标
    y_camera = (V - CY) * Z_CAMERA / FY
    #z坐标
    z_camera = Z_CAMERA

    p_camera = np.array([
        x_camera,
        y_camera,
        z_camera
    ])

    print("像素坐标反投影：像素坐标到相机坐标")

    print(f"像素坐标：u = {U}, v = {V}")
    print(f"深度：Z = {Z_CAMERA:.6f} m")

    print("\n圆盘中心在相机坐标系下的坐标：")

    print(f"Xc = {x_camera:.6f} m")
    print(f"Yc = {y_camera:.6f} m")
    print(f"Zc = {z_camera:.6f} m")

    return p_camera



#相机坐标到基地坐标
def camera_to_base(p_camera):

    # 相机在基底坐标下的变换矩阵
    T_base_camera = pose_to_matrix(
        P_BASE_CAMERA,
        RPY_BASE_CAMERA
    )

    #将三维点扩展为齐次坐标
    p_camera_h = np.append(
        p_camera, 1.0
    )

    p_base_h = T_base_camera @ p_camera_h

    #得到三位坐标
    p_base = p_base_h[:3]

    print("相机坐标到基地坐标")

    print("\n圆盘中心在基座坐标系下的坐标：")

    print(f"X = {p_base[0]:.6f} m")
    print(f"Y = {p_base[1]:.6f} m")
    print(f"Z = {p_base[2]:.6f} m")

    return p_base


#工件的完整6DoF位姿  x y z rx ry rz

def calculate_object_pose(p_base):#p_base 圆盘中心在机器人坐标下的位置

    #工件在基低坐标系下的完整位姿矩阵
    T_base_object = pose_to_matrix(
        p_base,
        RPY_BASE_OBJECT
    )

    print_pose(
        "工件在机器人基座坐标系下的完整位姿",
        T_base_object
    )

    return T_base_object




def main():

    # 第一步：像素坐标转换为相机坐标
    p_camera = pixel_to_camera()

    # 第二步：相机坐标转换为机器人基座坐标
    p_base = camera_to_base(p_camera)

    # 第三步：计算圆盘工件完整位姿
    calculate_object_pose(p_base)



if __name__ == "__main__":
    main()










