import numpy as np

ACTIONS = {
    0: (0, 0),
    1: (-1, 0),
    2: (1, 0),
    3: (0, -1),
    4: (0, 1),
}
NUM_ACTIONS = 5


def _clamp_move(row, col, drow, dcol, N):
    new_row, new_col = row + drow, col + dcol
    if 0 <= new_row < N and 0 <= new_col < N:
        return new_row, new_col
    return row, col


def _prey_next_positions(row, col, N):
    candidates = [(row, col)]
    for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + drow, col + dcol
        if 0 <= nr < N and 0 <= nc < N:
            candidates.append((nr, nc))
    p = 1.0 / len(candidates)
    return [(r, c, p) for r, c in candidates]


def simulator(N, pred_pos, prey_pos, action):
    pr, pc = pred_pos[0] - 1, pred_pos[1] - 1
    qr, qc = prey_pos[0] - 1, prey_pos[1] - 1

    drow, dcol = ACTIONS[action]
    new_pr, new_pc = _clamp_move(pr, pc, drow, dcol, N)

    prey_moves = _prey_next_positions(qr, qc, N)
    probs = [t[2] for t in prey_moves]
    chosen = np.random.choice(len(prey_moves), p=probs)
    new_qr, new_qc = prey_moves[chosen][0], prey_moves[chosen][1]

    if new_pr == new_qr and new_pc == new_qc:
        reward = 1.0
        all_cells = [
            (r, c)
            for r in range(N)
            for c in range(N)
            if not (r == new_pr and c == new_pc)
        ]
        idx = np.random.randint(len(all_cells))
        new_qr, new_qc = all_cells[idx]
    else:
        reward = 0.0

    return (new_pr + 1, new_pc + 1), (new_qr + 1, new_qc + 1), reward