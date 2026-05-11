import numpy as np


def induced_reward(R, Pi):
    assert R.shape == Pi.shape, (
        f"Shape mismatch: R is {R.shape}, Pi is {Pi.shape}."
    )

    r_pi = np.sum(Pi * R, axis=1, keepdims=True)
    return r_pi