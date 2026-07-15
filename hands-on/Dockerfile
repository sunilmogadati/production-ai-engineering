# ---------------------------------------------------------------------------
# Dockerfile for the Prospect Scoring API (serve.py)
#
# WHY a container: "it works on my machine" is not a deployment strategy. A
# container packages the exact Python version, dependencies, model file, and
# code into ONE image that runs identically on your laptop, a teammate's
# machine, or any cloud.
#
#   Build:  docker build -t prospect-api .
#   Run:    docker run -p 8000:8000 prospect-api
#   Check:  curl http://localhost:8000/health
#   UI:     open http://localhost:8000
# ---------------------------------------------------------------------------

# Start from a small, official Python base image. "slim" = no build bloat.
FROM python:3.12-slim

# WHY these env vars:
#  - PYTHONUNBUFFERED: logs appear immediately, so `docker logs` shows them live
#  - PYTHONDONTWRITEBYTECODE: skip .pyc files we do not need inside a container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# WHY copy requirements FIRST, before the rest of the code:
# Docker builds in cached layers. Dependencies change rarely; code changes often.
# Installing deps in their own layer means editing serve.py does NOT reinstall
# pandas + scikit-learn every build. This one ordering trick saves huge time.
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

# Copy ONLY what serve-time needs: the app, the trained model + its card,
# the lead pool the /api/prospects endpoint reads, and the UI.
COPY serve.py .
COPY models/prospect_model.joblib models/prospect_model.json ./models/
COPY data/leads.csv ./data/leads.csv
COPY static/ ./static/

# Document the port the app listens on (informational; -p still does the mapping).
EXPOSE 8000

# HEALTHCHECK: Docker periodically hits /health and marks the container
# "unhealthy" if it stops responding. This is the SAME endpoint we added to
# serve.py -- that is why a health endpoint exists: platforms consume it.
# We use python (already installed) instead of curl (not in the slim image).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Start the API. WHY 0.0.0.0 (not 127.0.0.1): inside a container, 127.0.0.1 is
# only reachable from within the container. 0.0.0.0 lets the mapped port reach it.
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]
