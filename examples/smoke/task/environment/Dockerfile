FROM python:3.12-slim

WORKDIR /testbed
RUN printf '%s\n' \
  'def normalize_name(name):' \
  '    return name.strip().lower()' \
  > app.py
RUN mkdir -p /logs/verifier
