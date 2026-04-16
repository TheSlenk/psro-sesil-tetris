import pyspiel
from tetris import Tetris
import itertools
# from display import Display
import numpy as np

class MyCustomGameGame(pyspiel.Game):
    def __init__(self, params=None):
        # Initialize game parameters (e.g., board size, players)
        game_type = pyspiel.GameType(
            short_name="tetris_game",
            long_name="My Tetris Game",
            dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
            chance_mode=pyspiel.GameType.ChanceMode.DETERMINISTIC,
            information=pyspiel.GameType.Information.PERFECT_INFORMATION,
            utility=pyspiel.GameType.Utility.GENERAL_SUM,
            reward_model=pyspiel.GameType.RewardModel.TERMINAL,
            max_num_players=2,
            min_num_players=2,
            provides_information_state_string=False,
            provides_information_state_tensor=True,
            provides_observation_string=False,
            provides_observation_tensor=True,
        )
        game_info = pyspiel.GameInfo(
            num_distinct_actions=76,
            max_chance_outcomes=0,
            num_players=2,
            min_utility=0.0,
            max_utility=1000.0,
            utility_sum=None,
            max_game_length=10000
        )
        super().__init__(game_type, game_info, params or {})

    def num_players(self):
        return 2

    def observation_tensor_shape(self):
        # Return shape of observation tensor: simple representation of board state
        return [20, 10]  # Height x Width
    
    def information_state_tensor_size(self):
        return 200

    def new_initial_state(self) -> pyspiel.State:
        return MyCustomGameState(self)

    # Override other methods as needed

class MyCustomGameState(pyspiel.State):
    def __init__(self, game):
        super().__init__(game)
        # Initialize state (e.g., board, current player)
        self.height, self.width = 20, 10
        num_players = game.num_players()
        self.envs: list[Tetris] = [Tetris(self.width, self.height) for _ in range(num_players)]
        self.total_rewards: list[float] = [0.0] * num_players
        self.current_player_idx = 0

        self.action_mapping = list(itertools.product(range(-self.width + 1, self.width), (0, 90, 180, 270)))
        # self.display = Display(num_players=num_players)
        # self.display.start()

    def current_player(self):
        # Return current player index
        return self.current_player_idx

    def legal_actions(self, player_id=None):

        cur_player_idx = self.current_player_idx if player_id is None else player_id
        # Return list of legal actions for current player
        valid_actions = list(self.envs[cur_player_idx].get_next_states().keys())
        return [self.action_mapping.index(a) for a in valid_actions]

    def _apply_action(self, action_idx):
        action = self.action_mapping[action_idx]

        _, _, reward, _ = self.envs[self.current_player_idx].play(action)
        # self.update_display()
        self.total_rewards[self.current_player_idx] += reward

        self.pass_turn()

    def is_terminal(self):
        total_steps = sum([env.step for env in self.envs])
        return any([env.done for env in self.envs]) or total_steps > 50

    def returns(self):
        # Return payoffs for all players
        return self.total_rewards
    
    def rewards(self):
        return self.total_rewards
    
    def observation_tensor(self, player):
        board = self.envs[player].get_raw_flat_board()
        if board is not None:
            return np.array(board, dtype=np.float32)
        else:
            return np.zeros((20, 10), dtype=np.float32).flatten()
    
    def information_state_tensor(self, player):
        # For RL, use observation as information state
        return self.observation_tensor(player)
    
    def pass_turn(self):
        self.current_player_idx = 1 - self.current_player_idx
    
    def __str__(self):
        # String representation of state for tracking/hashing
        state_str = f"player:{self.current_player_idx}|rewards:{self.total_rewards}|boards:"
        for i, env in enumerate(self.envs):
            board = env.get_current_board()
            if board is not None:
                state_str += f"{i}:{hash(board.tobytes())}"
        return state_str
    
    def update_display(self):
        self.display.update([(env.get_current_board(), env.done) for env in self.envs])
    # Override other methods as needed

# Register the game
pyspiel.register_game(
    pyspiel.GameType(
        short_name="tetris_game",
        long_name="My Tetris Game",
        dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
        chance_mode=pyspiel.GameType.ChanceMode.DETERMINISTIC,
        information=pyspiel.GameType.Information.PERFECT_INFORMATION,
        utility=pyspiel.GameType.Utility.GENERAL_SUM,
        reward_model=pyspiel.GameType.RewardModel.TERMINAL,
        max_num_players=2,
        min_num_players=2,
        provides_information_state_string=False,
        provides_information_state_tensor=True,
        provides_observation_string=False,
        provides_observation_tensor=True,
    ),
    MyCustomGameGame
)