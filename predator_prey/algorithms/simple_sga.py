import torch
from predator_prey.core.gradient_estimate import gradient_estimate

MAX_GRAD_NORM = 1.0


def simple_SGA(policy, lr, num_iterations):
    rewards_history = []

    for i in range(num_iterations):
        loss, avg_reward = gradient_estimate(policy)

        policy.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(policy.parameters(), MAX_GRAD_NORM)

        with torch.no_grad():
            for param in policy.parameters():
                param.data -= lr * param.grad

        rewards_history.append(avg_reward)
        if (i + 1) % 50 == 0:
            print(f"SGA  Iter {i+1:4d}/{num_iterations}  |  Avg Reward: {avg_reward:.3f}")

    return rewards_history
