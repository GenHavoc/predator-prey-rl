import torch
import torch.nn as nn
import torch.nn.functional as F

N = 4


class PolicyNetwork(nn.Module):

    def __init__(self, n=N):
        super(PolicyNetwork, self).__init__()
        self.n = n
        input_size = n * n * 2
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, 5)

        for layer in [self.fc1, self.fc2, self.fc3]:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        logits = self.fc3(x)
        return logits


def state_to_tensor(pred, prey, n=N):
    state = torch.zeros(n * n * 2)
    pred_idx = (pred[0] - 1) * n + (pred[1] - 1)
    state[pred_idx] = 1.0
    prey_idx = (prey[0] - 1) * n + (prey[1] - 1)
    state[n * n + prey_idx] = 1.0
    return state
