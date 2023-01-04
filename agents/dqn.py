import os
import random
from gym import Env

import numpy as np
from agents.agent import Agent
from buffer import ReplayBuffer
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from agents.transition import Transition

class DQN(Agent):
    batch_size = 64
    memory_size = 1000000
    seed = 42

    def __init__(self, action_space, state_space, checkpoint=False):
        Agent.__init__(self, action_space, state_space, ReplayBuffer(self.memory_size, self.batch_size, self.seed))
        self.checkpoint = checkpoint
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001
        self.gamma = 0.99
        self.max_steps = 2000
        self.model = self.build_model()
        
    def build_model(self):
        model = Sequential()
        model.add(Dense(150, input_dim=self.state_space, activation='relu'))
        model.add(Dense(120, activation='relu'))
        model.add(Dense(self.action_space, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self, state):
        # Epsilon greedy
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_space)
        else:
            action_values = self.model.predict(state)
            return np.argmax(action_values[0])

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        mini_batch = self.memory.sample()
        states = np.array([transition.state for transition in mini_batch])
        next_states = np.array([transition.next_state for transition in mini_batch])
        rewards = np.array([transition.reward for transition in mini_batch])
        dones = np.array([transition.done for transition in mini_batch])
        actions = np.array([transition.action for transition in mini_batch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        target_q_values = rewards + self.gamma * np.amax(self.model.predict_on_batch(next_states), axis=1) * (1 - dones)
        q_values = self.model.predict_on_batch(states)
        indices = np.array([i for i in range(self.batch_size)])
        q_values[[indices], [actions]] = target_q_values

        self.model.fit(states, q_values, epochs=1, verbose=0)

    def train(self, env: Env, episodes=1000):
        env.seed(0)
        np.random.seed(0)
        rewards = []

        for episode in range(episodes):
            print(f"Starting episode {episode} with epsilon {self.epsilon}")

            episode_reward = 0
            state = env.reset()
            state = np.reshape(state, (1,8))

            for step in range(1, self.max_steps + 1):
                action = self.act(state)
                new_state, reward, done, _ = env.step(action)
                new_state = np.reshape(new_state, (1,8))

                episode_reward += reward

                state_transition = Transition(
                    state, action, reward, new_state, done)
                self.remember(state_transition)

                state = new_state
                self.replay()

                if done:
                    break
            rewards.append(episode_reward)
            print(f"{episode}/{episodes}: {step} steps with reward {episode_reward}")

            running_mean= np.mean(rewards[-100:])
            if running_mean > 200:
                print(f"Solved after {episode} episodes with reward {running_mean}")
                break
            
            print(f"Average over last 100 episodes: {running_mean}")
            if episode != 0 and episode % 50 == 0 and self.checkpoint:
                self.save_model(episode)         

            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
               

    def save_model(self, episode: int):
        script_dir = os.path.dirname(__file__)
        backup_file = f"dqn{episode}.h5"
        print(f"Backing up model to {backup_file}")
        self.model.save(os.path.join(script_dir, backup_file))


    def load(self):
        pass