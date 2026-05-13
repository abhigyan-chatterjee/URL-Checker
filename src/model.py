import torch
import torch.nn as nn

from config import INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, ADDITIONAL_FEATURE_DIM


class RNNClassifier(nn.Module):
    def __init__(
        self,
        input_dim: int = INPUT_DIM,
        hidden_dim: int = HIDDEN_DIM,
        output_dim: int = OUTPUT_DIM,
        additional_feature_dim: int = ADDITIONAL_FEATURE_DIM,
    ):
        super().__init__()
        self.rnn = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim + additional_feature_dim, 128)
        self.fc2 = nn.Linear(128, output_dim)

    def forward(self, rnn_input: torch.Tensor, additional_features: torch.Tensor) -> torch.Tensor:
        h, _ = self.rnn(rnn_input)
        h = h[:, -1, :]
        combined_input = torch.cat((h, additional_features), dim=1)
        x = torch.relu(self.fc1(combined_input))
        out = torch.sigmoid(self.fc2(x))
        return out