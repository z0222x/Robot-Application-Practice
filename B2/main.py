
import numpy as np
from scipy.spatial.transform import Rotation



#法兰在机器人基座坐标系下的位姿
P_BASE_FLANGE = [0.420, 0.150, 0.560]
RPY_BASE_FLANGE = [150, 0, 45]

# 夹爪中心相对法兰的位姿
P_FLANGE_GRIPPER = [0.000, 0.000, 0.165]
RPY_FLANGE_GRIPPER = [0, 0, 90]

#工件相对夹爪中心的位姿
P_GRIPPER_OBJECT = [0.025, 0.000, 0.060]
RPY_GRIPPER_OBJECT = [0, 0, 0]

#下料时工件的目标位姿
P_BASE_OBJECT_TARGET = [0.350, -0.450, 0.090]
RPY_BASE_OBJECT_TARGET = [180, 0, 0]



#位姿转换函数
def pose_to_matrix(position, rpy_deg):

    rotation = Rotation.from_euler(
        'xyz', rpy_deg, degrees=True
    )

    T = np.eye(4)

    T[:3, :3] = rotation.as_matrix()
    T[:3, 3] = position

    return T

#清理浮点计算产生的极小误差
def clean(values):

    values = np.array(values, dtype=float).copy()
    values[np.abs(values) < 1e-12] = 0.0

    return values


def print_pose(title, T):

    #平移坐标
    position = clean(T[:3, 3])

    #旋转矩阵
    rotation = Rotation.from_matrix(T[:3, :3])

    #将旋转矩阵转为rpy
    rpy = clean(
        rotation.as_euler('xyz', degrees=True)
    )

    #旋转矩阵转四元数
    quaternion = clean(rotation.as_quat())


    print(title)

    print("平移 (m)：")
    print(f"X = {position[0]:.6f}")
    print(f"Y = {position[1]:.6f}")
    print(f"Z = {position[2]:.6f}")

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

#两矩阵最大绝对误差
def max_error(A, B):

    return np.max(np.abs(A - B))



# 法兰在基座坐标系下的位姿
T_base_flange = pose_to_matrix(
    P_BASE_FLANGE,
    RPY_BASE_FLANGE
)

# 夹爪在法兰坐标系下的位姿
T_flange_gripper = pose_to_matrix(
    P_FLANGE_GRIPPER,
    RPY_FLANGE_GRIPPER
)

# 工件在夹爪坐标系下的位姿
T_gripper_object = pose_to_matrix(
    P_GRIPPER_OBJECT,
    RPY_GRIPPER_OBJECT
)



#夹爪在基座坐标系下的位姿
T_base_gripper = (
    T_base_flange @ T_flange_gripper
)

#工件在基座坐标系下的位姿
T_base_object = (
    T_base_gripper @ T_gripper_object
)

print_pose(
    "夹爪在基座坐标系下的位姿",
    T_base_gripper
)

print_pose(
    "工件在基座坐标系下的位姿",
    T_base_object
)


# 将夹爪安装关系和工件相对夹爪的关系合并得到工件相对于法兰的位置
T_flange_object = (
    T_flange_gripper @ T_gripper_object
)


print("固定安装链合并结果")
print("T_flange_object =")
print(clean(T_flange_object))

print_pose(
    "法兰到工件的合并位姿",
    T_flange_object
)



#反向校验：工件位姿反解回法兰位姿

T_base_flange_recovered = (
    T_base_object @ np.linalg.inv(T_flange_object)
)

reverse_error = max_error(
    T_base_flange_recovered,
    T_base_flange
)


print("反向校验")

print(f"反向校验误差：{reverse_error:.12e}")

if reverse_error < 1e-9:
    print("反向校验通过！")
else:
    raise RuntimeError("反向校验失败！")



#下料放置：计算法兰目标位姿

# 工件在料盘中的目标位姿
T_base_object_target = pose_to_matrix(
    P_BASE_OBJECT_TARGET,
    RPY_BASE_OBJECT_TARGET
)

# 根据目标工件位姿反解法兰目标位姿
T_base_flange_target = (
    T_base_object_target
    @ np.linalg.inv(T_flange_object)
)

print_pose(
    "下料时机器人法兰的目标位姿",
    T_base_flange_target
)


#回代验证：工件是否到达目标位置

# 使用计算出的法兰目标位姿重新计算工件位姿
T_base_object_check = (
    T_base_flange_target @ T_flange_object
)

placement_error = max_error(
    T_base_object_check,
    T_base_object_target
)


print("下料回代验证")
print(f"下料回代误差：{placement_error:.12e}")

if placement_error < 1e-9:
    print("下料回代验证通过！")
else:
    raise RuntimeError("下料回代验证失败！")

















