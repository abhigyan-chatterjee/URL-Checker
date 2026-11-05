# URL Checker

A URL-based malware classifier built with **Streamlit** and **PyTorch**. It classifies URLs as
malicious or safe using a hybrid model: a character-level LSTM over the raw URL, concatenated with
seven handcrafted security features.

## Architecture

- **Sequence path**: character-level URL (max 75 characters) → LSTM (`hidden_dim=32`) → 32-dim latent
  representation
- **Feature path**: 7 handcrafted features concatenated with the LSTM output → `Linear(39, 128)` →
  ReLU → `Linear(128, 1)` → sigmoid

### Handcrafted features

| Feature | Description |
|---|---|
| `special_char_count` | Count of `?`, `&`, `=` characters |
| `subdomain_count` | Number of subdomain labels |
| `has_ip` | Whether the URL contains an IPv4 address |
| `entropy` | Shannon entropy of the URL string |
| `has_suspicious_name` | Whether the URL contains any of 56 phishing keywords (e.g. login, verify, secure) |
| `is_popular_domain` | Whether the domain is in a whitelist of **103** popular sites |
| `tld_risk` | Whether the TLD is in a list of **31** high-risk TLDs (e.g. .tk, .ml, .top) |

These capture domain reputation and structural signals that a character-level model alone cannot
learn — distinguishing `google.com` from `google-verify.tk` requires knowing which domains are
trusted and which TLDs are abusively cheap.

## Dataset

The original `data.csv` had a labeling problem: URLs were classified mainly by length and path
structure rather than malice. "Good" URLs were systematically long commerce URLs with paths (e.g.
`amazon.com/Batman-Begins/dp/...`) while "bad" URLs had odd subdomain patterns, so the model learned
to flag anything short and pathless — including `google.com` — as malicious. The accuracy was
inflated by structural artifacts in the split rather than genuine detection.

It was replaced with the **ISC Malicious URLs Dataset**
([sid321axn/malicious-urls-dataset](https://www.kaggle.com/datasets/sid321axn/malicious-urls-dataset)),
which ships as `malicious_phish.csv` in this repo:

| Class | Rows |
|---|---|
| benign | 428,103 |
| defacement | 96,457 |
| phishing | 94,111 |
| malware | 32,520 |
| **total** | **651,191** |

Defacement, phishing and malware are merged into one malicious class. Training draws a balanced
sample — **50,000 malicious and 50,000 benign** — then splits 80/20, leaving 20,000 rows held out
for evaluation. The model therefore trains on 100,000 of the 651,191 rows, a deliberate cap to keep
training time on CPU reasonable.

## Results

Measured on the 20,000 held-out rows with the committed `model.pth`:

| Metric | Value |
|---|---|
| Accuracy | 78.52% |
| Precision (malicious) | 78.49% |
| Recall (malicious) | 78.10% |
| F1 (malicious) | 78.30% |

Reproduce it without retraining:

```bash
python training/evaluate.py malicious_phish.csv
```

`training/evaluate.py` mirrors the data preparation in `training/train.py` exactly — same balance,
same seeds, same split — and only loads the shipped weights.

## Project structure

```
URL-Checker/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt            # full training + app deps
├── requirements-app.txt        # lean deps for the container
├── model.pth
├── malicious_phish.csv
├── Dockerfile
├── docker-compose.yml
├── Caddyfile
├── DEPLOY.md                   # Oracle Free Tier + Docker + Caddy walkthrough
├── src/
│   ├── __init__.py
│   ├── app.py                  # Streamlit UI
│   ├── config.py               # constants, feature lists, model params
│   ├── features.py             # feature extraction
│   ├── model.py                # RNNClassifier definition
│   ├── predict.py              # inference pipeline
│   └── validate.py             # URL validation and scheme stripping
├── training/
│   ├── train.py
│   └── evaluate.py
└── notebooks/
    └── exploration.ipynb       # original training notebook (reference)
```

## Getting started

Prerequisites: Python 3.8+, PyTorch, Streamlit.

```bash
git clone https://github.com/abhigyan-chatterjee/URL-Checker.git
cd URL-Checker
pip install -r requirements.txt
streamlit run src/app.py
```

Opens at `http://localhost:8501`. Enter a URL starting with `http://` or `https://`; the app
validates it, extracts features, runs the model, and shows the classification, confidence,
suspicious keywords found and a feature breakdown.

To deploy on a VM, see [DEPLOY.md](DEPLOY.md).

## Known limitations

- **78.5% accuracy is functional, not production-grade.** Character-level analysis cannot interpret
  domain semantics, brand names or certificate chains. The popularity whitelist mitigates this but
  is necessarily incomplete at 103 domains.
- **URLs are truncated to 75 characters.** Anything longer loses its tail, which is where path-based
  obfuscation often lives.
- **The model trains on 100,000 of 651,191 rows**, so most of the dataset never influences the
  weights.
- **There is no test suite.** `training/evaluate.py` is a metric harness, not a regression test.
- **`subdomain_count` counts dots in the whole URL, not the hostname**, so a long path with dots can
  inflate it.
- URLs with ambiguous structure can score near the decision boundary (e.g.
  `en.wikipedia.org/wiki/Python`).

This is best read as a demonstration of the hybrid architecture rather than a deployable security
tool.

## License

MIT. See [LICENSE](LICENSE).
