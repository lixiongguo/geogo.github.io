import gym
import time
import matplotlib.pyplot as plt
import cv2
import numpy as np

import imageio.v2 as imageio
import os


# def preprcoessing(obs):
#     obs = cv2.cvtColor(cv2.resize(obs,(60,40)),cv2.COLOR_BGR2GRAY)
#     # _,obs = cv2.threshold(obs,127,255,cv2.THRESH_BINARY)
#     print(obs.shape)
#     return obs
         
env = gym.make('MountainCar-v0',render_mode='human') #render_mode='human'
state,_ = env.reset()
step,done = 0,False
while not done and step<10000:
    action = 2
    next_state, reward, done, *rest = env.step(action)
    # frame = env.render()
    # cv2.imwrite(f'frame_{step}.jpg',frame)
    step += 3
env.close()

# image_name = 'tmp/frame_1.jpg'
# plt.imshow(plt.imread(image_name))
# plt.show()

# # 图像文件所在的目录
# image_folder = './tmp2/'

# # 输出的 GIF 文件名
# output_gif = 'output.gif'

# # 获取图像文件列表
# images = []
# for filename in sorted(os.listdir(image_folder)):
#     if filename.endswith('.png') or filename.endswith('.jpg'):
#         file_path = os.path.join(image_folder, filename)
#         images.append(imageio.imread(file_path))

# # 将图像列表保存为 GIF
# imageio.mimsave(output_gif, images, duration=0.5)  # duration 参数控制每帧的显示时间
