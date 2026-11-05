"""Reproduce the held-out evaluation quoted in the README.

This mirrors load_data() and prepare_data() in training/train.py exactly: the same
50,000-per-class balance, the same seeds, the same 80/20 split. It only evaluates
the committed model.pth, so it measures the weights that are actually in the repo.

    python training/evaluate.py malicious_phish.csv

Prints accuracy, precision, recall and F1 for the malicious class.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

from config import (
    ADDITIONAL_FEATURE_DIM,
    HIDDEN_DIM,
    INPUT_DIM,
    MAX_LEN,
    OUTPUT_DIM,
)
from features import extract_features, get_additional_features, pad_sequences
from model import RNNClassifier

MAX_SAMPLES = 50000


def strip_scheme(url: str) -> str:
    return re.sub(r"^https?://", "", url, flags=re.IGNORECASE)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="?", default="malicious_phish.csv")
    ap.add_argument("--model", default="model.pth")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, on_bad_lines="skip")
    df["url"] = df["url"].apply(strip_scheme)
    df["label"] = [0 if t == "benign" else 1 for t in df["type"]]
    df = df[["url", "label"]]

    malicious = df[df["label"] == 1]
    benign = df[df["label"] == 0]
    n = min(MAX_SAMPLES, len(malicious), len(benign))
    balanced = (
        pd.concat(
            [malicious.sample(n=n, random_state=42), benign.sample(n=n, random_state=42)]
        )
        .sample(frac=1, random_state=42)
        .reset_index(drop=True)
    )

    feats = [extract_features(u) for u in balanced["url"].values]
    x_rnn = pad_sequences([f["tokenized_url"] for f in feats], MAX_LEN)
    x_add = torch.tensor([get_additional_features(f) for f in feats], dtype=torch.float32)
    y = torch.tensor(balanced["label"].values, dtype=torch.float32)

    _, x_rnn_te, _, x_add_te, _, y_te = train_test_split(
        x_rnn, x_add, y, test_size=0.2, random_state=42
    )
    loader = DataLoader(
        TensorDataset(x_rnn_te, x_add_te, y_te), batch_size=64, shuffle=False
    )

    model = RNNClassifier(INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, ADDITIONAL_FEATURE_DIM)
    model.load_state_dict(torch.load(args.model, map_location="cpu", weights_only=True))
    model.eval()

    tp = fp = tn = fn = 0
    with torch.no_grad():
        for xb, ab, yb in loader:
            pred = (model(xb.unsqueeze(-1), ab) > 0.5).int().squeeze()
            for p, t in zip(pred.tolist(), yb.int().tolist()):
                if p == 1 and t == 1:
                    tp += 1
                elif p == 1:
                    fp += 1
                elif t == 0:
                    tn += 1
                else:
                    fn += 1

    total = tp + fp + tn + fn
    acc = (tp + tn) / total
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0

    print(f"test rows        : {total:,}")
    print(f"accuracy         : {acc * 100:.2f}%")
    print(f"precision (mal)  : {prec * 100:.2f}%")
    print(f"recall (mal)     : {rec * 100:.2f}%")
    print(f"f1 (mal)         : {f1 * 100:.2f}%")
    print(f"confusion matrix : tp={tp} fp={fp} tn={tn} fn={fn}")


if __name__ == "__main__":
    main()
