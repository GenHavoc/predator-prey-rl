import os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from predator_prey.env.transition_engine import build_transition_engine
from predator_prey.algorithms.value_iteration import value_iteration
from predator_prey.algorithms.policy_iteration import policy_iteration

os.makedirs("plots_q2", exist_ok=True)

GRID_SIZES = [5, 10, 15, 20, 25]


def run_experiment(N):
    R, eng = build_transition_engine(N)

    t0 = time.perf_counter()
    Q_vi = value_iteration(eng, R)
    t_vi = time.perf_counter() - t0

    t0 = time.perf_counter()
    Q_pi = policy_iteration(eng, R)
    t_pi = time.perf_counter() - t0

    l1 = float(np.sum(np.abs(Q_vi.max(axis=1) - Q_pi.max(axis=1))))
    return l1, t_vi, t_pi


def plot_l1(N_vals, l1_vals, path="plots_q2/l1_difference.png"):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.plot(N_vals, l1_vals, marker="o", linewidth=2.5,
            color="#2ecc71", markerfacecolor="white",
            markeredgewidth=2.5, markersize=10, zorder=3)
    for x, y in zip(N_vals, l1_vals):
        ax.annotate(f"{y:.3f}", (x, y),
                    textcoords="offset points", xytext=(0, 13),
                    ha="center", fontsize=9.5, color="#1a5c35", fontweight="bold")
    ax.set_xlabel("Grid size  N", fontsize=13)
    ax.set_ylabel(r"$\|V^*_{\mathrm{VI}} - V^*_{\mathrm{PI}}\|_1$", fontsize=13)
    ax.set_title(
        r"$L_1$-difference between VI and PI optimal value functions"
        "\nvs grid size N",
        fontsize=11)
    ax.set_xticks(N_vals)
    ax.set_xlim(N_vals[0]-1, N_vals[-1]+1)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def plot_runtimes(N_vals, t_vi, t_pi, path="plots_q2/runtimes_q2.png"):
    t_tot = [a+b for a,b in zip(t_vi, t_pi)]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(N_vals, t_vi, marker="o", linewidth=2.2, label="Value Iteration",
            color="#1a6fad", markerfacecolor="white", markeredgewidth=2.2, markersize=9)
    ax.plot(N_vals, t_pi, marker="s", linewidth=2.2, label="Policy Iteration",
            color="#c0392b", markerfacecolor="white", markeredgewidth=2.2, markersize=9)
    ax.plot(N_vals, t_tot, marker="^", linewidth=2.2, label="Total (VI + PI)",
            color="#8e44ad", markerfacecolor="white", markeredgewidth=2.2, markersize=9,
            linestyle="--")
    for x, y in zip(N_vals, t_vi):
        ax.annotate(f"{y:.1f}s", (x, y), textcoords="offset points",
                    xytext=(-18,6), ha="center", fontsize=8.5, color="#1a3a5c")
    for x, y in zip(N_vals, t_pi):
        ax.annotate(f"{y:.1f}s", (x, y), textcoords="offset points",
                    xytext=(18,6), ha="center", fontsize=8.5, color="#7b1c1c")
    ax.set_xlabel("Grid size  N", fontsize=13)
    ax.set_ylabel("Run time (seconds)", fontsize=13)
    ax.set_title("Run times of Value Iteration and Policy Iteration vs N", fontsize=12)
    ax.set_xticks(N_vals)
    ax.set_xlim(N_vals[0]-1, N_vals[-1]+1)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def main():
    l1_list, tvi_list, tpi_list = [], [], []

    print(f"\n{'N':>4}  {'|S|=N^4':>10}  {'L1(V)':>12}  {'t_VI(s)':>9}  {'t_PI(s)':>9}")
    print("-" * 52)

    for N in GRID_SIZES:
        print(f"{N:>4}  {N**4:>10}  running...", end="", flush=True)
        l1, t_vi, t_pi = run_experiment(N)
        l1_list.append(l1); tvi_list.append(t_vi); tpi_list.append(t_pi)
        print(f"\r{N:>4}  {N**4:>10}  {l1:>12.4f}  {t_vi:>9.2f}  {t_pi:>9.2f}")

    print()
    plot_l1(GRID_SIZES, l1_list)
    plot_runtimes(GRID_SIZES, tvi_list, tpi_list)
    print("\nDone. Plots saved to plots_q2/")


if __name__ == "__main__":
    main()