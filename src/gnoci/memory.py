from collections import deque
import numpy as np


class Memory:
    def __init__(self, num_observations, num_actions):
        self.observations = deque(maxlen=num_observations)
        self.actions = deque(maxlen=num_actions)

    def add(self, observation, action):
        self.observations.append(observation)
        self.actions.append(action)

    def get():
        obs = np.concatenate(self.observations, self.actions)
        print(obs.shape)
        return obs
