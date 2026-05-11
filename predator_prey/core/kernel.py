import numpy as np
from predator_prey.env.state_space import (
    NUM_ACTIONS, pos_to_idx, idx_to_pos,
    state_to_idx, idx_to_state,
    apply_action, prey_transition_probs,
)


def kernel(N):
    n2 = N * N
    S = n2 * n2
    P = np.zeros((S * NUM_ACTIONS, S))

    for pred_idx in range(n2):
        pr, pc = idx_to_pos(pred_idx, N)

        for prey_idx in range(n2):
            qr, qc = idx_to_pos(prey_idx, N)
            s = state_to_idx(pred_idx, prey_idx, N)

            for a in range(NUM_ACTIONS):
                sa = s * NUM_ACTIONS + a

                new_pr, new_pc = apply_action(pr, pc, a, N)
                new_pred_idx = pos_to_idx(new_pr, new_pc, N)

                for nqr, nqc, p_prey in prey_transition_probs(qr, qc, N):
                    new_prey_idx = pos_to_idx(nqr, nqc, N)

                    if new_pred_idx == new_prey_idx:
                        spawn_p = 1.0 / (n2 - 1)
                        for spawn_idx in range(n2):
                            if spawn_idx != new_pred_idx:
                                ns = state_to_idx(new_pred_idx, spawn_idx, N)
                                P[sa, ns] += p_prey * spawn_p
                    else:
                        ns = state_to_idx(new_pred_idx, new_prey_idx, N)
                        P[sa, ns] += p_prey

    return P


def verify_kernel(P, tol=1e-9):
    row_sums = P.sum(axis=1)
    ok = np.allclose(row_sums, 1.0, atol=tol)
    status = "PASSED" if ok else "FAILED"
    print(f"Kernel row-sum check: {status}  "
          f"(min={row_sums.min():.8f}, max={row_sums.max():.8f})")
    return ok