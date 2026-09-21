FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first, as its own step — more reliable than
# relying on requirements.txt to pick the right variant on arm64 (Apple Silicon)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
