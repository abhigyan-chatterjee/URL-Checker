import streamlit as st

from config import HIDDEN_DIM, MAX_LEN
from features import find_suspicious_keywords
from predict import load_model, predict
from validate import is_valid_url

st.set_page_config(page_title="Malware Detection Tool", page_icon=":shield:", layout="centered")

with st.sidebar:
    st.header("About")
    st.write(
        "This tool detects malicious URLs using a hybrid LSTM-RNN model "
        "that combines character-level sequence analysis with handcrafted features."
    )
    st.subheader("Model Architecture")
    st.write(f"- **Type:** LSTM + Fully Connected\n- **Hidden Dim:** {HIDDEN_DIM}\n- **Max Sequence Length:** {MAX_LEN}\n- **Additional Features:** 5")
    st.subheader("Features Used")
    st.write(
        "- Special character count\n- Subdomain count\n- IP address presence\n"
        "- Shannon entropy\n- Suspicious keyword detection"
    )

st.title("Malware Detection Tool")
st.write("Enter a URL to check if it's malicious or safe.")

url = st.text_input("Enter the URL", placeholder="https://example.com")

if url:
    if not is_valid_url(url):
        st.error("Invalid URL format. Please enter a valid URL starting with http:// or https://.")
    else:
        with st.status("Analyzing URL..."):
            model = load_model()
            result = predict(url, model)

        confidence_pct = f"{result['confidence'] * 100:.1f}%"
        probability_pct = f"{result['probability'] * 100:.1f}%"

        if result["is_malicious"]:
            st.error(f":warning: **This URL is malicious** — Confidence: {confidence_pct}")
        else:
            st.success(f":white_check_mark: **This URL is safe** — Confidence: {confidence_pct}")

        st.metric("Raw Probability (Malicious)", probability_pct)

        keywords = find_suspicious_keywords(url)
        if keywords:
            st.warning(f"Suspicious keywords detected: {', '.join(keywords)}")

        with st.expander("Feature Breakdown"):
            features = result["features"]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("URL Length", features["url_length"])
                st.metric("Special Characters", features["special_char_count"])
                st.metric("Subdomains", features["subdomain_count"])
            with col2:
                st.metric("Has IP Address", "Yes" if features["has_ip"] else "No")
                st.metric("Entropy", f"{features['entropy']:.3f}")
                st.metric("Suspicious Name", "Yes" if features["has_suspicious_name"] else "No")