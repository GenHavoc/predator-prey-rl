import numpy as np
from predator_prey.env.state_space import (
    NUM_ACTIONS, pos_to_idx, idx_to_pos,
    state_to_idx, apply_action, prey_transition_probs,
)

K_MAX = 5


def build_transition_engine(N):
    n2 = N * N
    S = n2 * n2
    A = NUM_ACTIONS
    spawn_p = 1.0 / (n2 - 1)

    new_pred = np.empty((S, A), dtype=np.int32)
    for pred_idx in range(n2):
        pr, pc = idx_to_pos(pred_idx, N)
        for a in range(A):
            new_pr, new_pc = apply_action(pr, pc, a, N)
            new_pred[pred_idx * n2:(pred_idx + 1) * n2, a] = \
                pos_to_idx(new_pr, new_pc, N)

    prey_nb = np.full((n2, K_MAX), -1, dtype=np.int32)
    prey_pr = np.zeros((n2, K_MAX), dtype=np.float64)
    for prey_idx in range(n2):
        qr, qc = idx_to_pos(prey_idx, N)
        for k, (nr, nc, p) in enumerate(prey_transition_probs(qr, qc, N)):
            prey_nb[prey_idx, k] = pos_to_idx(nr, nc, N)
            prey_pr[prey_idx, k] = p

    pi_arr = np.arange(S, dtype=np.int32) % n2
    prey_nb_s = prey_nb[pi_arr]
    prey_pr_s = prey_pr[pi_arr]

    R = np.zeros((S, A), dtype=np.float64)
    for a in range(A):
        np_a = new_pred[:, a]
        for k in range(K_MAX):
            mask = (prey_nb_s[:, k] >= 0) & (prey_nb_s[:, k] == np_a)
            R[mask, a] += prey_pr_s[mask, k]

    nc_src_ak = [[None]*K_MAX for _ in range(A)]
    nc_dst_ak = [[None]*K_MAX for _ in range(A)]
    nc_wt_ak  = [[None]*K_MAX for _ in range(A)]
    ca_src_ak = [[None]*K_MAX for _ in range(A)]
    ca_nprow_ak = [[None]*K_MAX for _ in range(A)]
    ca_self_ak  = [[None]*K_MAX for _ in range(A)]
    ca_wt_ak    = [[None]*K_MAX for _ in range(A)]

    for a in range(A):
        np_a = new_pred[:, a]
        for k in range(K_MAX):
            nq = prey_nb_s[:, k]
            pp = prey_pr_s[:, k]
            valid = nq >= 0
            catch = valid & (nq == np_a)
            no_catch = valid & ~catch

            nc = np.where(no_catch)[0]
            nc_src_ak[a][k] = nc.astype(np.int32)
            nc_dst_ak[a][k] = (np_a[nc].astype(np.int64)*n2
                              + nq[nc].astype(np.int64)).astype(np.int32)
            nc_wt_ak[a][k] = pp[nc]

            ca = np.where(catch)[0]
            ca_src_ak[a][k] = ca.astype(np.int32)
            ca_nprow_ak[a][k] = (np_a[ca].astype(np.int64)*n2).astype(np.int32)
            ca_self_ak[a][k] = (np_a[ca].astype(np.int64)*(n2+1)).astype(np.int32)
            ca_wt_ak[a][k] = pp[ca] * spawn_p

    eng = dict(
        N=N, n2=n2, S=S, A=A,
        nc_src=nc_src_ak, nc_dst=nc_dst_ak, nc_wt=nc_wt_ak,
        ca_src=ca_src_ak, ca_nprow=ca_nprow_ak,
        ca_self=ca_self_ak, ca_wt=ca_wt_ak,
    )
    return R, eng


def matvec_P(v, eng):
    n2 = eng['n2']; S = eng['S']; A = eng['A']
    nc_src = eng['nc_src']; nc_dst = eng['nc_dst']; nc_wt = eng['nc_wt']
    ca_src = eng['ca_src']; ca_nprow = eng['ca_nprow']
    ca_self = eng['ca_self']; ca_wt = eng['ca_wt']

    v_ = np.ascontiguousarray(v, dtype=np.float64).ravel()
    row_sum = v_.reshape(n2, n2).sum(axis=1)
    w = np.zeros(S * A, dtype=np.float64)

    for a in range(A):
        w_a = np.zeros(S, dtype=np.float64)
        for k in range(K_MAX):
            src = nc_src[a][k]
            if src.size:
                w_a[src] += nc_wt[a][k] * v_[nc_dst[a][k]]

            src = ca_src[a][k]
            if src.size:
                w_a[src] += ca_wt[a][k] * (
                    row_sum[ca_nprow[a][k] // n2]
                    - v_[ca_self[a][k]]
                )
        w[a::A] = w_a
    return w


def matvec_Ppi(v, Pi, eng):
    S, A = Pi.shape
    w = matvec_P(v, eng)
    return np.sum(Pi * w.reshape(S, A), axis=1)