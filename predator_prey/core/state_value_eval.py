import numpy as np
from predator_prey.core.induced_kernel import induced_kernel
from predator_prey.env.induced_reward import induced_reward


GAMMA = 0.99
MAX_ITER = 100_000
TOL = 1e-6


def state_value_eval(Pi, P, R, gamma=GAMMA, tol=TOL, max_iter=MAX_ITER):
    S = Pi.shape[0]

    P_pi = induced_kernel(P, Pi)
    r_pi = induced_reward(R, Pi)

    V = np.zeros((S, 1))

    for iteration in range(max_iter):
        V_new = r_pi + gamma * (P_pi @ V)

        delta = np.max(np.abs(V_new - V))
        V = V_new

        if delta < tol:
            break

    return V