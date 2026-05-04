FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY requirements_backend.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_backend.txt

# Copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
