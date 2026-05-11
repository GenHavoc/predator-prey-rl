import numpy as np
from predator_prey.env.state_space import (
    NUM_ACTIONS, pos_to_idx, idx_to_pos,
    state_to_idx, apply_action, prey_transition_probs,
)


def reward_function(N):
    n2 = N * N
    S = n2 * n2
    R = np.zeros((S, NUM_ACTIONS))

    for pred_idx in range(n2):
        pr, pc = idx_to_pos(pred_idx, N)

        for prey_idx in range(n2):
            qr, qc = idx_to_pos(prey_idx, N)
            s = state_to_idx(pred_idx, prey_idx, N)

            for a in range(NUM_ACTIONS):
                new_pr, new_pc = apply_action(pr, pc, a, N)
                new_pred_idx = pos_to_idx(new_pr, new_pc, N)

                catch_prob = 0.0
                for nqr, nqc, p_prey in prey_transition_probs(qr, qc, N):
                    if pos_to_idx(nqr, nqc, N) == new_pred_idx:
                        catch_prob += p_prey

                R[s, a] = catch_prob

    return R