import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from predator_prey.algorithms.policy_network import PolicyNetwork
from predator_prey.algorithms.simple_sga import simple_SGA
from predator_prey.algorithms.run_adam import run_adam

LR_SGA  = 0.005
LR_ADAM = 0.003
ITERATIONS = 2000
SEED = 42


def smooth(scalars, weight=0.95):
    last = scalars[0]
    smoothed = []
    for point in scalars:
        smoothed_val = last * weight + (1 - weight) * point
        smoothed.append(smoothed_val)
        last = smoothed_val
    return smoothed


def rolling_stats(data, window=50):
    data = np.array(data, dtype=np.float64)
    n = len(data)
    means = np.empty(n)
    stds = np.empty(n)
    for i in range(n):
        start = max(0, i - window + 1)
        chunk = data[start:i+1]
        means[i] = chunk.mean()
        stds[i] = chunk.std() if len(chunk) > 1 else 0.0
    return means, stds


def main():
    torch.manual_seed(SEED)
    np.random.seed(SEED)

    print("=" * 60)
    print("  Training with Simple SGA")
    print("=" * 60)
    policy_sga = PolicyNetwork()
    sga_rewards = simple_SGA(policy_sga, lr=LR_SGA, num_iterations=ITERATIONS)

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    print("\n" + "=" * 60)
    print("  Training with Adam Optimizer")
    print("=" * 60)
    policy_adam = PolicyNetwork()
    adam_rewards = run_adam(policy_adam, lr=LR_ADAM, num_iterations=ITERATIONS)

    sga_smooth = smooth(sga_rewards)
    adam_smooth = smooth(adam_rewards)

    sga_mean, sga_std = rolling_stats(sga_rewards, window=50)
    adam_mean, adam_std = rolling_stats(adam_rewards, window=50)

    iters = np.arange(len(sga_rewards))

    fig, ax = plt.subplots(figsize=(13, 6))

    ax.fill_between(iters, sga_mean - sga_std, sga_mean + sga_std,
                    alpha=0.12, color="#1f77b4")
    ax.fill_between(iters, adam_mean - adam_std, adam_mean + adam_std,
                    alpha=0.12, color="#ff7f0e")

    ax.plot(sga_rewards,  alpha=0.08, color="#1f77b4", linewidth=0.5)
    ax.plot(adam_rewards, alpha=0.08, color="#ff7f0e", linewidth=0.5)

    ax.plot(sga_smooth,  label=f"Simple SGA  (lr={LR_SGA})",
            linewidth=2.2, color="#1f77b4")
    ax.plot(adam_smooth,  label=f"Adam  (lr={LR_ADAM})",
            linewidth=2.2, color="#ff7f0e")

    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Average Total Reward per Episode", fontsize=12)
    ax.set_title("Learning Curves: Policy Gradient on Predator-Prey (N = 4)",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=11, loc="lower right")
    ax.grid(True, alpha=0.25, linestyle="--")
    fig.tight_layout()
    fig.savefig("learning_curves.png", dpi=150)
    print(f"\nPlot saved to learning_curves.png")


if __name__ == "__main__":
    main()
