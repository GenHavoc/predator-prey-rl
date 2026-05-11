import numpy as np
from scipy.sparse import csr_matrix, diags

from predator_prey.core.kernel_sparse import kernel_sparse
from predator_prey.env.reward_function import reward_function
from predator_prey.algorithms.sample_policy import sample_policy
from predator_prey.env.induced_reward import induced_reward


GAMMA = 0.99
MAX_ITER = 100_000
TOL = 1e-9


def _induced_kernel_fast(P_sparse, Pi):
    S, A = Pi.shape

    P_pi = None
    for a in range(A):
        row_indices = np.arange(S) * A + a
        P_a = P_sparse[row_indices]
        W_a = diags(Pi[:, a])
        contrib = W_a @ P_a
        P_pi = contrib if P_pi is None else P_pi + contrib

    return csr_matrix(P_pi)


def state_value_eval_sparse(Pi, P_sparse, R, gamma=GAMMA, tol=TOL, max_iter=MAX_ITER):
    S = Pi.shape[0]

    P_pi = _induced_kernel_fast(P_sparse, Pi)

    r_pi = np.asarray(induced_reward(R, Pi)).reshape(S, 1)

    V = np.zeros((S, 1))

    for _ in range(max_iter):
        V_new = r_pi + gamma * P_pi.dot(V)
        delta = np.linalg.norm(V_new - V, np.inf)
        V = V_new
        if delta < tol:
            break

    return V