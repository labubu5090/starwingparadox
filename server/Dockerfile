# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv pip install --system --no-cache -e ".[dev]"

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 4001 6666

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4001"]
