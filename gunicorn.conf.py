"""Gunicorn defaults for Render deployments."""

bind = "0.0.0.0:5000"
timeout = 120
graceful_timeout = 30
workers = 1
