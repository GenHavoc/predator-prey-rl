# predator-prey-rl

Implementations of several RL methods applied to a predator-prey game on an N×N grid. Goes from basic tabular policy evaluation all the way to a neural network policy trained with REINFORCE.

The project is split into four parts, each building on the last:

- **Q1** — dense matrix policy evaluation (kernel, reward, V^π, Q^π)
- **Q2** — sparse matrices + value iteration + policy iteration
- **Q3** — model-free kernel estimation from simulator samples
- **Q4** — neural net policy trained with Simple SGA and Adam

---

## the environment

Grid of size N×N (default N=4). Predator moves deterministically, prey moves uniformly at random over valid neighbors. Catch happens when they land on the same cell — prey re-spawns somewhere else.

```
|S| = N^4    |A| = 5    γ = 0.99
```

Actions: stay, up, down, left, right.

State encoding: `pred_idx * N² + prey_idx` where each position is `row * N + col` (0-indexed internally, 1-indexed at the simulator interface).

---

## structure

```
predator_prey/
  env/
    simulator.py          one-step MDP simulator
    state_space.py        encoding/decoding helpers
    reward_function.py    R matrix [|S| x |A|]
    transition_engine.py  builds the full transition kernel
    induced_reward.py     r_π for a given policy
  core/
    kernel.py             dense P kernel [|S|·|A| x |S|]
    kernel_sparse.py      same but sparse
    induced_kernel.py     P_π [|S| x |S|]
    estimate_kernel.py    model-free kernel from samples (Q3)
    q_value_eval.py       Q^π
    state_value_eval.py   V^π via Bellman iteration
    gradient_estimate.py  REINFORCE gradient estimator
  algorithms/
    value_iteration.py
    policy_iteration.py
    sample_policy.py      greedy-mix policy
    policy_network.py     PyTorch net (32→128→128→5)
    simple_sga.py         manual gradient ascent
    run_adam.py           Adam optimizer loop

scripts/
  run_q1.py               builds Q1 report PDF
  run_q2.py               builds Q2 report PDF
  run_q3.py               builds Q3 report PDF
  run_q4.py               builds Q4 report PDF
  generate_plots_q*.py    plot generation for each part
```

---

## setup

```bash
pip install -r requirements.txt
```

Needs Python ≥ 3.9. PyTorch only required for Q4.

---

## running

```bash
# Q1: dense tabular evaluation
python scripts/generate_plots_q1.py
python scripts/run_q1.py

# Q2: sparse + value/policy iteration
python scripts/generate_plots_q2.py
python scripts/run_q2.py

# Q3: kernel estimation
python scripts/generate_plots_q3.py
python scripts/run_q3.py

# Q4: policy gradient — takes ~10-20 min on CPU
python scripts/generate_plots_q4.py   # saves learning_curves.png
python scripts/run_q4.py
```

---

## Q4 details

Network: `Linear(32→128) + ReLU → Linear(128→128) + ReLU → Linear(128→5)`

Input is a 32-dim one-hot vector — 16 dims for predator position, 16 for prey.

Gradient estimate uses discounted returns with baseline subtraction and advantage normalization. Gradient clipping at norm 1.0.

| param | value |
|---|---|
| episodes per gradient step | 20 |
| max steps per episode | 50 |
| iterations | 2000 |
| SGA lr | 0.005 |
| Adam lr | 0.003 |

---

## memory note (Q1 dense kernel)

The dense kernel has shape `(5·N⁴, N⁴)`. Gets expensive fast:

| N | states | kernel RAM |
|---|--------|-----------|
| 5 | 625 | ~16 MB |
| 6 | 1296 | ~133 MB |
| 7 | 2401 | ~661 MB |

Q1 experiments run up to N=7. Switch to the sparse variant for larger grids.
