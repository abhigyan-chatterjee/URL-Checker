import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import re
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

from src.config import MAX_LEN, INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, ADDITIONAL_FEATURE_DIM, MODEL_PATH
from src.features import extract_features, get_additional_features, pad_sequences
from src.model import RNNClassifier


def strip_scheme(url: str) -> str:
    return re.sub(r"^https?://", "", url, flags=re.IGNORECASE)


def load_data(path: str, max_samples: int = 50000) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip")
    df["url"] = df["url"].apply(strip_scheme)
    df["label"] = [0 if t == "benign" else 1 for t in df["type"]]
    df = df[["url", "label"]]

    malicious = df[df["label"] == 1]
    benign = df[df["label"] == 0]

    n = min(max_samples, len(malicious), len(benign))
    malicious_sample = malicious.sample(n=n, random_state=42)
    benign_sample = benign.sample(n=n, random_state=42)

    balanced = pd.concat([malicious_sample, benign_sample]).sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"Malicious: {n}")
    print(f"Benign: {n}")
    print(f"Total: {len(balanced)}")
    return balanced


def prepare_data(df: pd.DataFrame):
    features_list = [extract_features(url) for url in df["url"].values]

    tokenized = [f["tokenized_url"] for f in features_list]
    additional = [get_additional_features(f) for f in features_list]

    X_rnn = pad_sequences(tokenized, MAX_LEN)
    X_additional = torch.tensor(additional, dtype=torch.float32)
    y = torch.tensor(df["label"].values, dtype=torch.float32)

    X_rnn_train, X_rnn_test, X_additional_train, X_additional_test, y_train, y_test = train_test_split(
        X_rnn, X_additional, y, test_size=0.2, random_state=42
    )

    train_data = TensorDataset(X_rnn_train, X_additional_train, y_train)
    test_data = TensorDataset(X_rnn_test, X_additional_test, y_test)

    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

    print(f"Train: {len(train_data)}, Test: {len(test_data)}")
    return train_loader, test_loader


def train_model(train_loader: DataLoader, epochs: int = 10, lr: float = 0.001):
    model = RNNClassifier(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, ADDITIONAL_FEATURE_DIM)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for X_rnn_batch, X_additional_batch, y_batch in train_loader:
            optimizer.zero_grad()
            X_rnn_batch = X_rnn_batch.unsqueeze(-1)
            y_batch = y_batch.unsqueeze(-1)
            outputs = model(X_rnn_batch, X_additional_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(train_loader):.4f}")

    return model


def evaluate(model: RNNClassifier, test_loader: DataLoader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X_rnn_batch, X_additional_batch, y_batch in test_loader:
            X_rnn_batch = X_rnn_batch.unsqueeze(-1)
            y_pred = model(X_rnn_batch, X_additional_batch)
            y_pred = (y_pred > 0.5).int()
            correct += (y_pred.squeeze() == y_batch).sum().item()
            total += y_batch.size(0)
    accuracy = correct / total
    print(f"Accuracy: {accuracy * 100:.2f}%")
    return accuracy


if __name__ == "__main__":
    import sys

    data_path = sys.argv[1] if len(sys.argv) > 1 else "malicious_phish.csv"
    df = load_data(data_path)
    train_loader, test_loader = prepare_data(df)
    model = train_model(train_loader, epochs=10)
    accuracy = evaluate(model, test_loader)
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")