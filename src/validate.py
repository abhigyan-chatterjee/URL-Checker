import re

def is_valid_url(url: str) -> bool:
    pattern = re.compile(r"^(http|https)://[a-zA-Z0-9-._~:/?#@!$&'()*+,;=%]+$")
    return bool(re.match(pattern, url))


def strip_scheme(url: str) -> str:
    return re.sub(r"^https?://", "", url, flags=re.IGNORECASE)