import numpy as np
from predator_prey.env.state_space import (
    NUM_ACTIONS, pos_to_idx, idx_to_pos,
    state_to_idx, idx_to_state,
)
from predator_prey.env.simulator import simulator


def estimate_kernel(N, K, seed=None):
    if seed is not None:
        np.random.seed(seed)

    n2 = N * N
    S = n2 * n2
    A = NUM_ACTIONS

    counts = np.zeros((S * A, S), dtype=np.float64)

    for pred_idx in range(n2):
        pr, pc = idx_to_pos(pred_idx, N)
        pred_pos_1 = (pr + 1, pc + 1)

        for prey_idx in range(n2):
            qr, qc = idx_to_pos(prey_idx, N)
            prey_pos_1 = (qr + 1, qc + 1)

            s = state_to_idx(pred_idx, prey_idx, N)

            for a in range(A):
                sa = s * A + a

                for _ in range(K):
                    next_pred_1, next_prey_1, _ = simulator(
                        N, pred_pos_1, prey_pos_1, a
                    )

                    npr, npc = next_pred_1[0] - 1, next_pred_1[1] - 1
                    nqr, nqc = next_prey_1[0] - 1, next_prey_1[1] - 1

                    new_pred_idx = pos_to_idx(npr, npc, N)
                    new_prey_idx = pos_to_idx(nqr, nqc, N)
                    ns = state_to_idx(new_pred_idx, new_prey_idx, N)

                    counts[sa, ns] += 1.0

    P_hat = counts / K
    return P_hat