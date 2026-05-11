import numpy as np
from predator_prey.env.transition_engine import matvec_P

GAMMA = 0.99
EPSILON = 1e-6
MAX_ITER = 100_000


def value_iteration(P, R, gamma=GAMMA, epsilon=EPSILON, max_iter=MAX_ITER):
    S, A = R.shape
    R_flat = R.ravel()
    Q = np.zeros((S, A), dtype=np.float64)
    use_eng = isinstance(P, dict)

    for _ in range(max_iter):
        V = Q.max(axis=1)
        PV = matvec_P(V, P) if use_eng else (P @ V)
        Q_new = (R_flat + gamma * PV).reshape(S, A)
        if np.max(np.abs(Q_new - Q)) < epsilon:
            Q = Q_new
            break
        Q = Q_new

    return Q