import numpy as np
from predator_prey.env.transition_engine import matvec_P, matvec_Ppi
from predator_prey.algorithms.induced_policy import induced_policy

GAMMA = 0.99
EVAL_STEPS = 50
EPSILON = 1e-6
MAX_OUTER = 10_000


def policy_iteration(P, R, gamma=GAMMA, eval_steps=EVAL_STEPS,
                     epsilon=EPSILON, max_outer=MAX_OUTER):
    S, A = R.shape
    R_flat = R.ravel()
    use_eng = isinstance(P, dict)

    Pi = np.full((S, A), 1.0 / A, dtype=np.float64)
    Q = np.zeros((S, A), dtype=np.float64)
    V = np.zeros(S, dtype=np.float64)

    for _ in range(max_outer):
        r_pi = np.sum(Pi * R, axis=1)
        for _ in range(eval_steps):
            V = r_pi + gamma * (
                matvec_Ppi(V, Pi, P) if use_eng else (
                    __import__('induced_kernel', fromlist=['']).induced_kernel(P, Pi) @ V
                )
            )

        PV = matvec_P(V, P) if use_eng else (P @ V)
        Q_new = (R_flat + gamma * PV).reshape(S, A)

        Pi_new = induced_policy(Q_new)
        delta = float(np.max(np.abs(Q_new - Q)))
        Q = Q_new

        if np.array_equal(Pi_new, Pi) or delta < epsilon:
            break
        Pi = Pi_new

    return Q