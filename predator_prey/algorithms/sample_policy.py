import numpy as np
from predator_prey.env.state_space import (
    NUM_ACTIONS, idx_to_pos, state_to_idx, apply_action,
)


def _manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)


def sample_policy(N):
    n2 = N * N
    S = n2 * n2
    Pi = np.zeros((S, NUM_ACTIONS))

    for pred_idx in range(n2):
        pr, pc = idx_to_pos(pred_idx, N)

        for prey_idx in range(n2):
            qr, qc = idx_to_pos(prey_idx, N)
            s = state_to_idx(pred_idx, prey_idx, N)

            action_dist = []
            for a in range(NUM_ACTIONS):
                new_pr, new_pc = apply_action(pr, pc, a, N)
                d = _manhattan(new_pr, new_pc, qr, qc)
                action_dist.append((a, d))

            min_dist = min(d for _, d in action_dist)
            greedy_set = [a for a, d in action_dist if d == min_dist]
            other_set = [a for a, d in action_dist if d > min_dist]

            if other_set:
                for a in greedy_set:
                    Pi[s, a] += 0.5 / len(greedy_set)
                for a in other_set:
                    Pi[s, a] += 0.5 / len(other_set)
            else:
                for a in greedy_set:
                    Pi[s, a] += 1.0 / len(greedy_set)

    return Pi


def verify_policy(Pi, tol=1e-9):
    row_sums = Pi.sum(axis=1)
    ok = np.allclose(row_sums, 1.0, atol=tol)
    status = "PASSED" if ok else "FAILED"
    print(f"Policy row-sum check: {status}  "
          f"(min={row_sums.min():.8f}, max={row_sums.max():.8f})")
    return ok