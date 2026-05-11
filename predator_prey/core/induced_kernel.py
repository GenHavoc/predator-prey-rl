import numpy as np


def induced_kernel(P, Pi):
    S, A = Pi.shape
    assert P.shape == (S * A, S), (
        f"Shape mismatch: expected P of shape ({S*A}, {S}), got {P.shape}."
    )

    P_3d = P.reshape(S, A, S)
    P_pi = np.einsum("ij,ijk->ik", Pi, P_3d)

    return P_pi


def verify_induced_kernel(P_pi, tol=1e-9):
    row_sums = P_pi.sum(axis=1)
    ok = np.allclose(row_sums, 1.0, atol=tol)
    status = "PASSED" if ok else "FAILED"
    print(f"Induced kernel row-sum check: {status}  "
          f"(min={row_sums.min():.8f}, max={row_sums.max():.8f})")
    return ok