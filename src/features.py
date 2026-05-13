import math
import re

import torch

from config import MAX_LEN, POPULAR_DOMAINS, RISKY_TLDS, SUSPICIOUS_NAMES


def calculate_entropy(url: str) -> float:
    freq: dict[str, int] = {}
    for char in url:
        freq[char] = freq.get(char, 0) + 1

    entropy = 0.0
    length = len(url)
    for count in freq.values():
        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


def tokenize_url(url: str) -> list[int]:
    return [ord(char) for char in url]


def _extract_domain(url: str) -> str:
    parts = url.split("/")[0].lower()
    return parts


def _is_popular_domain(url: str) -> int:
    domain = _extract_domain(url)
    return 1 if domain in POPULAR_DOMAINS else 0


def _tld_risk(url: str) -> int:
    domain = _extract_domain(url)
    parts = domain.rsplit(".", 1)
    if len(parts) < 2:
        return 0
    tld = parts[1]
    return 1 if tld in RISKY_TLDS else 0


def extract_features(url: str) -> dict[str, float | int | list[int]]:
    url_length = len(url)
    special_char_count = len(re.findall(r"[?&=]", url))
    subdomain_count = max(0, len(url.split(".")) - 2)
    has_ip = 1 if re.search(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", url) else 0
    entropy = calculate_entropy(url)
    has_suspicious_name = 1 if any(name in url for name in SUSPICIOUS_NAMES) else 0
    is_popular_domain = _is_popular_domain(url)
    tld_risk = _tld_risk(url)
    tokenized_url = tokenize_url(url)

    return {
        "url_length": url_length,
        "special_char_count": special_char_count,
        "subdomain_count": subdomain_count,
        "has_ip": has_ip,
        "entropy": entropy,
        "has_suspicious_name": has_suspicious_name,
        "is_popular_domain": is_popular_domain,
        "tld_risk": tld_risk,
        "tokenized_url": tokenized_url,
    }


def get_additional_features(features: dict) -> list[float]:
    return [
        float(features["special_char_count"]),
        float(features["subdomain_count"]),
        float(features["has_ip"]),
        float(features["entropy"]),
        float(features["has_suspicious_name"]),
        float(features["is_popular_domain"]),
        float(features["tld_risk"]),
    ]


def pad_sequences(sequences: list[list[int]], max_len: int = MAX_LEN) -> torch.Tensor:
    padded = torch.zeros((len(sequences), max_len), dtype=torch.float32)
    for i, seq in enumerate(sequences):
        seq_len = min(len(seq), max_len)
        padded[i, :seq_len] = torch.tensor(seq[:seq_len], dtype=torch.float32)
    return padded


def find_suspicious_keywords(url: str) -> list[str]:
    return [name for name in SUSPICIOUS_NAMES if name in url]