import numpy as np


def induced_policy(Q):
    S, A = Q.shape
    Pi = np.zeros((S, A), dtype=np.float64)
    Pi[np.arange(S), np.argmax(Q, axis=1)] = 1.0
    return Pi