import torch
import torch.optim as optim
from predator_prey.core.gradient_estimate import gradient_estimate

MAX_GRAD_NORM = 1.0


def run_adam(policy, lr, num_iterations):
    optimizer = optim.Adam(policy.parameters(), lr=lr)
    rewards_history = []

    for i in range(num_iterations):
        loss, avg_reward = gradient_estimate(policy)

        optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(policy.parameters(), MAX_GRAD_NORM)

        optimizer.step()

        rewards_history.append(avg_reward)
        if (i + 1) % 50 == 0:
            print(f"Adam Iter {i+1:4d}/{num_iterations}  |  Avg Reward: {avg_reward:.3f}")

    return rewards_history
