import torch
from torch.distributions import Categorical
import numpy as np
from predator_prey.env.simulator import simulator
from predator_prey.algorithms.policy_network import state_to_tensor

N = 4
GAMMA = 0.99
MAX_STEPS = 50
NUM_EPISODES_PER_ITER = 20


def run_episode(policy, n=N, max_steps=MAX_STEPS):
    pred_pos = (np.random.randint(1, n + 1), np.random.randint(1, n + 1))
    prey_pos = (np.random.randint(1, n + 1), np.random.randint(1, n + 1))

    log_probs = []
    rewards = []

    for _ in range(max_steps):
        state = state_to_tensor(pred_pos, prey_pos, n)
        logits = policy(state)

        dist = Categorical(logits=logits)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        next_pred, next_prey, reward = simulator(n, pred_pos, prey_pos, action.item())

        log_probs.append(log_prob)
        rewards.append(reward)

        pred_pos = next_pred
        prey_pos = next_prey

    return log_probs, rewards


def gradient_estimate(policy, n=N, num_episodes=NUM_EPISODES_PER_ITER, gamma=GAMMA):
    total_loss = torch.tensor(0.0)
    total_reward = 0.0

    all_returns = []

    episode_data = []
    for _ in range(num_episodes):
        log_probs, rewards = run_episode(policy, n)
        total_reward += sum(rewards)

        returns = []
        G = 0.0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        returns = torch.tensor(returns)
        all_returns.append(returns)
        episode_data.append((log_probs, returns))

    stacked = torch.stack(all_returns)
    baseline = stacked.mean(dim=0)

    for log_probs, returns in episode_data:
        advantages = returns - baseline
        std = advantages.std()
        if std > 1e-8:
            advantages = advantages / std

        episode_loss = torch.tensor(0.0)
        for lp, adv in zip(log_probs, advantages):
            episode_loss = episode_loss - lp * adv

        total_loss = total_loss + episode_loss

    total_loss = total_loss / num_episodes
    avg_reward = total_reward / num_episodes

    return total_loss, avg_reward
