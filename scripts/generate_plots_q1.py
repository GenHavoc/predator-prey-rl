import os
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from predator_prey.env.state_space import pos_to_idx, state_to_idx
from predator_prey.core.kernel_sparse import kernel_sparse
from predator_prey.env.reward_function import reward_function
from predator_prey.algorithms.sample_policy import sample_policy
from predator_prey.env.induced_reward import induced_reward

os.makedirs("plots", exist_ok=True)

GRID_SIZES = [5, 10, 15, 20, 25]
GAMMA = 0.99
TOL = 1e-9
MAX_ITER = 10_000


def initial_state_index(N):
    pred_idx = pos_to_idx(0, 0, N)
    prey_idx = pos_to_idx(N - 1, N - 1, N)
    return state_to_idx(pred_idx, prey_idx, N)


def state_value_eval_sparse(Pi, P_sparse, R):
    S, A = Pi.shape
    r_pi = np.asarray(induced_reward(R, Pi)).reshape(S, 1)
    P_slices = [P_sparse[np.arange(S) * A + a] for a in range(A)]
    V = np.zeros((S, 1))

    for _ in range(MAX_ITER):
        Pv = sum(
            Pi[:, a].reshape(-1, 1) * np.asarray(P_slices[a].dot(V)).reshape(S, 1)
            for a in range(A)
        )
        V_new = r_pi + GAMMA * Pv
        delta = np.linalg.norm(V_new - V, np.inf)
        V = V_new
        if delta < TOL:
            break

    return V


def run_experiment(N):
    t0 = time.perf_counter()
    P = kernel_sparse(N)
    R = reward_function(N)
    Pi = sample_policy(N)
    V = state_value_eval_sparse(Pi, P, R)
    elapsed = time.perf_counter() - t0
    s0 = initial_state_index(N)
    return float(V[s0, 0]), elapsed


def plot_state_values(N_vals, values, save_path="plots/state_values.png"):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.plot(N_vals, values, marker="o", linewidth=2.5,
            color="#1a6fad", markerfacecolor="white",
            markeredgewidth=2.5, markersize=10, zorder=3)
    for x, y in zip(N_vals, values):
        ax.annotate(f"{y:.5f}", (x, y),
                    textcoords="offset points", xytext=(0, 13),
                    ha="center", fontsize=9.5, color="#1a3a5c", fontweight="bold")
    ax.set_xlabel("Grid size  N", fontsize=13)
    ax.set_ylabel(r"State value  $V^{\pi}(s_0)$", fontsize=13)
    ax.set_title(
        "State value at initial state  ((1,1), (N,N))\n"
        "under the greedy-mix policy  (\u03b3 = 0.99)",
        fontsize=12)
    ax.set_xticks(N_vals)
    ax.set_xlim(N_vals[0] - 0.5, N_vals[-1] + 0.5)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"Saved {save_path}")


def plot_runtimes(N_vals, runtimes, save_path="plots/runtimes.png"):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.plot(N_vals, runtimes, marker="s", linewidth=2.5,
            color="#c0392b", markerfacecolor="white",
            markeredgewidth=2.5, markersize=10, zorder=3)
    for x, y in zip(N_vals, runtimes):
        label = f"{y:.2f}s" if y >= 0.1 else f"{y*1000:.0f}ms"
        ax.annotate(label, (x, y),
                    textcoords="offset points", xytext=(0, 13),
                    ha="center", fontsize=9.5, color="#7b1c1c", fontweight="bold")
    ax.set_xlabel("Grid size  N", fontsize=13)
    ax.set_ylabel("Run time (seconds)", fontsize=13)
    ax.set_title(
        "Total computation time\n"
        "(kernel + reward + policy + value eval)  vs  N",
        fontsize=12)
    ax.set_xticks(N_vals)
    ax.set_xlim(N_vals[0] - 0.5, N_vals[-1] + 0.5)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"Saved {save_path}")


def main():
    state_values = []
    runtimes = []

    print(f"\n{'N':>4}  {'|S|=N^4':>10}  {'V^pi(s0)':>14}  {'Time (s)':>10}")
    print("-" * 46)

    for N in GRID_SIZES:
        print(f"{N:>4}  {N**4:>10}  computing...", end="", flush=True)
        value, elapsed = run_experiment(N)
        state_values.append(value)
        runtimes.append(elapsed)
        print(f"\r{N:>4}  {N**4:>10}  {value:>14.6f}  {elapsed:>10.2f}")

    print()
    plot_state_values(GRID_SIZES, state_values)
    plot_runtimes(GRID_SIZES, runtimes)
    print("\nDone.  Both plots saved to the plots/ directory.")


if __name__ == "__main__":
    main()