import argparse
import datetime
import os
import gym
import numpy as np
from agents.dqn import DQN
from agents.ddqn import DDQN
from agents.dqfd import DQFD

if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(
        prog='ReinforcementLearning',
        description='Performs reinforcement learning on the Lunar Lander environment'
    )
    parser.add_argument('-a', '--algorithm', default='dqn')
    args = vars(parser.parse_args())
    algorithm = args['algorithm']
    env = gym.make('LunarLander-v2')
    rewards = []

    if algorithm == 'dqn':
        print("Running DQN")
        agent = DQN(action_space=env.action_space.n, state_space=env.observation_space.shape[0])
        rewards = agent.train(env, 1000)
    elif algorithm == 'ddqn':
        print("Running Double DQN")
        agent = DDQN(action_space=env.action_space.n, state_space=env.observation_space.shape[0])
        rewards = agent.train(env, 1000)
    elif algorithm == 'dqfd':
        print("Running Deep Q-learning from Demonstrations")
        agent = DQFD(action_space=env.action_space.n, state_space=env.observation_space.shape[0])
        rewards = agent.train(env, 1000)
    else:
        print("That is not a permitted algorithm")
        exit(1)

    #  Get unix timestamp with datetime
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    with open(os.path.join(script_dir, f'{algorithm}{timestamp}.txt'), 'w') as file:
        rewards = np.array(rewards)
        np.savetxt(file, rewards)
    print('Done')
    