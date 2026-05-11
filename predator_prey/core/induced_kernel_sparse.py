import numpy as np
from scipy.sparse import csr_matrix, diags


def induced_kernel_sparse(P_sparse, Pi):
    S, A = Pi.shape
    assert P_sparse.shape == (S * A, S), (
        f"Expected P_sparse shape ({S*A}, {S}), got {P_sparse.shape}"
    )

    P_pi = None
    for a in range(A):
        row_indices = np.arange(S) * A + a
        P_a = P_sparse[row_indices]
        W_a = diags(Pi[:, a])
        contrib = W_a @ P_a
        P_pi = contrib if P_pi is None else P_pi + contrib

    return csr_matrix(P_pi)