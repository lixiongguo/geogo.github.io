import torch
import torch.nn.functional as F
import numpy as np
import torch.nn as nn
import collections
import random

import cv2

empty_frame = np.zeros((40, 90), dtype=np.float32)
empty_state = np.stack((empty_frame, empty_frame,empty_frame,empty_frame), axis=0)
# empty_state = np.zeros((1,40, 90), dtype=np.float32)
      

class PolicyNet(torch.nn.Module):
    
    def __init__(self,action_dim):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 32, kernel_size=8, stride=4, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64* 4 * 11, 128) # 64 * 4 * 7 #64* 4 * 11
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 32)
        self.out = nn.Linear(32, action_dim)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.softmax(self.out(x))
        return x
    
class PolicyNet2(torch.nn.Module):
    def __init__(self, state_dim = 4, hidden_dim =128, action_dim = 2):
        super(PolicyNet2, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return F.softmax(self.fc2(x), dim=1)
        
class PolicyGradient:

    def __init__(self,action_dim, learning_rate, gamma,device):
        self.policy_net = PolicyNet(action_dim).to(device) 
        # self.policy_net = PolicyNet2().to(device)
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(),lr=learning_rate)
        self.gamma = gamma
        self.device = device
        self.current_state = empty_state
        
    def take_action(self): 
        state = torch.tensor(np.array([self.current_state]), dtype=torch.float).to(self.device)  #增加batch轴
        probs = self.policy_net(state)
        Categroy = torch.distributions.Categorical(probs)
        action = Categroy.sample().item()
        return action

    def update(self, transition_dict):
        # states = torch.tensor(transition_dict['states'],dtype=torch.float).to(self.device)
        # actions = torch.tensor(transition_dict['actions']).view(-1, 1).to(self.device)
        # rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        # next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        # dones = torch.tensor(transition_dict['dones'],dtype=torch.float).view(-1, 1).to(self.device)

        # probs = self.policy_net(states)
        # probs = torch.gather(probs, dim=1, index=actions)
        # log_probs = torch.log(probs)
        
        # for i in reversed(range(len(rewards)-1)):
        #     rewards[i] = rewards[i] + self.gamma * rewards[i+1] * (1 - dones[i+1])

        # policy_loss = -torch.mean(torch.sum(rewards*log_probs)) 
        # self.optimizer.zero_grad()  
        # policy_loss.backward()  
        # self.optimizer.step()

        #在线策略，所以不是一个batch了
        reward_list = transition_dict['rewards']
        state_list = transition_dict['states']
        action_list = transition_dict['actions']

        G = 0
        self.optimizer.zero_grad()
        for i in reversed(range(len(reward_list))):  # 从最后一步算起
            reward = reward_list[i]
            state = torch.tensor([state_list[i]],dtype=torch.float).to(self.device)
            action = torch.tensor([action_list[i]]).view(-1, 1).to(self.device)
            log_prob = torch.log(self.policy_net(state).gather(1, action))
            G = self.gamma * G + reward
            loss = -log_prob * G  # 每一步的损失函数
            loss.backward()  # 反向传播计算梯度
        self.optimizer.step()  # 梯度下降
    def set_initial_state_gt(self, state=None):
        self.current_state = state
        self.last_obs = state

    def set_initial_state(self, obs=None):
        self.current_state = empty_state
        self.last_obs = obs

    def get_state_from_obs(self, o_next):
        next_state = np.append(self.current_state[1:,:,:], o_next.reshape((1,)+o_next.shape), axis=0)
        # next_state = o_next #o_next-self.last_obs
        # next_state = next_state[np.newaxis,:]
        return next_state
    

    def set_next_state(self, o_next):
        next_state = self.get_state_from_obs(o_next)
        self.last_obs = o_next
        self.current_state = next_state

    def set_next_state_gt(self, next_state):
        self.last_obs = next_state
        self.current_state = next_state
