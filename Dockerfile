# Stage 1: Build dependencies
FROM python:3.13-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime + offline model bake
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN useradd -m -s /bin/bash avera_user

COPY --from=builder /install /usr/local

COPY src/ ./src/
COPY scripts/download_model.py ./scripts/
COPY rank.py DataSet/validate_submission.py DataSet/job_description.txt app.py ./

ENV AVERA_MODEL_OUT=/app/models/all-MiniLM-L6-v2
ENV AVERA_CROSS_ENCODER_OUT=/app/models/ms-marco-MiniLM-L-6-v2
RUN python scripts/download_model.py \
    && mkdir -p /app/.sandbox \
    && chown -R avera_user:avera_user /app/models /app/.sandbox /app/src /app/scripts /app/rank.py /app/app.py

ENV AVERA_SEMANTIC_MODEL=/app/models/all-MiniLM-L6-v2
ENV AVERA_CROSS_ENCODER_MODEL=/app/models/ms-marco-MiniLM-L-6-v2

USER avera_user

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
  CMD python rank.py --health || exit 1

CMD ["python", "app.py"]
