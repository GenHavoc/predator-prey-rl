NUM_ACTIONS = 5

ACTION_DELTAS = {
    0: (0, 0),
    1: (-1, 0),
    2: (1, 0),
    3: (0, -1),
    4: (0, 1),
}


def pos_to_idx(row, col, N):
    return row * N + col


def idx_to_pos(idx, N):
    return divmod(idx, N)


def state_to_idx(pred_idx, prey_idx, N):
    return pred_idx * (N * N) + prey_idx


def idx_to_state(s, N):
    return divmod(s, N * N)


def apply_action(row, col, action, N):
    drow, dcol = ACTION_DELTAS[action]
    nr, nc = row + drow, col + dcol
    if 0 <= nr < N and 0 <= nc < N:
        return nr, nc
    return row, col


def prey_transition_probs(row, col, N):
    candidates = [(row, col)]
    for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + drow, col + dcol
        if 0 <= nr < N and 0 <= nc < N:
            candidates.append((nr, nc))
    p = 1.0 / len(candidates)
    return [(r, c, p) for r, c in candidates]