FROM docker.io/library/python:3.12-slim

WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt \
      --extra-index-url https://download.pytorch.org/whl/cpu

COPY src/ ./src/
COPY model.pth .

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
