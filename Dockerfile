# Stage 1: Build the Nuxt frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ .
RUN npm run generate

# Stage 2: Build the FastAPI backend
FROM python:3.12-slim
WORKDIR /app

# Install uv securely
RUN pip install uv

# Copy backend definitions strictly
COPY backend/pyproject.toml backend/uv.lock* ./backend/
WORKDIR /app/backend
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy actual project files strictly
COPY backend/ .
RUN uv sync --no-dev

# Copy frontend static build (for future serving)
COPY --from=frontend-build /app/frontend/.output/public /app/frontend/.output/public

# Expose FastAPI port
EXPOSE 8000

# Run uvicorn via uv run
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
