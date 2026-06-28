# Stage 1: Build & Dependencies
FROM python:3.13-slim as builder

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user for security
RUN useradd -m -s /bin/bash avera_user
RUN chown -R avera_user:avera_user /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=avera_user:avera_user src/ ./src/
COPY --chown=avera_user:avera_user rank.py DataSet/validate_submission.py app.py ./

# Switch to non-root user
USER avera_user

# Expose Gradio port
EXPOSE 7860

# Default command runs the Gradio Sandbox
CMD ["python", "app.py"]
