import numpy as np
from scipy.sparse import csr_matrix
from predator_prey.env.state_space import (
    NUM_ACTIONS, pos_to_idx, idx_to_pos,
    state_to_idx, apply_action, prey_transition_probs,
)


def kernel_sparse(N):
    if N < 2:
        raise ValueError(f"N must be >= 2 (got {N}); spawn redistribution "
                         "requires at least 2 cells.")

    n2 = N * N
    S = n2 * n2
    SA = S * NUM_ACTIONS

    pos_table = np.array([idx_to_pos(i, N) for i in range(n2)])

    rows = []
    cols = []
    data = []

    spawn_p = 1.0 / (n2 - 1)

    for pred_idx in range(n2):
        pr, pc = pos_table[pred_idx]

        for prey_idx in range(n2):
            qr, qc = pos_table[prey_idx]
            s = state_to_idx(pred_idx, prey_idx, N)

            for a in range(NUM_ACTIONS):
                sa = s * NUM_ACTIONS + a

                new_pr, new_pc = apply_action(pr, pc, a, N)
                new_pred_idx = pos_to_idx(new_pr, new_pc, N)

                for nqr, nqc, p_prey in prey_transition_probs(qr, qc, N):
                    new_prey_idx = pos_to_idx(nqr, nqc, N)

                    if new_pred_idx == new_prey_idx:
                        for spawn_idx in range(n2):
                            if spawn_idx != new_pred_idx:
                                ns = state_to_idx(new_pred_idx, spawn_idx, N)
                                rows.append(sa)
                                cols.append(ns)
                                data.append(p_prey * spawn_p)
                    else:
                        ns = state_to_idx(new_pred_idx, new_prey_idx, N)
                        rows.append(sa)
                        cols.append(ns)
                        data.append(p_prey)

    P = csr_matrix(
        (np.array(data), (np.array(rows), np.array(cols))),
        shape=(SA, S),
        dtype=np.float64,
    )
    return P


def verify_kernel_sparse(P, tol=1e-9):
    row_sums = np.asarray(P.sum(axis=1)).ravel()
    ok = np.allclose(row_sums, 1.0, atol=tol)
    status = "PASSED" if ok else "FAILED"
    print(f"Sparse kernel row-sum check: {status}  "
          f"(min={row_sums.min():.8f}, max={row_sums.max():.8f})")
    return ok