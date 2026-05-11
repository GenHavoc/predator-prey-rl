import numpy as np
from predator_prey.core.state_value_eval_sparse import state_value_eval_sparse, GAMMA


def q_value_eval(Pi, P, R, gamma=GAMMA):
    S, A = Pi.shape

    V = state_value_eval_sparse(Pi, P, R, gamma=gamma)

    R_flat = R.reshape(-1, 1)
    Q_flat = R_flat + gamma * (P @ V)

    Q = Q_flat.reshape(S, A)

    return Q