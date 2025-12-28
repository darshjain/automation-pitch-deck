# Build Stage
FROM python:3.10-slim as builder

WORKDIR /app

COPY pitch_deck_automation/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime Stage
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy source code
COPY pitch_deck_automation/src ./src
COPY pitch_deck_automation/data ./data
COPY pitch_deck_automation/README.md .

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the server by default
CMD ["python", "src/server.py"]
