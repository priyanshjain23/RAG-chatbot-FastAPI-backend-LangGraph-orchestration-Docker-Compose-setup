FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# requirements.txt is in the rag_app root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend source code
COPY backend/app ./app
COPY backend/data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]