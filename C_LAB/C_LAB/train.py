import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import argparse
import torch
import gym
# from PPO import PPO
import rl_utils
from DQN import DQN
from PPO import PPO
from rl_utils import Replay_Buffer
import cv2

from tqdm import tqdm
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
import ensemble_dynamic_model
from mbpo import MBPO
from PG import PolicyGradient

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

env_name = 'CartPole-v1'
env = gym.make(env_name,render_mode='human')



torch.manual_seed(0)
gamma = 0.98
state_dim = env.observation_space.shape[0]
action_dim = env.action_space.n

def preprocess(frame):
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    frame = frame[160:300,180:420]
    frame = cv2.resize(frame,(90,40))
    frame = np.asarray(frame).astype(np.float32)
    frame = 255 -frame
    frame = frame/255.
    # frame = frame[::2, ::2, 0]  # 每两个像素采样一次
    # frame = frame.astype('float32') / 255.0  # 归一化
    return frame


def trainDQN():
    epsilon = 0.01
    dq_lr = 1e-3
    target_update = 10


    mem_size = 10000
    replay_memory = Replay_Buffer(mem_size)
    
    model = DQN(action_dim, dq_lr, gamma, epsilon,target_update,device)


    batch_size = 8
    minimal_size = 32
    num_episodes = 1000
    return_list = []

    for i in range(10):
        with tqdm(total=int(num_episodes/10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes/10)):
                done, truncated,episode_return =False,False, 0.
                env.reset()
                obs = env.render()
                obs = preprocess(obs)
                model.set_initial_state(obs)
                while not done :
                    action = model.take_action()
                    # action = env.action_space.sample()
                    _, reward, done, truncated, info = env.step(action)
                    obs = env.render()
                    obs = preprocess(obs)

                    # time.sleep(0.1)
                    # print(next_state.shape)
                    # if step < 100:
                    #     for_show = next_state.copy()*255
                    #     cv2.imwrite(f'tmp/frame_{step}.jpg',for_show)
                    #     step+=1
                    _, reward, done, truncated, info = env.step(action)
                    obs = env.render()
                    obs = preprocess(obs)
                    next_state = model.get_state_from_obs(obs)
                    replay_memory.add(model.current_state, action, reward, next_state, done)
                    if not done:
                        model.set_next_state(obs)
                    # model.store_transition(obs, action, reward, done)
                    if replay_memory.size() > minimal_size:
                        b_s, b_a, b_r, b_ns, b_d = replay_memory.sample(batch_size)
                        transition_dict = {'states': b_s, 'actions': b_a, 'next_states': b_ns, 'rewards': b_r, 'dones': b_d}
                        model.update(transition_dict)
                    episode_return += reward
                return_list.append(episode_return)
                # model.epsilon -= 0.005
                # print('episode: {}, epsilon: {:.4f}, total reward: {:.6f}'.format(episode, model.epsilon, total_reward))
                if (i_episode+1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes/10 * i + i_episode+1), 'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    
    episodes_list = list(range(len(return_list)))
    plt.plot(episodes_list, return_list)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format(env_name))
    plt.show()

    mv_return = rl_utils.moving_average(return_list, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format(env_name))
    plt.show()


def trainDQN_MBPO():
    # actor_lr = 5e-4
    # critic_lr = 5e-3
    # alpha_lr = 1e-3
    # hidden_dim = 128
    # gamma = 0.98
    # tau = 0.005  # 软更新参数
    # target_entropy = -1


    # agent = SACContinuous(state_dim, hidden_dim, action_dim, actor_lr,
    #             critic_lr, alpha_lr, target_entropy, tau, gamma,device)
    
    epsilon = 0.01
    dq_lr = 1e-3
    target_update = 10

    
    model = DQN(action_dim, dq_lr, gamma, epsilon,target_update,device)

 
    model_alpha = 0.01  # 模型损失函数中的加权权重
    model = ensemble_dynamic_model.EnsembleDynamicsModel(state_dim, action_dim, model_alpha)
    fake_env = ensemble_dynamic_model.FakeEnv(model)
    buffer_size = 10000
    env_pool = Replay_Buffer(buffer_size)
    rollout_batch_size = 1000
    rollout_length = 3  # 推演长度k,推荐更多尝试
    model_pool_size = rollout_batch_size * rollout_length
    model_pool = Replay_Buffer(model_pool_size)
    real_ratio = 0.5

    num_episodes = 20
    mbpo = MBPO(env, model, fake_env, env_pool, model_pool, rollout_length,rollout_batch_size, real_ratio, num_episodes)

    return_list = mbpo.train()

    episodes_list = list(range(len(return_list)))
    plt.plot(episodes_list, return_list)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    env_name = 'MyLaserSimulator-v1'
    plt.title('MBPO on {}'.format(env_name))
    plt.show()



def train_PG():
    dq_lr = 1e-4
    model = PolicyGradient(action_dim,dq_lr,gamma,device)
    num_episodes = 2000
    return_list = []
    for i in range(10):
        with tqdm(total=int(num_episodes/10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes/10)):
                episode_return,done =  0,False
                transition_dict = {'states': [], 'actions': [], 'next_states': [], 'rewards': [], 'dones': []}
                next_state_gt,_ = env.reset()
                obs = env.render()
                obs = preprocess(obs)
                model.set_initial_state(obs)
                # model.set_initial_state_gt(next_state_gt)
                while not done:
                    action = model.take_action()
                    # action = env.action_space.sample()

                    # next_state_gt, reward, done, truncated, info = env.step(action)
                    _, reward, done, truncated, info = env.step(action)
                    obs = env.render()
                    obs = preprocess(obs)
                    next_state = model.get_state_from_obs(obs)

                    transition_dict['states'].append(model.current_state)
                    transition_dict['actions'].append(action)
                    # # transition_dict['next_states'].append(next_state)
                    # transition_dict['next_states'].append(next_state_gt)
                    transition_dict['rewards'].append(reward)
                    # transition_dict['dones'].append(done)

                    if not done: 
                        model.set_next_state(obs)
                        # model.set_next_state_gt(next_state_gt)
                    episode_return += reward
                return_list.append(episode_return)
                model.update(transition_dict)

                if (i_episode+1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes/10 * i + i_episode+1), 'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
    episodes_list = list(range(len(return_list)))
    plt.plot(episodes_list, return_list)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('PG on {}'.format(env_name))
    plt.show()

    mv_return = rl_utils.moving_average(return_list, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('PG on {}'.format(env_name))
    plt.show()


def trainPPO():
    actor_lr = 1e-3
    critic_lr = 1e-2
    lmbda = 0.95
    epochs = 2
    eps = 0.2

    model = PPO(action_dim,actor_lr,critic_lr,eps,lmbda,epochs,gamma,device)
    num_episodes = 2000
    return_list = []
    for i in range(10):
        with tqdm(total=int(num_episodes/10), desc='Iteration %d' % i) as pbar:
            for i_episode in range(int(num_episodes/10)):
                episode_return,done =  0,False
                transition_dict = {'states': [], 'actions': [], 'next_states': [], 'rewards': [], 'dones': []}
                env.reset()
                obs = env.render()
                obs = preprocess(obs)
                model.set_initial_state(obs)
                while not done:
                    action = model.take_action()
                    _, reward, done, truncated, info = env.step(action)
                    obs = env.render()
                    obs = preprocess(obs)
                    next_state = model.get_state_from_obs(obs)
            
                    transition_dict['states'].append(model.current_state)
                    transition_dict['actions'].append(action)
                    transition_dict['next_states'].append(next_state)
                    transition_dict['rewards'].append(reward)
                    transition_dict['dones'].append(done)

                    if not done:
                        model.set_next_state(obs)
                    episode_return += reward
                return_list.append(episode_return)
                model.update(transition_dict)

                if (i_episode+1) % 10 == 0:
                    pbar.set_postfix({'episode': '%d' % (num_episodes/10 * i + i_episode+1), 'return': '%.3f' % np.mean(return_list[-10:])})
                pbar.update(1)
        episodes_list = list(range(len(return_list)))
    
    plt.plot(episodes_list, return_list)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format(env_name))
    plt.show()

    mv_return = rl_utils.moving_average(return_list, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel('Episodes')
    plt.ylabel('Returns')
    plt.title('DQN on {}'.format(env_name))
    plt.show()

    model.save_model()

    # model.load_model()
    # episode_return,step,done =  0,0,False
    # for _ in range(100):
    #     env.reset()
    #     obs = env.render()
    #     obs = preprocess(obs)
    #     model.set_initial_state(obs)
    #     done = False
    #     while not done:
    #         action = model.take_action()
    #         _, reward, done, truncated, info = env.step(action)
    #         frame = env.render()
    #         cv2.imwrite(f'tmp2/frame_{step}.jpg',frame)
    #         step+=1
    #         if not done:
    #             model.set_next_state(obs)
        

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--DQN',action='store_true')
    parser.add_argument('--PPO',action='store_true' )
    parser.add_argument('--PG',action='store_true' )
    parser.add_argument('--A2C',action='store_true' )
    args = parser.parse_args()
    if args.PPO:
        trainPPO()
    elif args.DQN:
        trainDQN()
    elif args.PG:
        train_PG()

    # elif args.PPO:
    #     trainPPO()


# def trainPPO():
#     num_episodes = 500
#     hidden_dim = 64
#     actor_lr = 1e-2
#     critic_lr = 1e-2
#     lmbda = 0.95
#     epochs = 10
#     eps = 0.2
#     agent = PPO(state_dim,hidden_dim,action_dim, actor_lr,critic_lr,lmbda,epochs,eps, gamma,device)

#     return_list = []
#     for i in range(10):
#         with tqdm(total=int(num_episodes/10), desc='Iteration %d' % i) as pbar:
#             for i_episode in range(int(num_episodes/10)):
#                 episode_return = 0
#                 transition_dict = {'states': [], 'actions': [], 'next_states': [], 'rewards': [], 'dones': []}
#                 state,_ = env.reset()
#                 done = False
#                 while not done:
#                     action = agent.take_action(state)
#                     next_state, reward, done, truncated, info = env.step(action)
#                     transition_dict['states'].append(state)
#                     transition_dict['actions'].append(action)
#                     transition_dict['next_states'].append(next_state)
#                     transition_dict['rewards'].append(reward)
#                     transition_dict['dones'].append(done)
#                     state = next_state
#                     episode_return += reward
#                 return_list.append(episode_return)
#                 agent.update(transition_dict)
#                 if (i_episode+1) % 10 == 0:
#                     pbar.set_postfix({'episode': '%d' % (num_episodes/10 * i + i_episode+1), 'return': '%.3f' % np.mean(return_list[-10:])})
#                 pbar.update(1)