ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

ARG EMAIL
ARG SERVER
ARG SERVER_PASS
ARG PORT

# Set the environment variables
ENV EMAIL=$EMAIL
ENV SERVER=$SERVER
ENV SERVER_PASS=$SERVER_PASS
ENV PORT=$PORT

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Grant permissions to the non-privileged user to the /app directory.
RUN chown -R appuser:appuser /app

# Create the uploads directory and set permissions
RUN mkdir -p /app/static/uploads \
    && chown -R appuser:appuser /app/static/uploads

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
# CMD python server.py
CMD python local-env.py
# CMD gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 0 app:app --keyfile certs/key.pem --certfile certs/cert.pem

# Healthcheck to ensure the container is running correctly.
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --silent --fail http://localhost:5000/healthcheck || exit 1
