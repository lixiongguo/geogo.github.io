from collections import namedtuple
import itertools
from itertools import count
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions.normal import Normal
import numpy as np
import collections
import random
import matplotlib.pyplot as plt
from DQN import *
from ensemble_dynamic_model import *
from rl_utils import *

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

class MBPO:
    def __init__(self, env, agent:DQN, fake_env:FakeEnv, env_pool:Replay_Buffer, model_pool:Replay_Buffer,
                 rollout_length, rollout_batch_size, real_ratio, num_episode):

        self.env = env
        self.agent = agent
        self.fake_env = fake_env
        self.env_pool = env_pool
        self.model_pool = model_pool
        self.rollout_length = rollout_length
        self.rollout_batch_size = rollout_batch_size
        self.real_ratio = real_ratio
        self.num_episode = num_episode

    def rollout_model(self):
        observations, _, _, _, _ = self.env_pool.sample(
            self.rollout_batch_size)
        for obs in observations:
            for i in range(self.rollout_length):
                action = self.agent.take_action(obs)
                reward, next_obs = self.fake_env.step(obs, action)
                self.model_pool.add(obs, action, reward, next_obs, False)
                obs = next_obs

    def update_agent(self, policy_train_batch_size=64):
        env_batch_size = int(policy_train_batch_size * self.real_ratio)
        model_batch_size = policy_train_batch_size - env_batch_size
        for epoch in range(10):
            env_obs, env_action, env_reward, env_next_obs, env_done = self.env_pool.sample(env_batch_size)
            if self.model_pool.size() > 0:
                model_obs, model_action, model_reward, model_next_obs, model_done = self.model_pool.sample(model_batch_size)
                obs = np.concatenate((env_obs, model_obs), axis=0)
                action = np.concatenate((env_action, model_action), axis=0)
                next_obs = np.concatenate((env_next_obs, model_next_obs),axis=0)
                reward = np.concatenate((env_reward, model_reward), axis=0)
                done = np.concatenate((env_done, model_done), axis=0)
            else:
                obs, action, next_obs, reward, done = env_obs, env_action, env_next_obs, env_reward, env_done
            transition_dict = {
                'states': obs,
                'actions': action,
                'next_states': next_obs,
                'rewards': reward,
                'dones': done
            }
            self.agent.update(transition_dict)

    def train_model(self):
        obs, action, reward, next_obs, done = self.env_pool.return_all_samples()
        inputs = np.concatenate((obs, action), axis=-1)
        reward = np.array(reward)
        labels = np.concatenate((np.reshape(reward, (reward.shape[0], -1)), next_obs),axis=-1)

        self.fake_env.model.train(inputs, labels)

    def explore(self):
        self.env.reset()
        obs = self.env.render()
        obs = preprocess(obs)
        self.agent.set_initial_state(obs)

        done, episode_return,truncated =  False, 0,False
        while not done and not truncated:
            action = self.agent.take_action()
            _, reward, done, truncated,_ = self.env.step(action)
            next_obs = self.env.render()
            next_obs = preprocess(next_obs)
            next_state = self.agent.get_state_from_obs(next_obs)
            self.env_pool.add(self.agent.current_state, action, reward, next_state, done)
            if not done:
                self.agent.set_next_state(next_obs)
            episode_return += reward
        return episode_return

    def train(self):
        return_list = []
        explore_return = self.explore()  # 随机探索采取数据
        print('episode: 1, return: %d' % explore_return)
        return_list.append(explore_return)
        step = 0
        for i_episode in range(self.num_episode - 1):
            self.env.reset()
            obs = self.env.render()
            obs = preprocess(obs)
            self.agent.set_initial_state(obs)
            done, truncated,episode_return =  False,False, 0
            while not done and not truncated:
                if step % 10 == 0:
                    self.train_model()
                    self.rollout_model()
                action = self.agent.take_action()
                _, reward, done,truncated, _ = self.env.step(action)
                next_obs = self.env.render()
                next_obs = preprocess(next_obs)
                next_state = self.agent.get_state_from_obs(next_obs)
                self.env_pool.add(self.agent.current_state, action, reward, next_state, done)
                if not done:
                    self.agent.set_next_state(next_obs)
                episode_return += reward
                self.update_agent()
                step += 1
            return_list.append(episode_return)
            if (i_episode + 1) % 10 == 0:
                print('episode: %d,steps: %d, return: %d' % (i_episode + 2,step, episode_return))
        return return_list


