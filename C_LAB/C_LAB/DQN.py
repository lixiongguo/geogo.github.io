import torch
import torch.nn.functional as F
import numpy as np
import torch.nn as nn
import collections
import random

import cv2

empty_frame = np.zeros((40, 90), dtype=np.float32)
empty_state = np.stack((empty_frame, empty_frame), axis=0)
# empty_state = np.zeros((1,40, 90), dtype=np.float32)
      

    
class VAnet(torch.nn.Module):
    ''' 只有一层隐藏层的A网络和V网络 '''
    def __init__(self,action_dim):
        super(VAnet, self).__init__()
        self.conv1 = nn.Conv2d(4, 32, kernel_size=8, stride=4, padding=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        # self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        # self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        # self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 5 * 7, 120)
        self.fc2 = nn.Linear(120, 84)

        self.fc_A = torch.nn.Linear(84, action_dim)
        self.fc_V = torch.nn.Linear(84, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        # x = torch.flatten(x, 1)
        x = x.view(-1, 64 * 4 * 11)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        A = self.fc_A(x)
        V = self.fc_V(x)
       
        Q = V + A - A.mean(1).view(-1, 1)  # Q值由V值和A值计算得到
        return Q

    

class Qnet(torch.nn.Module):
    
    def __init__(self,action_dim):
        super().__init__()
        self.conv1 = nn.Conv2d(2, 4, kernel_size=3)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3)
        self.conv3 = nn.Conv2d(8, 8, kernel_size=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(320, 32) # 64 * 4 * 7 #64* 4 * 11
        self.fc2 = nn.Linear(32, 64)
        self.fc3 = nn.Linear(64, 128)
        self.out = nn.Linear(128, action_dim)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = torch.flatten(x, 1)
        # x = x.view(-1, 64 * 4 * 11)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.out(x)
        return x
class DQN:

    def __init__(self,   action_dim, learning_rate, gamma,
                 epsilon, target_update, device):
        self.action_dim = action_dim
        # self.q_net = VAnet(action_dim).to(device)  # Q网络
        # self.target_q_net = VAnet(action_dim).to(device)
        self.q_net = Qnet(action_dim).to(device)  # Q网络
        self.target_q_net = Qnet(action_dim).to(device)
        self.optimizer = torch.optim.Adam(self.q_net.parameters(),lr=learning_rate)
        self.gamma = gamma  # 折扣因子
        self.epsilon = epsilon  # epsilon-贪婪策略
        self.target_update = target_update  # 目标网络更新频率
        self.count = 0  # 计数器,记录更新次数
        self.device = device

    def take_action(self): 
        if np.random.random() < self.epsilon:
            action = np.random.randint(self.action_dim)
        else:
            state = self.current_state
            state = torch.tensor(np.array([state]), dtype=torch.float).to(self.device)    #增加batch轴
            action = self.q_net(state).argmax().item()
        return action

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'],dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions']).view(-1, 1).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'],dtype=torch.float).view(-1, 1).to(self.device)
        q_values = self.q_net(states).gather(1, actions)  # Q值
        # 下个状态的最大Q值
        max_next_q_values = self.target_q_net(next_states).max(1)[0].view(-1, 1)
        #Double DQN
        # max_action = self.q_net(next_states).max(1)[1].view(-1, 1) 
        # max_next_q_values = self.target_q_net(next_states).gather(1, max_action)
        q_targets = rewards + self.gamma * max_next_q_values * (1 - dones)  # TD误差目标
        # print(q_values[0],q_targets[0])
        dqn_loss = torch.mean(F.mse_loss(q_values, q_targets))  # 均方误差损失函数
        self.optimizer.zero_grad()  # PyTorch中默认梯度会累积,这里需要显式将梯度置为0
        dqn_loss.backward()  # 反向传播更新参数
        self.optimizer.step()

        if self.count % self.target_update == 0:
            self.target_q_net.load_state_dict(self.q_net.state_dict())  # 更新目标网络
        self.count += 1
        
    def set_initial_state(self, obs=None):
        self.current_state = empty_state
        self.last_obs = obs
    def preprocess(self,frame):
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        frame = frame[160:300,180:420]
        frame = cv2.resize(frame,(90,40))
        frame = np.asarray(frame).astype(np.float32)
        frame = 255 -frame
        frame = frame/255.
        # frame = frame[::2, ::2, 0]  # 每两个像素采样一次
        # frame = frame.astype('float32') / 255.0  # 归一化
        return frame
    
    def get_state_from_obs(self, o_next):
        next_state = np.append(self.current_state[1:,:,:], o_next.reshape((1,)+o_next.shape), axis=0)
        # next_state = o_next-self.last_obs
        # next_state = next_state[np.newaxis,:]
        return next_state
    
    def store_transition(self, o_next, action, reward, terminal):
        next_state = o_next-self.last_obs
        next_state = next_state[np.newaxis,:]
        self.replay_memory.add(self.current_state, action, reward, next_state, terminal)
        
        if not terminal:
            self.last_obs = o_next
            self.current_state = next_state

    def set_next_state(self, o_next):
        next_state = self.get_state_from_obs(o_next)
        self.last_obs = o_next
        self.current_state = next_state

    def save_model(self):
        torch.save(self.q_net.state_dict(), 'dqn.pth')

    def load_model(self):
        self.q_net.load_state_dict(torch.load('dqn.pth', map_location='cpu'))


