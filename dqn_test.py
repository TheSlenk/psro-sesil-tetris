"""
2-player Tetris — Independent DQN using OpenSpiel's built-in DQN agent.

Each player has their own DQN. Each agent's step() is only called when it is
that player's turn, so time_step.rewards is always valid when the agent reads
it internally.
"""

import pyspiel
import tetris_open_game  # registers "tetris_game"

from open_spiel.python.rl_environment import Environment
from open_spiel.python.pytorch.dqn import DQN

NUM_EPISODES = 10_000

# 1. Single environment
env  = Environment(pyspiel.load_game("tetris_game"))
game = env._game

num_actions  = game.num_distinct_actions()
obs_size     = game.information_state_tensor_size()

# 2. One DQN per player
agents = [
    DQN(
        player_id              = pid,
        state_representation_size = obs_size,
        num_actions            = num_actions,
        hidden_layers_sizes    = (128, 128),
        replay_buffer_capacity = 10_000,
        learning_rate          = 1e-3,
        epsilon_start          = 1.0,
        epsilon_end            = 0.05,
        epsilon_decay_duration = NUM_EPISODES * 200,
        optimizer_str          = "adam",
    )
    for pid in range(2)
]

# 3. Training loop
for ep in range(NUM_EPISODES):
    time_step = env.reset()

    while not time_step.last():
        pid    = time_step.observations["current_player"]
        output = agents[pid].step(time_step)          # act + maybe learn
        time_step = env.step([output.action])

    # Terminal step: deliver final reward to both agents
    for agent in agents:
        agent.step(time_step)

    if (ep + 1) % 500 == 0:
        print(f"Episode {ep+1}/{NUM_EPISODES} | "
              f"returns: p0={time_step.rewards[0]:.1f}  "
              f"p1={time_step.rewards[1]:.1f}")