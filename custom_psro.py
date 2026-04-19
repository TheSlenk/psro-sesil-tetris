import torch
import torch.nn as nn
import numpy as np
from tetris import Tetris

class TetrisGame:
    def __init__(self):
        self.width, self.height = 10, 20
        self.num_players = 2

    def init_new_state(self):
        return Tetris(self)

class TetrisState:
    def __init__(self, game: TetrisGame):
        self.envs = [Tetris() for _ in range(game.num_players)]
        self.current_player_idx = 0
    
    def legal_actions(self):
        return self.envs[self.current_player_idx].get_next_states()

    def apply_action(self, action)
    def is_terminal(self):
        return any([env.done for env in self.envs])

class PSRO:
    def __init__(self, game):
        self.a_policies: list[Policy] = []
        self.b_policies: list[Policy] = []


        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def init_policies(self, num_init_policies = 2):
        for _ in num_init_policies:
            self.a_policies.append(Policy(self.game, self.device))
            self.b_policies.append(Policy(self.game, self.device))
    
    def compute_payoffs_tables(self):
        payoffs = np.zeros((len(self.a_policies), len(self.b_policies)))
        for a_i, a_p in enumerate(self.a_policies):
            for b_i, b_p in enumerate(self.b_policies):
                payoffs[a_i, b_i] = a_p.play(b_p)
    
    def play(self, a_p: Policy, b_p: Policy):
        

class Policy:
    def __init__(self, game, device):
        self.game = game
        self.device = device
        self.model = DQNModel().to(device)

    def play(self):
        return

class DQNModel(nn.Module):
    def __init__(self, obs_size = 200):
        super().__init__()

        self.fc = nn.Sequential(
            nn.Linear(obs_size, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
    
    def forward(self, x):
        return self.fc(x)