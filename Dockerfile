# Dockerfile

# Step 1: Use a minimal Python image
FROM python:3.11-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy application code
COPY ./app ./app

# Step 5: Start the server using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
