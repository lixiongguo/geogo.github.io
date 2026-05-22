import cv2
import numpy as np
import glob

# 设置棋盘格参数
CHECKERBOARD = (9, 6)  # 内角点数目 (width, height)
square_size = 0.025    # 每个格子的实际物理尺寸（单位：米，例如 25mm = 0.025m）

# 准备世界坐标（Z=0 平面）
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= square_size

# 存储所有图像的3D点和2D点
objpoints = []  # 3D 点（世界坐标）
imgpoints = []  # 2D 点（图像像素坐标）

# 读取所有棋盘格图像
images = glob.glob('calibration_images/*.jpg')  # 替换为你的图像路径

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 寻找棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    if ret:
        objpoints.append(objp)
        # 亚像素级角点优化
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # 可选：可视化角点
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv2.imshow('Corners', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# 相机标定
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("相机内参矩阵 (Intrinsic Matrix):\n", mtx)
print("畸变系数 (Distortion Coefficients):\n", dist.ravel())