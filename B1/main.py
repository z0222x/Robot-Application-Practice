
import numpy as np #数值计算库
from scipy.spatial.transform import Rotation as Rotation #三维空间旋转



# 工件在机器人基座坐标系下的位姿
P_BASE_OBJECT = np.array([0.520, -0.180, 0.120]) #x y z
RPY_BASE_OBJECT = [180, 0, -30] #绕x y z轴旋转

#夹爪中心相对于法兰的位姿
P_FLANGE_GRIPPER = np.array([0.000, 0.000, 0.165])
RPY_FLANGE_GRIPPER = [0, 0, 45]



#RPY 转换为齐次变换矩阵
def pose_to_matrix(position, rpy_deg):#位置 rpy角度

    #将欧拉角转换为旋转对象
    rotation = Rotation.from_euler(#固定轴坐标轴XYZ旋转顺序  单位为角度
        'xyz', rpy_deg, degrees=True
    )

    T = np.eye(4)#4×4单位矩阵

    # rotation.as_matrix()将rotation转换为3×3的旋转矩阵
    #将矩阵写在前3行前3列
    T[:3, :3] = rotation.as_matrix()
    #将其写在第最后一列前三行
    T[:3, 3] = position

    return T



#方法一：使用齐次变换矩阵计算
def calculate_by_matrix():

    #计算工件的齐次变换矩阵
    T_base_object = pose_to_matrix(
        P_BASE_OBJECT,
        RPY_BASE_OBJECT
    )

    #计算夹爪的齐次变换矩阵
    T_flange_gripper = pose_to_matrix(
        P_FLANGE_GRIPPER,
        RPY_FLANGE_GRIPPER
    )

   #题目给的 夹爪相对于法兰的位置  np.linalg.inv(T_flange_gripper)求逆得到 法兰相对夹爪的位置
    #矩阵相乘得到法兰相对基地的位置
    T_base_flange = (
        T_base_object @ np.linalg.inv(T_flange_gripper)
    )

    return T_base_flange


#方法二：使用四元数计算
def calculate_by_quaternion():

    #as_quat()将旋转对象转换成四元数
    q_base_object = Rotation.from_euler(
        'xyz', RPY_BASE_OBJECT, degrees=True
    ).as_quat()

    q_flange_gripper = Rotation.from_euler(
        'xyz', RPY_FLANGE_GRIPPER, degrees=True
    ).as_quat()

    #四元数创建旋转对象
    R_base_object = Rotation.from_quat(q_base_object)
    R_flange_gripper = Rotation.from_quat(q_flange_gripper)

    #计算法兰在基座坐标系下的旋转
    R_base_flange = (
        R_base_object * R_flange_gripper.inv()
    )

    # 计算法兰平移  apply把夹爪相对于法兰的平移向量，旋转到基座坐标系中
    P_base_flange = (
        P_BASE_OBJECT
        - R_base_flange.apply(P_FLANGE_GRIPPER)
    )

    # 组合成齐次变换矩阵，方便交叉验证
    T = np.eye(4)

    T[:3, :3] = R_base_flange.as_matrix()
    T[:3, 3] = P_base_flange#进行齐次比较

    return T, R_base_flange



#输出计算结果
def clean(values):
    values = np.array(values, dtype=float).copy()
    values[np.abs(values) < 1e-12] = 0.0
    return values


def main():

    #齐次变换矩阵计算
    T_matrix = calculate_by_matrix()

    #四元数计算
    T_quaternion, R_quaternion = calculate_by_quaternion()

    # 交叉验证
    error = np.max(
        np.abs(T_matrix - T_quaternion)
    )

    print("机器人末端法兰位姿反解")

    print("\n【交叉验证】")
    print(f"两种方法最大误差：{error:.12e}")

    if error < 1e-9:
        print("验证通过！误差小于 1e-9")
    else:
        raise RuntimeError("交叉验证失败！")

    # 提取平移、旋转矩阵、RPY、四元数

    #提取法兰平移坐标 pose_to_matrix有此函数得 前3行第4列为平移坐标
    position = clean(T_matrix[:3, 3])
     #提取旋转坐标  前三行前三列
    rotation_matrix = clean(T_matrix[:3, :3])

    # 旋转矩阵转 RPY
    rpy = Rotation.from_matrix(
        T_matrix[:3, :3]
    ).as_euler('xyz', degrees=True)

    rpy = clean(rpy)#清理浮点误差

    # 获取四元数 x, y, z, w
    quaternion = clean(R_quaternion.as_quat())


    print("\n 法兰平移坐标")
    print(
        f"X = {position[0]:.6f} m\n"
        f"Y = {position[1]:.6f} m\n"
        f"Z = {position[2]:.6f} m"
    )

    print("\n旋转矩阵")
    for row in rotation_matrix:
        print(
            "[" + ", ".join(f"{v: .10f}" for v in row) + "]"
        )

    print("\nRPY 姿态")
    print(
        f"Rx = {rpy[0]:.6f} deg\n"
        f"Ry = {rpy[1]:.6f} deg\n"
        f"Rz = {rpy[2]:.6f} deg"
    )

    print("\n四元数 (x, y, z, w)")
    print(
        "(" + ", ".join(f"{v:.10f}" for v in quaternion) + ")"
    )



if __name__ == "__main__":
    main()













