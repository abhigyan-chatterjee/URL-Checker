---

# URL Malware Detection Tool

A URL-based malware detection tool built with **Streamlit** and **PyTorch**. Classifies URLs as malicious or safe using a hybrid RNN model that combines character-level sequence analysis with handcrafted security features.

## Architecture

The model uses a hybrid approach:

- **Sequence path**: Character-level URL input → LSTM (hidden_dim=32) → 32-dim latent representation
- **Feature path**: 7 handcrafted features concatenated with LSTM output → FC layers (39→128→1) → sigmoid probability

### Handcrafted Features

| Feature | Description |
|---|---|
| `special_char_count` | Count of `?`, `&`, `=` characters |
| `subdomain_count` | Number of subdomain levels |
| `has_ip` | Whether the URL contains an IPv4 address |
| `entropy` | Shannon entropy of the URL string |
| `has_suspicious_name` | Whether URL contains phishing keywords (e.g. login, verify, secure) |
| `is_popular_domain` | Whether the domain is in a whitelist of 200+ popular sites |
| `tld_risk` | Whether the TLD is in a list of 40+ high-risk TLDs (e.g. .tk, .ml, .top) |

These features capture domain reputation and structural signals that a character-level model alone cannot learn — distinguishing `google.com` from `google-verify.tk` requires knowing which domains are trusted and which TLDs are abusively cheap.

## Why We Changed the Dataset

The original `data.csv` had a fundamental labeling problem: URLs were classified primarily by length and path structure rather than actual malice. "Good" URLs were systematically long commerce URLs with paths (e.g. `amazon.com/Batman-Begins/dp/...`) while "bad" URLs had odd-looking subdomain patterns. The model learned to flag anything short without a path — including `google.com` — as malicious. The accuracy metric was misleading, inflated by structural artifacts in the training split rather than genuine detection capability.

We replaced it with the **ISC Malicious URLs Dataset** ([sid321axn/malicious-urls-dataset](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)) from Kaggle, which contains 651,191 URLs across four labeled classes: benign, defacement, phishing, and malware. Labels come from actual URL blocklists and security feeds. We combined defacement, phishing, and malware into a single malicious class and balanced it 1:1 with benign samples for training.

**Current accuracy: 78.3%** on a held-out test set — an honest measurement on properly-labeled data.

## Project Structure

```
url-checker/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── model.pth
├── malicious_phish.csv
├── src/
│   ├── app.py                      # Streamlit UI
│   ├── config.py                   # Constants, feature lists, model params
│   ├── features.py                 # Feature extraction
│   ├── model.py                    # RNNClassifier definition
│   ├── predict.py                  # Inference pipeline
│   └── validate.py                 # URL validation and scheme handling
├── training/
│   └── train.py                    # Training script
├── notebooks/
│   └── exploration.ipynb           # Original training notebook (reference)
└── tests/
    ├── conftest.py
    ├── test_features.py
    ├── test_model.py
    ├── test_predict.py
    └── test_validate.py
```

## Getting Started

### Prerequisites

- Python 3.8+
- PyTorch
- Streamlit
- scikit-learn
- pandas

### Installation

```bash
git clone https://github.com/xcalibur5678/URL-checker.git
cd URL-checker
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run src/app.py
```

Opens the application at `http://localhost:8501`.

### Usage

1. Enter a URL starting with `http://` or `https://`.
2. The tool validates the URL, extracts features, and runs the model.
3. Results show the classification (safe/malicious), confidence score, suspicious keywords found, and a feature breakdown.

### Running Tests

```bash
pytest tests/
```

61 tests covering feature extraction, model instantiation, prediction consistency, and URL validation.

## Known Limitations

The model achieves 78.3% accuracy — functional but far from production-grade. Character-level analysis cannot interpret domain semantics, brand names, or certificate chains. The popular domain whitelist mitigates this but is necessarily incomplete. URLs with ambiguous structure may score near the decision boundary (e.g. `en.wikipedia.org/wiki/Python`). This is best viewed as a demonstration of the hybrid architecture approach rather than a deployable security tool.

## Contributing

Pull requests are welcome. Please include tests for new features.

## License

MIT License. See [LICENSE](LICENSE) for details.

---
