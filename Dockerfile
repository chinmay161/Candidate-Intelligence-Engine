FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt /app/

# Install system dependencies if any, then python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and default assets
COPY src/ /app/src/
COPY configs/ /app/configs/
COPY data/ /app/data/
COPY rank.py /app/

# Define default entrypoint command
ENTRYPOINT ["python", "rank.py"]
