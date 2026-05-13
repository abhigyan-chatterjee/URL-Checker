import os

MAX_LEN = 75
INPUT_DIM = 1
HIDDEN_DIM = 32
OUTPUT_DIM = 1
ADDITIONAL_FEATURE_DIM = 7
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model.pth")

SUSPICIOUS_NAMES = sorted(
    {"account", "alert", "amazing", "best", "breaking", "burning", "cash", "cheap", "click", "compulsory", "confirm",
     "crisis", "crucial", "critical", "deal", "discount", "emergency", "essential", "exclusive", "fatal", "free",
     "game", "high-priority", "hot", "immediate", "important", "key", "latest", "limited", "login", "mandatory",
     "money", "necessary", "new", "offer", "obligatory", "paramount", "password", "popular", "preeminent", "pressing",
     "prize", "required", "sale", "secure", "sensational", "signin", "top", "top-priority", "trending", "urgent",
     "update", "verify", "vital", "warning", "win"})

POPULAR_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "linkedin.com", "wikipedia.org", "en.wikipedia.org", "amazon.com", "reddit.com", "netflix.com",
    "microsoft.com", "office.com", "apple.com", "github.com", "stackoverflow.com",
    "whatsapp.com", "web.whatsapp.com", "t.me", "telegram.org", "zoom.us",
    "yahoo.com", "bing.com", "duckduckgo.com", "ebay.com", "paypal.com",
    "spotify.com", "twitch.tv", "discord.com", "slack.com", "adobe.com",
    "dropbox.com", "cloudflare.com", "wordpress.com", "medium.com", "quora.com",
    "pinterest.com", "tumblr.com", "flickr.com", "vimeo.com", "etsy.com",
    "indeed.com", "glassdoor.com", "imdb.com", "yelp.com", "zillow.com",
    "weather.com", "cnn.com", "bbc.com", "nytimes.com", "bloomberg.com",
    "wsj.com", "theguardian.com", "reuters.com", "espn.com", "stackexchange.com",
    "gitlab.com", "bitbucket.org", "npmjs.com", "pypi.org",
    "docker.com", "digitalocean.com", "heroku.com", "salesforce.com",
    "oracle.com", "ibm.com", "nvidia.com", "amd.com",
    "tesla.com", "walmart.com", "target.com", "canva.com", "notion.so",
    "atlassian.com", "asana.com", "trello.com", "grammarly.com",
    "android.com", "ubuntu.com", "debian.org",
    "python.org", "golang.org", "rust-lang.org", "nodejs.org",
    "reactjs.org", "vuejs.org", "angular.io", "svelte.dev", "nextjs.org",
    "mysql.com", "postgresql.org", "mongodb.com", "redis.io",
    "jupyter.org", "kaggle.com", "huggingface.co",
    "arxiv.org", "mit.edu", "stanford.edu", "harvard.edu", "berkeley.edu",
    "mozilla.org", "apache.org",
}

RISKY_TLDS = {
    "tk", "ml", "ga", "cf", "gq",
    "top", "icu", "xyz", "club", "online",
    "site", "work", "biz", "info", "click",
    "download", "review", "country", "stream",
    "racing", "accountant", "science", "date",
    "loan", "win", "party", "pro",
    "pw", "tw", "cc", "su",
}
