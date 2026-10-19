FROM python:3.11.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src:/app

WORKDIR /app

COPY requirements-repro.txt ./
RUN python -m pip install --no-cache-dir pip==24.3.1 \
    && python -m pip install --no-cache-dir -r requirements-repro.txt

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-deps --no-build-isolation .

COPY configs ./configs
COPY harness ./harness
COPY scripts ./scripts
COPY tests ./tests
COPY results ./results
COPY docs ./docs
COPY data/README.md ./data/README.md

ENTRYPOINT ["python", "scripts/container_entrypoint.py"]
CMD ["pytest", "-q"]
