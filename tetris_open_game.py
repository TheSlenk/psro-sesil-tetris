import pyspiel
from tetris_game import TetrisGame, OBS_SHAPE, NUM_DISTINCT_ACTIONS, MAX_GAME_LEN
import numpy as np
from display import Display

NUM_PLAYERS = 2
game_type = pyspiel.GameType(
    short_name="tetris_game",
    long_name="My Tetris Game",
    dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
    chance_mode=pyspiel.GameType.ChanceMode.EXPLICIT_STOCHASTIC,
    information=pyspiel.GameType.Information.PERFECT_INFORMATION,
    utility=pyspiel.GameType.Utility.GENERAL_SUM,
    reward_model=pyspiel.GameType.RewardModel.REWARDS,
    max_num_players=2,
    min_num_players=1,
    provides_information_state_string=False,
    provides_information_state_tensor=True,
    provides_observation_string=False,
    provides_observation_tensor=True,
)
game_info = pyspiel.GameInfo(
    num_distinct_actions=NUM_DISTINCT_ACTIONS,
    max_chance_outcomes=7,
    num_players=NUM_PLAYERS,
    min_utility=-1000,
    max_utility=1000.0,
    utility_sum=None,
    max_game_length=MAX_GAME_LEN
)

class MyCustomGameGame(pyspiel.Game):
    def __init__(self, params=None):
        # Initialize game parameters (e.g., board size, players)
        super().__init__(game_type, game_info, params or {})

    def num_players(self):
        return NUM_PLAYERS

    def observation_tensor_shape(self):
        # Return shape of observation tensor: simple representation of board state
        return OBS_SHAPE  # Height x Width
    
    def information_state_tensor_size(self):
        return OBS_SHAPE

    def new_initial_state(self, show: Display = None) -> pyspiel.State:
        return MyCustomGameState(self, show)

    # Override other methods as needed

class MyCustomGameState(pyspiel.State):
    def __init__(self, game: MyCustomGameGame, show: Display = False):
        super().__init__(game)
        # Initialize state (e.g., board, current player)
        self.env = TetrisGame(num_players=game.num_players())
        
        if show is not None:
            show.update(self.env)

    def current_player(self):
        # Return current player index
        return self.env.current_player_idx

    def legal_actions(self, player_id: int = None):
        return self.env.legal_actions(player_id)

    def apply_action(self, action_idx):
        self.env.apply_action(action_idx)
    
    def is_terminal(self):
        return self.env.is_terminated()

    def returns(self):
        return self.env.rewards()
    
    def rewards(self):
        return self.env.rewards()
    
    def observation_tensor(self, player):
        self.env.get_current_state(player)
    
    def information_state_tensor(self, player):
        return self.env.get_current_state(player)
    
    def __str__(self):
        # String representation of state for tracking/hashing
        state_str = f"player:{self.current_player_idx}|rewards:{self.total_rewards}|boards:"
        for i, env in enumerate(self.envs):
            board = env.get_current_board()
            if board is not None:
                state_str += f"{i}:{hash(board.tobytes())}"
        return state_str

# Register the game
pyspiel.register_game(
    game_type,
    MyCustomGameGame
)