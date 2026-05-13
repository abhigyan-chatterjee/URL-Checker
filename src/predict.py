import torch

from config import MODEL_PATH
from features import extract_features, get_additional_features, pad_sequences
from model import RNNClassifier
from validate import strip_scheme


def load_model(model_path: str = MODEL_PATH) -> RNNClassifier:
    model = RNNClassifier()
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model


def predict(url: str, model: RNNClassifier | None = None) -> dict:
    if model is None:
        model = load_model()

    clean_url = strip_scheme(url)
    features = extract_features(clean_url)

    rnn_data = pad_sequences([features["tokenized_url"]])
    additional_data = torch.tensor([get_additional_features(features)], dtype=torch.float32)
    rnn_data = rnn_data.unsqueeze(-1)

    with torch.no_grad():
        probability = model(rnn_data, additional_data).item()

    is_malicious = probability > 0.5
    label = "malicious" if is_malicious else "safe"
    confidence = probability if is_malicious else 1.0 - probability

    return {
        "label": label,
        "is_malicious": is_malicious,
        "confidence": confidence,
        "probability": probability,
        "features": features,
    }