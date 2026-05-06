"""
2-player Tetris — PPO training using OpenSpiel's built-in PPO implementation.

One PPO agent is trained per player (Independent PPO / self-play).
Follows the exact pattern from open_spiel/python/examples/ppo_example.py.
"""

import collections
import pyspiel
import torch
import numpy as np

import tetris_open_game  # registers "tetris_game"

from open_spiel.python.rl_environment import Environment, ChanceEventSampler
from open_spiel.python.vector_env import SyncVectorEnv
from open_spiel.python.pytorch.ppo import PPO, PPOAgent

# ── Hyperparameters ───────────────────────────────────────────────────────────
NUM_ENVS        = 1      # parallel environments per player
STEPS_PER_BATCH = 128    # steps collected before each PPO update
TOTAL_TIMESTEPS = 500_000
NUM_UPDATES     = TOTAL_TIMESTEPS // (NUM_ENVS * STEPS_PER_BATCH)
ANNEAL_LR       = True
DEVICE          = "cuda" if torch.cuda.is_available() else "cpu"

# ── Build vectorised environments (one set per player) ────────────────────────
def make_envs(num_envs):
    return SyncVectorEnv([
        Environment(pyspiel.load_game("tetris_game"),
                    chance_event_sampler=ChanceEventSampler(seed=i))
        for i in range(num_envs)
    ])

envs = [make_envs(NUM_ENVS), make_envs(NUM_ENVS)]

game             = envs[0].envs[0]._game
obs_shape        = game.observation_tensor_shape()
num_actions      = game.num_distinct_actions()
num_players      = game.num_players()

print(f"obs_shape={obs_shape}  num_actions={num_actions}  device={DEVICE}")

# ── One PPO agent per player ──────────────────────────────────────────────────
agents = [
    PPO(
        input_shape       = obs_shape,
        num_actions       = num_actions,
        num_players       = num_players,
        player_id         = pid,
        num_envs          = NUM_ENVS,
        steps_per_batch   = STEPS_PER_BATCH,
        num_minibatches   = 4,
        update_epochs     = 4,
        learning_rate     = 2.5e-4,
        gamma             = 0.99,
        gae_lambda        = 0.95,
        clip_coef         = 0.2,
        entropy_coef      = 0.01,
        value_coef        = 0.5,
        device            = DEVICE,
        agent_fn          = PPOAgent,   # MLP — suitable for flat board tensors
    )
    for pid in range(num_players)
]

# ── Reset both env sets ───────────────────────────────────────────────────────
time_steps = [envs[pid].reset() for pid in range(num_players)]

recent_rewards = [collections.deque(maxlen=50) for _ in range(num_players)]

# ── Training loop ─────────────────────────────────────────────────────────────
for update in range(NUM_UPDATES):

    # -- collect STEPS_PER_BATCH steps for each agent -------------------------
    for _ in range(STEPS_PER_BATCH):
        for pid in range(num_players):
            # Agent picks actions for all parallel envs
            agent_output = agents[pid].step(time_steps[pid])

            new_ts, rewards, done, unreset_ts = envs[pid].step(
                agent_output, reset_if_done=True
            )

            # rewards is a list of [r0, r1] or None per env;
            # PPO only cares about its own player's reward.
            player_rewards = [
                (r[pid] if r is not None else 0.0) for r in rewards
            ]

            agents[pid].post_step(player_rewards, done)
            time_steps[pid] = new_ts

            # Track episode returns
            for ts in unreset_ts:
                if ts.last() and ts.rewards is not None:
                    recent_rewards[pid].append(ts.rewards[pid])

    # -- PPO update for each agent --------------------------------------------
    if ANNEAL_LR:
        for pid in range(num_players):
            agents[pid].anneal_learning_rate(update, NUM_UPDATES)

    for pid in range(num_players):
        agents[pid].learn(time_steps[pid])

    # -- Logging --------------------------------------------------------------
    if (update + 1) % 10 == 0:
        for pid in range(num_players):
            rews = recent_rewards[pid]
            mean_r = np.mean(rews) if rews else float("nan")
            print(
                f"update {update+1:>5}/{NUM_UPDATES} | "
                f"player {pid} | "
                f"mean_ep_return (last 50): {mean_r:>8.2f} | "
                f"total_steps: {agents[pid].total_steps_done:>8}"
            )

print("Training complete.")