import numpy as np
import trimesh
import matplotlib.pyplot as plt
import matplotlib.tri as tri

# 创建一个平面圆盘作为透镜的基础
radius = 1.0  # 圆盘半径
resolution = 64  # 圆盘的分辨率

# 生成圆盘的顶点
theta = np.linspace(0, 2*np.pi, resolution, endpoint=False)  # 不包含最后一个点，避免重复
r = np.linspace(0, radius, resolution//2)
T, R = np.meshgrid(theta, r)
X = R * np.cos(T)
Y = R * np.sin(T)
Z = np.zeros_like(X)
# 将网格转换为三角网格
vertices_2d = np.column_stack([X.ravel(), Y.ravel()])
triangulation = tri.Triangulation(vertices_2d[:, 0], vertices_2d[:, 1])

# 创建双面透镜（需要厚度）
# 上表面顶点
vertices_top = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
print(len(vertices_top))

# 下表面顶点（与上表面相同，但z坐标为负）
thickness = 0.1  # 透镜厚度
vertices_bottom = vertices_top.copy()
vertices_bottom[:, 2] -= thickness

# 合并顶点
vertices = np.vstack([vertices_top])

# 创建面
# 上表面面
faces_top = triangulation.triangles.copy()
# 下表面面（需要反转顶点顺序）
faces_bottom = faces_top.copy()
faces_bottom[:, [0, 1, 2]] = faces_bottom[:, [1, 0, 2]]
faces_bottom += len(vertices_top)  # 调整索引

# 侧面连接 - 修复版本
faces_side = []
num_radial = resolution//2  # 径向分辨率
num_angular = resolution      # 角度分辨率

# 只连接外圈顶点（r > 0）形成侧面
for i in range(num_angular):
    for j in range(num_radial - 1):  # 不包括中心点
        # 获取四个顶点的索引
        # 上表面索引
        top_idx1 = j * num_angular + i
        top_idx2 = (j + 1) * num_angular + i
        top_idx3 = j * num_angular + (i + 1) % num_angular
        top_idx4 = (j + 1) * num_angular + (i + 1) % num_angular
        
        # 下表面索引
        bottom_idx1 = top_idx1 + len(vertices_top)
        bottom_idx2 = top_idx2 + len(vertices_top)
        bottom_idx3 = top_idx3 + len(vertices_top)
        bottom_idx4 = top_idx4 + len(vertices_top)
        
        # 创建四个三角面来连接上下表面
        # 侧面由四个三角形组成
        faces_side.append([top_idx1, top_idx2, bottom_idx1])
        faces_side.append([bottom_idx1, bottom_idx2, top_idx2])


# 合并所有面
faces = np.vstack([faces_top])

# 现在修改上表面为抛物面
# 选择上表面的顶点
selected_vertices = np.arange(len(vertices_top))

# 获取选中顶点的 x, y 坐标
x = vertices[selected_vertices, 0]
y = vertices[selected_vertices, 1]

# 定义抛物面：z = a*(x^2 + y^2)
# 这将创建一个向外凸出的抛物面
a = 0.5  # 抛物面曲率
z_offset = a * (x**2 + y**2)

# 修改选中顶点的 z 值
new_vertices = vertices.copy()
new_vertices[selected_vertices, 2] += 0.5 - z_offset

# 创建新的网格
lens_mesh = trimesh.Trimesh(vertices=new_vertices, faces=faces, process=False)

# 可视化
fig = plt.figure(figsize=(12, 6))

# 凸透镜
lens_mesh.show()

# 导出为PLY文件
lens_mesh.export('parabolic_lens_flat3.ply')
print("以平面为基础的凸透镜模型已保存为 parabolic_lens_flat2.ply")