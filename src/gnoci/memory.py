from collections import deque
import numpy as np


class Memory:
    def __init__(self, num_states, num_actions, action_dim, state_dim):
        self.states = deque(maxlen=num_states)
        self.actions = deque(maxlen=num_actions)
        self.num_states = num_states
        self.num_actions = num_actions
        self.action_dim = action_dim
        self.state_dim = state_dim
        for i in range(self.num_actions):
            self.actions.append(np.zeros(self.action_dim))
        for i in range(self.num_states):
            self.states.append(np.zeros(self.state_dim))

    def add_state(self, state):
        self.states.append(state)

    def add_action(self, action):
        self.actions.append(action)

    def get_observation(self):
        obs = np.concatenate(self.states)
        actions = np.concatenate(self.actions)
        return np.concatenate((obs, actions))
