import os, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from predator_prey.env.transition_engine import build_transition_engine
from predator_prey.algorithms.value_iteration import value_iteration
from predator_prey.env.reward_function import reward_function
from predator_prey.core.estimate_kernel import estimate_kernel

os.makedirs("plots_q3", exist_ok=True)

N = 5
K_VALS = [5, 10, 15, 20, 25]
SEEDS = [0, 1, 2, 3, 4]


def compute_exact_Q(N):
    R, eng = build_transition_engine(N)
    return value_iteration(eng, R, epsilon=1e-6), R


def run_experiments(N, K_vals, seeds):
    Q_exact, R_mat = compute_exact_Q(N)
    V_exact = Q_exact.max(axis=1)
    print(f"Exact Q* ready. V range: [{V_exact.min():.4f}, {V_exact.max():.4f}]")

    means, stds, all_l1 = [], [], []

    for K in K_vals:
        l1_list = []
        for seed in seeds:
            P_hat = estimate_kernel(N, K, seed=seed)
            Q_est = value_iteration(P_hat, R_mat, epsilon=1e-6)
            V_est = Q_est.max(axis=1)
            l1 = float(np.sum(np.abs(V_exact - V_est)))
            l1_list.append(l1)
            print(f"  K={K:2d}  seed={seed}  L1={l1:.2f}")
        means.append(float(np.mean(l1_list)))
        stds.append(float(np.std(l1_list)))
        all_l1.append(l1_list)
        print(f"  K={K:2d}  mean={means[-1]:.2f}  std={stds[-1]:.2f}\n")

    return means, stds, all_l1


def plot_l1_vs_K(K_vals, means, stds, all_l1,
                 path="plots_q3/l1_vs_K.png"):
    fig, ax = plt.subplots(figsize=(8, 5))

    means_arr = np.array(means)
    stds_arr = np.array(stds)

    ax.fill_between(K_vals,
                    means_arr - stds_arr,
                    means_arr + stds_arr,
                    alpha=0.20, color="#1a6fad", label=r"$\pm 1$ std")

    for i, seed in enumerate(SEEDS):
        l1s = [all_l1[ki][i] for ki in range(len(K_vals))]
        ax.plot(K_vals, l1s, color="#1a6fad", alpha=0.25,
                linewidth=1, linestyle="--")

    ax.errorbar(K_vals, means_arr, yerr=stds_arr,
                marker="o", linewidth=2.5, color="#1a6fad",
                markerfacecolor="white", markeredgewidth=2.5,
                markersize=10, capsize=6, capthick=2,
                label="Mean L1", zorder=5)

    for x, y in zip(K_vals, means_arr):
        ax.annotate(f"{y:.1f}", (x, y),
                    textcoords="offset points", xytext=(0, 14),
                    ha="center", fontsize=9.5,
                    color="#1a3a5c", fontweight="bold")

    ax.set_xlabel("K  (simulator calls per (s, a) pair)", fontsize=13)
    ax.set_ylabel(r"$\|V^*_{\mathrm{exact}} - V^*_{\mathrm{est}}\|_1$",
                  fontsize=13)
    ax.set_title(
        f"L$_1$-difference between exact and estimated optimal value functions\n"
        f"N={N},  5 seeds,  mean ± std",
        fontsize=11)
    ax.set_xticks(K_vals)
    ax.set_xlim(K_vals[0] - 2, K_vals[-1] + 2)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def main():
    print(f"Running experiment: N={N}, K={K_VALS}, seeds={SEEDS}\n")
    t0 = time.perf_counter()
    means, stds, all_l1 = run_experiments(N, K_VALS, SEEDS)
    print(f"\nTotal time: {time.perf_counter()-t0:.1f}s")

    print("\n=== Summary ===")
    print(f"{'K':>4}  {'mean L1':>10}  {'std L1':>10}")
    for K, m, s in zip(K_VALS, means, stds):
        print(f"{K:>4}  {m:>10.2f}  {s:>10.2f}")

    plot_l1_vs_K(K_VALS, means, stds, all_l1)
    print("\nDone. Plot saved to plots_q3/")


if __name__ == "__main__":
    main()