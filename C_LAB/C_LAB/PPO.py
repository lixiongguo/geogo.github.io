import torch
import torch.nn.functional as F
import numpy as np
import torch.nn as nn
import collections
import random
import rl_utils
import cv2

empty_frame = np.zeros((40, 90), dtype=np.float32)
empty_state = np.stack((empty_frame, empty_frame,empty_frame, empty_frame), axis=0)
# empty_state = np.zeros((1,40, 90), dtype=np.float32)
      

class PolicyNet(torch.nn.Module):
    
    def __init__(self,action_dim):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 4, kernel_size=8)
        self.conv2 = nn.Conv2d(4, 16, kernel_size=8)
        # self.conv3 = nn.Conv2d(16, 16, kernel_size=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.pool2 = nn.MaxPool2d(4, 4)
        self.fc1 = nn.Linear(256, 128) # 64 * 4 * 7 #64* 4 * 11
        self.fc2 = nn.Linear(128, 64)
        # self.fc3 = nn.Linear(64, 32)
        self.policy_out = nn.Linear(64, action_dim)

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        # x =  self.pool(F.relu(self.conv3(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # x = F.relu(self.fc3(x))
        x = F.softmax(self.policy_out(x),dim=1)

        return x
    
class CriticNet(torch.nn.Module):
    
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(4, 4, kernel_size=8)
        self.conv2 = nn.Conv2d(4, 16, kernel_size=8)
        # self.conv3 = nn.Conv2d(16, 16, kernel_size=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.pool2 = nn.MaxPool2d(4, 4)
        self.fc1 = nn.Linear(256, 128) # 64 * 4 * 7 #64* 4 * 11
        self.fc2 = nn.Linear(128, 64)
        # self.fc3 = nn.Linear(64, 32)
        self.out = nn.Linear(64, 1)

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        # x =  self.pool(F.relu(self.conv3(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        # x = F.relu(self.fc3(x))
        x = self.out(x)
        return x    
class PPO:

    def __init__(self,action_dim, actor_lr,critic_lr,eps,lmbda,epochs,gamma,device):
        self.actor = PolicyNet(action_dim).to(device)
        self.critic = CriticNet().to(device)  
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(),lr=actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(),lr=critic_lr)
        self.epochs = epochs  # 一条序列的数据用来训练轮数
        self.gamma = gamma
        self.lmbda = lmbda
        self.eps = eps  # PPO中截断范围的参数
        self.device = device

    def take_action(self): 
        state = torch.tensor(np.array([self.current_state]), dtype=torch.float).to(self.device)  #增加batch轴
        probs = self.actor(state)
        Categroy = torch.distributions.Categorical(probs)
        action = Categroy.sample().item()
        return action

    def update(self, transition_dict):
        states = torch.tensor(transition_dict['states'],dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict['actions']).view(-1, 1).to(self.device)
        rewards = torch.tensor(transition_dict['rewards'], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict['next_states'], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict['dones'],dtype=torch.float).view(-1, 1).to(self.device)

        td_targets = rewards + self.gamma*self.critic(next_states)*(1 - dones)
        td_delta = td_targets - self.critic(states)
        advantage = rl_utils.compute_advantage(self.gamma, self.lmbda,td_delta.cpu()).to(self.device)
        old_log_probs = torch.log(torch.gather(self.actor(states), dim=1, index=actions)).detach()
        for _ in range(self.epochs):
            log_probs = torch.log(torch.gather(self.actor(states),dim=1,index=actions))
            ratio = torch.exp(log_probs - old_log_probs)
            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio,1-self.eps,self.eps)*advantage
            actor_loss = torch.mean(-torch.min(surr1,surr2))
            critic_loss = torch.mean(F.mse_loss(self.critic(states), td_targets.detach()))
            self.actor_optimizer.zero_grad() 
            self.critic_optimizer.zero_grad()
            actor_loss.backward()  
            critic_loss.backward()
            self.actor_optimizer.step()
            self.critic_optimizer.step()

      
    def set_initial_state(self, obs=None):
        self.current_state = empty_state
        self.last_obs = obs

    def get_state_from_obs(self, o_next):
        next_state = np.append(self.current_state[1:,:,:], o_next.reshape((1,)+o_next.shape), axis=0)
        # next_state = o_next
        # next_state = next_state[np.newaxis,:]
        return next_state
    

    def set_next_state(self, o_next):
        next_state = self.get_state_from_obs(o_next)
        self.last_obs = o_next
        self.current_state = next_state

    def save_model(self):
        torch.save(self.actor.state_dict(), 'ppo_actor.pth')
        torch.save(self.critic.state_dict(), 'ppo_critic.pth')
    def load_model(self):
        self.actor.load_state_dict(torch.load('ppo_actor.pth',map_location='cpu'))
        self.critic.load_state_dict(torch.load('ppo_critic.pth',map_location='cpu'))
        self.actor.train()
        self.critic.train()


